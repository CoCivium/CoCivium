"""Candidate-only capability passport contract tests. No cross-provider ACK."""
import unittest

REQUIRED = {"worker_id", "provider", "model_id", "source_ref", "source_revision",
            "capabilities", "limitations", "tool_access", "authority_scope",
            "privacy_scope", "alternatives", "recommended_work_id",
            "receiver_id", "receiver_readproof"}
def validate(passport):
    missing = sorted(REQUIRED - set(passport))
    if missing:
        return "HOLD_MISSING_FIELDS", missing
    if not passport["source_revision"] or not passport["source_ref"]:
        return "HOLD_UNBOUND_SOURCE", []
    if passport["receiver_readproof"] is None:
        return "SOURCE_ONLY_NO_PICKUP", []
    if not passport["receiver_id"]:
        return "HOLD_NO_RECEIVER_ID", []
    return "RECEIVER_EVIDENCE_PRESENT_NOT_ACCEPTANCE", []

def fixture(**overrides):
    p = dict(worker_id="candidate-worker", provider="unknown", model_id="unknown",
             source_ref="SESSION_BOOTSTRAP.md", source_revision="example-only",
             capabilities=["read-only-review"], limitations=["no-runtime-access"],
             tool_access=[], authority_scope="read-only", privacy_scope="public-safe",
             alternatives=["human-review"], recommended_work_id=None,
             receiver_id=None, receiver_readproof=None)
    p.update(overrides)
    return p

class CapabilityPassportTests(unittest.TestCase):
    def test_missing_fields_hold(self):
        self.assertEqual(validate({})[0], "HOLD_MISSING_FIELDS")
    def test_source_must_be_bound(self):
        self.assertEqual(validate(fixture(source_revision=""))[0], "HOLD_UNBOUND_SOURCE")
    def test_source_publication_not_pickup(self):
        self.assertEqual(validate(fixture())[0], "SOURCE_ONLY_NO_PICKUP")
    def test_assent_is_not_receiver_proof(self):
        self.assertEqual(validate(fixture(receiver_readproof=None))[0], "SOURCE_ONLY_NO_PICKUP")
    def test_receiver_identity_required(self):
        self.assertEqual(validate(fixture(receiver_readproof="example"))[0], "HOLD_NO_RECEIVER_ID")
    def test_proof_presence_not_acceptance(self):
        self.assertEqual(validate(fixture(receiver_id="test-receiver", receiver_readproof="example"))[0], "RECEIVER_EVIDENCE_PRESENT_NOT_ACCEPTANCE")

if __name__ == "__main__":
    unittest.main()
