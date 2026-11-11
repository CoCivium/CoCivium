import tempfile
import unittest
from pathlib import Path
from workid_convergence import inspect_with_source
from workid_handoff_gate import SOURCE_REF, SOURCE_SHA256, WORK_ID


def packet():
    return dict(schema='CoAll.CoOwnedWork.BrowserLocal.R0.Packet', work_id=WORK_ID,
        source_ref=SOURCE_REF, source_sha256=SOURCE_SHA256, narrative_summary='synthetic',
        prior_decisions=[], open_blockers=[], next_safe_deed='inspect',
        privacy='PUBLIC_SYNTHETIC', consent='SYNTHETIC_TEST_ONLY', lease_epoch=1)


def auth():
    return dict(scope='PUBLIC_SYNTHETIC_HANDOFF', source_ref=SOURCE_REF, consent_epoch=1)


class ConvergenceTests(unittest.TestCase):
    def test_valid_proposal_with_missing_source_held(self):
        with tempfile.TemporaryDirectory() as d:
            result = inspect_with_source(packet(), auth(), Path(d) / 'CoPre.md')
            self.assertEqual(result['state'], 'HELD_SOURCE_PROOF')
            self.assertEqual(result['source_state'], 'HELD_SOURCE_UNAVAILABLE')
            self.assertFalse(result['receiver_ack'])

    def test_valid_proposal_with_tampered_source_held(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'CoPre.md'
            p.write_bytes(b'tampered')
            self.assertEqual(inspect_with_source(packet(), auth(), p)['source_state'],
                             'HELD_SOURCE_BYTES_MISMATCH')

    def test_missing_authorization_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(inspect_with_source(packet(), None, Path(d) / 'CoPre.md')['state'],
                             'HELD_AUTHORIZATION')

    def test_wrong_packet_source_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            p = packet(); p['source_sha256'] = '0' * 64
            self.assertEqual(inspect_with_source(p, auth(), Path(d) / 'CoPre.md')['state'],
                             'HELD_SOURCE')


if __name__ == '__main__':
    unittest.main()
