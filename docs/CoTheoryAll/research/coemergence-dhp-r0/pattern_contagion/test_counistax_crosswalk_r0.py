"""Synthetic negative-control tests for CoUniStax+ analogy translation R0."""
from __future__ import annotations
import copy
import unittest
from counistax_crosswalk_r0 import compare

def pattern(id="pattern.bio",substrate="BIOLOGICAL",mechanism="NATURAL_SELECTION",motif="SELECTION",family="family.a",digest="a",**changes):
    p={
        "schema":"CoUniStax.PatternSyntheticR0",
        "pattern_id":id,
        "substrate":substrate,
        "motif":motif,
        "mechanism":mechanism,
        "source_family":family,
        "source_sha256":digest*64,
        "epistemic":"SYNTHETIC_FIXTURE",
        "privacy":"PUBLIC_SAFE",
        "authority":"NONE",
        "observed_at":1000,
        "receiver_ack":False,
    }
    p.update(changes)
    return p

def src(): return pattern()
def dst(): return pattern(id="pattern.social",substrate="SOCIAL",mechanism="IMITATION",family="family.b",digest="b")
def run(s=None,d=None,**kw):
    return compare(src() if s is None else s,dst() if d is None else d,now=kw.pop("now",1100),**kw)

class CoUniStaxTests(unittest.TestCase):
    def held(self,r,code):
        self.assertEqual(r["state"],"HOLD",r)
        self.assertIn(code,r["holds"])
        self.assertEqual(r["effect"],"NONE")
        self.assertFalse(r["automated_spread"])
        self.assertFalse(r["release_authorized"])
    def test_cross_substrate_same_motif_is_analogy_only(self):
        r=run()
        self.assertEqual(r["state"],"SHADOW_ANALOGY_ONLY")
        self.assertEqual(r["motif"],"SELECTION")
        self.assertIn("CROSS_SUBSTRATE_DOMAIN_ASSUMPTIONS",r["lost_relations"])
        self.assertEqual(r["claim_causal_transfer"],False)
        self.assertEqual(r["claim_universal_law"],False)
        self.assertFalse(r["release_authorized"])
        self.assertEqual(r["independent_receiver_ack"],"NOT_ESTABLISHED")
        self.assertEqual(r["reversible_translation"],"NOT_PROVEN")
    def test_source_copy_family_is_not_independent(self):
        d=dst();d["source_family"]="family.a"
        r=run(d=d)
        self.assertEqual(r["state"],"COPY_FAMILY_NOT_INDEPENDENT")
        self.assertIsNone(r["motif"])
    def test_exact_digest_copy_is_not_independent(self):
        d=dst();d["source_sha256"]="a"*64
        self.assertEqual(run(d=d)["state"],"COPY_DIGEST_NOT_INDEPENDENT")
    def test_distinct_motifs_are_not_force_fitted(self):
        d=dst();d["motif"]="FEEDBACK"
        self.assertEqual(run(d=d)["state"],"NO_SHARED_MOTIF")
    def test_private_source_fails_closed(self):
        self.held(run(s=pattern(privacy="PRIVATE")),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_private_target_fails_closed(self):
        self.held(run(d=pattern(privacy="PRIVATE")),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_unauthorized_source_fails_closed(self):
        self.held(run(s=pattern(authority="PUBLISH")),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_claimed_receiver_ack_fails(self):
        self.held(run(d=pattern(receiver_ack=True)),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_unknown_epistemic_fails(self):
        self.held(run(d=pattern(epistemic="OBSERVED")),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_unmatched_mechanism_fails(self):
        d=dst();d["mechanism"]="CELL_SIGNALLING"
        self.held(run(d=d),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_missing_key_fails(self):
        d=dst();d.pop("source_family")
        self.held(run(d=d),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_extra_raw_content_fails(self):
        d=dst();d["messages"]=[{"content":"not-for-public"}]
        self.held(run(d=d),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_duplicate_id_fails(self):
        d=dst();d["pattern_id"]="pattern.bio"
        self.held(run(d=d),"DUPLICATE_PATTERN_ID")
    def test_stale_pattern_fails(self):
        self.held(run(d=pattern(observed_at=1),max_age=100),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_future_dated_fails(self):
        self.held(run(d=pattern(observed_at=2000)),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_invalid_timestamp_bool_fails(self):
        self.held(run(d=pattern(observed_at=True)),"UNQUALIFIED_OR_NONPUBLIC_PATTERN")
    def test_negative_time_fails(self):
        self.held(run(now=-1),"INVALID_TIME")
    def test_invalid_horizon_fails(self):
        self.held(run(max_age=0),"INVALID_TIME")
    def test_same_substrate_still_has_loss(self):
        d=pattern(id="pattern.bio2",mechanism="CELL_SIGNALLING",family="family.b",digest="b")
        r=run(d=d)
        self.assertEqual(r["state"],"SHADOW_ANALOGY_ONLY")
        self.assertNotIn("CROSS_SUBSTRATE_DOMAIN_ASSUMPTIONS",r["lost_relations"])
        self.assertIn("CAUSAL_IDENTIFICATION",r["lost_relations"])
    def test_random_null_and_inverse_tests_required(self):
        r=run()
        self.assertIn("TEST_NULL_RANDOM_MOTIF_MATCH_BASELINE",r["candidate_tests"])
        self.assertIn("TEST_INVERSE_OR_BREAK_PATH",r["candidate_tests"])
    def test_order_invariance_of_pattern_ids(self):
        self.assertEqual(run()["pattern_ids"],run(s=dst(),d=src())["pattern_ids"])
    def test_does_not_mutate_source(self):
        a=src();b=dst();before=copy.deepcopy((a,b))
        run(s=a,d=b)
        self.assertEqual((a,b),before)
    def test_does_not_conflate_source_count_with_evidence(self):
        self.assertEqual(run()["evidence_transfer"],"PROHIBITED")
    def test_not_claimed_future_prediction(self):
        self.assertEqual(run()["future_prediction"],"NOT_ESTABLISHED")
    def test_no_effect_adapter_in_source(self):
        from pathlib import Path
        code=(Path(__file__).parent/"counistax_crosswalk_r0.py").read_text()
        for forbidden in ("subprocess","os.system","socket","urllib.request","requests.post","git push","Popen"):
            self.assertNotIn(forbidden,code)

if __name__=="__main__":
    unittest.main()
