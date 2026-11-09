"""Independent effect attestation reference tests; NOT deployed on X2.

Two distinct test-only keys model separate actors. This does not establish
real-world observer independence or production authorization.
"""
import hashlib
import hmac
import json
import unittest

ACTUATOR_KEY = b"fixture-actuator-only"
OBSERVER_KEY = b"fixture-observer-only"


def encoded(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")


def mac(record, key):
    return hmac.new(key, encoded(record), hashlib.sha256).hexdigest()


def check_effect(intent, action, observation, action_mac, observation_mac):
    if not hmac.compare_digest(mac(action, ACTUATOR_KEY), action_mac):
        return "BAD_ACTION_AUTHENTICITY"
    if not hmac.compare_digest(mac(observation, OBSERVER_KEY), observation_mac):
        return "BAD_OBSERVATION_AUTHENTICITY"
    if action.get("intent_id") != intent.get("intent_id"):
        return "ACTION_NOT_BOUND_TO_INTENT"
    if observation.get("action_id") != action.get("action_id"):
        return "OBSERVATION_NOT_BOUND_TO_ACTION"
    if observation.get("work_id") != intent.get("work_id"):
        return "WRONG_WORK"
    if observation.get("epoch") != action.get("epoch"):
        return "STALE_EPOCH"
    if observation.get("result") != intent.get("expected_result"):
        return "EFFECT_NOT_OBSERVED"
    return "ATTESTED_FIXTURE_ONLY"


class EffectAttestationTests(unittest.TestCase):
    def setUp(self):
        self.intent = {"intent_id": "i1", "work_id": "seed", "expected_result": "visible"}
        self.action = {"action_id": "a1", "intent_id": "i1", "epoch": 3, "claimed_result": "visible"}
        self.observation = {"action_id": "a1", "work_id": "seed", "epoch": 3, "result": "visible"}

    def check(self, action=None, observation=None):
        a = self.action if action is None else action
        o = self.observation if observation is None else observation
        return check_effect(self.intent, a, o, mac(a, ACTUATOR_KEY), mac(o, OBSERVER_KEY))

    def test_independently_attested_fixture(self):
        self.assertEqual(self.check(), "ATTESTED_FIXTURE_ONLY")

    def test_action_claim_without_observed_effect_fails(self):
        o = dict(self.observation, result="missing")
        self.assertEqual(self.check(observation=o), "EFFECT_NOT_OBSERVED")

    def test_cross_action_replay_fails(self):
        o = dict(self.observation, action_id="another-action")
        self.assertEqual(self.check(observation=o), "OBSERVATION_NOT_BOUND_TO_ACTION")

    def test_stale_epoch_fails(self):
        o = dict(self.observation, epoch=2)
        self.assertEqual(self.check(observation=o), "STALE_EPOCH")

    def test_tampered_observation_signature_fails(self):
        self.assertEqual(check_effect(self.intent, self.action, self.observation,
                                      mac(self.action, ACTUATOR_KEY), mac(self.action, OBSERVER_KEY)),
                         "BAD_OBSERVATION_AUTHENTICITY")

    def test_intent_substitution_fails(self):
        a = dict(self.action, intent_id="other")
        self.assertEqual(self.check(action=a), "ACTION_NOT_BOUND_TO_INTENT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
