from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "CoHistoricalReplayPlannerR0.py"
IMPORT = importlib.util.spec_from_file_location("historical_replay", SCRIPT)
replay = importlib.util.module_from_spec(IMPORT)
IMPORT.loader.exec_module(replay)

SOURCE_PATH = "ai/currentness/session-writeback-r1.json"
SOURCE_BLOB = "30307b6f36d9baa6324a84a17acd1080205afa46"


def base_spec():
    return {
        "format": "CoHistoricalReplaySpecR0",
        "source": {
            "path": SOURCE_PATH,
            "git_blob_sha1": SOURCE_BLOB,
            "source_ref": "repository-history-r1",
            "artifact_kind": "HISTORICAL_REPOSITORY_RECORD",
        },
        "historical_environment": {
            "provider": None,
            "model_id": None,
            "model_version": None,
            "tool_environment": None,
            "completeness": "UNKNOWN",
        },
        "target_lanes": [
            "DETERMINISTIC_BASELINE",
            "LOCAL_MODEL",
            "CLAUDE",
            "OPENAI_COMPATIBLE",
        ],
        "evaluation_dimensions": [
            "SOURCE_FIDELITY",
            "EVIDENCE_QUALITY",
            "UNCERTAINTY_CALIBRATION",
            "CONTRADICTION_HANDLING",
            "REPRODUCIBILITY",
        ],
        "preserve_original": True,
        "execution_policy": "PLAN_ONLY",
    }


class HistoricalReplayPlannerTests(unittest.TestCase):
    def test_real_repository_artifact_compiles_zero_execution_plan(self):
        plan = replay.build_plan(ROOT, base_spec())
        self.assertEqual(plan["state"], "HISTORICAL_REPLAY_PLAN__ZERO_EXECUTION")
        self.assertFalse(plan["execution_performed"])
        self.assertEqual(plan["external_effects"], 0)
        self.assertEqual(len(plan["replay_cells"]), 4)
        self.assertTrue(all(
            cell["state"] == "PLANNED__NOT_EXECUTED"
            for cell in plan["replay_cells"]
        ))

    def test_unknown_historical_environment_stays_explicit(self):
        plan = replay.build_plan(ROOT, base_spec())
        self.assertEqual(
            plan["historical_unknown_fields"],
            ["provider", "model_id", "model_version", "tool_environment"],
        )
        self.assertTrue(all(
            cell["historical_equivalence"] == "NOT_CLAIMED"
            for cell in plan["replay_cells"]
        ))

    def test_provider_diversity_is_not_evidence_independence(self):
        plan = replay.build_plan(ROOT, base_spec())
        self.assertFalse(
            plan["comparison_policy"]["provider_diversity_implies_independent_evidence"]
        )
        self.assertTrue(all(
            cell["evidence_independence"] == "UNKNOWN__SHARED_SOURCE_ARTIFACT"
            for cell in plan["replay_cells"]
        ))

    def test_newer_model_is_not_assumed_better(self):
        plan = replay.build_plan(ROOT, base_spec())
        self.assertFalse(plan["comparison_policy"]["newer_model_implies_better"])
        self.assertFalse(plan["comparison_policy"]["same_prompt_same_experiment"])
        self.assertIn("NEWER_MODEL_NE_BETTER_RESULT", plan["nonclaims"])

    def test_plan_is_deterministic(self):
        self.assertEqual(
            replay.build_plan(ROOT, base_spec()),
            replay.build_plan(ROOT, base_spec()),
        )

    def test_source_bytes_are_not_changed(self):
        path = ROOT / SOURCE_PATH
        before = path.read_bytes()
        replay.build_plan(ROOT, base_spec())
        self.assertEqual(path.read_bytes(), before)

    def test_blob_mismatch_holds(self):
        spec = base_spec()
        spec["source"]["git_blob_sha1"] = "0" * 40
        with self.assertRaisesRegex(replay.ReplayError, "source bytes"):
            replay.build_plan(ROOT, spec)

    def test_path_traversal_holds(self):
        spec = base_spec()
        spec["source"]["path"] = "../outside.json"
        with self.assertRaises(replay.ReplayError):
            replay.build_plan(ROOT, spec)

    def test_duplicate_and_unknown_lanes_hold(self):
        duplicate = base_spec()
        duplicate["target_lanes"].append("CLAUDE")
        with self.assertRaisesRegex(replay.ReplayError, "duplicate target lane"):
            replay.validate_spec(duplicate)

        unknown = base_spec()
        unknown["target_lanes"] = ["UNREGISTERED"]
        with self.assertRaisesRegex(replay.ReplayError, "unknown target lane"):
            replay.validate_spec(unknown)

    def test_original_must_be_preserved_and_policy_must_be_plan_only(self):
        for mutation in (
            lambda spec: spec.update({"preserve_original": False}),
            lambda spec: spec.update({"execution_policy": "EXECUTE"}),
        ):
            spec = base_spec()
            mutation(spec)
            with self.assertRaises(replay.ReplayError):
                replay.validate_spec(spec)


if __name__ == "__main__":
    unittest.main()
