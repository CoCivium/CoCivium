"""Positive source-pin and convergence checks from immutable Git history.

Requires full Git history (CI checkout fetch-depth: 0). No network fetch here.
"""
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from workid_source_pin import EXPECTED_COMMIT, EXPECTED_REF, EXPECTED_SHA256, verify_source
from workid_convergence import inspect_with_source
from workid_handoff_gate import WORK_ID


def pinned_source_bytes():
    repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{EXPECTED_COMMIT}:CoPre.md"],
        capture_output=True, check=False,
    )
    if proc.returncode != 0:
        raise AssertionError("Pinned Git object unavailable; full history required")
    return proc.stdout


class HistoricalSourcePinTests(unittest.TestCase):
    def test_pinned_git_object_matches_fixture_and_verifier(self):
        raw = pinned_source_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "CoPre.md"
            source.write_bytes(raw)
            result = verify_source(source, EXPECTED_REF)
            self.assertEqual(result["state"], "SOURCE_BYTES_MATCH_FIXTURE_PIN")
            self.assertTrue(result["source_verified"])
            self.assertFalse(result["authenticated_origin"])
            self.assertFalse(result["receiver_ack"])

    def test_pinned_source_converges_to_proposal_never_ack(self):
        raw = pinned_source_bytes()
        packet = dict(
            schema="CoAll.CoOwnedWork.BrowserLocal.R0.Packet",
            work_id=WORK_ID, source_ref=EXPECTED_REF, source_sha256=EXPECTED_SHA256,
            narrative_summary="Synthetic public WorkID source verification",
            prior_decisions=[], open_blockers=[], next_safe_deed="Inspect synthetic proof",
            privacy="PUBLIC_SYNTHETIC", consent="SYNTHETIC_TEST_ONLY", lease_epoch=1,
        )
        authorization = dict(
            scope="PUBLIC_SYNTHETIC_HANDOFF", source_ref=EXPECTED_REF, consent_epoch=1,
        )
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "CoPre.md"
            source.write_bytes(raw)
            result = inspect_with_source(packet, authorization, source)
            self.assertEqual(result["state"], "PROPOSAL_SOURCE_BYTES_MATCHED_ONLY")
            self.assertEqual(result["work_id"], WORK_ID)
            self.assertFalse(result["authenticated_origin"])
            self.assertFalse(result["authorization_authenticated"])
            self.assertFalse(result["receiver_ack"])


    def test_browser_to_sqlite_adapter_cold_replay_conflict_and_revoke(self):
        from workid_sqlite_adapter import commit_proposal
        from CoNarrativeWorkIDR0 import Held, readback, revoke
        raw = pinned_source_bytes()
        packet = dict(
            schema="CoAll.CoOwnedWork.BrowserLocal.R0.Packet",
            work_id=WORK_ID, source_ref=EXPECTED_REF, source_sha256=EXPECTED_SHA256,
            narrative_summary="Synthetic browser to durable receiver",
            prior_decisions=["Source pinned"], open_blockers=["External ACK absent"],
            next_safe_deed="Cold readback", privacy="PUBLIC_SYNTHETIC",
            consent="SYNTHETIC_TEST_ONLY", lease_epoch=1,
        )
        auth = dict(scope="PUBLIC_SYNTHETIC_HANDOFF",
                    source_ref=EXPECTED_REF, consent_epoch=1)
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "CoPre.md"
            source.write_bytes(raw)
            db = Path(d) / "receiver.sqlite"
            first = commit_proposal(db, packet, auth, source)
            self.assertEqual(first["new_commits"], 1)
            self.assertFalse(first["external_receiver_ack"])
            second = commit_proposal(db, packet, auth, source)
            self.assertEqual(second["new_commits"], 0)
            self.assertTrue(second["duplicate"])
            changed = dict(packet, narrative_summary="Different synthetic payload")
            with self.assertRaisesRegex(Held, "WORK_ID_REVISION_CONFLICT"):
                commit_proposal(db, changed, auth, source)
            with self.assertRaisesRegex(Held, "BROWSER_PROPOSAL_HELD"):
                commit_proposal(db, packet, dict(auth, consent_epoch=2), source)
            from workid_sqlite_adapter import adapt_proposal
            converted = adapt_proposal(packet, auth, source)
            revoke(db, converted)
            self.assertEqual(readback(db)["state"], "HELD_REVOKED")
            with self.assertRaisesRegex(Held, "HELD_REVOKED"):
                commit_proposal(db, packet, auth, source)


if __name__ == "__main__":
    unittest.main()
