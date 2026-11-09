"""CoFront/CoEcho scoped historical recovery proof: synthetic-only."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("front_echo",Path(__file__).with_name("CoFrontEchoCoverageR0.py"))
echo=importlib.util.module_from_spec(spec);spec.loader.exec_module(echo)

def window(**kw):
    d={"id":"hist","root_ref":"public:fixture","from_time":"2020-01-01T00:00:00Z",
       "until_time":"2026-12-31T23:59:59Z","completeness":"PARTIAL"}
    d.update(kw);return d
def obj(**kw):
    d={"front_id":"fixture-front","window_id":"hist","source_ref":"fixture:source",
       "source_sha256":"a"*64,"observed_at":"2026-11-09T21:00:00Z",
       "state":"DISCOVERED","disposition":"REVERIFY","visibility":"PUBLIC"}
    d.update(kw);return d
def packet(items=None,windows=None):
    return {"schema":"CoFront.EchoCoverage.Input.R0","windows":windows if windows is not None else [window()],
            "observations":items if items is not None else [obj()]}

class TestFrontEcho(unittest.TestCase):
    def test_partial_never_claims_complete(self):
        r=echo.audit(packet())
        self.assertFalse(r["coverage"]["global_history_complete"])
        self.assertEqual(r["coverage"]["observed_objects"],1)
        self.assertIn("DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",r["nonclaims"])
    def test_exact_echo_deduplicated(self):
        x=obj();r=echo.audit(packet([x,dict(x)]))
        self.assertEqual(r["coverage"]["observed_objects"],1)
        self.assertEqual(r["coverage"]["exact_replays_suppressed"],1)
    def test_conflict_held_not_silently_elected(self):
        r=echo.audit(packet([obj(),obj(state="REVIEW_REQUIRED")]))
        self.assertEqual(r["coverage"]["conflicting_same_identity"],1)
        self.assertEqual(r["fronts"][0]["state"],"DISCOVERED")
    def test_private_cannot_leak_id_hash_or_counts(self):
        p=obj(front_id="secret-name",source_ref="private:secret",source_sha256="b"*64,visibility="PRIVATE")
        baseline=echo.audit(packet([]))
        with_private=echo.audit(packet([p]))
        self.assertEqual(with_private,baseline)
    def test_private_replays_do_not_change_public_counts(self):
        private=obj(front_id="private-only",source_ref="private:sealed",
                    source_sha256="b"*64,visibility="PRIVATE")
        baseline=echo.audit(packet([]))
        replayed=echo.audit(packet([private,dict(private)]))
        self.assertEqual(replayed,baseline)

    def test_private_collision_does_not_suppress_public_front(self):
        public=obj()
        private=dict(public,source_sha256="b"*64,visibility="PRIVATE")
        expected=echo.audit(packet([public]))
        actual=echo.audit(packet([private,public]))
        self.assertEqual(actual,expected)
        self.assertEqual(actual["coverage"]["conflicting_same_identity"],0)

    def test_private_after_public_is_also_noninterfering(self):
        public=obj()
        private=dict(public,source_sha256="b"*64,visibility="PRIVATE")
        expected=echo.audit(packet([public]))
        actual=echo.audit(packet([public,private,private]))
        self.assertEqual(actual,expected)

    def test_qualified_requires_exact_evidence(self):
        with self.assertRaisesRegex(ValueError,"QUALIFIED_WITHOUT_EVIDENCE"):
            echo.audit(packet([obj(state="QUALIFIED")]))
    def test_supersession_requires_successor(self):
        with self.assertRaisesRegex(ValueError,"SUPERSEDED_WITHOUT_SUCCESSOR"):
            echo.audit(packet([obj(state="SUPERSEDED")]))
    def test_unknown_and_unscanned_stay_explicit(self):
        r=echo.audit(packet([obj(state="UNKNOWN",disposition="UNKNOWN")],[window(completeness="UNSCANNED")]))
        self.assertEqual(r["coverage"]["unscanned_window_ids"],["hist"])
        self.assertEqual(r["state_counts"]["UNKNOWN"],1)
    def test_no_source_mutation(self):
        x=packet();before=copy.deepcopy(x);echo.audit(x);self.assertEqual(x,before)
    def test_bounded_inputs(self):
        with self.assertRaisesRegex(ValueError,"BOUNDED_WINDOWS_OBSERVATIONS_REQUIRED"):
            echo.audit(packet([obj()]*2001))
    def test_same_content_distinct_source_kept(self):
        r=echo.audit(packet([obj(),obj(source_ref="fixture:another")]))
        self.assertEqual(r["coverage"]["observed_objects"],2)
        self.assertTrue(all(a["receiver_pickup"]=="UNPROVEN" for a in r["fronts"]))
if __name__=="__main__":
    unittest.main(verbosity=2)
