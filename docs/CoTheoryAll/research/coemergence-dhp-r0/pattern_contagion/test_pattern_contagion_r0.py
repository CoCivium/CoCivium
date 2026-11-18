import copy
import json
import unittest
from pathlib import Path
from pattern_contagion_r0 import Held, validate, forward, backward_candidates, counterfactual, emit, perturb

D = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))

class Tests(unittest.TestCase):
    def mutate(self, key, value):
        x = copy.deepcopy(D)
        x[key] = value
        return x
    def test_fixture(self): self.assertEqual(len(validate(D)[0]), 6)
    def test_deterministic(self): self.assertEqual(emit(D), emit(copy.deepcopy(D)))
    def test_order_independent_nodes(self):
        x = copy.deepcopy(D); x["nodes"].reverse(); x["edges"].reverse()
        self.assertEqual(emit(D), emit(x))
    def test_bounded_ticks(self): self.assertEqual(len(forward(D)["trail"]), D["steps"]+1)
    def test_no_real_world_claim(self): self.assertFalse(emit(D)["forward"]["observed_real_world_transmission"])
    def test_no_benefit_greenwash(self): self.assertIsNone(emit(D)["speedo_projection"]["benefit_needle"])
    def test_effect_hold(self): self.assertFalse(emit(D)["oomph_projection"]["automatic_acceleration"])
    def test_consent_gate(self): self.assertNotIn("receiver", forward(D)["active"])
    def test_synthetic_actives(self): self.assertTrue({"question", "pattern", "speedo", "oomph"}.issubset(forward(D)["active"]))
    def test_backtrace_not_cause(self):
        x = backward_candidates(D, "speedo")
        self.assertIn("pattern", x["candidate_upstream"])
        self.assertFalse(x["causality_established"])
    def test_backcast_no_future_knowledge(self):
        x = backward_candidates(D, "receiver", "BACKCAST")
        self.assertIn("question", x["candidate_upstream"])
        self.assertFalse(x["retrocausality_claim"])
    def test_counterfactual_reduces_active(self):
        x = counterfactual(D, {("pattern", "speedo")})
        self.assertLess(x["delta_synthetic_active"], 0)
    def test_no_edges(self):
        x = self.mutate("edges", [])
        self.assertEqual(forward(x)["active"], ["question"])
    def test_zero_ticks(self):
        x = self.mutate("steps", 0)
        self.assertEqual(forward(x)["active"], ["question"])
    def test_noise_deterministic(self):
        self.assertEqual(perturb(17, 2, "a", 0.2), perturb(17, 2, "a", 0.2))
    def test_noise_control(self):
        x = self.mutate("noise_amplitude", 0.26)
        with self.assertRaises(Held): validate(x)
    def test_no_effects(self):
        x = self.mutate("external_effects", "SEND")
        with self.assertRaises(Held): validate(x)
    def test_duplicate_nodes(self):
        x = copy.deepcopy(D); x["nodes"].append(x["nodes"][0])
        with self.assertRaises(Held): validate(x)
    def test_dangling_edge(self):
        x = copy.deepcopy(D); x["edges"][0]["to"] = "orphan"
        with self.assertRaises(Held): validate(x)
    def test_edge_authority(self):
        x = copy.deepcopy(D); x["edges"][0]["authority"] = "PUBLISH"
        with self.assertRaises(Held): validate(x)
    def test_false_causal_label(self):
        x = copy.deepcopy(D); x["edges"][0]["relation_type"] = "PROVEN_CAUSAL"
        with self.assertRaises(Held): validate(x)
    def test_dupe_edge(self):
        x = copy.deepcopy(D); x["edges"].append(copy.deepcopy(x["edges"][0]))
        with self.assertRaises(Held): validate(x)
    def test_invalid_seed(self):
        x = self.mutate("seeds", ["receiver"])
        with self.assertRaises(Held): validate(x)
    def test_cycle_terminates(self):
        self.assertLessEqual(len(forward(D)["trail"]), 13)
    def test_unknown_counterfactual(self):
        with self.assertRaises(Held): counterfactual(D, {("foo", "bar")})

if __name__ == "__main__": unittest.main()
