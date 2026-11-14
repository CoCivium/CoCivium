"""Bounded CoPreGeneric retro-CoEcho sample: historical conservation, not a census."""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ai/onramp/copregeneric-retro-echo-sample-20261109.json"
SAFE_PATH = re.compile(r"^[A-Za-z0-9_./+-]{1,200}$")
BLOB = re.compile(r"^[0-9a-f]{40}$")


def audit(obj: dict) -> dict:
    if obj.get("schema") != "CoAll.CoPreGeneric.RetroEchoSample.R0":
        raise ValueError("WRONG_SCHEMA")
    coverage = obj["coverage"]
    if coverage["complete_history"] is not False or coverage["unscanned_sources"] != "UNKNOWN":
        raise ValueError("FALSE_CENSUS_COMPLETENESS")
    if coverage["private_sources"] != "NOT_INSPECTED":
        raise ValueError("PRIVATE_SOURCE_SCOPE_MISREPRESENTED")
    items = obj["candidates"]
    if not isinstance(items, list) or len(items) > 30:
        raise ValueError("UNBOUNDED_SAMPLE")
    found = {}
    for item in items:
        ident, path = item["id"], item["source_path"]
        if ident in found:
            raise ValueError("DUPLICATE_HISTORICAL_ID")
        if not isinstance(path, str) or not SAFE_PATH.fullmatch(path) or ".." in path.split("/"):
            raise ValueError("UNSAFE_SOURCE_PATH")
        b = item["source_blob"]
        if b is not None and (not isinstance(b, str) or not BLOB.fullmatch(b)):
            raise ValueError("INVALID_SOURCE_BLOB")
        if item["role"] not in {
            "HISTORICAL_WITNESS", "HISTORICAL_PUBLIC_SNAPSHOT",
            "PRESERVATION_POLICY_CANDIDATE", "LIFECYCLE_POLICY_CANDIDATE",
            "RECENT_CANDIDATE_BRANCH_NOT_MERGED"
        }:
            raise ValueError("UNVERIFIED_PROMOTION_ROLE")
        found[ident] = item
    chronological = sorted(items, key=lambda i:(i["event_at"],i["id"]))
    if chronological != items:
        raise ValueError("NOT_CHRONOLOGICAL")
    for item in items:
        for target in item["links"]:
            if target not in found:
                raise ValueError("BROKEN_REVERSE_OR_FORWARD_POINTER")
            if found[target]["event_at"] < item["event_at"]:
                raise ValueError("HIDDEN_REVERSE_TIME_CLAIM")
    if obj["transitions"]["picked_up"] != "UNPROVEN" or obj["transitions"]["coex"] != "UNPROVEN":
        raise ValueError("FALSE_PROMOTION")
    return {"state":"PASS_BOUNDED_METADATA_STRUCTURE","sample_count":len(items),
            "exact_blob_bound":sum(x["source_blob"] is not None for x in items),
            "unscanned":"UNKNOWN","actual_receiver_ack":False}


class RetroEchoAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj = json.loads(SOURCE.read_text("utf-8"))

    def test_sample_contract(self):
        r = audit(self.obj)
        self.assertEqual(r["sample_count"],5)
        self.assertFalse(r["actual_receiver_ack"])

    def test_no_complete_history_claim(self):
        o=copy.deepcopy(self.obj)
        o["coverage"]["complete_history"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_CENSUS"):audit(o)

    def test_unknown_private_not_scanned(self):
        o=copy.deepcopy(self.obj)
        o["coverage"]["private_sources"]="PUBLIC"
        with self.assertRaisesRegex(ValueError,"PRIVATE_SOURCE"):audit(o)

    def test_historical_duplicate_held(self):
        o=copy.deepcopy(self.obj)
        o["candidates"].append(copy.deepcopy(o["candidates"][-1]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):audit(o)

    def test_time_reordering_rejected(self):
        o=copy.deepcopy(self.obj)
        o["candidates"]=list(reversed(o["candidates"]))
        with self.assertRaisesRegex(ValueError,"NOT_CHRONOLOGICAL"):audit(o)

    def test_broken_link_rejected(self):
        o=copy.deepcopy(self.obj)
        o["candidates"][0]["links"]=["echo:missing"]
        with self.assertRaisesRegex(ValueError,"BROKEN"):audit(o)

    def test_no_unreviewed_role_promotion(self):
        o=copy.deepcopy(self.obj)
        o["candidates"][0]["role"]="CURRENT_CANON"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_PROMOTION"):audit(o)

    def test_receiver_ack_does_not_appear_from_landing(self):
        o=copy.deepcopy(self.obj)
        o["transitions"]["picked_up"]="PROVEN"
        with self.assertRaisesRegex(ValueError,"FALSE_PROMOTION"):audit(o)

    def test_no_private_paths_or_unsafe_names(self):
        o=copy.deepcopy(self.obj)
        o["candidates"][0]["source_path"]="../private/secret.txt"
        with self.assertRaisesRegex(ValueError,"UNSAFE_SOURCE_PATH"):audit(o)

    def test_source_blob_requires_exact_git40(self):
        o=copy.deepcopy(self.obj)
        o["candidates"][1]["source_blob"]="fakehash"
        with self.assertRaisesRegex(ValueError,"INVALID_SOURCE_BLOB"):audit(o)


if __name__=="__main__":
    unittest.main()
