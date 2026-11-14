"""Adversarial CoTermable operator-expression test. Syntactic, not semantic adoption."""
from __future__ import annotations
import copy
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from coterm_operator_r0 import (ROOTS,OPERATORS,NONCLAIMS,root,compose,candidates,
                                dooferate,rehydrate,demo)
class OperatorTests(unittest.TestCase):
    def reject(self,code,func,*args,**kw):
        with self.assertRaisesRegex(ValueError,code):
            func(*args,**kw)
    def test_roots_are_source_linked(self):
        self.assertEqual(len(ROOTS),5)
        for id in ROOTS:
            self.assertTrue(root(id)["source"])
    def test_root_unknown(self): self.reject("UNKNOWN_SOURCE_BOUND_ROOT",root,"new-mystery")
    def test_root_forged_source(self):
        changed=root("colex");changed["source"]="invented"
        self.reject("FORGED_ROOT_OR_MEANING",compose,"DOOFERATE",changed)
    def test_unknown_operator(self): self.reject("UNKNOWN_OPERATOR",compose,"MAKE_SENTIENT",root("coagent"))
    def test_arity(self): self.reject("OPERATOR_ARITY",compose,"SAME?",root("colex"))
    def test_operator_type(self):
        self.reject("INCOMPATIBLE_OPERATOR_KIND",compose,"SENTIENT?",root("coregroup"))
    def test_no_auto_equiv_sentience(self):
        self.reject("INCOMPATIBLE_OPERATOR_KIND",compose,"AUTO",compose("SENTIENT?",root("coagent")))
    def test_auto_process_is_candidate(self):
        x=compose("AUTO",root("coregroup"))
        self.assertEqual(x["authority"],"NONE")
        self.assertEqual(x["epistemic_class"],"HYPOTHESIS")
        self.assertTrue(x["display"].startswith("AUTO("))
    def test_sentient_question_only(self):
        x=compose("SENTIENT?",root("coagent"))
        self.assertIn("SENTIENT?",x["display"])
        self.assertIn("SENTIENT_LABEL_NE_CONSCIOUSNESS",NONCLAIMS)
    def test_same_requires_context(self):
        self.reject("SAME_REQUIRES_CONTEXT",compose,"SAME?",root("coregroup"),root("coboogie"))
    def test_same_not_identity_collapse(self):
        a=compose("SAME?",root("coregroup"),root("coboogie"),params={"context":"role"})
        b=compose("SAME?",root("coregroup"),root("coboogie"),params={"context":"purpose"})
        self.assertNotEqual(a["expression_id"],b["expression_id"])
        self.assertEqual(a["epistemic_class"],"HYPOTHESIS")
    def test_same_self_tautology_not_new_term(self):
        self.reject("SAME_TAUTOLOGY_NOT_NOVELTY",compose,"SAME?",root("coregroup"),root("coregroup"),params={"context":"role"})
    def test_scendent_requires_frames(self):
        self.reject("CROSS_FRAME_REQUIRED",compose,"COSCENDENT",root("coglyphrail"))
    def test_scendent_distinct_frames(self):
        self.reject("CROSS_FRAME_MUST_DIFFER",compose,"COSCENDENT",root("coglyphrail"),params={"from_frame":"TEXT","to_frame":"TEXT"})
    def test_scendent_no_superiority(self):
        x=compose("COSCENDENT",root("coglyphrail"),params={"from_frame":"TEXT","to_frame":"VOICE"})
        self.assertEqual(x["authority"],"NONE")
        self.assertIn("COSCENDENT_NE_SUPERIORITY",NONCLAIMS)
    def test_dooferate_not_recovery(self):
        b=b"Everything important cannot be kept in a tiny excerpt."
        card=dooferate(b,"fixture:source",7)
        self.assertEqual(card["preview_hex"],b[:7].hex())
        self.assertEqual(card["omitted_byte_count"],len(b)-7)
        self.reject("SOURCE_UNAVAILABLE",rehydrate,card,{})
    def test_dooferate_roundtrip_with_exact_source(self):
        source=b"\x00\xef\x00 Synthetic bytes"
        c=dooferate(source,"fixture:source")
        self.assertEqual(rehydrate(c,{"fixture:source":source}),source)
    def test_dooferate_mismatch_fails(self):
        c=dooferate(b"secret","fixture:source")
        self.reject("SOURCE_MISMATCH",rehydrate,c,{"fixture:source":b"other"})
    def test_dooferate_empty_valid(self):
        c=dooferate(b"","fixture:e",0)
        self.assertEqual(rehydrate(c,{"fixture:e":b""}),b"")
    def test_dooferate_rejects_bad_bound(self):
        self.reject("PREVIEW_BUDGET",dooferate,b"x","fixture:s",True)
        self.reject("PREVIEW_BUDGET",dooferate,b"x","fixture:s",10000)
    def test_no_source_pointer(self):
        self.reject("SOURCE_BYTES_AND_ID_REQUIRED",dooferate,b""," ")
    def test_untrusted_operand(self):
        self.reject("UNTRUSTED_OPERAND",compose,"DOOFERATE","CoLex+")
    def test_forged_effect_field_rejected(self):
        x=compose("AUTO",root("coregroup"));x["authority"]="EFFECT_GATED"
        self.reject("FORGED_EXPRESSION_OR_AUTHORITY",compose,"NULL",x)
    def test_forged_display_field_rejected(self):
        x=compose("AUTO",root("coregroup"));x["display"]="AUTO_GRANTED"
        self.reject("EXPRESSION_SIGNATURE_OR_CONTENT_MISMATCH",compose,"NULL",x)
    def test_forged_key_rejected(self):
        x=compose("AUTO",root("coregroup"));x["expression_id"]="fake"
        self.reject("EXPRESSION_SIGNATURE_OR_CONTENT_MISMATCH",compose,"NULL",x)
    def test_nested_depth_limited(self):
        x=compose("AUTO",root("coregroup"));y=compose("AUTO",x)
        self.reject("COMPOSITION_DEPTH_BUDGET",compose,"AUTO",y)
    def test_nested_order_matters(self):
        a=compose("DOOFERATE",compose("AUTO",root("coregroup")))
        b=compose("NULL",compose("AUTO",root("coregroup")))
        self.assertNotEqual(a["expression_id"],b["expression_id"])
    def test_same_operator_output_cannot_auto(self):
        x=compose("SAME?",root("coregroup"),root("coboogie"),params={"context":"same?"})
        self.reject("INCOMPATIBLE_OPERATOR_KIND",compose,"AUTO",x)
    def test_unknown_context_rejected(self):
        self.reject("UNKNOWN_OR_INVALID_CONTEXT",compose,"AUTO",root("coregroup"),params={"permission":"yes"})
    def test_inapplicable_context_rejected(self):
        self.reject("OPERATOR_CONTEXT_NOT_APPLICABLE",compose,"AUTO",root("coregroup"),params={"context":"bogus"})
    def test_limit_enforced(self):
        self.assertEqual(len(list(candidates(list(ROOTS),list(OPERATORS),limit=3))),3)
        self.assertEqual(len(list(candidates(list(ROOTS),list(OPERATORS),limit=0))),0)
    def test_no_unbounded_limit(self):
        self.reject("CANDIDATE_LIMIT",lambda:list(candidates(list(ROOTS),list(OPERATORS),limit=99999)))
    def test_same_inputs_stable_id(self):
        self.assertEqual(compose("AUTO",root("coregroup"))["expression_id"],
                         compose("AUTO",root("coregroup"))["expression_id"])
    def test_provenance_unchanged_by_expression(self):
        before=copy.deepcopy(root("coregroup"))
        compose("AUTO",before)
        self.assertEqual(before,root("coregroup"))
    def test_demo_separates_evidence_from_naming(self):
        d=demo()
        self.assertEqual(d["actual_effects"],0)
        self.assertEqual(d["human_adoption"],"NOT_TESTED")
        self.assertEqual(len(d["examples"]),6)
        self.assertTrue(d["rehydration_with_source"])
        self.assertEqual(d["rehydration_without_source"],"EXPECTED_HOLD")
    def test_no_synthetic_claim_of_registered_terms(self):
        self.assertIn("EXPRESSION_NE_REGISTERED_COTERM",NONCLAIMS)
        self.assertIn("NAME_NE_AUTHORITY",NONCLAIMS)

if __name__=="__main__":unittest.main()
