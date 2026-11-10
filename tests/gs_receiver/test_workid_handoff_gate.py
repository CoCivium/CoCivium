import unittest
from workid_handoff_gate import inspect, SOURCE_REF, SOURCE_SHA256, WORK_ID


def packet():
    return dict(schema='CoAll.CoOwnedWork.BrowserLocal.R0.Packet', work_id=WORK_ID, source_ref=SOURCE_REF, source_sha256=SOURCE_SHA256, narrative_summary='synthetic', prior_decisions=[], open_blockers=[], next_safe_deed='inspect', privacy='PUBLIC_SYNTHETIC', consent='SYNTHETIC_TEST_ONLY', lease_epoch=1)


def auth():
    return dict(scope='PUBLIC_SYNTHETIC_HANDOFF', source_ref=SOURCE_REF, consent_epoch=1)


class GateTests(unittest.TestCase):
    def test_proposal_not_ack(self):
        self.assertEqual(inspect(packet(), auth())['state'], 'PROPOSAL_ONLY')
        self.assertFalse(inspect(packet(), auth())['receiver_ack'])

    def test_missing_authorization(self):
        self.assertEqual(inspect(packet())['state'], 'HELD_AUTHORIZATION')

    def test_missing_consent_epoch(self):
        a = auth(); a.pop('consent_epoch')
        self.assertEqual(inspect(packet(), a)['state'], 'HELD_AUTHORIZATION')

    def test_wrong_source(self):
        p = packet(); p['source_sha256'] = '0' * 64
        self.assertEqual(inspect(p, auth())['state'], 'HELD_SOURCE')

    def test_private_scope(self):
        p = packet(); p['privacy'] = 'PRIVATE'
        self.assertEqual(inspect(p, auth())['state'], 'HELD_SCOPE')

    def test_stale_epoch(self):
        p = packet(); p['lease_epoch'] = 0
        self.assertEqual(inspect(p, auth())['state'], 'HELD_EPOCH')

    def test_extra_field(self):
        p = packet(); p['receiver_ack'] = True
        self.assertEqual(inspect(p, auth())['state'], 'HELD_SCHEMA')

    def test_boolean_epoch(self):
        p = packet(); p['lease_epoch'] = True
        self.assertEqual(inspect(p, auth())['state'], 'HELD_EPOCH')


if __name__ == '__main__': unittest.main()
