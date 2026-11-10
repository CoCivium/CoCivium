"""Cross-run qualification controls for CoPre >24h evidence.

Synthetic timestamps demonstrate rule behavior, not 24h of actual uptime.
"""
import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).with_name("copre_seed_24h_canary_r0.py")
s=importlib.util.spec_from_file_location("copre_seed_24h_canary_r0",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def obs(when,run="1",digest=None):
    return m.make_observation(status=200,digest=digest or m.EXPECTED_SHA256,length=9187,
                              run_id=run,observed_at=when)

class SurvivalEvidence(unittest.TestCase):
    def setUp(self):
        self.a=obs("2026-11-09T00:00:00+00:00","1")
        self.b=obs("2026-11-10T00:00:01+00:00","2")

    def test_baseline_only(self):
        self.assertEqual(m.evaluate(self.a),"BASELINE_ONLY")

    def test_24h_distinct_runs(self):
        self.assertEqual(m.evaluate(self.b,self.a),"VERIFIED_SOURCE_REFETCH_24H_PLUS_NOT_RUNTIME_SURVIVAL")

    def test_below_24h(self):
        self.b["observed_at"]="2026-11-09T23:59:59+00:00"
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_LESS_THAN_24H")

    def test_source_mutation_rejected(self):
        self.b["sha256"]="a"*64
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_SOURCE_UNVERIFIED")

    def test_prior_mutation_rejected(self):
        self.a["sha256"]="a"*64
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_PRIOR_UNVERIFIED")

    def test_same_run_does_not_qualify(self):
        self.b["workflow_run_id"]="1"
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_SAME_RUN")

    def test_clock_inversion(self):
        self.b["observed_at"]="2026-11-08T00:00:00+00:00"
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_CLOCK_INVERSION")

    def test_foreign_commit(self):
        self.a["source_commit"]="other"
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_PRIOR_SOURCE_MISMATCH")

    def test_unknown_source_fails_closed(self):
        self.b["state"]="HELD_SOURCE_UNVERIFIED"
        self.assertEqual(m.evaluate(self.b,self.a),"HELD_SOURCE_UNVERIFIED")

    def test_transport_fail(self):
        x=m.make_observation(status=None,digest=None,length=None,run_id="3",
                              observed_at="2026-11-10T00:00:00+00:00")
        self.assertEqual(m.evaluate(x,self.a),"HELD_SOURCE_UNVERIFIED")

    def test_run_id_not_permission_or_ack(self):
        self.assertNotIn("receiver_ack",self.b)
        self.assertNotIn("exactly_once_effect_handoff",self.b)

    def test_exact_baseline_hash(self):
        self.assertRegex(m.EXPECTED_SHA256,r"^[0-9a-f]{64}$")
        self.assertEqual(len(m.PINNED_COMMIT),40)

if __name__=="__main__":
    unittest.main()
