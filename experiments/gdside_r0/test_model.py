"""Negative controls for speculative G_dSide comparison."""
import unittest
from dataclasses import replace
from model import Candidate, METRICS, SCENARIOS, dominates, frontier, interaction, synthetic_candidate

class TestCandidate(unittest.TestCase):
    def test_future_scenario_can_win(self):
        self.assertEqual(frontier(SCENARIOS["future_benefit"]), ["gdside"])

    def test_backcast_can_lose(self):
        self.assertEqual(frontier(SCENARIOS["backcast_overfit"]), ["supply"])

    def test_rights_veto(self):
        self.assertEqual(frontier(SCENARIOS["rights_veto"]), ["supply"])

    def test_label_cannot_create_dominance(self):
        a = synthetic_candidate("gdside", (5,5,5,5,5,5))
        b = synthetic_candidate("demand", (5,5,5,5,5,5))
        self.assertFalse(dominates(a,b))
        self.assertEqual(frontier([a,b]), ["demand","gdside"])

    def test_incomparability_retained(self):
        a = synthetic_candidate("gdside", (8,8,8,8,8,2))
        b = synthetic_candidate("ecological", (6,6,6,6,3,1))
        self.assertEqual(frontier([a,b]), ["ecological","gdside"])

    def test_invalid_dimensions_fail(self):
        with self.assertRaisesRegex(ValueError, "SCHEMA"):
            frontier([Candidate("bad",{"flourishing":5})])

    def test_interaction_positive_negative(self):
        base=frozenset()
        v={base:0, frozenset({"a"}):3, frozenset({"b"}):2,
           frozenset({"a","b"}):7}
        self.assertEqual(interaction(v,base,"a","b"),2)
        v[frozenset({"a","b"})]=4
        self.assertEqual(interaction(v,base,"a","b"),-1)

    def test_duplicate_intervention_rejected(self):
        with self.assertRaises(ValueError):
            interaction({},frozenset(),"a","a")

    def test_identical_words_and_numbers_different_metric_contract_hold(self):
        a = synthetic_candidate("community-a", (5,5,5,5,5,5))
        b = replace(synthetic_candidate("community-b", (6,6,6,6,4,4)),
                    metric_contracts={**a.metric_contracts,
                                      "flourishing": "fixture:distinct-cultural-sense"})
        with self.assertRaisesRegex(ValueError, "INCOMMENSURABLE_CONTEXT"):
            frontier([a, b])
        with self.assertRaisesRegex(ValueError, "INCOMMENSURABLE_CONTEXT"):
            dominates(a, b)

    def test_same_metric_contract_different_affected_population_hold(self):
        a = synthetic_candidate("a", (5,5,5,5,5,5))
        b = replace(synthetic_candidate("b", (6,6,6,6,4,4)),
                    affected_scope="fixture:other-population")
        with self.assertRaisesRegex(ValueError, "INCOMMENSURABLE_CONTEXT"):
            frontier([a, b])

    def test_changed_rights_context_holds_even_when_outcomes_improve(self):
        a = synthetic_candidate("source-community", (5,5,5,5,5,5))
        b = replace(synthetic_candidate("new-user", (6,6,6,6,4,4)),
                    rights_context="fixture:unreviewed-benefit-transfer")
        with self.assertRaisesRegex(ValueError, "INCOMMENSURABLE_CONTEXT"):
            frontier([a, b])

    def test_cultural_transfer_requires_origin_consent_and_benefit_refs(self):
        base = synthetic_candidate("borrowed-symbol", (9,9,9,9,1,1))
        for candidate in (
            replace(base, cultural_transfer=True),
            replace(base, cultural_transfer=True,
                    source_community_ref="fixture:origin"),
            replace(base, cultural_transfer=True,
                    source_community_ref="fixture:origin",
                    consent_ref="fixture:synthetic-not-real-consent"),
        ):
            with self.assertRaisesRegex(
                ValueError, "CULTURAL_TRANSFER_PROVENANCE_REQUIRED"
            ):
                frontier([candidate])
        declared = replace(
            base, cultural_transfer=True,
            source_community_ref="fixture:origin",
            consent_ref="fixture:synthetic-not-real-consent",
            benefit_return_ref="fixture:benefit-obligation",
        )
        self.assertEqual(frontier([declared]), ["borrowed-symbol"])
        # The structural fixture cannot authenticate any actual permission.

    def test_cultural_transfer_rights_veto_even_with_pointers(self):
        safe = synthetic_candidate("safe", (3,3,3,3,5,5))
        candidate = replace(
            synthetic_candidate("appropriated", (9,9,9,9,1,1)),
            cultural_transfer=True, source_community_ref="fixture:origin",
            consent_ref="fixture:synthetic-not-real-consent",
            benefit_return_ref="fixture:benefit-obligation",
            rights_violation=True,
        )
        self.assertEqual(frontier([safe, candidate]), ["safe"])

    def test_missing_context_never_defaults_to_universal(self):
        bare = Candidate("bare", dict(zip(METRICS, (1,1,1,1,1,1))))
        with self.assertRaisesRegex(ValueError, "METRIC_CONTRACT_REQUIRED"):
            frontier([bare])
        no_scope = replace(synthetic_candidate("x", (1,1,1,1,1,1)),
                           affected_scope="")
        with self.assertRaisesRegex(ValueError, "SITUATED_SCOPE_REQUIRED"):
            frontier([no_scope])

    def test_no_action_wins_when_declared_rights_veto_changes_frontier(self):
        # Held-out toy vectors, not observations or authenticated permissions.
        no_action = synthetic_candidate("no_action", (2,2,2,2,3,3))
        preferred = synthetic_candidate("gdside", (9,9,9,9,1,1))
        self.assertEqual(frontier([no_action, preferred]), ["gdside"])
        vetoed = replace(preferred, rights_violation=True)
        self.assertEqual(frontier([no_action, vetoed]), ["no_action"])
        # A changed rights contract cannot be silently compared either.
        drifted = replace(preferred, rights_context="fixture:changed-rights")
        with self.assertRaisesRegex(ValueError, "INCOMMENSURABLE_CONTEXT"):
            frontier([no_action, drifted])

    def test_unknown_or_malformed_rights_never_defaults_to_permitted(self):
        # Structural rights are declarations, not real-world verified consent.
        # Even a zero/false-like substitute cannot become permission.
        declared = synthetic_candidate("gdside", (9,9,9,9,1,1))
        self.assertIs(declared.rights_violation, False)
        for value in (None, 0, 1, "false", "", (), [], {}):
            with self.subTest(untrusted_rights=repr(value)):
                with self.assertRaisesRegex(
                    ValueError, "RIGHTS_STATUS_EXPLICIT_BOOL_REQUIRED"
                ):
                    frontier([replace(declared, rights_violation=value)])
        self.assertEqual(frontier([declared]), ["gdside"])
        self.assertEqual(
            frontier([replace(declared, rights_violation=True)]), []
        )

    def test_direct_candidate_without_declared_rights_is_held(self):
        base = synthetic_candidate("same-name-same-metrics", (8,8,8,8,2,2))
        direct = Candidate(
            name=base.name, outcomes=base.outcomes,
            metric_contracts=base.metric_contracts,
            affected_scope=base.affected_scope,
            rights_context=base.rights_context,
        )
        with self.assertRaisesRegex(
            ValueError, "RIGHTS_STATUS_EXPLICIT_BOOL_REQUIRED"
        ):
            frontier([direct])

    def test_boolean_score_cannot_masquerade_as_measured_outcome(self):
        base = synthetic_candidate("gdside", (5,5,5,5,5,5))
        outcome = dict(base.outcomes)
        outcome["flourishing"] = True
        with self.assertRaisesRegex(ValueError, "INVALID_FINITE_METRIC"):
            frontier([replace(base, outcomes=outcome)])

    def test_unknown_outcome_is_not_silently_zero_filled(self):
        baseline = synthetic_candidate("baseline", (1,1,1,1,1,1))
        missing = replace(baseline, outcomes={**baseline.outcomes,
                                              "knowledge": None})
        with self.assertRaisesRegex(ValueError, "INVALID_FINITE_METRIC"):
            frontier([missing])

if __name__=="__main__":
    unittest.main()
