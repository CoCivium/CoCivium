import copy
import unittest
from harvest_gate import GateError, evaluate, RESULT_SCHEMA


def fixture():
    engineering = {
        "candidate_id": "a" * 20,
        "axes": {"scenario": "ENGINEERING_DEVICE", "substrate": "DETERMINISTIC_LOCAL", "operator": "NULL"},
        "epistemic_class": "ENGINEERING_CANDIDATE", "proof_boundary": "BOUNDED_POLICY_TEST_ONLY",
        "authority": "NONE", "effects": {"network": 0, "devices": 0, "emails": 0, "workers": 0},
        "score": 64, "micro_canary_eligible": True, "review_state": "PASS_SHADOW_POLICY_ONLY",
    }
    metaphysical = {
        "candidate_id": "b" * 20,
        "axes": {"scenario": "G_D_PHILOSOPHY", "substrate": "HUMAN_REVIEW", "operator": "COUNTERFACTUAL"},
        "epistemic_class": "PHILOSOPHICAL_OR_METAPHORICAL", "proof_boundary": "NOT_AN_EMPIRICAL_ENTITY_FINDER",
        "authority": "NONE", "effects": {"network": 0, "devices": 0, "emails": 0, "workers": 0},
        "score": 100, "micro_canary_eligible": False,
        "review_state": "HELD_NO_QUALIFIED_EXECUTOR_OR_EMPIRICAL_EVIDENCE",
    }
    return {"schema": "CoDoodle.CoNex.CandidateFrontier.R1", "source_sha256": "c" * 64,
            "selected": [engineering, metaphysical], "selected_count": 2,
            "active_workers": 0, "no_execution": True, "total_syntactic_descriptors": "2247370997760"}


class TestHarvestGate(unittest.TestCase):
    def test_one_canary_not_two(self):
        result = evaluate(fixture())
        self.assertEqual(result["schema"], RESULT_SCHEMA)
        self.assertEqual(result["elected_candidate_id"], "a" * 20)
        self.assertEqual(result["considered_count"], 2)
        self.assertFalse(result["receiver_ack"])
        self.assertFalse(result["CoStead_landed"])
        self.assertEqual(result["actual_worker_count"], 0)
        self.assertIn("NULL", result["challenge_operators_present"])

    def test_no_effect_from_high_speculative_score(self):
        inp = fixture()
        inp["selected"] = [inp["selected"][1]]
        inp["selected_count"] = 1
        self.assertIsNone(evaluate(inp)["elected_candidate_id"])

    def test_input_not_mutated_and_repeat_is_stable(self):
        inp = fixture()
        prior = copy.deepcopy(inp)
        self.assertEqual(evaluate(inp), evaluate(inp))
        self.assertEqual(inp, prior)

    def test_authority_escalation_fails_closed(self):
        inp = fixture()
        inp["selected"][0]["authority"] = "SEND_EMAIL"
        with self.assertRaisesRegex(GateError, "AUTHORITY"):
            evaluate(inp)

    def test_device_effect_fails_closed(self):
        inp = fixture()
        inp["selected"][0]["effects"]["devices"] = 1
        with self.assertRaisesRegex(GateError, "EFFECTS"):
            evaluate(inp)

    def test_unknown_effect_fails_closed(self):
        inp = fixture()
        inp["selected"][0]["effects"]["network"] = None
        with self.assertRaisesRegex(GateError, "EFFECTS"):
            evaluate(inp)

    def test_metaphysical_mislabeled_empirical_fails(self):
        inp = fixture()
        inp["selected"][1]["epistemic_class"] = "EMPIRICAL_HYPOTHESIS"
        with self.assertRaisesRegex(GateError, "EVIDENCE_CLASS"):
            evaluate(inp)

    def test_duplicate_ids_fails(self):
        inp = fixture()
        inp["selected"][1]["candidate_id"] = "a" * 20
        with self.assertRaisesRegex(GateError, "DUPLICATE"):
            evaluate(inp)

    def test_invalid_source_binding_fails(self):
        inp = fixture()
        inp["source_sha256"] = "unbound"
        with self.assertRaisesRegex(GateError, "SOURCE_BINDING"):
            evaluate(inp)

    def test_nonlocal_reviewer_cannot_be_approved_by_renaming(self):
        inp = fixture()
        inp["selected"][1]["micro_canary_eligible"] = True
        inp["selected"][1]["review_state"] = "PASS_SHADOW_POLICY_ONLY"
        with self.assertRaisesRegex(GateError, "UNGATED"):
            evaluate(inp)

    def test_bounds_and_unknown_schema(self):
        inp = fixture()
        inp["schema"] = "MYSTERY"
        with self.assertRaisesRegex(GateError, "SCHEMA"):
            evaluate(inp)
        inp = fixture()
        inp["selected_count"] = 3
        with self.assertRaisesRegex(GateError, "COUNT"):
            evaluate(inp)
        inp = fixture()
        inp["selected"] = [copy.deepcopy(inp["selected"][0]) for _ in range(33)]
        inp["selected_count"] = 33
        with self.assertRaisesRegex(GateError, "UNBOUNDED"):
            evaluate(inp)


if __name__ == "__main__":
    unittest.main()
