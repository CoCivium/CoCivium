"""Evidence boundaries for CoOrb membrane and predictive rays."""
import unittest
from dataclasses import replace
from scripts.CoOrbMembraneTemporalR0 import BoundaryEvent,project

def edge(**kw):
    d=dict(edge_id="e1",object_id="o1",relation="enables",direction="INBOUND",
           epistemic_class="OBSERVED",source_revision="sha1",
           source_uri="github:blob",observed_at="2026-11-08T10:00:00Z",
           valid_at="2026-11-08T10:00:00Z",target_version="v1")
    d.update(kw)
    return BoundaryEvent(**d)

def run(edges=None,**kwargs):
    return project("v1",tuple(edges if edges is not None else (edge(),)),
                   as_of="2026-11-08T11:00:00Z",work_id="work1",**kwargs)

class Tests(unittest.TestCase):
    def test_observed_current(self):
        d=run()["membrane_edges"][0]
        self.assertEqual(d["kind"],"OBSERVED_EDGE")
        self.assertEqual(d["version_relation"],"CURRENT")
    def test_future_validity_never_observed_edge(self):
        d=run((edge(valid_at="2026-11-09T10:00:00Z"),))["membrane_edges"][0]
        self.assertEqual(d["kind"],"FORECAST_RAY")
    def test_prediction_never_observed(self):
        d=run((edge(epistemic_class="PREDICTED"),))["membrane_edges"][0]
        self.assertEqual(d["kind"],"FORECAST_RAY")
    def test_preferred_not_observed(self):
        self.assertEqual(run((edge(epistemic_class="PREFERRED"),))["membrane_edges"][0]["kind"],"FORECAST_RAY")
    def test_claimed_ack_not_authenticated(self):
        d=run((edge(receiver_ack=True),))["membrane_edges"][0]
        self.assertEqual(d["receiver_ack"],"CLAIMED_NOT_AUTHENTICATED")
    def test_cross_version_not_upgraded(self):
        d=run((edge(target_version="v2"),))
        self.assertEqual(d["membrane_edges"][0]["version_relation"],"OTHER_VERSION")
        self.assertFalse(d["version_upgrade_claimed"])
    def test_bounded_hidden_edges(self):
        d=run((edge(),edge(edge_id="e2")),max_visible=1)
        self.assertEqual(d["hidden_count"],1)
    def test_duplicate_edge_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            run((edge(),edge()))
    def test_future_observation_rejected(self):
        with self.assertRaisesRegex(ValueError,"FUTURE_OBSERVATION"):
            run((edge(observed_at="2026-11-09T11:00:00Z"),))
    def test_bad_relation_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_RELATION"):
            run((edge(direction="OMNISCIENT"),))
    def test_source_required(self):
        with self.assertRaisesRegex(ValueError,"UNBOUND"):
            run((edge(source_revision=""),))
    def test_no_native_or_predictive_authority(self):
        d=run()
        self.assertFalse(d["native_renderer_changed"])
        self.assertFalse(d["predictive_authority"])
if __name__=="__main__":
    unittest.main()
