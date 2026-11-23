"""R1C independent-style adversarial harness against R1B, with a fail-closed shim.

This is a second source implementation, NOT an independent person, host or verifier.
It intentionally cannot authenticate human consent, keys, witnesses or effects.
"""
import dataclasses
import importlib.util
from pathlib import Path
import sys
import unittest

P = Path(__file__).with_name("cocapture_sequence_r1b.py")
spec = importlib.util.spec_from_file_location("copri_r1b", P)
r1b = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r1b
spec.loader.exec_module(r1b)

# This pinned fixture is an example of a separately governed immutable policy.
# Source-level pinning does not secure an actual runtime or signing keys.
PINNED = r1b.Policy()

def reviewed_without_effects(baseline, changes, supplied_policy=PINNED, witnesses=frozenset()):
    """Reject policy substitution and effects before invoking the R1B pure evaluator."""
    if type(supplied_policy) is not r1b.Policy or supplied_policy != PINNED:
        return r1b.Result("HOLD", baseline, ("POLICY_DIGEST_OR_CONTENT_MISMATCH",), 0)
    if type(baseline) is not r1b.State or baseline.policy_id != PINNED.id:
        return r1b.Result("HOLD", baseline, ("BASELINE_UNTRUSTED",), 0)
    if any(type(m) is not r1b.Mutation for m in changes):
        return r1b.Result("HOLD", baseline, ("MUTATION_TYPE_UNTRUSTED",), 0)
    if any(m.effectful for m in changes):
        return r1b.Result("HOLD", baseline, ("EFFECT_AUTHORITY_UNVERIFIED",), 0)
    # Do not accept claimed or caller-supplied witness identities as proof.
    return r1b.review(baseline, changes, PINNED, frozenset())

class AdversarialR1C(unittest.TestCase):
    def setUp(self):
        self.s = r1b.State()
    def test_reproduce_threshold_substitution_in_r1b(self):
        p = dataclasses.replace(PINNED, max_control=1.0, max_control_growth=1.0)
        x = r1b.review(self.s, (r1b.Mutation("a", .7),), p)
        self.assertEqual(x.verdict, "REVIEW_CANDIDATE")
    def test_reject_threshold_substitution_r1c(self):
        p = dataclasses.replace(PINNED, max_control=1.0, max_control_growth=1.0)
        x = reviewed_without_effects(self.s, (r1b.Mutation("a", .7),), p)
        self.assertEqual(x.reasons, ("POLICY_DIGEST_OR_CONTENT_MISMATCH",))
    def test_reproduce_caller_claimed_independence_r1b(self):
        x = r1b.review(self.s, (r1b.Mutation("a", effectful=True),), PINNED, frozenset({"w1","w2"}))
        self.assertEqual(x.verdict, "REVIEW_CANDIDATE")
    def test_reject_effectful_even_with_claimed_witnesses(self):
        x = reviewed_without_effects(self.s, (r1b.Mutation("a", effectful=True),), PINNED, frozenset({"w1","w2"}))
        self.assertEqual(x.reasons, ("EFFECT_AUTHORITY_UNVERIFIED",))
    def test_reject_different_policy_id(self):
        p = dataclasses.replace(PINNED, id="lookalike")
        self.assertEqual(reviewed_without_effects(self.s, (), p).verdict, "HOLD")
    def test_reject_weaker_control_growth(self):
        p = dataclasses.replace(PINNED, max_control_growth=.8)
        self.assertEqual(reviewed_without_effects(self.s, (), p).verdict, "HOLD")
    def test_reject_weaker_exit_limit(self):
        p = dataclasses.replace(PINNED, max_exit_friction=.9)
        self.assertEqual(reviewed_without_effects(self.s, (), p).verdict, "HOLD")
    def test_reject_lookalike_policy_type(self):
        class Subclass(r1b.Policy): pass
        self.assertEqual(reviewed_without_effects(self.s, (), Subclass()).verdict, "HOLD")
    def test_reject_malformed_mutation_subclass(self):
        class Subclass(r1b.Mutation): pass
        self.assertEqual(reviewed_without_effects(self.s, (Subclass("a"),)).verdict, "HOLD")
    def test_safe_mutation_still_review_only(self):
        self.assertEqual(reviewed_without_effects(self.s, (r1b.Mutation("a", .05),)).verdict, "REVIEW_CANDIDATE")
    def test_cumulative_capture_still_hold(self):
        x = reviewed_without_effects(self.s, tuple(r1b.Mutation(str(i), .1, .05) for i in range(4)))
        self.assertEqual(x.reasons, ("CUMULATIVE_CAPTURE",))
    def test_policy_rewrite_still_hold(self):
        self.assertEqual(reviewed_without_effects(self.s, (r1b.Mutation("a", rewrite_policy=True),)).verdict, "HOLD")
    def test_no_change_not_approval(self):
        self.assertEqual(reviewed_without_effects(self.s, ()).verdict, "NO_CHANGE")
    def test_fake_witnesses_not_used_for_non_effectful(self):
        a=reviewed_without_effects(self.s,(r1b.Mutation("a"),),witnesses=frozenset({"faker"}))
        b=reviewed_without_effects(self.s,(r1b.Mutation("a"),))
        self.assertEqual(a,b)

if __name__ == "__main__":
    unittest.main()
