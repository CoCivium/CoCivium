"""CoTalkItOut gate proves classification only; no provider, X2, or tool effects."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"examples"/"cotalkitout"))
from decision_gate import Proposal, route

def base(**changes):
    p=Proposal(work_id="w1",decision_id="d1",
       source_refs=("commit:abc",),alternatives=("reuse R5","replace R5"),
       objections=("replacement may break receipts",),
       experiment="compare exact R5 contract and adapter response",
       effect="READ_ONLY_TEST",authorized_effects=("READ_ONLY_TEST",))
    return replace(p,**changes)

class GateTests(unittest.TestCase):
    def test_unqualified_replacement_becomes_test(self):
        self.assertEqual(route(base())["state"],"TEST")
    def test_disagreement_without_test_stays_talk(self):
        self.assertEqual(route(base(experiment=""))["reason"],
                         "objection_without_discriminating_test")
    def test_no_competing_alternative_fails_open_discussion(self):
        self.assertEqual(route(base(alternatives=("replace R5",)))["state"],"TALK")
    def test_external_send_never_authorized_by_dialogue(self):
        self.assertEqual(route(base(effect="SEND_WHATSAPP"))["state"],"HELD")
    def test_self_asserted_verification_is_not_receipt(self):
        self.assertEqual(route(base(verified_result=True))["reason"],
                         "verified_result_without_receipt")
    def test_source_bound_verification_qualifies_without_execution(self):
        x=route(base(verified_result=True,evidence_refs=("job:123",)), verified_evidence=("job:123",))
        self.assertEqual(x["state"],"QUALIFIED")
        self.assertEqual(x["receipt_refs"],("job:123",))
    def test_self_claim_with_receipt_string_is_held(self):
        x=route(base(verified_result=True,evidence_refs=("job:forged",)))
        self.assertEqual(x["state"],"HELD")
        self.assertEqual(x["reason"],"independent_verifier_evidence_missing")
    def test_mismatched_verifier_ref_is_held(self):
        x=route(base(verified_result=True,evidence_refs=("job:forged",)),
                verified_evidence=("job:different",))
        self.assertEqual(x["state"],"HELD")
    def test_partial_verifier_match_is_held(self):
        x=route(base(verified_result=True,evidence_refs=("job:a","job:b")),
                verified_evidence=("job:a",))
        self.assertEqual(x["state"],"HELD")
    def test_missing_identity_is_held(self):
        self.assertEqual(route(base(source_refs=()))["state"],"HELD")

if __name__=="__main__":
    unittest.main(verbosity=2)
