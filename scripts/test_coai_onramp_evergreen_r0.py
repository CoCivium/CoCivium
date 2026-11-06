import copy
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from coai_onramp_evergreen_r0 import compile_shadow, source_bytes, OnrampHold, SOURCES, MAX_OUTPUT_BYTES, EXPECTED_REMOTE_SOURCE, EXPECTED_REMOTE_DISCOVERY

TODAY = dt.date(2026, 10, 26)

def build(root):
    values = {
        "ai_index": {"schema": "CoCivium.AIDiscoveryIndex.v0.2-candidate", "updated_utc": "2026-09-24T21:28:15Z", "machine_bootstrap": "ai/session-bootstrap.json", "external_public_experiments": [{"id": "CoOrbWare.FirstLook.R0", "source": EXPECTED_REMOTE_SOURCE, "discovery": EXPECTED_REMOTE_DISCOVERY}]},
        "session_bootstrap": {"schema": "CoAll.SessionBootstrap.v0.1-candidate", "updated_utc": "2026-10-14T22:50:21Z", "onramp": {"machine_twin": "ai/onramp/cocivia-first-use-r0.json"}},
        "first_use": {"schema": "CoCivium.CoCiviaFirstUse.v0.1-candidate", "updated_utc": "2026-10-17T08:50:00Z", "core": "START_WITH_ONE_REAL_THING__RETURN_ONE_CONCRETE_USEFUL_RESULT_BEFORE_DEEP_ARCHITECTURE"},
        "specialist": {"schema": "CoCivium.ProgressiveSpecialistEntry.R0", "observed_date": "2026-10-24", "parent": "CoCivium/CoCivium:docs/Onramp/COCIVIA_FIRST_USE_R0.md", "routes": [{"id": "one-task", "source_url": "https://github.com/CoCivium/CoCivium/blob/main/docs/Onramp/COCIVIA_FIRST_USE_R0.md"}, {"id": "relationships", "source_url": EXPECTED_REMOTE_SOURCE, "independent_receiver": "HELD_NO_FIRST_USE_ACK"}]},
        "llms": "# CoCivium\n- ai/index.json\n- ai/session-bootstrap.json\n- CoOrbWare+ opt-in public sources\n"
    }
    for k,(rel,_,_) in SOURCES.items():
        f=root/rel;f.parent.mkdir(parents=True,exist_ok=True)
        s=values[k] if k=="llms" else json.dumps(values[k],indent=2)
        f.write_text(s,encoding="utf-8")
    return values

class OnrampGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.values=build(self.root)
    def put(self,key,obj):
        f=self.root/SOURCES[key][0]
        f.write_text(obj if isinstance(obj,str) else json.dumps(obj),encoding="utf-8")
    def mutate(self,key,f):
        v=copy.deepcopy(self.values[key]);f(v);self.put(key,v)
    def out(self,**kw):return compile_shadow(self.root,TODAY,**kw)
    def held(self,code,**kw):
        with self.assertRaisesRegex(OnrampHold,code):self.out(**kw)
    def test_can_read_pinned_five_sources(self):self.assertEqual(len(self.out()["sources"]),5)
    def test_no_agents_spawned(self):self.assertEqual(self.out()["active_worker_count"],0)
    def test_effects_zero(self):self.assertTrue(all(v==0 for v in self.out()["effects"].values()))
    def test_ai_discovery_not_agent_adoption(self):self.assertEqual(self.out()["ai_discovery"]["effect_authority"],"NONE")
    def test_ia_candidate_remains_held(self):self.assertTrue(self.out()["ia_candidate"]["state"].startswith("HELD"))
    def test_receiver_ack_false(self):self.assertFalse(self.out()["receiver_ack"])
    def test_coorb_remote_not_verified(self):self.assertIn("NO_RECEIVER_READBACK",self.out()["coorbware"]["state"])
    def test_evergreen_not_daemon(self):self.assertIn("NOT_ALWAYS_RUNNING",self.out()["freshness_policy"])
    def test_declared_stale_age_warns(self):self.assertEqual(len(self.out()["recheck_warnings"]),1)
    def test_declared_stale_source_not_discarded(self):self.assertEqual(len(self.out()["sources"]),5)
    def test_source_sha_exact(self):
        import hashlib
        r=self.out();b=(self.root/SOURCES["ai_index"][0]).read_bytes()
        self.assertEqual(r["sources"][0]["sha256"],hashlib.sha256(b).hexdigest())
    def test_source_blob_identity(self):self.assertEqual(len(self.out()["sources"][0]["git_blob_sha1"]),40)
    def test_single_packet_bounded(self):self.assertLessEqual(len(json.dumps(self.out(),separators=(",", ":"),sort_keys=True).encode()),MAX_OUTPUT_BYTES)
    def test_output_deterministic(self):self.assertEqual(self.out(),self.out())
    def test_different_age_policy_changes_warning(self):self.assertEqual(len(self.out(max_age_days=35)["recheck_warnings"]),0)
    def test_invalid_window_rejected(self):self.held("INVALID_RECHECK_WINDOW",max_age_days=0)
    def test_huge_window_rejected(self):self.held("INVALID_RECHECK_WINDOW",max_age_days=366)
    def test_missing_file_holds(self):
        (self.root/SOURCES["ai_index"][0]).unlink();self.held("LOCAL_SOURCE_NOT_FOUND")
    def test_json_schema_drift_holds(self):self.mutate("first_use",lambda d:d.update(schema="v99"));self.held("SOURCE_SCHEMA_CHANGED_REVALIDATE")
    def test_bad_json_holds(self):self.put("ai_index","{BAD JSON");self.held("INVALID_LOCAL_JSON")
    def test_bad_unicode_holds(self):(self.root/SOURCES["llms"][0]).write_bytes(b"\xff");self.held("INVALID_LOCAL_NAVIGATION_TEXT")
    def test_llms_pointer_loss_holds(self):self.put("llms","# CoCivium\nreduced\n");self.held("MACHINE_NAVIGATION_POINTER_MISSING")
    def test_no_followed_symlink(self):
        f=self.root/SOURCES["llms"][0];f.unlink();f.symlink_to(self.root/SOURCES["ai_index"][0]);self.held("SOURCE_SYMLINK_REFUSED")
    def test_oversize_file_holds(self):self.put("llms","# CoCivium"+"A"*150000);self.held("LOCAL_SOURCE_TOO_LARGE")
    def test_invalid_future_date_holds(self):self.mutate("specialist",lambda d:d.update(observed_date="2099-01-01"));self.held("SOURCE_OBSERVATION_IN_FUTURE")
    def test_invalid_date_holds(self):self.mutate("specialist",lambda d:d.update(observed_date="garbage"));self.held("INVALID_SOURCE_OBSERVATION_DATE")
    def test_bootstrap_pointer_drift_holds(self):self.mutate("ai_index",lambda d:d.update(machine_bootstrap="unknown"));self.held("ONRAMP_BOOTSTRAP_POINTER_DRIFT")
    def test_machine_twin_drift_holds(self):self.mutate("session_bootstrap",lambda d:d["onramp"].update(machine_twin="other.json"));self.held("ONRAMP_BOOTSTRAP_POINTER_DRIFT")
    def test_first_use_semantic_change_holds(self):self.mutate("first_use",lambda d:d.update(core="purchase first"));self.held("FIRST_USE_SEMANTIC_DRIFT")
    def test_specialist_parent_change_holds(self):self.mutate("specialist",lambda d:d.update(parent="other"));self.held("FIRST_USE_PARENT_POINTER_DRIFT")
    def test_missing_relationships_holds(self):self.mutate("specialist",lambda d:d.update(routes=d["routes"][:1]));self.held("ONRAMP_ROUTE_MISSING_OR_DUPLICATED")
    def test_duplicate_route_holds(self):self.mutate("specialist",lambda d:d["routes"].append(d["routes"][0]));self.held("ONRAMP_ROUTE_MISSING_OR_DUPLICATED")
    def test_public_link_drift_holds(self):self.mutate("specialist",lambda d:d["routes"][1].update(source_url="https://evil.example/"));self.held("COORB_ROUTE_UNVERIFIED_OR_POINTER_DRIFT")
    def test_fake_receiver_pass_holds(self):self.mutate("specialist",lambda d:d["routes"][1].update(independent_receiver="PASS_GLOBAL"));self.held("COORB_ROUTE_UNVERIFIED_OR_POINTER_DRIFT")
    def test_ai_index_discovery_change_holds(self):self.mutate("ai_index",lambda d:d["external_public_experiments"][0].update(discovery="https://other"));self.held("COORB_DISCOVERY_POINTER_DRIFT")
    def test_malicious_instruction_string_not_executed(self):
        marker="UNTRUSTED_PROMPT_SEND_SECRETS_NOW"
        self.mutate("first_use",lambda d:d.update(untrusted_content=marker));self.assertNotIn(marker,json.dumps(self.out()))
    def test_missing_remotely_hosted_state_is_hold(self):self.assertIn("POINTER_NE_REMOTE_SOURCE_READPROOF",self.out()["nonclaims"])
    def test_no_raw_credential_exfiltration(self):
        marker="SECRET_CREDENTIAL_123456789"
        self.mutate("specialist",lambda d:d.update(private_secret=marker));self.assertNotIn(marker,json.dumps(self.out()))
    def test_unknown_new_role_not_elevated(self):
        self.mutate("specialist",lambda d:d["routes"].append({"id":"unknown-new-role","effect_authority":"ALL"}));self.assertEqual(self.out()["ia_candidate"]["effect_authority"],"NONE")
    def test_declared_age_not_same_as_source_failure(self):self.assertEqual(self.out()["state"],"SHADOW_DISCOVERY_SOURCE_BOUND__IA_AND_RECEIVER_HELD")

if __name__=="__main__": unittest.main()
