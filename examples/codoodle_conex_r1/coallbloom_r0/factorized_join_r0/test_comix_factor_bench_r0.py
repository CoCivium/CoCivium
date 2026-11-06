import unittest
from CoMixFactorBenchR0 import (
    RECEIVERS, LENSES, EVIDENCE, MEDIA, TIMES, PRIVACY, ACTIONS,
    sources, admissible, exhaustive, factorized, indexed, incremental, flatten, manifest_hash,
)

class CoMixFactorTests(unittest.TestCase):
    def test_one_source_equivalence(self):
        s=sources(1)
        self.assertEqual(manifest_hash(exhaustive(s)), manifest_hash(factorized(s)))
    def test_four_source_equivalence(self):
        s=sources(4)
        self.assertEqual(manifest_hash(exhaustive(s)),manifest_hash(factorized(s)))
    def test_forecast_does_not_impersonate_observed(self):
        self.assertTrue(all(not (c[4]=='OBSERVED' and c[6]=='FORECAST') for c in factorized(sources(1))))
    def test_distinct_belief_and_empirical(self):
        self.assertTrue(all(not (c[3]=='EMPIRICAL' and c[4]=='BELIEF') for c in factorized(sources(1))))
    def test_no_unconsented_private(self):
        self.assertTrue(all(c[7]=='PUBLIC' for c in factorized(sources(1))))
    def test_no_public_send(self):
        self.assertTrue(all(c[8]!='PUBLISH' for c in factorized(sources(1))))
    def test_receiver_chosen_lenses(self):
        r={x.rid:x for x in RECEIVERS}
        self.assertTrue(all(x[3] in r[x[2]].chosen_lenses for x in factorized(sources(1))))
    def test_receiver_capabilities(self):
        r={x.rid:x for x in RECEIVERS}
        self.assertTrue(all(x[5] in r[x[2]].supported_media for x in factorized(sources(1))))
    def test_prototype_typed(self):
        self.assertTrue(all(x[4]=='TESTABLE' and x[3] in ('EMPIRICAL','FUTURE') for x in factorized(sources(1)) if x[5]=='PROTOTYPE'))
    def test_source_version_delta_parity(self):
        src=sources(8); old=indexed(src); new=incremental(old,'S004','v2')
        self.assertEqual(manifest_hash(flatten(new)),manifest_hash(factorized(sources(8,4))))
    def test_unaffected_source_identity(self):
        old=indexed(sources(4)); new=incremental(old,'S002','v2')
        self.assertIs(old['S001'], new['S001'])
        self.assertIsNot(old['S002'],new['S002'])
    def test_copy_on_write(self):
        old=indexed(sources(4)); new=incremental(old,'S002','v2')
        self.assertEqual(old['S002'][0][1],'v1')
        self.assertEqual(new['S002'][0][1],'v2')
    def test_unknown_delta_fails(self):
        with self.assertRaises(ValueError):incremental(indexed(sources(1)),'unbound','v2')
    def test_bad_version_fails(self):
        with self.assertRaises(ValueError):incremental(indexed(sources(1)),'S000','v9')
    def test_no_unbound_source(self):
        with self.assertRaises(ValueError):sources(49)
    def test_bool_source_rejected(self):
        with self.assertRaises(ValueError):sources(True)
    def test_conditional_null_is_not_failure(self):
        self.assertTrue(any(x[4]=='UNKNOWN' for x in factorized(sources(1))))
    def test_forbidden_negative_qualifier(self):
        rec=RECEIVERS[0]
        self.assertFalse(admissible(rec,'EMPIRICAL','OBSERVED','TEXT','CURRENT','WITHHELD','PREVIEW'))
    def test_unauthorized_publish(self):
        rec=RECEIVERS[0]
        self.assertFalse(admissible(rec,'EMPIRICAL','OBSERVED','TEXT','CURRENT','PUBLIC','PUBLISH'))
    def test_no_churn_on_repeat_version(self):
        idx=indexed(sources(2)); after=incremental(idx,'S000','v1')
        self.assertEqual(manifest_hash(flatten(idx)),manifest_hash(flatten(after)))

if __name__=='__main__':unittest.main()
