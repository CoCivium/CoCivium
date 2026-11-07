"""Adversarial R1.1 metadata tests. No filesystem, network or device effects."""
import unittest
from fabric_ingestion_r1 import triage, fixture

class AdversarialSoftQuarantine(unittest.TestCase):
    def state(self, **changes):
        return triage(fixture(**changes))['state']
    def test_unhashable_source_type(self):
        self.assertEqual(self.state(source_type=[]), 'SOFT_QUARANTINE_UNKNOWN_TYPE')
    def test_unhashable_transform_kind(self):
        self.assertEqual(self.state(transform_kind={}), 'SOFT_QUARANTINE_TRANSFORM')
    def test_unencodable_raw(self):
        x=fixture(); x['raw']='\ud800'
        self.assertEqual(triage(x)['state'], 'SOFT_QUARANTINE_INVALID_ENCODING')
    def test_numeric_prior_hashes(self):
        self.assertEqual(triage(fixture(), prior_hashes=17)['state'], 'SOFT_QUARANTINE_INVALID_PRIORS')
    def test_invalid_prior_hash(self):
        self.assertEqual(triage(fixture(), prior_hashes=['not-a-hash'])['state'], 'SOFT_QUARANTINE_INVALID_PRIORS')
    def test_unhashable_prior(self):
        self.assertEqual(triage(fixture(), prior_hashes=[{}])['state'], 'SOFT_QUARANTINE_INVALID_PRIORS')
    def test_id_newline(self):
        self.assertEqual(self.state(source_id='a\nFAKE_PASS'), 'SOFT_QUARANTINE_MISSING_ID')
    def test_nontext_inverse_version(self):
        self.assertEqual(self.state(transform_kind='TRUE_INVERSE', lossless_proven=True, transform_version={'bad':'v1'}), 'SOFT_QUARANTINE_NONINVERTIBLE')
    def test_no_implicit_authority(self):
        x=triage(fixture())
        self.assertEqual((x['effect'],x['delivery'],x['receiver_ack']),('NONE','NOT_ATTEMPTED','NOT_PROVEN'))
    def test_multibyte_length(self):
        self.assertEqual(self.state(raw='é'*65000), 'SOFT_QUARANTINE_SOURCE_SIZE')
    def test_valid_empty_priors(self):
        self.assertEqual(triage(fixture(), prior_hashes=[])['state'], 'SHADOW_REVIEW_READY')
if __name__ == '__main__':
    unittest.main()
