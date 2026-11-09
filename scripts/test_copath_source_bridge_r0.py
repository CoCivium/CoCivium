#!/usr/bin/env python3
"""CoPath proof boundaries and fail-closed tests; no external effects."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from CoPathSourceBridgeR0 import assess, canonical, git_blob, validate, write_receipt

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "ai/copregeneric/copath-front-bridge-r0-20261109.json"


def loaded():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_graph():
    v = loaded()
    for s in v["sources"]:
        if s["id"] == "copre-entry":
            s["git_blob_sha1"] = git_blob(b"known mock source")
        elif s["id"] == "seed-fabric":
            s["git_blob_sha1"] = git_blob(b"other known source")
    return v


class CoPathSourceBridgeTests(unittest.TestCase):
    def test_manifest_validate_and_no_ambiguous_canon(self):
        v = loaded()
        sources = validate(v)
        self.assertGreaterEqual(len(sources), 10)
        self.assertEqual(v["path_rules"]["external_effect_authority"], "NONE")
        self.assertEqual(v["selected_receiver_readproof_state"], "NONE")
        self.assertTrue(all(not m["verified"] for m in v["website_mirrors"]))

    def test_every_route_bounded_source_linked_and_reusable(self):
        v = loaded()
        sources = validate(v)
        self.assertGreaterEqual(len(v["routes"]), 5)
        for role, ids in v["routes"].items():
            self.assertEqual(ids[0], "copre-entry")
            self.assertEqual(len(ids), len(set(ids)))
            self.assertTrue(all(s in sources for s in ids))
        self.assertIn("pr429-graph", v["routes"]["synth"])
        self.assertIn("retro-coverage", v["routes"]["recovery"])
        self.assertIn("highlights", v["routes"]["highlight"])
        self.assertIn("corun-donor", v["routes"]["builder"])
        self.assertIn("comvp-controller", v["routes"]["lockstep"])
        self.assertEqual(sources["corun-donor"]["branch"], "corun")

    def test_valid_mock_source_readback_not_receiver_pickup(self):
        v = test_graph()
        v["routes"]["testonly"] = ["copre-entry", "seed-fabric"]
        def reader(branch, path):
            if path == "CoPre.md":
                return b"known mock source"
            return b"other known source"
        proof = assess(v, "testonly", reader)
        self.assertEqual(proof["status"], "SOURCE_PATH_READBACK__NOT_PICKUP")
        self.assertEqual(proof["source_readbacks"], 2)
        self.assertFalse(proof["receiver_acknowledged"])
        self.assertFalse(proof["public_mirrors_qualified"])
        self.assertEqual(proof["effects"], "NONE")
        self.assertEqual(proof["cross_front_integration"], "NOT_ESTABLISHED")

    def test_corun_branch_donor_no_promotion(self):
        v = test_graph()
        v["sources"][-1]["git_blob_sha1"] = git_blob(b"separate donor")
        v["routes"]["testonly"] = ["copre-entry", "corun-donor"]
        proof = assess(v, "testonly", lambda branch, path:
                       b"known mock source" if branch == "main" else b"separate donor")
        self.assertEqual(proof["status"], "SOURCE_PATH_READBACK__NOT_PICKUP")
        self.assertEqual(proof["route"][1]["branch"], "corun")
        self.assertFalse(proof["receiver_acknowledged"])
        self.assertEqual(proof["cross_front_integration"], "NOT_ESTABLISHED")

    def test_tampered_source_fails_without_promotion(self):
        v = test_graph()
        v["routes"]["testonly"] = ["copre-entry"]
        proof = assess(v, "testonly", lambda branch, path: b"tampered")
        self.assertEqual(proof["status"], "HELD_SOURCE_PATH_UNVERIFIED")
        self.assertEqual(proof["route"][0]["readback_state"], "HELD_PIN_MISMATCH")
        self.assertIsNone(proof["route"][0]["receiver_ack"])

    def test_missing_source_held_not_fabricated(self):
        v = test_graph()
        v["routes"]["testonly"] = ["copre-entry"]
        def not_found(branch, path):
            raise OSError("not present")
        proof = assess(v, "testonly", not_found)
        self.assertEqual(proof["route"][0]["readback_state"], "HELD_SOURCE_UNAVAILABLE")
        self.assertIsNone(proof["route"][0]["source_sha256_actual"])

    def test_dropped_source_link_blocks_contract(self):
        v = loaded()
        v["sources"] = [x for x in v["sources"] if x["id"] != "pr429-graph"]
        with self.assertRaisesRegex(ValueError, "UNRESOLVED_ROUTE"):
            validate(v)

    def test_duplicate_sources_fail(self):
        v = loaded()
        v["sources"].append(copy.deepcopy(v["sources"][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_SOURCE_ID"):
            validate(v)

    def test_unsafe_path_fails(self):
        v = loaded()
        v["sources"][0]["path"] = "../../private/notes"
        with self.assertRaisesRegex(ValueError, "UNSAFE_PATH"):
            validate(v)

    def test_claimed_authority_mirrors_or_receiver_fail(self):
        v = loaded()
        v["path_rules"]["external_effect_authority"] = "SEND_EMAIL"
        with self.assertRaisesRegex(ValueError, "EFFECT_AUTHORITY_NOT_FENCED"):
            validate(v)
        v = loaded()
        v["website_mirrors"][0]["verified"] = True
        with self.assertRaisesRegex(ValueError, "MIRRORS_UNEARNED"):
            validate(v)
        v = loaded()
        v["sources"][0]["receiver_ack"] = "SELF_CLAIMED"
        with self.assertRaisesRegex(ValueError, "SELF_REPORTED_RECEIVER_ACK"):
            validate(v)

    def test_unknown_role_fails(self):
        with self.assertRaisesRegex(ValueError, "UNKNOWN_ROLE"):
            assess(loaded(), "anything_not_elected", lambda branch, path: b"")

    def test_receipt_sha_and_no_overwrite(self):
        result = assess(test_graph(), "synth", lambda branch, path: b"wrong")
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "receipt.json"
            digest = write_receipt(file, result)
            self.assertEqual(digest, hashlib.sha256(file.read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):
                write_receipt(file, result)


if __name__ == "__main__":
    unittest.main()
