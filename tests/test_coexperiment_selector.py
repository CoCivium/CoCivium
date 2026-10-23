from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "CoExperimentSelectorR0.py"
IMPORT = importlib.util.spec_from_file_location("selector", SCRIPT)
selector = importlib.util.module_from_spec(IMPORT)
IMPORT.loader.exec_module(selector)


def metrics(values, prefix):
    return {
        name: {"value": value, "evidence_ref": f"{prefix}:{name}"}
        for name, value in zip(selector.BENEFITS if prefix.startswith("b") else selector.PENALTIES, values)
    }


def candidate(
    cid,
    *,
    lanes=(),
    benefits=(50, 50, 50, 50, 50),
    penalties=(50, 50, 50, 50, 50),
    family="MODEL_QUALITY",
    substrate="LOCAL_MODEL",
    focus="CORRECTNESS",
):
    return {
        "experiment_descriptor_id": cid,
        "facets": {
            "experiment_family": family,
            "substrate_class": substrate,
            "evaluation_focus": focus,
        },
        "lanes": list(lanes),
        "benefits": metrics(benefits, "benefit"),
        "penalties": metrics(penalties, "penalty"),
    }


def payload():
    return {
        "format": "CoExperimentSelectorInputR0",
        "selection_slots": 6,
        "reserves": {
            "CHALLENGE": 1,
            "EXPLORATION": 1,
            "WEIRD": 1,
            "REPLAY": 1,
            "FAULT": 1,
        },
        "candidates": [
            candidate(
                "exp:champion",
                benefits=(90, 90, 95, 55, 80),
                penalties=(15, 15, 10, 15, 10),
                focus="RECEIVER_VALUE",
            ),
            candidate(
                "exp:challenge",
                lanes=("CHALLENGE",),
                benefits=(75, 98, 75, 70, 85),
                penalties=(20, 25, 15, 20, 20),
                focus="CORRECTNESS",
            ),
            candidate(
                "exp:explore",
                lanes=("EXPLORATION",),
                benefits=(90, 75, 65, 99, 70),
                penalties=(25, 30, 20, 25, 25),
                family="RETRIEVAL",
                substrate="DETERMINISTIC_LOCAL",
            ),
            candidate(
                "exp:weird",
                lanes=("WEIRD",),
                benefits=(80, 70, 55, 100, 55),
                penalties=(30, 35, 25, 30, 25),
                family="UX_ACCESSIBILITY",
                substrate="BROWSER_STATIC",
                focus="ACCESSIBILITY",
            ),
            candidate(
                "exp:replay",
                lanes=("REPLAY",),
                benefits=(85, 80, 70, 85, 65),
                penalties=(25, 35, 20, 25, 25),
                family="HISTORICAL_REPLAY",
                substrate="DETERMINISTIC_LOCAL",
                focus="PROOF_DEBT",
            ),
            candidate(
                "exp:fault",
                lanes=("FAULT",),
                benefits=(88, 95, 80, 75, 75),
                penalties=(30, 30, 25, 25, 20),
                family="FAULT_INJECTION",
                substrate="GITHUB_CI",
                focus="RECOVERY_TIME",
            ),
            candidate(
                "exp:dominated",
                benefits=(20, 20, 20, 20, 20),
                penalties=(90, 90, 90, 90, 90),
            ),
            candidate(
                "exp:alternate",
                benefits=(78, 82, 88, 65, 78),
                penalties=(18, 22, 18, 18, 15),
                family="PROVENANCE",
                substrate="MCP_ADAPTER",
                focus="PROOF_DEBT",
            ),
        ],
    }


class CoExperimentSelectorTests(unittest.TestCase):
    def test_selector_is_zero_execution(self):
        result = selector.select(payload())
        self.assertEqual(result["state"], "SELECTOR_OUTPUT__ZERO_EXECUTION")
        self.assertEqual(result["effects"]["experiments_executed"], 0)
        self.assertEqual(result["effects"]["workers_started"], 0)
        self.assertEqual(result["effects"]["provider_sessions_created"], 0)
        self.assertEqual(result["effects"]["external_mutations"], 0)

    def test_reserved_lanes_are_filled_when_candidates_exist(self):
        result = selector.select(payload())
        lanes = {
            decision["reserved_lane"]
            for decision in result["selection_order"]
            if decision["reserved_lane"] is not None
        }
        self.assertEqual(lanes, set(selector.LANES))
        self.assertEqual(result["unfilled_reserves"], {})

    def test_selection_is_bounded_and_unique(self):
        result = selector.select(payload())
        self.assertEqual(result["selected_count"], 6)
        ids = result["selected_descriptor_ids"]
        self.assertEqual(len(ids), len(set(ids)))

    def test_dominated_candidate_is_on_later_pareto_layer(self):
        data = payload()
        layers = selector.pareto_layers(data["candidates"])
        self.assertGreater(layers["exp:dominated"], 0)
        self.assertEqual(layers["exp:champion"], 0)

    def test_no_single_scalar_quality_score(self):
        result = selector.select(payload())
        policy = result["ranking_policy"]
        self.assertFalse(policy["single_scalar_quality_score"])
        self.assertFalse(policy["raw_descriptor_facets_auto_scored"])
        self.assertEqual(policy["primary"], "PARETO_LAYER")

    def test_selector_is_deterministic(self):
        self.assertEqual(selector.select(payload()), selector.select(payload()))

    def test_unfilled_reserve_is_explicit(self):
        data = payload()
        data["candidates"] = [
            item for item in data["candidates"] if "WEIRD" not in item["lanes"]
        ]
        result = selector.select(data)
        self.assertEqual(result["unfilled_reserves"], {"WEIRD": 1})
        self.assertLessEqual(result["selected_count"], data["selection_slots"])

    def test_metric_evidence_reference_is_required(self):
        data = payload()
        data["candidates"][0]["benefits"]["information_gain"]["evidence_ref"] = ""
        with self.assertRaisesRegex(selector.SelectorError, "evidence_ref"):
            selector.select(data)

    def test_metric_range_fails_closed(self):
        data = payload()
        data["candidates"][0]["penalties"]["risk"]["value"] = 101
        with self.assertRaisesRegex(selector.SelectorError, "integer 0..100"):
            selector.select(data)

    def test_reserve_sum_cannot_exceed_slots(self):
        data = payload()
        data["selection_slots"] = 3
        with self.assertRaisesRegex(selector.SelectorError, "sum of reserves"):
            selector.select(data)

    def test_duplicate_candidate_id_fails_closed(self):
        data = payload()
        data["candidates"].append(data["candidates"][0].copy())
        with self.assertRaisesRegex(selector.SelectorError, "duplicate experiment_descriptor_id"):
            selector.select(data)

    def test_diversity_is_not_claimed_as_independence(self):
        result = selector.select(payload())
        self.assertIn("DIVERSITY_NE_INDEPENDENCE", result["nonclaims"])
        self.assertIn("SELECTED_NE_EXECUTED", result["nonclaims"])


if __name__ == "__main__":
    unittest.main()
