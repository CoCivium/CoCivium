"""Source-only CoSessionShadowLedger duplicate observation regressions."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from CoSessionShadowLedger import compile_ledger

def obs(**changes):
    result={"session_id":"fixture-session","observed_at":"2026-11-09T21:00:00Z",
            "observer":"synthetic-test","work_state":"ACTIVE",
            "evidence_state":"UNVERIFIED","authority_ceiling":"NONE",
            "currentness":"UNKNOWN","source_refs":["fixture:synthetic"]}
    result.update(changes)
    return result

def compile(items):
    return compile_ledger({"observations":items},"fixture:safe","f"*64)

class Tests(unittest.TestCase):
    def test_exact_replay_no_new_session(self):
        item=obs()
        result=compile([item,dict(item)])
        self.assertEqual(result["coverage"]["observation_count"],1)
        self.assertEqual(result["coverage"]["supplied_observation_count"],2)
        self.assertEqual(result["coverage"]["exact_duplicate_observations_suppressed"],1)
        self.assertEqual(len(result["label_signals"]),1)

    def test_conflict_same_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"conflicting same-identity event"):
            compile([obs(),obs(work_state="WORKING")])

    def test_changed_time_is_new_event(self):
        result=compile([obs(),obs(observed_at="2026-11-09T21:01:00Z")])
        self.assertEqual(result["coverage"]["observation_count"],2)
        self.assertEqual(result["coverage"]["exact_duplicate_observations_suppressed"],0)

    def test_dedup_never_mutates_source(self):
        item=obs()
        original=dict(item)
        compile([item,item])
        self.assertEqual(item,original)

    def test_no_provider_or_public_effects(self):
        result=compile([obs(),obs()])
        self.assertTrue(all(v==0 for v in result["effects"].values()))
        self.assertIn("NO_PROVIDER_SESSION_MUTATION",result["nonclaims"])

    def test_duplicated_unoriented_does_not_manufacture_progress(self):
        item=obs(work_state="UNKNOWN")
        result=compile([item,item])
        self.assertEqual(result["sessions"][0]["projection"],"UNORIENTED")
        self.assertEqual(result["coverage"]["exact_duplicate_observations_suppressed"],1)

if __name__=="__main__":
    unittest.main(verbosity=2)
