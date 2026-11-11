"""Synthetic-only browser WorkID handoff gate; no transport or receiver ACK."""
import re

WORK_ID = 'CoPre.ReadyCycle.Synthetic.R0'
SOURCE_REF = 'CoCivium/CoCivium:CoPre.md@63b41ead8797e5a781699f32bcbc77b78bdbd7af'
SOURCE_SHA256 = '58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a'
PACKET_FIELDS = frozenset({'schema','work_id','source_ref','source_sha256','narrative_summary','prior_decisions','open_blockers','next_safe_deed','privacy','consent','lease_epoch'})


def inspect(packet, authorization=None):
    """Return held reason or a *proposal*, never a receiver acceptance."""
    if not isinstance(packet, dict) or set(packet) != PACKET_FIELDS:
        return {'state': 'HELD_SCHEMA'}
    if packet['schema'] != 'CoAll.CoOwnedWork.BrowserLocal.R0.Packet' or packet['work_id'] != WORK_ID:
        return {'state': 'HELD_IDENTITY'}
    if packet['source_ref'] != SOURCE_REF or packet['source_sha256'] != SOURCE_SHA256:
        return {'state': 'HELD_SOURCE'}
    if packet['privacy'] != 'PUBLIC_SYNTHETIC' or packet['consent'] != 'SYNTHETIC_TEST_ONLY':
        return {'state': 'HELD_SCOPE'}
    if type(packet['lease_epoch']) is not int or packet['lease_epoch'] != 1:
        return {'state': 'HELD_EPOCH'}
    if not isinstance(packet['narrative_summary'], str) or not (1 <= len(packet['narrative_summary']) <= 240):
        return {'state': 'HELD_CONTENT'}
    for key in ('next_safe_deed',):
        if not isinstance(packet[key], str) or not (1 <= len(packet[key]) <= 240):
            return {'state': 'HELD_CONTENT'}
    for key in ('prior_decisions', 'open_blockers'):
        values = packet[key]
        if not isinstance(values, list) or len(values) > 8 or not all(isinstance(x, str) and 1 <= len(x) <= 160 for x in values):
            return {'state': 'HELD_CONTENT'}
    if not isinstance(authorization, dict) or authorization.get('scope') != 'PUBLIC_SYNTHETIC_HANDOFF' or authorization.get('source_ref') != SOURCE_REF or type(authorization.get('consent_epoch')) is not int or authorization['consent_epoch'] != 1:
        return {'state': 'HELD_AUTHORIZATION'}
    return {'state': 'PROPOSAL_ONLY', 'work_id': WORK_ID, 'receiver_ack': False, 'requires_source_byte_readback': True, 'requires_revocation_readback': True}
