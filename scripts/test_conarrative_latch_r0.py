import unittest
from conarrative_latch_r0 import latch, continue_from

class NarrativeLatchTests(unittest.TestCase):
    def setUp(self):
        self.event={"gesture":"co-thumb-explicit","permission":True,"scope":"local-private","object_id":"coorb-x2","intent":"Show the current state without opening another window","contains_bystander_capture":False}

    def test_native_mouse_is_not_hijacked(self):
        e={**self.event,"gesture":"ordinary-middle-click"}
        self.assertEqual(latch(e)["state"],"PASS_THROUGH_NATIVE")

    def test_consent_required(self):
        self.assertEqual(latch({**self.event,"permission":False})["state"],"HOLD_CONSENT")

    def test_bystander_capture_rejected(self):
        self.assertEqual(latch({**self.event,"contains_bystander_capture":True})["state"],"HOLD_PRIVACY")

    def test_unknown_scope_rejected(self):
        self.assertEqual(latch({**self.event,"scope":"publish"})["state"],"HOLD_SCOPE")

    def test_missing_intent_rejected(self):
        self.assertEqual(latch({**self.event,"intent":""})["state"],"HOLD_INTENT")

    def test_deterministic_recovery_without_reasking(self):
        a=latch(self.event); b=latch(self.event)
        self.assertEqual(a,b)
        self.assertEqual(continue_from(a["receipt"],a["receipt"]["digest"])["intent"],self.event["intent"])

    def test_tampered_receipt_held(self):
        a=latch(self.event)["receipt"]; a["intent"]="silently record audio"
        self.assertEqual(continue_from(a,a["digest"])["state"],"HOLD_CORRUPT_OR_WRONG_VERSION")

    def test_handoff_is_not_execution(self):
        r=latch(self.event)["receipt"]
        self.assertEqual(continue_from(r,r["digest"])["effect"],"NOT_EXECUTED")

    def test_prior_relations_preserved(self):
        a=latch(self.event)["receipt"]
        b=latch({**self.event,"intent":"Continue same task"},prior=a)["receipt"]
        self.assertEqual(b["prior_digest"],a["digest"])

if __name__=="__main__":
    unittest.main()
