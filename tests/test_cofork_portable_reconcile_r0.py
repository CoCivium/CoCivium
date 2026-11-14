#!/usr/bin/env python3
"""Adversarial synthetic-only tests; never inspect or mutate provider conversations."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoForkPortableReconcileR0 import (
    BUNDLE, Held, SCHEMA, canonical, reconcile, sha, verify_bundle,
)


def fixture():
    return {
        "schema": SCHEMA, "scope": "PUBLIC_SYNTHETIC",
        "work_id": "cofork:synthetic:two-viewers:r0",
        "common_base": {
            "goal": "Recover one synthetic task",
            "progress": "base",
            "next_deed": "inspect",
        },
        "forks": {
            "edge": {
                "snapshot": {
                    "goal": "Recover one synthetic task",
                    "progress": "edge evidence added",
                    "next_deed": "inspect",
                },
                "reported_state": "PENDING",
            },
            "firefox": {
                "snapshot": {
                    "goal": "Recover one synthetic task",
                    "progress": "base",
                    "next_deed": "independently check",
                },
                "reported_state": "HELD",
            },
        },
    }


class ForkPortabilityR0(unittest.TestCase):
    def raw(self, p=None):
        return canonical(p if p is not None else fixture())

    def test_disjoint_edits_yield_only_proposal(self):
        result = reconcile(self.raw())
        self.assertEqual(result["state"], "MERGE_PROPOSAL_ONLY")
        self.assertFalse(result["receiver_ack"])
        self.assertFalse(result["authorized_merge"])
        self.assertEqual(result["proposed_snapshot"]["progress"], "edge evidence added")
        self.assertEqual(result["proposed_snapshot"]["next_deed"], "independently check")
        self.assertEqual(result["source_statuses_unverified"]["firefox"], "HELD")

    def test_conflicting_edits_hold_without_losing_either(self):
        p = fixture()
        p["forks"]["firefox"]["snapshot"]["progress"] = "firefox alternative"
        raw = self.raw(p)
        result = reconcile(raw)
        self.assertEqual(result["state"], "CONFLICT_HELD")
        self.assertIsNone(result["proposed_snapshot"])
        self.assertEqual(result["conflicts"]["progress"]["edge"], "edge evidence added")
        self.assertEqual(result["conflicts"]["progress"]["firefox"], "firefox alternative")
        self.assertEqual(verify_bundle(result), raw)
        self.assertFalse(result["source_history_deleted"])

    def test_same_concurrent_edit_is_deduplicated_without_ack(self):
        p = fixture()
        p["forks"]["firefox"]["snapshot"]["progress"] = "edge evidence added"
        result = reconcile(self.raw(p))
        self.assertEqual(result["state"], "MERGE_PROPOSAL_ONLY")
        self.assertFalse(result["receiver_ack"])
        self.assertFalse(result["authorized_merge"])

    def test_changed_reported_state_does_not_promote_receiver(self):
        p = fixture()
        p["forks"]["edge"]["reported_state"] = "UNVERIFIED"
        result = reconcile(self.raw(p))
        self.assertEqual(result["source_statuses_unverified"]["edge"], "UNVERIFIED")
        self.assertFalse(result["receiver_ack"])

    def test_missing_ancestor_or_wrong_scope_holds(self):
        p = fixture()
        del p["common_base"]
        with self.assertRaisesRegex(Held, "HELD_INPUT_SCHEMA"):
            reconcile(self.raw(p))
        p = fixture()
        p["scope"] = "PRIVATE_LIVE_CHAT"
        with self.assertRaisesRegex(Held, "HELD_NOT_PUBLIC_SYNTHETIC"):
            reconcile(self.raw(p))

    def test_missing_or_third_fork_holds(self):
        p = fixture()
        del p["forks"]["edge"]
        with self.assertRaisesRegex(Held, "HELD_FORK_COUNT"):
            reconcile(self.raw(p))
        p = fixture()
        p["forks"]["third"] = copy.deepcopy(p["forks"]["edge"])
        with self.assertRaisesRegex(Held, "HELD_FORK_COUNT"):
            reconcile(self.raw(p))

    def test_tampered_source_or_manifest_holds(self):
        p = reconcile(self.raw())
        modified = copy.deepcopy(p)
        modified["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(Held, "HELD_SOURCE_HASH"):
            verify_bundle(modified)
        modified = copy.deepcopy(p)
        modified["receiver_ack"] = True
        with self.assertRaisesRegex(Held, "HELD_BUNDLE_MANIFEST_TAMPER"):
            verify_bundle(modified)
        modified = copy.deepcopy(p)
        modified["proposed_snapshot"]["goal"] = "unauthorized rewrite"
        with self.assertRaisesRegex(Held, "HELD_BUNDLE_MANIFEST_TAMPER"):
            verify_bundle(modified)

    def test_wrong_field_or_type_holds(self):
        p = fixture()
        p["forks"]["edge"]["snapshot"]["progress"] = True
        with self.assertRaisesRegex(Held, "HELD_FORK_SNAPSHOT"):
            reconcile(self.raw(p))
        p = fixture()
        p["common_base"]["injected_key"] = "silently merged"
        with self.assertRaisesRegex(Held, "HELD_BASE"):
            reconcile(self.raw(p))

    def test_portable_cold_process_reads_same_exact_bytes(self):
        p = fixture()
        p["forks"]["firefox"]["snapshot"]["progress"] = "other progress"
        raw = self.raw(p)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source, bundle = root / "fixture.json", root / "bundle.json"
            source.write_bytes(raw)
            cmd = [sys.executable, "-B", str(ROOT/"scripts"/"CoForkPortableReconcileR0.py")]
            first = subprocess.run(cmd + ["--input",str(source),"--output",str(bundle)],
                                   capture_output=True,text=True,check=True)
            self.assertIn("CONFLICT_HELD", first.stdout)
            frozen = bundle.read_bytes()
            cold = subprocess.run(cmd + ["--verify",str(bundle)],
                                  capture_output=True,text=True,check=True)
            self.assertIn(sha(raw), cold.stdout)
            self.assertEqual(frozen, bundle.read_bytes())
            self.assertEqual(verify_bundle(json.loads(frozen)), raw)
            # A second write cannot overwrite the existing bundle.
            overwrite = subprocess.run(cmd + ["--input",str(source),"--output",str(bundle)],
                                       capture_output=True,text=True)
            self.assertNotEqual(overwrite.returncode,0)
            self.assertEqual(frozen,bundle.read_bytes())

    def test_roundtrip_keeps_utf8_exactly(self):
        p = fixture()
        p["forks"]["edge"]["snapshot"]["goal"] = "Renamed label: 文字"
        raw = self.raw(p)
        self.assertEqual(verify_bundle(reconcile(raw)), raw)


if __name__ == "__main__":
    unittest.main()
