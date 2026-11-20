"""Candidate-only CoPre9.3 priority drift regression. No authority promotion."""
import unittest

REFERENCE = "Priority=Value+Urgency+Deps+Risk"
DRIFT = "Priory+Deps+Risk"

def classify(candidate, authority=False):
    if candidate != REFERENCE:
        return {"state": "DRIFT_HOLD", "promoted": False}
    return {"state": "ELIGIBLE_FOR_AUTHORITY_CHECK" if authority else "MATCH_ONLY", "promoted": False}

class CoPre93PriorityDriftTests(unittest.TestCase):
    def test_typo_and_omissions_hold(self):
        self.assertEqual(classify(DRIFT)["state"], "DRIFT_HOLD")
    def test_authority_cannot_override_drift(self):
        self.assertFalse(classify(DRIFT, authority=True)["promoted"])
    def test_reference_is_not_automatically_promoted(self):
        self.assertEqual(classify(REFERENCE)["state"], "MATCH_ONLY")
    def test_chat_assent_is_not_authority(self):
        self.assertFalse(classify("Agreed all")["promoted"])
    def test_extra_tokens_do_not_match(self):
        self.assertEqual(classify(REFERENCE + "|CoGo+")["state"], "DRIFT_HOLD")
    def test_authority_check_is_not_promotion(self):
        self.assertFalse(classify(REFERENCE, authority=True)["promoted"])

if __name__ == "__main__":
    unittest.main()
