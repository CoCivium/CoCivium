#!/usr/bin/env python3
"""Synthetic federated CoBF/FuturePull compatibility and authority tests."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from CoBestFaceFutureShadowR0 import shadow_select
from CoFedGRAILSShadowBridgeR0 import shadow_federate
from test_cobestface_future_shadow_r0 import b, c


def cell(label="home", *, operator=None, domain=None, digest=None, **changes):
    obj = {
        "schema": "CoFedGRAILS.ShadowCellR0",
        "cell_id": "cell."+label,
        "operator_id": operator or "operator."+label,
        "failure_domain_id": domain or "failure."+label,
        "work_id": "work.public001",
        "source_sha256": digest or ("a"*64),
        "privacy": "PUBLIC_SAFE",
        "authority": "OBSERVE_ONLY",
        "observed_at": 1050,
        "cursor": 5,
        "ack_state": "NOT_ESTABLISHED",
        "claimed_state": "DECLARED_SHADOW_ONLY",
    }
    obj.update(changes)
    return obj


def run(peers=None, baseline=None, candidates=None, **kwargs):
    return shadow_federate(
        cell("home"),
        [cell("peer")] if peers is None else peers,
        b() if baseline is None else baseline,
        [c()] if candidates is None else candidates,
        event=kwargs.pop("event", "MATERIAL_SOURCE_DELTA"),
        now_s=kwargs.pop("now_s", 1100),
        **kwargs
    )


class CoFedGRAILSShadowR0(unittest.TestCase):
    def assert_held(self, x, code):
        self.assertEqual(x["state"], "HOLD", x)
        self.assertIn(code, x["holds"], x)
        self.assertEqual(x["effect"], "NONE")
        self.assertFalse(x["release_authorized"])
        self.assertFalse(x["federation_authority"])

    def test_two_cells_make_shadow_compatibility_not_deployment(self):
        x=run()
        self.assertEqual(x["state"],"FEDERATION_SHADOW_COMPATIBLE")
        self.assertEqual(x["selected_live_id"],"face.lastgood")
        self.assertEqual(x["candidate_ids"],["face.future1"])
        self.assertEqual(x["effect"],"NONE")
        self.assertFalse(x["global_control_plane"])
        self.assertFalse(x["release_authorized"])
        self.assertEqual(x["independent_receiver_ack"],"NOT_ESTABLISHED")
        self.assertIn("PEER_AUTHENTICATION_UNPROVEN",x["holds"])
        self.assertIn("RECEIVER_READPROOF_UNPROVEN",x["holds"])

    def test_timer_does_not_federate(self):
        self.assertEqual(run(event="TIMER_TICK")["state"],"QUIET_NO_MATERIAL_EVENT")

    def test_peer_event_may_trigger_shadow_not_release(self):
        x=run(event="FEDERATION_PEER_DIFF")
        self.assertEqual(x["state"],"FEDERATION_SHADOW_COMPATIBLE")
        self.assertFalse(x["release_authorized"])

    def test_no_peers(self):
        self.assert_held(run(peers=[]),"PEER_BUDGET_OR_TYPE")

    def test_oversize_peer_fanout(self):
        self.assert_held(run(peers=[cell("x%d"%i) for i in range(5)]),"PEER_BUDGET_OR_TYPE")

    def test_bad_local_privacy(self):
        self.assert_held(shadow_federate(cell(privacy="PRIVATE"), [cell("peer")], b(), [c()], event="MATERIAL_SOURCE_DELTA",now_s=1100),"INVALID_LOCAL_CELL")

    def test_peer_private_data_blocked(self):
        self.assert_held(run(peers=[cell("peer",privacy="PRIVATE")]),"INVALID_PEER_CELL")

    def test_peer_authority_claim_blocked(self):
        self.assert_held(run(peers=[cell("peer",authority="EXECUTE_ALL")]),"INVALID_PEER_CELL")

    def test_peer_fake_ack_blocked(self):
        self.assert_held(run(peers=[cell("peer",ack_state="ACKED")]),"INVALID_PEER_CELL")

    def test_peer_fake_runtime_blocked(self):
        self.assert_held(run(peers=[cell("peer",claimed_state="RUNTIME")]),"INVALID_PEER_CELL")

    def test_peer_unexpected_field_fails(self):
        self.assert_held(run(peers=[cell("peer",password="NOT_A_SECRET")]),"INVALID_PEER_CELL")

    def test_duplicate_cell_id_blocked(self):
        self.assert_held(run(peers=[cell("home")]),"DUPLICATE_CELL")

    def test_shared_operator_blocked(self):
        self.assert_held(run(peers=[cell("peer",operator="operator.home")]),"NONINDEPENDENT_DECLARED_DOMAINS")

    def test_shared_failure_domain_blocked(self):
        self.assert_held(run(peers=[cell("peer",domain="failure.home")]),"NONINDEPENDENT_DECLARED_DOMAINS")

    def test_peer_work_id_conflict(self):
        self.assert_held(run(peers=[cell("peer",work_id="work.other")]),"WORK_ID_CONFLICT")

    def test_peer_different_source_revision(self):
        self.assert_held(run(peers=[cell("peer",digest="c"*64)]),"SOURCE_REVISION_CONFLICT")

    def test_peer_cursor_behind(self):
        self.assert_held(run(peers=[cell("peer",cursor=4)]),"PEER_CURSOR_BEHIND_SOURCE")

    def test_peer_stale(self):
        self.assert_held(run(peers=[cell("peer",observed_at=1)],age_limit_s=100),"INVALID_PEER_CELL")

    def test_peer_future_dated(self):
        self.assert_held(run(peers=[cell("peer",observed_at=2200)]),"INVALID_PEER_CELL")

    def test_baseline_work_conflict(self):
        base=b();base["work_id"]="work.other"
        self.assert_held(run(baseline=base),"COBF_SOURCE_IDENTITY_MISMATCH")

    def test_baseline_source_conflict(self):
        base=b();base["source_sha256"]="d"*64
        self.assert_held(run(baseline=base),"COBF_SOURCE_IDENTITY_MISMATCH")

    def test_no_candidate_not_an_improvement(self):
        x=run(candidates=[])
        self.assertEqual(x["state"],"FEDERATION_SHADOW_NO_IMPROVEMENT")
        self.assertEqual(x["candidate_ids"],[])

    def test_worse_candidate_not_selected(self):
        alt=c();alt["metrics"]["interruptions"]=1
        self.assertEqual(run(candidates=[alt])["state"],"FEDERATION_SHADOW_NO_IMPROVEMENT")

    def test_three_cells_bounded(self):
        x=run(peers=[cell("east"),cell("west")])
        self.assertEqual(x["state"],"FEDERATION_SHADOW_COMPATIBLE")
        self.assertEqual(x["declared_peer_count"],2)
        self.assertEqual(x["received_from_peers"],0)

    def test_bad_time_fails(self):
        self.assert_held(run(now_s=True),"INVALID_TIME")

    def test_does_not_mutate_inputs(self):
        original=cell("peer"); peers=[original]; baseline=b(); candidates=[c()]
        before=copy.deepcopy((peers,baseline,candidates))
        shadow_federate(cell("home"),peers,baseline,candidates,
                        event="MATERIAL_SOURCE_DELTA",now_s=1100)
        self.assertEqual((peers,baseline,candidates),before)

    def test_source_has_no_action_adapter(self):
        src=(Path(__file__).resolve().parent/"CoFedGRAILSShadowBridgeR0.py").read_text()
        for forbidden in ("subprocess","os.system","socket","urllib.request","requests.post","git push","Popen","delete_session"):
            self.assertNotIn(forbidden,src)

if __name__=="__main__":
    unittest.main()
