"""Synthetic CoOrb membrane and temporal/version invariant tests; not runtime integration."""
import unittest
from dataclasses import dataclass

KINDS = {'RECORDED_PAST', 'OBSERVED_PRESENT', 'PREDICTED_FUTURE', 'COUNTERFACTUAL'}

@dataclass(frozen=True)
class View:
    work_id: str
    seed_revision: str
    projection_revision: int
    semantic_revision: int
    observed_at: str | None

@dataclass(frozen=True)
class TemporalClaim:
    kind: str
    text: str
    observed_at: str | None
    predicted_for: str | None = None
    uncertainty: str | None = None
    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError('invalid temporal kind')
        if self.kind == 'PREDICTED_FUTURE' and (not self.predicted_for or not self.uncertainty):
            raise ValueError('prediction needs horizon and uncertainty')

def next_view(previous, *, seed_revision=None, semantic_change=False):
    return View(previous.work_id, seed_revision or previous.seed_revision,
                previous.projection_revision + 1,
                previous.semantic_revision + int(semantic_change), previous.observed_at)

def cross_border(kind, *, consent=False, authority=False, receiver_readproof=False):
    if kind == 'CONTEXT_EXPORT' and not consent:
        return 'DENIED'
    if kind == 'EFFECT_EXECUTE' and not authority:
        return 'DENIED'
    if kind in {'CONTEXT_EXPORT','PEER_DELEGATE','RECEIVER_ACK'} and not receiver_readproof:
        return 'SENT_UNVERIFIED'
    return 'VERIFIED_FIXTURE_ONLY'

def freshness(observed_at):
    return 'UNKNOWN' if observed_at is None else 'TIMESTAMP_PRESENT_NOT_VERIFIED_CURRENT'

class Tests(unittest.TestCase):
    def setUp(self):
        self.initial = View('wid-1', 'seed-a', 1, 1, '2026-11-08T20:00:00Z')
    def test_pinned_version_retained(self):
        updated = next_view(self.initial, seed_revision='seed-b', semantic_change=True)
        self.assertEqual(self.initial.seed_revision,'seed-a')
        self.assertEqual(updated.seed_revision,'seed-b')
        self.assertEqual(updated.semantic_revision,2)
        self.assertEqual(updated.work_id,self.initial.work_id)
    def test_visual_change_not_semantic_evidence(self):
        updated = next_view(self.initial)
        self.assertEqual(updated.semantic_revision,self.initial.semantic_revision)
        self.assertEqual(updated.projection_revision,2)
    def test_no_receiver_ack_by_projection(self):
        self.assertEqual(cross_border('PEER_DELEGATE'), 'SENT_UNVERIFIED')
    def test_export_no_consent_denied(self):
        self.assertEqual(cross_border('CONTEXT_EXPORT', receiver_readproof=True), 'DENIED')
    def test_effect_requires_authority(self):
        self.assertEqual(cross_border('EFFECT_EXECUTE'), 'DENIED')
    def test_missing_time_unknown(self):
        self.assertEqual(freshness(None),'UNKNOWN')
    def test_prediction_requires_uncertainty_and_horizon(self):
        with self.assertRaises(ValueError): TemporalClaim('PREDICTED_FUTURE','tomorrow',None)
        c=TemporalClaim('PREDICTED_FUTURE','tomorrow',None,'2026-11-09','wide interval')
        self.assertNotEqual(c.kind,'OBSERVED_PRESENT')
    def test_invalid_temporal_class_rejected(self):
        with self.assertRaises(ValueError): TemporalClaim('VERIFIED_DESTINY','no',None)

if __name__ == '__main__': unittest.main(verbosity=2)
