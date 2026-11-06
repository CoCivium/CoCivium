import copy
import json
import unittest
from pathlib import Path
from recipe_replay import replay, validate, sha256

RECORDS = json.loads(Path(__file__).with_name("fixture.json").read_text(encoding="utf-8"))
EARLY = "2026-11-02T20:00:00Z"
LATE = "2026-11-02T22:00:00Z"


class RecipeReplayTests(unittest.TestCase):
    def test_deterministic_replay_and_immutable_sources(self):
        before = sha256(RECORDS)
        early = replay(RECORDS, EARLY)
        late = replay(RECORDS, LATE)
        self.assertEqual(before, sha256(RECORDS))
        self.assertEqual(early, replay(RECORDS, EARLY))
        self.assertEqual(late, replay(RECORDS, LATE))
        self.assertEqual(early["source_manifest_sha256"], late["source_manifest_sha256"])
        self.assertNotEqual(early["receipt_sha256"], late["receipt_sha256"])
        self.assertFalse(late["historical_interpretation"]["historical_events_modified"])

    def test_later_evidence_changes_interpretation_not_history(self):
        early = replay(RECORDS, EARLY)
        late = replay(RECORDS, LATE)
        self.assertEqual(early["historical_interpretation"]["state"], "UNTESTED_CROSS_DOMAIN_CANDIDATE")
        self.assertEqual(late["historical_interpretation"]["state"], "MOCK_TEST_PASSED_LIMITED_SCOPE")
        self.assertEqual(len(early["visible_sources"]), 3)
        self.assertEqual(len(late["visible_sources"]), 4)
        self.assertNotIn("synthetic-late-evidence", [x["id"] for x in early["visible_sources"]])

    def test_recipe_inverse_null_and_effect_ceiling(self):
        result = replay(RECORDS, LATE)
        candidates = result["candidates"]
        recipe = next(x for x in candidates if x["id"] == "recipe/evidence-bound-status")
        self.assertEqual(len(recipe["source_ids"]), 2)
        self.assertEqual(result["elected"], [recipe["id"]])
        self.assertTrue({"branch/null", "branch/inverse"} <= {x["id"] for x in candidates})
        self.assertEqual(result["external_effects"], 0)
        self.assertTrue(all(x["effect"] == "NONE" for x in candidates))

    def test_forecast_and_symbolic_nonpromotion(self):
        result = replay(RECORDS, LATE)
        self.assertEqual([x["class"] for x in result["future_branches"]], ["SCENARIO", "COUNTERFACTUAL"])
        sym = next(x for x in result["candidates"] if x["id"] == "branch/gnosis-g_d-symbolic")
        self.assertEqual((sym["state"], sym["authority"]), ("HYPOTHESIS_ONLY", "NONE"))
        self.assertNotIn(sym["id"], result["elected"])

    def test_fail_closed_invalid_fixture(self):
        cases = []
        x = copy.deepcopy(RECORDS); x[0]["id"] = x[1]["id"]; cases.append(x)
        x = copy.deepcopy(RECORDS); x[0]["class"] = "PROVEN_SUPERNATURAL"; cases.append(x)
        x = copy.deepcopy(RECORDS); x[0]["recorded_at"] = "2025-01-01T00:00:00Z"; cases.append(x)
        x = copy.deepcopy(RECORDS); x[0]["source_ref"] = "https://example.org"; cases.append(x)
        for case in cases:
            with self.subTest(record=case[0]):
                with self.assertRaises(ValueError):
                    validate(case)


if __name__ == "__main__":
    unittest.main()
