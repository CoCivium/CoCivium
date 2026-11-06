#!/usr/bin/env python3
"""CoReaderFederation: source, privacy, expiration, and combinatorial nonclaims."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("reader_route", ROOT / "route.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
AT = "2026-10-25T12:00:00Z"


def run(catalog=None, interests=None, audience="curious", fmt="text",
        mode="SNAPSHOT", when=AT, limit=4):
    return MODULE.preview(CATALOG if catalog is None else catalog,
        ["publishing"] if interests is None else interests,
        audience, fmt, mode, when, limit)


def augmented_offer():
    catalog = copy.deepcopy(CATALOG)
    catalog["entries"][0]["offer"] = {
        "starts_at": "2026-10-24T00:00:00Z",
        "ends_at": "2026-10-26T00:00:00Z",
        "offer_url": catalog["entries"][0]["source_url"],
        "archive_url": catalog["entries"][0]["source_url"],
        "evidence_url": catalog["entries"][0]["source_url"],
    }
    return catalog


class ReaderFederationTests(unittest.TestCase):
    def test_catalog_is_valid(self):
        MODULE.validate_catalog(CATALOG)

    def test_trillion_is_potential_only(self):
        p = run()
        self.assertEqual(int(p["illustrative_space"]["raw_product"]), 10 ** 12)
        self.assertIn("TRILLION_CONFIGURATIONS_NE_TRILLION_MEANINGFUL_PAGES", p["nonclaims"])
        self.assertLessEqual(len(p["candidates"]), 4)

    def test_explicit_interest_ranking(self):
        p = run(interests=["governance"], audience="researcher")
        self.assertEqual(p["selected_count"], 1)
        self.assertEqual(p["candidates"][0]["id"], "civ2-readiness")
        self.assertEqual(p["candidates"][0]["rank_reason"]["declared_topic_matches"], ["governance"])

    def test_interest_changes_relevance_without_profile(self):
        a = run(interests=["education"], audience="educator")
        b = run(interests=["recovery"], audience="researcher")
        self.assertNotEqual(a["candidates"][0]["id"], b["candidates"][0]["id"])
        self.assertFalse(a["privacy"]["click_tracking"])
        self.assertFalse(b["privacy"]["inferred_interests"])

    def test_canonical_bytes_are_not_mutated(self):
        before = copy.deepcopy(CATALOG)
        run()
        self.assertEqual(CATALOG, before)

    def test_empty_interest_is_a_deliberate_all_topics_view(self):
        p = run(interests=[],limit=10)
        self.assertEqual(p["selected_count"], len(CATALOG["entries"]))
        self.assertEqual(len({x["id"] for x in p["candidates"]}), len(CATALOG["entries"]))

    def test_offer_is_active_only_in_real_window(self):
        p = run(catalog=augmented_offer(), when=AT, limit=10)
        item = next(x for x in p["candidates"] if x["id"] == "great-refact")
        self.assertEqual(item["offer"]["state"], "ACTIVE")
        self.assertIsNotNone(item["offer"]["offer_url"])
        self.assertTrue(item["offer"]["evidence_url"].startswith("https://github.com/"))

    def test_expired_offer_keeps_source_and_archive(self):
        p = run(catalog=augmented_offer(), when="2026-10-27T00:00:00Z", limit=10)
        item = next(x for x in p["candidates"] if x["id"] == "great-refact")
        self.assertEqual(item["offer"]["state"], "EXPIRED")
        self.assertIsNone(item["offer"]["offer_url"])
        self.assertTrue(item["public_source_url"])
        self.assertTrue(item["offer"]["archive_url"])
        self.assertTrue(item["historical_source_preserved"])

    def test_upcoming_offer_is_not_exposed_as_active(self):
        p = run(catalog=augmented_offer(), when="2026-10-23T00:00:00Z", limit=10)
        item = next(x for x in p["candidates"] if x["id"] == "great-refact")
        self.assertEqual(item["offer"]["state"], "UPCOMING")
        self.assertIsNone(item["offer"]["offer_url"])

    def test_missing_offer_evidence_fails_closed(self):
        catalog = augmented_offer()
        del catalog["entries"][0]["offer"]["evidence_url"]
        with self.assertRaises(ValueError):
            run(catalog=catalog)

    def test_reverse_or_naive_time_fails_closed(self):
        catalog = augmented_offer()
        catalog["entries"][0]["offer"]["ends_at"] = "2026-10-23T00:00:00Z"
        with self.assertRaises(ValueError):
            run(catalog=catalog)
        catalog = augmented_offer()
        catalog["entries"][0]["offer"]["starts_at"] = "2026-10-25T00:00:00"
        with self.assertRaises(ValueError):
            run(catalog=catalog)

    def test_untrusted_url_fails_closed(self):
        for link in ("http://github.com/CoCivium/x", "https://evil.example/capture",
                     "https://github.com@evil.example/x"):
            catalog = copy.deepcopy(CATALOG)
            catalog["entries"][0]["source_url"] = link
            with self.subTest(link=link), self.assertRaises(ValueError):
                run(catalog=catalog)

    def test_unknown_explicit_interest_fails_closed(self):
        for choices in (["mysticism"], ["publishing", "publishing"], "publishing"):
            with self.subTest(choices=choices), self.assertRaises(ValueError):
                run(interests=choices)

    def test_bad_mode_and_limit_fail_closed(self):
        for m in ("AUTO_PUBLISH", "SILENT_REWRITE"):
            with self.subTest(mode=m), self.assertRaises(ValueError):
                run(mode=m)
        for bound in (-1, 11, True):
            with self.subTest(limit=bound), self.assertRaises(ValueError):
                run(limit=bound)

    def test_deterministic_with_explicit_timestamp(self):
        self.assertEqual(run(), run())
        self.assertNotEqual(run(when=AT)["selection"]["as_of"],
            run(when="2026-10-26T12:00:00Z")["selection"]["as_of"])

    def test_github_pointer_not_immutable_snapshot_proof(self):
        for item in run(interests=[], limit=10)["candidates"]:
            self.assertEqual(len(item["source_git_blob_sha"]), 40)
            self.assertEqual(item["source_pointer_freshness"], "NOT_LIVE_VERIFIED")
            self.assertEqual(item["observed_version_recovery"],
                "REQUIRES_EXACT_GIT_BLOB_FETCH_AND_READPROOF")

    def test_zero_external_effects(self):
        p = run(mode="DIFF_AVAILABLE")
        self.assertEqual(sum(p["effects"].values()), 0)
        self.assertEqual(p["privacy"]["subscriptions_created"], 0)
        self.assertIn("DIFF_AVAILABLE_NE_ACTUAL_PUSH_OR_LIVE_DIFF", p["nonclaims"])


if __name__ == "__main__":
    unittest.main()
