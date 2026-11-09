"""Adversarial regression tests for CoNoDrop public frontier validation."""
import copy
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "validate_frontier_index.py"
spec = importlib.util.spec_from_file_location("frontier_validator", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASE = {
    "schema": "cocivium.frontier-index.r0",
    "fronts": [
        {"id": ident, "status": "proposed", "next_gate": "independent observation", "blocked_claims": ["UNVERIFIED"]}
        for ident in sorted(mod.REQUIRED)
    ],
}


class NoDropTests(unittest.TestCase):
    def test_valid_baseline(self):
        self.assertEqual(mod.validate(copy.deepcopy(BASE)), [])

    def test_front_disappearance_fails(self):
        data = copy.deepcopy(BASE)
        data["fronts"].pop()
        self.assertTrue(any("missing tracked front" in x for x in mod.validate(data)))

    def test_missing_next_gate_fails(self):
        data = copy.deepcopy(BASE)
        data["fronts"][0].pop("next_gate")
        self.assertTrue(any("missing next gate" in x for x in mod.validate(data)))

    def test_duplicate_identity_fails(self):
        data = copy.deepcopy(BASE)
        data["fronts"].append(copy.deepcopy(data["fronts"][0]))
        self.assertIn("duplicate front IDs", mod.validate(data))

    def test_claim_promotion_without_receipt_fails(self):
        data = copy.deepcopy(BASE)
        data["fronts"][0]["status"] = "tests_executed"
        self.assertTrue(any("requires scoped test receipt" in x for x in mod.validate(data)))

    def test_unverified_blocker_must_be_structured(self):
        data = copy.deepcopy(BASE)
        data["fronts"][0]["blocked_claims"] = "none"
        self.assertTrue(any("blocked claims must be string array" in x for x in mod.validate(data)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
