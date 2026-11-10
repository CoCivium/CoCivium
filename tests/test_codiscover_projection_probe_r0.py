"""Synthetic negative tests for CoDiscover projection losses and receiver qualification."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "CoDiscoverProjectionProbeR0.py"
spec = importlib.util.spec_from_file_location("codiscover_projection", SCRIPT)
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)
bridge = discovery.bridge


def items(requirements):
    result = discovery.compare(requirements)
    return {r["format_id"]: r for r in result["alternatives"]}


class CoDiscoverProjectionTests(unittest.TestCase):
    def test_three_existing_projections_only(self):
        self.assertEqual(list(discovery.FORMATS),
                         ["typed_json", "ascii", "presentation_mathml"])

    def test_receiver_source_audit_requires_typed_json(self):
        result = discovery.compare(list(discovery.FACETS))
        self.assertEqual(result["qualified_for_probe"], ["typed_json"])

    def test_fast_explanation_can_use_ascii_not_bare_mathml(self):
        result = discovery.compare(["quantity_kind", "epistemic_state",
                                    "exact_base_value"])
        self.assertEqual(result["qualified_for_probe"],
                         ["ascii", "typed_json"])

    def test_value_only_has_three_synthetic_candidates(self):
        result = discovery.compare(["exact_base_value"])
        self.assertEqual(result["qualified_for_probe"], sorted(discovery.FORMATS))

    def test_source_identity_lost_in_ascii(self):
        r = items(["source_ref"])
        self.assertFalse(r["ascii"]["qualifies_for_this_synthetic_probe"])
        self.assertIn("source_ref", r["ascii"]["collapsed_facets_in_fixture"])

    def test_source_identity_lost_in_mathml(self):
        r = items(["source_ref"])
        self.assertFalse(r["presentation_mathml"]["qualifies_for_this_synthetic_probe"])

    def test_time_identity_lost_in_ascii(self):
        r = items(["observed_at_utc"])
        self.assertIn("observed_at_utc",
                      r["ascii"]["receiver_required_facets_lost_in_fixture"])

    def test_time_identity_lost_in_mathml(self):
        r = items(["observed_at_utc"])
        self.assertIn("observed_at_utc",
                      r["presentation_mathml"]["receiver_required_facets_lost_in_fixture"])

    def test_kind_lost_in_presentation_mathml(self):
        r = items(["quantity_kind"])
        self.assertIn("quantity_kind",
                      r["presentation_mathml"]["receiver_required_facets_lost_in_fixture"])

    def test_kind_preserved_in_ascii_synthetic_pair(self):
        r = items(["quantity_kind"])
        self.assertTrue(r["ascii"]["qualifies_for_this_synthetic_probe"])

    def test_epistemic_status_lost_in_mathml_zero_case(self):
        r = items(["epistemic_state"])
        self.assertIn("epistemic_state",
                      r["presentation_mathml"]["collapsed_facets_in_fixture"])

    def test_epistemic_status_preserved_in_ascii(self):
        r = items(["epistemic_state"])
        self.assertTrue(r["ascii"]["qualifies_for_this_synthetic_probe"])

    def test_exact_value_distinguished_in_all_three_fixture_pairs(self):
        for r in items(["exact_base_value"]).values():
            self.assertTrue(r["qualifies_for_this_synthetic_probe"])

    def test_typed_json_distinguishes_every_probed_facet(self):
        r = items(list(discovery.FACETS))["typed_json"]
        self.assertEqual(set(r["distinguished_facets_in_fixture"]),
                         set(discovery.FACETS))
        self.assertEqual(r["collapsed_facets_in_fixture"], [])

    def test_all_witness_pairs_have_distinct_canonical_digest(self):
        for left, right in discovery.witness_pairs().values():
            self.assertNotEqual(bridge.canonical_digest(left),
                                bridge.canonical_digest(right))

    def test_byte_counts_are_actual_encoded_length(self):
        r = items(["exact_base_value"])
        sample = discovery.witness_pairs()["source_ref"][0]
        for key, record in r.items():
            expected = len(discovery.projection(sample, key).encode("utf-8"))
            self.assertEqual(record["bytes_for_synthetic_example"], expected)

    def test_semantic_hash_is_source_not_presentation_checksum(self):
        result = discovery.compare(["exact_base_value"])
        sample = discovery.witness_pairs()["source_ref"][0]
        self.assertEqual(result["semantic_source_sha256"],
                         bridge.canonical_digest(sample))
        self.assertNotEqual(result["semantic_source_sha256"],
                            result["alternatives"][1]["projection_sha256"])

    def test_zero_effects_and_no_receiver_claim(self):
        result = discovery.compare(["source_ref"])
        self.assertEqual(result["network_requests"], 0)
        self.assertEqual(result["processes_spawned"], 0)
        self.assertEqual(result["external_receivers"], 0)
        self.assertEqual(result["independent_user_or_model_uptake"], "NOT_TESTED")
        self.assertEqual(result["effect_authority"], "NONE")

    def test_no_latency_or_energy_inferred_from_bytes(self):
        result = discovery.compare(["source_ref"])
        self.assertEqual(result["resource_measurement"],
                         "UTF8_BYTES_ONLY_NOT_ENERGY_LATENCY_OR_USEFULNESS")

    def test_empty_requirements_rejected(self):
        with self.assertRaisesRegex(bridge.Hold, "INVALID_RECEIVER_REQUIREMENTS"):
            discovery.compare([])

    def test_duplicate_requirements_rejected(self):
        with self.assertRaisesRegex(bridge.Hold, "DUPLICATE_REQUIREMENT"):
            discovery.compare(["source_ref", "source_ref"])

    def test_unknown_facet_rejected(self):
        with self.assertRaisesRegex(bridge.Hold, "UNKNOWN_RECEIVER_FACET"):
            discovery.compare(["invented_ability"])

    def test_non_list_requirements_rejected(self):
        with self.assertRaisesRegex(bridge.Hold, "INVALID_RECEIVER_REQUIREMENTS"):
            discovery.compare("source_ref")

    def test_excessive_requirements_rejected(self):
        with self.assertRaisesRegex(bridge.Hold, "INVALID_RECEIVER_REQUIREMENTS"):
            discovery.compare(["source_ref"] * 1000)

    def test_unknown_projection_never_executed(self):
        sample = discovery.witness_pairs()["source_ref"][0]
        with self.assertRaisesRegex(bridge.Hold, "UNKNOWN_PROJECTION_FORMAT"):
            discovery.projection(sample, "javascript_eval")

    def test_unknown_or_withheld_not_promoted_to_number(self):
        sample = bridge.fixture("ratio", "1", None, status="WITHHELD")
        result = discovery.projection(sample, "typed_json")
        self.assertIn('"exact_base_value":null', result)
        self.assertIn('"epistemic_state":"WITHHELD"', result)

    def test_external_source_mutation_changes_canonical_identity(self):
        a = discovery.witness_pairs()["source_ref"][0]
        b = deepcopy(a)
        b["source_ref"] = "fixture:another"
        self.assertNotEqual(bridge.canonical_digest(a), bridge.canonical_digest(b))


if __name__ == "__main__":
    unittest.main(verbosity=2)
