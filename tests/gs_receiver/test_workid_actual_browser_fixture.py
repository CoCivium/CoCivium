"""Bridge the actual browser JS fixture to the existing synthetic SQLite receiver.

This is an offline Node -> Python integration regression, NOT browser transport,
authenticated human consent, external receiver ACK, or deployment.
Requires node and full git history (receiver-reconciliation CI provides both).
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from workid_sqlite_adapter import adapt_proposal, commit_proposal
from CoNarrativeWorkIDR0 import Held, readback, revoke
from workid_source_pin import EXPECTED_COMMIT, EXPECTED_REF, EXPECTED_SHA256

REPO = Path(__file__).resolve().parents[2]
BROWSER_JS = REPO / "examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js"


def actual_browser_fixture():
    result = subprocess.run(
        ["node", "-e", "process.stdout.write(JSON.stringify(require(process.argv[1]).fixture()))",
         str(BROWSER_JS)],
        check=True, capture_output=True, text=True, timeout=15,
    )
    return json.loads(result.stdout)


def historical_source():
    return subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"{EXPECTED_COMMIT}:CoPre.md"], timeout=15
    )


class ActualBrowserFixtureReceiverTests(unittest.TestCase):
    def test_exact_js_fixture_cold_readback_replay_conflict_and_revoke(self):
        packet = actual_browser_fixture()
        self.assertEqual(packet["source_ref"], EXPECTED_REF)
        self.assertEqual(packet["source_sha256"], EXPECTED_SHA256)
        auth = {"scope": "PUBLIC_SYNTHETIC_HANDOFF",
                "source_ref": EXPECTED_REF, "consent_epoch": 1}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "CoPre.md"
            source.write_bytes(historical_source())
            db = Path(directory) / "receiver.sqlite"
            converted = adapt_proposal(packet, auth, source)
            for key in ("work_id", "source_ref", "source_sha256",
                        "narrative_summary", "prior_decisions", "open_blockers",
                        "next_safe_deed", "lease_epoch"):
                self.assertEqual(converted[key], packet[key])
            self.assertEqual(converted["consent_epoch"], 1)
            first = commit_proposal(db, packet, auth, source)
            self.assertEqual(first["new_commits"], 1)
            self.assertFalse(first["external_receiver_ack"])
            duplicate = commit_proposal(db, packet, auth, source)
            self.assertEqual(duplicate["new_commits"], 0)
            self.assertTrue(duplicate["duplicate"])
            self.assertEqual(first["receipt_sha256"], duplicate["receipt_sha256"])
            self.assertEqual(readback(db, expected_packet=converted, source_path=source)
                             ["state"], "COLD_SOURCE_RECONSTRUCTED")
            with self.assertRaisesRegex(Held, "WORK_ID_REVISION_CONFLICT"):
                commit_proposal(db, dict(packet, narrative_summary="Changed"), auth, source)
            with self.assertRaisesRegex(Held, "BROWSER_PROPOSAL_HELD"):
                commit_proposal(db, packet, dict(auth, consent_epoch=2), source)
            revoke(db, converted)
            self.assertEqual(readback(db)["state"], "HELD_REVOKED")
            with self.assertRaisesRegex(Held, "HELD_REVOKED"):
                commit_proposal(db, packet, auth, source)


if __name__ == "__main__":
    unittest.main()
