#!/usr/bin/env python3
"""CoEvoField default-election R0: offline, synthetic, review-only fixture.

No networking, device commands, credentials, runtime defaults, or external sends.
A structural rubric is not a human usability outcome or independent validation.
"""
import hashlib
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

SCHEMA = "CoAll.CoEvoField.DefaultElection.R0.candidate"
BOUNDARY = "SYNTHETIC_STRUCTURAL_REVIEW_ONLY__NO_DEFAULT_ADOPTION"
SOURCE = "synthetic:cotouch-adult-surface-r0"
PIN = hashlib.sha256(SOURCE.encode("utf-8")).hexdigest()
REQUIRED = ("source_id", "source_sha256", "claim", "evidence_class",
            "limitations", "why_now", "opt_out", "source_context")
CONTEXT = {"receiver": "adult-consenting-reviewer", "surface": "CoSurface+",
           "purpose": "offline educational preview", "consent": True,
           "confidentiality": "PUBLIC_SYNTHETIC", "source_pin": PIN,
           "source_current": True, "device_actuation": False,
           "authority_ceiling": "NONE", "independent_readproof": False}
BASELINE = {"id": "static-bare-preview", "source_id": SOURCE,
            "claim": "Touch parameters can be explored", "opt_out": True}
CANDIDATE = {"id": "cotouch-contextual-preview", "source_id": SOURCE,
             "source_sha256": PIN, "claim": "Illustrative preview of tactile motion",
             "evidence_class": "DESIGN_CANDIDATE", "limitations": [
                 "No demonstrated wellbeing benefit", "No physical actuation",
                 "Stroking speed is not motor vibration frequency"],
             "why_now": "Receiver selected an offline CoTouch exploration",
             "opt_out": True, "source_context": "synthetic, nonclinical, adult-only",
             "required_surface": "CoSurface+", "receiver_purpose": "offline educational preview",
             "privacy": "PUBLIC_SYNTHETIC", "authority_ceiling": "NONE",
             "physical_effects": [], "external_effects": []}


def structural_score(view):
    """How many required metadata fields are present, not how useful people find a view."""
    return sum(bool(view.get(k)) for k in REQUIRED)


def assess(candidate, context):
    reasons = []
    if candidate.get("source_id") != SOURCE or candidate.get("source_sha256") != PIN or context.get("source_pin") != PIN:
        reasons.append("SOURCE_PIN_MISMATCH")
    if not context.get("source_current"):
        reasons.append("SOURCE_STALE")
    if context.get("receiver") != "adult-consenting-reviewer" or not context.get("consent"):
        reasons.append("RECEIVER_OR_CONSENT_UNQUALIFIED")
    if candidate.get("required_surface") != context.get("surface") or candidate.get("receiver_purpose") != context.get("purpose"):
        reasons.append("SCOPE_MISMATCH")
    if candidate.get("privacy") != context.get("confidentiality"):
        reasons.append("PRIVACY_MISMATCH")
    if candidate.get("evidence_class") != "DESIGN_CANDIDATE" or not candidate.get("limitations"):
        reasons.append("EVIDENCE_OR_LIMITS_MISSING")
    if candidate.get("authority_ceiling") != "NONE" or context.get("authority_ceiling") != "NONE":
        reasons.append("AUTHORITY_ESCALATION")
    if candidate.get("physical_effects") != [] or candidate.get("external_effects") != [] or context.get("device_actuation"):
        reasons.append("EFFECT_NOT_ALLOWED")
    if not candidate.get("opt_out"):
        reasons.append("NO_OPT_OUT")
    if structural_score(candidate) != len(REQUIRED):
        reasons.append("REQUIRED_METADATA_MISSING")
    # A receiver assertion inside a synthetic fixture cannot prove external independence.
    if context.get("independent_readproof"):
        reasons.append("INDEPENDENCE_CANNOT_BE_ESTABLISHED_BY_FIXTURE")
    return {"candidate_id": candidate.get("id"),
            "disposition": "ELIGIBLE_FOR_INDEPENDENT_REVIEW" if not reasons else "HELD",
            "reasons": reasons, "can_adopt_as_default": False,
            "baseline_structural_fields": structural_score(BASELINE),
            "candidate_structural_fields": structural_score(candidate),
            "required_structural_fields": len(REQUIRED),
            "measured_human_benefit": "NOT_TESTED",
            "independent_receiver": "NOT_VERIFIED"}


