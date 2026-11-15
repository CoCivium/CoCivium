"""Quality-diversity adversarial controls for CoWave selection."""
import unittest
from wave_diversity_r0 import Deed, Wave, choose_wave, similarity


class WaveDiversityTests(unittest.TestCase):
    def deed(self, name, front="orb", method="test", **changes):
        base = dict(deed_id=name, front_id=front, work_id=name,
                    source_revision="sha-demo", method=method,
                    expected_evidence="receiver-readback",
                    collision_domain=front + ":" + name)
        return Deed(**{**base, **changes})

    def test_dissimilar_waves_have_lower_similarity(self):
        a = Wave("a", (self.deed("a", "orb", "browser"),))
        b = Wave("b", (self.deed("b", "media", "image"),))
        self.assertLess(similarity(a, b), 0.5)

    def test_necessary_repeated_maintenance_not_blocked(self):
        prev = Wave("old", (self.deed("old", "seed", "verify"),))
        new = self.deed("new", "seed", "verify")
        elected = choose_wave((new,), (prev,), continuity_fronts=("seed",))
        self.assertEqual(elected["wave"].deeds, (new,))

    def test_uncovered_front_receives_preference(self):
        prev = Wave("old", (self.deed("old", "orb"),))
        other = self.deed("other", "media")
        same = self.deed("same", "orb")
        result = choose_wave((same, other), (prev,), max_deeds=1)
        self.assertEqual(result["wave"].deeds[0].front_id, "media")

    def test_critical_continuity_beats_novelty(self):
        prev = Wave("old", (self.deed("old", "seed"),))
        seed = self.deed("seed-r", "seed", priority=1)
        flashy = self.deed("flashy", "new", priority=100)
        result = choose_wave((flashy, seed), (prev,), max_deeds=1,
                             continuity_fronts=("seed",))
        self.assertEqual(result["wave"].deeds, (seed,))

    def test_blocked_deed_not_elected(self):
        result = choose_wave((self.deed("a", blocked="OFFLINE"),), ())
        self.assertFalse(result["wave"].deeds)
        self.assertEqual(result["holds"][0][1], "BLOCKED:OFFLINE")

    def test_authority_boundary_precedes_diversity(self):
        result = choose_wave((self.deed("a", authority="PUBLIC_SEND"),), ())
        self.assertEqual(result["holds"][0][1], "AUTHORITY_GATE")

    def test_duplicate_work_id_fenced(self):
        a = self.deed("a", work_id="same")
        b = self.deed("b", work_id="same")
        result = choose_wave((a, b), (), max_deeds=2)
        self.assertEqual(len(result["wave"].deeds), 1)
        self.assertIn("DUPLICATE_EFFECT_HOLD", [x[1] for x in result["holds"]])

    def test_collision_domain_fenced(self):
        a = self.deed("a", collision_domain="same")
        b = self.deed("b", collision_domain="same")
        self.assertEqual(len(choose_wave((a, b), (), max_deeds=2)["wave"].deeds), 1)

    def test_missing_source_revision_holds(self):
        result = choose_wave((self.deed("a", source_revision=""),), ())
        self.assertEqual(result["holds"][0][1], "MISSING_EVIDENCE_POINTER")

    def test_cost_and_capacity_limit(self):
        a = self.deed("a", cost=4)
        b = self.deed("b", cost=4)
        result = choose_wave((a, b), (), max_cost=5)
        self.assertEqual(len(result["wave"].deeds), 1)
        self.assertLessEqual(result["used_cost"], 5)

    def test_uncovered_required_front_is_reported_not_faked(self):
        result = choose_wave((self.deed("a", "orb"),), (),
                             continuity_fronts=("orb", "seed"))
        self.assertEqual(result["uncovered_required_fronts"], ("seed",))

    def test_no_candidates_means_no_activity(self):
        result = choose_wave((), ())
        self.assertFalse(result["wave"].deeds)
        self.assertTrue(result["no_worker_execution_claimed"])


if __name__ == "__main__":
    unittest.main()
