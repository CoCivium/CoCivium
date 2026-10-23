import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import CoResourceAttractorBenchmarkR1 as a

FIXTURE_PATH = ROOT / "benchmarks" / "resource-attractor" / "r1-fixture.json"


class ResourceAttractorR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.report = a.benchmark(cls.payload)

    def need(self, need_id):
        return next(n for n in self.payload["needs"] if n["need_id"] == need_id)

    def resource(self, resource_id):
        return next(r for r in self.payload["resources"] if r["resource_id"] == resource_id)

    def method_row(self, method, need_id):
        return next(r for r in self.report["methods"][method] if r["need_id"] == need_id)

    def test_fixture_validates(self):
        self.assertEqual(a.validate_fixture(copy.deepcopy(self.payload))["format"], a.FORMAT)

    def test_descriptor_finds_browser_gold(self):
        self.assertEqual(
            self.method_row("descriptor", "browser_evidence")["selected"],
            ["coandrewfirst", "coevidence"],
        )

    def test_descriptor_finds_replay_gold(self):
        self.assertEqual(
            self.method_row("descriptor", "historical_replay")["selected"],
            ["replay_r3", "replaylab_v03"],
        )

    def test_keyword_decoys_reduce_keyword_hits(self):
        self.assertEqual(self.report["summary"]["descriptor"]["hits"], 7)
        self.assertEqual(self.report["summary"]["keyword"]["hits"], 5)
        self.assertTrue(self.report["descriptor_beats_keyword_hits"])

    def test_descriptor_not_worse_than_seeded_random_on_fixture(self):
        self.assertTrue(self.report["descriptor_not_worse_than_random_hits"])
        self.assertGreaterEqual(
            self.report["summary"]["descriptor"]["hits"],
            self.report["summary"]["random"]["hits"],
        )

    def test_private_and_stale_resources_fail_closed(self):
        need = self.need("browser_evidence")
        ok_private, reasons_private = a.eligibility(self.resource("private_browser"), need)
        ok_stale, reasons_stale = a.eligibility(self.resource("stale_browser"), need)
        self.assertFalse(ok_private)
        self.assertIn("PRIVACY_EXCEEDS_CEILING", reasons_private)
        self.assertFalse(ok_stale)
        self.assertIn("STALE", reasons_stale)

    def test_cospirit_hypothesis_not_promoted(self):
        need = self.need("browser_evidence")
        ok, reasons = a.eligibility(self.resource("cospirit_hypothesis"), need)
        self.assertFalse(ok)
        self.assertIn("NOT_QUALIFIED_LIFECYCLE", reasons)
        self.assertIn("RESOURCE_CLASS_NOT_ALLOWED", reasons)
        self.assertEqual(self.report["speculative_selected_in_standard_needs"], [])

    def test_null_resource_can_be_retrieved_as_absence(self):
        row = self.method_row("descriptor", "pi_status")
        self.assertEqual(row["selected"], ["null_pi_adapter"])
        r = self.resource("null_pi_adapter")
        self.assertEqual(r["resource_class"], "null_resource")
        self.assertEqual(r["availability"], "ABSENT")

    def test_anti_resource_can_be_retrieved_when_explicitly_requested(self):
        row = self.method_row("descriptor", "provider_scale_safety")
        self.assertEqual(row["selected"], ["anti_provider_swarm"])
        self.assertEqual(self.resource("anti_provider_swarm")["resource_class"], "anti_resource")

    def test_failure_probes_recover_alternatives(self):
        self.assertTrue(self.report["all_failure_probes_pass"])
        by_need = {p["need_id"]: p for p in self.report["failure_probes"]}
        self.assertIn("coevidence", by_need["browser_evidence"]["selected"])
        self.assertIn("replaylab_v03", by_need["historical_replay"]["selected"])

    def test_zero_effect_boundary(self):
        self.assertEqual(
            self.report["effects"],
            {
                "workers_started": 0,
                "provider_sessions_created": 0,
                "external_mutations": 0,
                "authority_granted": 0,
                "network_calls": 0,
            },
        )

    def test_deterministic_report(self):
        self.assertEqual(self.report, a.benchmark(copy.deepcopy(self.payload)))

    def test_unknown_resource_class_rejected(self):
        bad = copy.deepcopy(self.payload)
        bad["resources"][0]["resource_class"] = "mystical_force"
        with self.assertRaisesRegex(a.AttractorError, "unknown resource class"):
            a.validate_fixture(bad)

    def test_unknown_gold_id_rejected(self):
        bad = copy.deepcopy(self.payload)
        bad["needs"][0]["gold_relevant_ids"].append("not_real")
        with self.assertRaisesRegex(a.AttractorError, "unknown gold id"):
            a.validate_fixture(bad)


if __name__ == "__main__":
    unittest.main()
