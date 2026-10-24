import copy
import unittest
from codoodle import classify,SCHEMA,ROUTES


def doc(raw='mouse glyph media', consent=True, scope='PUBLIC_SYNTHETIC'):
    return {'schema':SCHEMA,'raw_doodle':raw,'opt_in_local_review':consent,'scope':scope}

class IntakeTests(unittest.TestCase):
    def test_seven_routing_families(self):
        text='mouse media diagram inversion stuck session claude historical'
        self.assertEqual(len(classify(doc(text))['candidates']),7)
    def test_raw_text_not_echoed(self):
        raw='mouse unique-private-notes-34812'
        self.assertNotIn('unique-private-notes',str(classify(doc(raw))))
    def test_deterministic(self):
        self.assertEqual(classify(doc()),classify(doc()))
    def test_zero_effects(self):
        out=classify(doc())
        self.assertTrue(all(v==0 for v in out['effects'].values()))
        self.assertTrue(all(c['authority']=='NONE' for c in out['candidates']))
    def test_no_consent(self):
        p=classify(doc(consent=False))
        self.assertEqual((p['state'],p['candidates']),('HELD_NO_OPT_IN',[]))
    def test_secret_context_fails_closed(self):
        p=classify(doc('mouse and private key'))
        self.assertEqual((p['state'],p['candidates']),('HELD_SENSITIVE_CONTEXT',[]))
    def test_input_size(self):
        with self.assertRaisesRegex(ValueError,'65536'):
            classify(doc('x'*65537))
    def test_scope_required(self):
        with self.assertRaisesRegex(ValueError,'scope'):
            classify(doc(scope='PUBLIC'))
    def test_explicit_boolean_required(self):
        p=doc();p['opt_in_local_review']='yes'
        with self.assertRaisesRegex(ValueError,'opt_in'):
            classify(p)
    def test_no_trigger_doesnt_invent(self):
        p=classify(doc('a randomly beautiful thought'))
        self.assertEqual((p['state'],p['candidates']),('HELD_NO_EFFECTS',[]))
    def test_input_immutability(self):
        p=doc();before=copy.deepcopy(p)
        classify(p)
        self.assertEqual(p,before)
    def test_recipient_unknown_not_ack(self):
        p=classify(doc('sessions and stuck work'))
        self.assertIn('NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF',p['nonclaims'])
    def test_very_large_logical_space_no_spawning(self):
        p=classify(doc(' '.join(['mouse','diagram','session','media']*500)))
        self.assertLessEqual(len(p['candidates']),len(ROUTES))
        self.assertEqual(p['effects']['workers'],0)

if __name__=='__main__': unittest.main()
