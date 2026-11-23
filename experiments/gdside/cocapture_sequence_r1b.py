"""CoPriMath261122 R1B: synthetic cumulative-capture adversarial canary.

Pure Python, no network, no real governance/consent/identity verification, no effects.
Thresholds are illustrative; passing tests is not security certification.
"""
from dataclasses import dataclass, replace
from math import isfinite
import unittest

@dataclass(frozen=True)
class Policy:
    id: str = "COEBE-CANDIDATE-R1B"
    max_control: float = 0.55
    max_exit_friction: float = 0.45
    max_control_growth: float = 0.22
    min_independent_domains: int = 2

@dataclass(frozen=True)
class State:
    control: float = 0.20
    exit_friction: float = 0.10
    rights_veto: bool = True
    policy_id: str = "COEBE-CANDIDATE-R1B"

@dataclass(frozen=True)
class Mutation:
    id: str
    control_delta: float = 0.0
    exit_delta: float = 0.0
    effectful: bool = False
    bypass_rights: bool = False
    rewrite_policy: bool = False
    suppress_dissent: bool = False
    prevent_exit: bool = False
    claimed_witnesses: tuple[str, ...] = ()  # self-asserted, never trusted

@dataclass(frozen=True)
class Result:
    verdict: str
    state: State
    reasons: tuple[str, ...]
    checked: int

def fraction(x):
    return type(x) in (int, float) and isfinite(x) and 0 <= x <= 1

def naive(m):
    """Deliberately inadequate per-change safety check."""
    return abs(m.control_delta) <= 0.12 and abs(m.exit_delta) <= 0.12

def review(baseline, changes, policy, externally_qualified_domains=frozenset()):
    """Synthetic REVIEW ONLY. Trusted input is not cryptographically authenticated."""
    if (not policy.id or baseline.policy_id != policy.id or not baseline.rights_veto
            or not fraction(baseline.control) or not fraction(baseline.exit_friction)):
        return Result("HOLD", baseline, ("BASELINE_OR_GUARD_UNTRUSTED",), 0)
    if not changes:
        return Result("NO_CHANGE", baseline, (), 0)
    state, seen = baseline, set()
    for i, m in enumerate(changes, 1):
        if not m.id or m.id in seen:
            return Result("HOLD", baseline, ("DUPLICATE_OR_MISSING_ID",), i)
        seen.add(m.id)
        if m.rewrite_policy:
            return Result("HOLD", baseline, ("SELF_AMENDMENT_BLOCKED",), i)
        if m.bypass_rights or m.suppress_dissent or m.prevent_exit:
            return Result("HOLD", baseline, ("RIGHTS_DISSENT_OR_EXIT_HARM",), i)
        if not all(type(v) in (int, float) and isfinite(v)
                   for v in (m.control_delta, m.exit_delta)):
            return Result("HOLD", baseline, ("BAD_DELTA",), i)
        # Count only externally supplied qualified domains, not claimed_witnesses.
        if m.effectful and len(externally_qualified_domains) < policy.min_independent_domains:
            return Result("HOLD", baseline, ("INDEPENDENCE_UNPROVEN",), i)
        c, e = state.control + m.control_delta, state.exit_friction + m.exit_delta
        if not fraction(c) or not fraction(e):
            return Result("HOLD", baseline, ("INVALID_RESULT_STATE",), i)
        if (c > policy.max_control or e > policy.max_exit_friction
                or c - baseline.control > policy.max_control_growth):
            return Result("HOLD", baseline, ("CUMULATIVE_CAPTURE",), i)
        state = replace(state, control=c, exit_friction=e)
    return Result("REVIEW_CANDIDATE", state, (), len(changes))

class FiniteTests(unittest.TestCase):
    def setUp(self):
        self.p, self.s = Policy(), State()
    def test_naive_four_locally_pass(self):
        self.assertTrue(all(naive(Mutation(str(i), .1, .05)) for i in range(4)))
    def test_four_collectively_hold(self):
        r = review(self.s, tuple(Mutation(str(i), .1, .05) for i in range(4)), self.p)
        self.assertEqual(r.reasons, ("CUMULATIVE_CAPTURE",))
        self.assertEqual(r.state, self.s)
    def test_two_remain_review_only(self):
        self.assertEqual(review(self.s, (Mutation('a', .09), Mutation('b', .09)), self.p).verdict, 'REVIEW_CANDIDATE')
    def test_self_rewrite(self):
        self.assertEqual(review(self.s, (Mutation('a', rewrite_policy=True),), self.p).verdict, 'HOLD')
    def test_rights(self):
        self.assertEqual(review(self.s, (Mutation('a', bypass_rights=True),), self.p).verdict, 'HOLD')
    def test_dissent(self):
        self.assertEqual(review(self.s, (Mutation('a', suppress_dissent=True),), self.p).verdict, 'HOLD')
    def test_no_exit(self):
        self.assertEqual(review(self.s, (Mutation('a', prevent_exit=True),), self.p).verdict, 'HOLD')
    def test_fake_witnesses(self):
        r = review(self.s, (Mutation('a', effectful=True, claimed_witnesses=('one','two')),), self.p)
        self.assertEqual(r.reasons, ('INDEPENDENCE_UNPROVEN',))
    def test_single_real_witness_not_enough(self):
        r = review(self.s, (Mutation('a', effectful=True),), self.p, frozenset({'one'}))
        self.assertEqual(r.verdict, 'HOLD')
    def test_qualified_domains_not_effect_authority(self):
        r = review(self.s, (Mutation('a', effectful=True),), self.p, frozenset({'one','two'}))
        self.assertEqual(r.verdict, 'REVIEW_CANDIDATE')
    def test_false_policy_identity(self):
        self.assertEqual(review(replace(self.s, policy_id='attacker'), (Mutation('a'),), self.p).verdict, 'HOLD')
    def test_removed_rights_veto(self):
        self.assertEqual(review(replace(self.s, rights_veto=False), (Mutation('a'),), self.p).verdict, 'HOLD')
    def test_duplicate_ids(self):
        self.assertEqual(review(self.s, (Mutation('a'), Mutation('a')), self.p).verdict, 'HOLD')
    def test_nan(self):
        self.assertEqual(review(self.s, (Mutation('a', float('nan')),), self.p).verdict, 'HOLD')
    def test_bool_not_numeric(self):
        self.assertEqual(review(self.s, (Mutation('a', True),), self.p).verdict, 'HOLD')
    def test_transient_capture_then_recovery(self):
        self.assertEqual(review(self.s, (Mutation('a', .30), Mutation('b', -.30)), self.p).verdict, 'HOLD')
    def test_accumulated_exit_friction(self):
        r = review(self.s, (Mutation('a', exit_delta=.20), Mutation('b', exit_delta=.20)), self.p)
        self.assertEqual(r.reasons, ('CUMULATIVE_CAPTURE',))
    def test_no_mutations_no_success(self):
        self.assertEqual(review(self.s, (), self.p).verdict, 'NO_CHANGE')

if __name__ == '__main__':
    unittest.main()