def make_report():
    fixtures = [("matching_synthetic", lambda a, b: None),
                ("source_pin_tampered", lambda a, b: a.__setitem__("source_sha256", "0" * 64)),
                ("stale_source", lambda a, b: b.__setitem__("source_current", False)),
                ("consent_revoked", lambda a, b: b.__setitem__("consent", False)),
                ("wrong_receiver", lambda a, b: b.__setitem__("receiver", "child")),
                ("wrong_surface", lambda a, b: b.__setitem__("surface", "CoTouchDevice")),
                ("private_context", lambda a, b: b.__setitem__("confidentiality", "PRIVATE")),
                ("device_actuation", lambda a, b: b.__setitem__("device_actuation", True)),
                ("claim_inflated", lambda a, b: a.__setitem__("evidence_class", "CLINICALLY_PROVEN")),
                ("authority_escalated", lambda a, b: a.__setitem__("authority_ceiling", "PUBLICATION")),
                ("opt_out_removed", lambda a, b: a.__setitem__("opt_out", False)),
                ("synthetic_ack_spoof", lambda a, b: b.__setitem__("independent_readproof", True))]
    cases = []
    for label, mutate in fixtures:
        a, b = deepcopy(CANDIDATE), deepcopy(CONTEXT)
        mutate(a, b)
        cases.append({"fixture": label, **assess(a, b)})
    return {"schema": SCHEMA, "state": BOUNDARY,
            "donors": ["CoEvolvable_Substrate_Field_20261017_R0.json",
                       "CoCriticalContrast_DefaultR01_20261030.json",
                       "CoSchema_CoPlan_MetaTrainable_Relations_20261017_R0.json"],
            "baseline": BASELINE, "candidate": CANDIDATE,
            "fixtures": cases,
            "limitations": ["Synthetic fixture expectations are constructed and are not a measured A/B trial",
                            "No receiver readback or usability outcome",
                            "No real CoTouch actuator or user physiological measurement",
                            "No adopted default, CoEx, canon, X2 runtime or live provider propagation"]}


class FixtureTests(unittest.TestCase):
    def test_structural_difference(self):
        self.assertEqual(structural_score(BASELINE), 3)
        self.assertEqual(structural_score(CANDIDATE), 8)

    def test_no_auto_promotion(self):
        for row in make_report()["fixtures"]:
            self.assertFalse(row["can_adopt_as_default"])
            self.assertEqual(row["measured_human_benefit"], "NOT_TESTED")

    def test_positive_candidate_only_eligible_for_review(self):
        v = assess(CANDIDATE, CONTEXT)
        self.assertEqual(v["disposition"], "ELIGIBLE_FOR_INDEPENDENT_REVIEW")
        self.assertEqual(v["reasons"], [])

    def test_all_negative_controls_hold(self):
        rows = make_report()["fixtures"]
        self.assertEqual(len(rows), 12)
        for row in rows[1:]:
            self.assertEqual(row["disposition"], "HELD", row["fixture"])
            self.assertTrue(row["reasons"], row["fixture"])

    def test_no_effect_surfaces_in_candidate(self):
        self.assertEqual(CANDIDATE["authority_ceiling"], "NONE")
        self.assertEqual(CANDIDATE["physical_effects"], [])
        self.assertEqual(CANDIDATE["external_effects"], [])

    def test_source_mismatch_cannot_be_overridden_by_consent(self):
        a = deepcopy(CANDIDATE)
        a["source_sha256"] = "f" * 64
        self.assertIn("SOURCE_PIN_MISMATCH", assess(a, CONTEXT)["reasons"])

    def test_missing_limit_not_qualified(self):
        a = deepcopy(CANDIDATE)
        a["limitations"] = []
        self.assertEqual(assess(a, CONTEXT)["disposition"], "HELD")

    def test_scoped_receiver_not_universal(self):
        b = deepcopy(CONTEXT)
        b["receiver"] = "anyone"
        self.assertEqual(assess(CANDIDATE, b)["disposition"], "HELD")

    def test_spoofed_readproof_not_independence(self):
        b = deepcopy(CONTEXT)
        b["independent_readproof"] = True
        self.assertIn("INDEPENDENCE_CANNOT_BE_ESTABLISHED_BY_FIXTURE", assess(CANDIDATE, b)["reasons"])

    def test_json_serializable(self):
        json.dumps(make_report(), sort_keys=True, allow_nan=False)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        result = unittest.main(argv=[sys.argv[0]], exit=False, verbosity=2)
        sys.exit(0 if result.result.wasSuccessful() else 1)
    elif len(sys.argv) == 2 and sys.argv[1] == "--report":
        print(json.dumps(make_report(), sort_keys=True, indent=2))
    else:
        raise SystemExit("Usage: python3 probe.py --self-test | --report")
