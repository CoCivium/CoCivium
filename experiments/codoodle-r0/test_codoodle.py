#!/usr/bin/env python3
"""Offline adversarial and property checks for CoDoodle descriptor adapter R0."""
from __future__ import annotations

import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import codoodle as co

FIXTURE = (Path(__file__).parent / "synthetic_doodle.txt").read_bytes()


class CoDoodleR0Tests(unittest.TestCase):
    def setUp(self):
        self.p = co.parse_doodle(FIXTURE)

    def test_01_exact_source_hash(self):
        self.assertEqual(self.p["source_sha256"], co.digest(FIXTURE))

    def test_02_source_text_is_not_embedded(self):
        self.assertNotIn("synthetic CoDoodle fixture", json.dumps(self.p))

    def test_03_empty_source_blocks(self):
        with self.assertRaises(ValueError): co.parse_doodle(b"")

    def test_04_oversize_blocks_no_truncation(self):
        with self.assertRaises(ValueError): co.parse_doodle(b"x" * (co.MAX_SOURCE_BYTES+1))

    def test_05_malformed_utf8_blocks(self):
        with self.assertRaises(ValueError): co.parse_doodle(b"\xff\xfe")

    def test_06_password_assignment_blocks(self):
        with self.assertRaises(ValueError): co.parse_doodle(b"password=ABC123987secret")

    def test_07_api_secret_assignment_blocks(self):
        with self.assertRaises(ValueError): co.parse_doodle(b"api_key: EXAMPLE_SECRET_123456")

    def test_08_key_banner_blocks(self):
        with self.assertRaises(ValueError): co.parse_doodle(b"-----BEGIN PRIVATE KEY-----\nabc")

    def test_09_credential_discussion_not_secret(self):
        self.assertTrue(co.parse_doodle(b"test credentials health without exposing secrets"))

    def test_10_unicode_source_preserves_hash(self):
        src = "\u2282EvoAll+ \u2192 CoMap".encode("utf-8")
        self.assertEqual(co.parse_doodle(src)["source_sha256"], co.digest(src))

    def test_11_topic_is_only_hint(self):
        self.assertEqual(self.p["semantic_certainty"], "NONE_KEYWORD_HINTS_ONLY")

    def test_12_detects_input_topic(self):
        self.assertIn("DEVICE_INPUT", self.p["topics_hint_only"])

    def test_13_detects_symbolic_topic(self):
        self.assertTrue(self.p["symbolic_or_speculative_terms_detected"])

    def test_14_unknown_input_does_not_claim_semantics(self):
        p = co.parse_doodle(b"glorb glorp flarbnk")
        self.assertEqual(p["topics_hint_only"], [])

    def test_15_large_logical_space_is_only_counted(self):
        self.assertGreater(co.logical_count(), 1_000_000)

    def test_16_rank_encode_decode_roundtrip(self):
        gen = random.Random(9)
        for _ in range(500):
            rank = gen.randrange(co.logical_count())
            self.assertEqual(co.encode_facets(co.decode_rank(rank)), rank)

    def test_17_rank_boundaries(self):
        for rank in (-1, co.logical_count(), "1", True):
            with self.assertRaises(ValueError): co.decode_rank(rank)

    def test_18_unknown_axis_value_held(self):
        x = co.decode_rank(99); x["perspective"] = "TRULY_EXTRATERRESTRIAL_OBSERVER"
        with self.assertRaises(ValueError): co.encode_facets(x)

    def test_19_sample_plan_coprime(self):
        _, step, total = co.sample_plan(self.p, "test")
        import math
        self.assertEqual(math.gcd(step, total), 1)

    def test_20_deterministic_exact_candidate_set(self):
        a = co.make_preview(self.p, limit=80, seed="same")
        b = co.make_preview(self.p, limit=80, seed="same")
        self.assertEqual(co.fingerprint(a), co.fingerprint(b))

    def test_21_different_seeds_do_change_candidates(self):
        a = co.make_preview(self.p, limit=16, seed="A")
        b = co.make_preview(self.p, limit=16, seed="B")
        self.assertNotEqual([x["experiment_descriptor_id"] for x in a["sample"]],
                            [x["experiment_descriptor_id"] for x in b["sample"]])

    def test_22_unique_sample_and_bounded_limit(self):
        a = co.make_preview(self.p, limit=co.MAX_SAMPLE, seed="max")
        ids = [c["experiment_descriptor_id"] for c in a["sample"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), co.MAX_SAMPLE)

    def test_23_invalid_sample_limits(self):
        for limit in (0, -1, co.MAX_SAMPLE + 1, 0.2, "2", True):
            with self.assertRaises(ValueError): co.make_preview(self.p, limit=limit)

    def test_24_focus_and_open_both_preserved(self):
        a = co.make_preview(co.parse_doodle(b"keyboard only"), limit=20)
        self.assertEqual(a["sample_buckets"], {"SOURCE_TOPIC_HINTS": 15, "OPEN_ELSE_SPACE": 5})
        self.assertTrue(all(c["facets"]["experiment_family"] == "DEVICE_INPUT"
                            for c in a["sample"] if c["sampling_bucket"] == "SOURCE_TOPIC_HINTS"))

    def test_25_unknown_topics_go_all_open(self):
        a = co.make_preview(co.parse_doodle(b"florb"), limit=7)
        self.assertEqual(a["sample_buckets"]["OPEN_ELSE_SPACE"], 7)

    def test_26_science_remains_unverified(self):
        a = co.make_preview(self.p)
        self.assertTrue(all(c["scientific_claim_status"] == "UNVERIFIED" for c in a["sample"]))

    def test_27_fiction_stays_fictional(self):
        p = self.p
        r = next(i for i in range(co.logical_count()) if co.decode_rank(i)["perspective"] == "ET_FICTIONAL")
        c = co.candidate(p, r)
        self.assertEqual(c["epistemic_class"], "FICTIONAL_VIEWPOINT")
        self.assertIn("WEIRD", c["lanes"])

    def test_28_logical_time_is_not_physics(self):
        a = co.make_preview(self.p)
        self.assertTrue(all(c["time_semantics"] == "LOGICAL_ORDER_IS_NOT_TIMELESS_PHYSICS" for c in a["sample"]))

    def test_29_everything_has_no_authority(self):
        a = co.make_preview(self.p)
        self.assertTrue(all(c["authority"] == "NONE" and c["external_effects"] == 0 for c in a["sample"]))

    def test_30_no_auto_scores_for_selector(self):
        a = co.make_preview(self.p)
        self.assertEqual(a["selector_handoff"]["state"], "HELD_UNSCORED")
        self.assertTrue(all(c["estimated_benefits"] is None for c in a["sample"]))

    def test_31_negative_authority_rejected(self):
        c = co.make_preview(self.p, limit=1)["sample"][0]
        c["authority"] = "ALL"
        self.assertIn("EFFECT_AUTHORITY_ESCALATION", co.validate_candidate(c, self.p["source_sha256"]))

    def test_32_negative_lied_execution_rejected(self):
        c = co.make_preview(self.p, limit=1)["sample"][0]
        c["state"] = "COMPLETE"
        self.assertIn("FALSE_EXECUTION_STATUS", co.validate_candidate(c, self.p["source_sha256"]))

    def test_33_negative_source_swap_rejected(self):
        c = co.make_preview(self.p, limit=1)["sample"][0]
        c["source_sha256"] = "f"*64
        self.assertIn("SOURCE_BINDING_MISMATCH", co.validate_candidate(c, self.p["source_sha256"]))

    def test_34_negative_sci_claim_rejected(self):
        c = co.make_preview(self.p, limit=1)["sample"][0]
        c["scientific_claim_status"] = "ESTABLISHED_NEW_LAW"
        self.assertIn("UNJUSTIFIED_SCIENCE_CLAIM", co.validate_candidate(c, self.p["source_sha256"]))

    def test_35_negative_facet_mutation_rejected(self):
        c = co.make_preview(self.p, limit=1)["sample"][0]
        c["facets"]["time_frame"] = "NEW_PHYSICS"
        self.assertTrue(co.validate_candidate(c, self.p["source_sha256"]))

    def test_36_negative_fiction_mislabeled_rejected(self):
        rank = next(i for i in range(co.logical_count()) if co.decode_rank(i)["perspective"] == "ET_FICTIONAL")
        c = co.candidate(self.p, rank)
        c["epistemic_class"] = "OBSERVED_REAL_ET"
        self.assertIn("FICTION_PRESENTED_AS_FACT", co.validate_candidate(c, self.p["source_sha256"]))

    def test_37_negative_lanes_changed_rejected(self):
        c = co.make_preview(self.p, limit=1)["sample"][0]
        c["lanes"] = ["UNLIMITED"]
        self.assertIn("LANE_MISMATCH", co.validate_candidate(c, self.p["source_sha256"]))

    def test_38_microcanary_runs_and_detects_injected_controls(self):
        a = co.make_preview(self.p, limit=32)
        r = co.static_microcanary(a)
        self.assertEqual(r["failed"], 0)
        self.assertEqual(r["passed"], 11)
        self.assertEqual(r["external_experiments_executed"], 0)

    def test_39_bench_counters_are_bounded(self):
        with self.assertRaises(ValueError): co.benchmark(self.p, iterations=1)
        with self.assertRaises(ValueError): co.benchmark(self.p, iterations=co.MAX_BENCH_ITERATIONS+1)
        with self.assertRaises(ValueError): co.benchmark(self.p, iterations=100, batches=41)

    def test_40_benchmark_reports_distinct_tiers(self):
        r = co.benchmark(self.p, iterations=1000, batches=4)
        self.assertGreater(r["address_only_amortized_batch_p50_us"], 0)
        self.assertGreater(r["complete_24_descriptor_preview_median_ms"], 0)
        self.assertEqual(r["external_experiments"], 0)

    def test_41_cli_offline_writes_only_scoped_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out"
            source = Path(d) / "source.txt"; source.write_bytes(FIXTURE)
            cp = subprocess.run([sys.executable, str(Path(__file__).parent/"codoodle.py"),
                        "--text-file", str(source), "--out", str(out), "--limit", "5"],
                        capture_output=True, text=True, timeout=15)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            self.assertEqual(len((out/"candidates.jsonl").read_text().splitlines()), 5)
            self.assertEqual(sorted(x.name for x in out.iterdir()),
                 ["candidates.jsonl", "preview.json", "static_microcanary.json"])

    def test_42_cli_secret_input_does_not_write_candidate_files(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out"
            source = Path(d) / "source.txt"; source.write_text("password: ExampleSecret123456789")
            cp = subprocess.run([sys.executable, str(Path(__file__).parent/"codoodle.py"),
                        "--text-file", str(source), "--out", str(out)],
                        capture_output=True, text=True, timeout=15)
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
