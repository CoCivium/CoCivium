"""CoPre9.3 shadow acceptance and falsification. No real worker or effects."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from copre93_shadow_job_admission_r0 import (
    Held, SyntheticLedger, audit_candidate_queue, shadow_rank
)

ROOT = Path(__file__).resolve().parents[2]
PINNED_WORKER_QUEUE_BLOB = "861b527cc6b7a9a4d88cb45afe8bd556c3ec9f16"
H = "a" * 64
SCOPE = "SYNTHETIC:CI_SCOPE_ONLY"
SCOPE2 = "SYNTHETIC:OTHER_SCOPE"
def job(jid, **overrides):
    value={"job_id":jid,"synthetic_scope":True,"collision_scope":SCOPE,
       "source_sha256":H,"ready":True,"dependencies":[],
       "value":8,"urgency":8,"unlock":2,"age":1,"risk":2}
    value.update(overrides)
    return value

class CoPre93Shadow(unittest.TestCase):
    def test_actual_source_queue_blob_pinned_and_unacknowledged(self):
        raw=(ROOT/"docs/CoOps/COCLAUDE_WORK_QUEUE_R0.json").read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        self.assertEqual(blob, PINNED_WORKER_QUEUE_BLOB)
        data=json.loads(raw)
        r=audit_candidate_queue(data)
        self.assertEqual(data["status"], "CANDIDATE_NOT_DISPATCHED")
        self.assertEqual(r["observed_candidate_labels"],10)
        self.assertEqual(r["source_job_ids_proved_ready"],0)
        self.assertEqual(r["actual_worker_acks"],0)
        self.assertEqual(r["dispatches"],0)

    def test_candidate_labels_are_not_verified_roles(self):
        r=audit_candidate_queue({"schema":"CoSessionMesh.WorkQueue.R0",
          "status":"CANDIDATE_NOT_DISPATCHED","workers":[{"worker_id":"W01","status":"PASS"}]})
        self.assertEqual(r["independently_authorized_workers"],0)

    def test_duplicate_worker_label_held(self):
        with self.assertRaises(Held):
            audit_candidate_queue({"schema":"CoSessionMesh.WorkQueue.R0",
                                   "workers":[{"worker_id":"W01"},{"worker_id":"W01"}]})

    def test_unbounded_worker_count_held(self):
        with self.assertRaises(Held):
            audit_candidate_queue({"schema":"CoSessionMesh.WorkQueue.R0",
                "workers":[{"worker_id":str(i)} for i in range(34)]})

    def test_rank_non_actuating_and_deterministic(self):
        r=shadow_rank([job("B"),job("A")],set(),{SCOPE})
        self.assertEqual([x["job_id"] for x in r["eligible"]],["A","B"])
        self.assertEqual(r["assignments"],0)
        self.assertEqual(r["actuations"],0)

    def test_priority_risk_changes_advisory_rank_only(self):
        r=shadow_rank([job("risk-high",risk=10),job("risk-low",risk=0)],set(),{SCOPE})
        self.assertEqual(r["eligible"][0]["job_id"],"risk-low")

    def test_authority_gate_precedes_value(self):
        r=shadow_rank([job("moonshot",value=10,collision_scope="PRODUCTION"),
                       job("safe",value=3)],set(),{SCOPE})
        self.assertEqual(len(r["eligible"]),1)
        self.assertEqual(r["eligible"][0]["job_id"],"safe")
        self.assertEqual(len(r["held"]),1)

    def test_dependencies_block(self):
        a=shadow_rank([job("locked",dependencies=["not-done"])],set(),{SCOPE})
        b=shadow_rank([job("locked",dependencies=["done"])],{"done"},{SCOPE})
        self.assertEqual(len(a["eligible"]),0)
        self.assertEqual(len(b["eligible"]),1)

    def test_missing_source_hash_held(self):
        r=shadow_rank([job("unbound",source_sha256="missing")],set(),{SCOPE})
        self.assertEqual(len(r["eligible"]),0)

    def test_bad_bool_or_score_held(self):
        r=shadow_rank([job("bad-ready",ready="true"),
                       job("bad-value",value=True)],set(),{SCOPE})
        self.assertEqual(len(r["held"]),2)

    def test_duplicate_workid_rejected(self):
        with self.assertRaises(Held):
            shadow_rank([job("dup"),job("dup")],set(),{SCOPE})

    def test_unverified_worker_name_not_capability(self):
        l=SyntheticLedger({SCOPE},{"W01":set(),"worker-verified":{"source-read"}})
        with self.assertRaises(Held):
            l.claim(job_id="test",scope=SCOPE,worker_id="W01",
                    required_capabilities={"source-read"},now=100,ttl=60)
        with self.assertRaises(Held):
            l.claim(job_id="test",scope=SCOPE,worker_id="PretendWorker",
                    required_capabilities=set(),now=100,ttl=60)

    def test_single_writer_per_collision_scope(self):
        l=SyntheticLedger({SCOPE},{"A":{"a"},"B":{"a"}})
        a=l.claim(job_id="J1",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=50)
        with self.assertRaises(Held):
            l.claim(job_id="J2",scope=SCOPE,worker_id="B",
                    required_capabilities={"a"},now=110,ttl=50)
        self.assertEqual(a.fencing_epoch,1)

    def test_steal_only_after_expiry_increments_fence(self):
        l=SyntheticLedger({SCOPE},{"A":{"a"},"B":{"a"}})
        a=l.claim(job_id="J",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=10)
        with self.assertRaises(Held):
            l.claim(job_id="J",scope=SCOPE,worker_id="B",
                    required_capabilities={"a"},now=109,ttl=10)
        b=l.claim(job_id="J",scope=SCOPE,worker_id="B",
                  required_capabilities={"a"},now=110,ttl=10)
        self.assertGreater(b.fencing_epoch,a.fencing_epoch)
        with self.assertRaises(Held):
            l.commit(a,now=111,result_sha256=H)
        self.assertEqual(l.commit(b,now=111,result_sha256=H),"SYNTHETIC_RECEIPT_COMMITTED")
        self.assertEqual(len([e for e in l.events if e[0]=="SYNTHETIC_RECEIPT_COMMITTED"]),1)

    def test_success_receipt_replay_safe_and_conflict_held(self):
        l=SyntheticLedger({SCOPE},{"A":{"a"}})
        a=l.claim(job_id="J",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=10)
        self.assertEqual(l.commit(a,now=103,result_sha256=H),"SYNTHETIC_RECEIPT_COMMITTED")
        self.assertEqual(l.commit(a,now=104,result_sha256=H),"REPLAY_SAME_SYNTHETIC_RECEIPT_NO_EFFECT")
        with self.assertRaises(Held):
            l.commit(a,now=105,result_sha256="b"*64)
        with self.assertRaises(Held):
            l.claim(job_id="J",scope=SCOPE,worker_id="A",
                    required_capabilities={"a"},now=120,ttl=10)

    def test_stop_wins_and_no_revival(self):
        l=SyntheticLedger({SCOPE},{"A":{"a"}})
        a=l.claim(job_id="J",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=10)
        l.stop("J")
        with self.assertRaises(Held):
            l.commit(a,now=103,result_sha256=H)
        with self.assertRaises(Held):
            l.claim(job_id="J",scope=SCOPE,worker_id="A",
                    required_capabilities={"a"},now=120,ttl=10)

    def test_scope_labels_never_expand_authority(self):
        with self.assertRaises(Held):
            SyntheticLedger({"PRODUCTION"},{"A":{"admin"}})
        l=SyntheticLedger({SCOPE},{"A":{"admin"}})
        with self.assertRaises(Held):
            l.claim(job_id="J",scope="PRODUCTION",worker_id="A",
                    required_capabilities={"admin"},now=100,ttl=10)

    def test_different_scopes_can_be_in_flight(self):
        l=SyntheticLedger({SCOPE,SCOPE2},{"A":{"a"},"B":{"b"}})
        a=l.claim(job_id="J1",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=20)
        b=l.claim(job_id="J2",scope=SCOPE2,worker_id="B",
                  required_capabilities={"b"},now=100,ttl=20)
        self.assertEqual(len(l.lease_by_scope),2)
        self.assertEqual(l.commit(a,now=101,result_sha256=H),"SYNTHETIC_RECEIPT_COMMITTED")
        self.assertEqual(l.commit(b,now=101,result_sha256="b"*64),"SYNTHETIC_RECEIPT_COMMITTED")

    def test_expired_lease_commit_held(self):
        l=SyntheticLedger({SCOPE},{"A":{"a"}})
        a=l.claim(job_id="J",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=10)
        with self.assertRaises(Held):
            l.commit(a,now=110,result_sha256=H)

    def test_invalid_result_sha_does_not_commit(self):
        l=SyntheticLedger({SCOPE},{"A":{"a"}})
        a=l.claim(job_id="J",scope=SCOPE,worker_id="A",
                  required_capabilities={"a"},now=100,ttl=10)
        with self.assertRaises(Held):
            l.commit(a,now=101,result_sha256="FAKE")
        self.assertEqual(l.finished,{})

if __name__=="__main__":unittest.main()
