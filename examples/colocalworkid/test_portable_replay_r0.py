"""Public synthetic WorkID capsule proof.  Never imports private X2 state."""
import hashlib, json, pathlib, sqlite3, subprocess, sys, tempfile, unittest, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cotalkitout"))
from due_work_catchup_r0 import DueWorkQueue

WORK="CoLocalFirstWorkID_SYNTHETIC_CI_R0"
DUE=1700000000
SOURCE={"work_id":WORK,"synthetic":True,"receiver_ack":False}
MODEL_LIKE={"work_id":WORK,"decision":"GO","receiver_ack":"yes"}
GUARD={"work_id":WORK,"decision":"HOLD","receiver_ack":False,"effects":0,"release":False}
NAMES=("source.json","proposal.json","decision.json","receipt.json","queue.sqlite3")
def data(o): return (json.dumps(o,sort_keys=True)+"\n").encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def filehash(p): return sha(p.read_bytes())
def verify(ok,code):
    if not ok: raise ValueError("HOLD_"+code)

def make(root):
    folder=root/"producer";folder.mkdir()
    s,p=data(SOURCE),data(MODEL_LIKE)
    verdict=data(dict(GUARD,source_sha256=sha(s),proposal_sha256=sha(p)))
    for name,raw in zip(NAMES[:3],(s,p,verdict)): (folder/name).write_bytes(raw)
    q=DueWorkQueue(str(folder/"queue.sqlite3"))
    try:
        verify(q.enqueue(WORK,"SYNTHETIC_R0",sha(s),DUE)=="ENQUEUED","ENQUEUE")
        claimed=q.claim_due(now=DUE+1,owner="SYNTHETIC",limit=1)
        verify(len(claimed)==1,"CLAIM")
        verify(q.complete(claimed[0],result_sha256=sha(verdict),now=DUE+2)=="COMMITTED_LOCAL_ONLY","FENCE")
    finally:q.close()
    (folder/"receipt.json").write_bytes(data({"work_id":WORK,"result_sha256":sha(verdict),"model_calls":0,"receiver_ack":False}))
    manifest={"schema":"CoAll.WorkID.PortableSynthetic.R0","origin":"INVENTED_ONLY",
              "work_id":WORK,"members":[{"name":n,"size":(folder/n).stat().st_size,"sha256":filehash(folder/n)} for n in NAMES],
              "nonclaims":["NOT_X2_CAPSULE","NOT_COSTEAD_ACK","NOT_AUTOWAKE","NOT_COBAR_RELEASE"]}
    capsule=root/"capsule.zip"
    with zipfile.ZipFile(capsule,"x",zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json",data(manifest))
        for name in NAMES:z.write(folder/name,arcname=name)
    return capsule,filehash(capsule)

def restore(capsule,pin,target):
    verify(not target.exists(),"DEST_EXISTS")
    verify(filehash(capsule)==pin,"CAPSULE_HASH")
    with zipfile.ZipFile(capsule) as z:
        inf=z.infolist();names=[e.filename for e in inf]
        verify(len(inf)==6 and len(set(names))==6 and set(names)==set(NAMES)|{"manifest.json"},"MEMBER_NAMES")
        verify(all(not e.is_dir() and not(e.flag_bits & 1) and 0<e.file_size<2000000 and
                   ((e.external_attr>>16)&0o170000)!=0o120000 for e in inf),"ZIP_SAFETY")
        verify(sum(e.file_size for e in inf)<8000000,"ZIP_BOMB")
        m=json.loads(z.read("manifest.json"))
        verify(m.get("schema")=="CoAll.WorkID.PortableSynthetic.R0" and m.get("origin")=="INVENTED_ONLY" and m.get("work_id")==WORK,"MANIFEST")
        rows=m["members"];verify(len(rows)==5,"MANIFEST_COUNT")
        index={v["name"]:v for v in rows}
        verify(set(index)==set(NAMES) and len(index)==5,"MANIFEST_NAMES")
        for n in NAMES:
            b=z.read(n)
            verify(len(b)==index[n]["size"] and sha(b)==index[n]["sha256"],"MEMBER_HASH")
        target.mkdir()
        for n in NAMES:
            (target/n).write_bytes(z.read(n))
            verify(filehash(target/n)==index[n]["sha256"],"RESTORE_HASH")

def replay(target):
    s,p,r=[target/n for n in NAMES[:3]]
    verify(s.read_bytes()==data(SOURCE) and p.read_bytes()==data(MODEL_LIKE),"SOURCE")
    # Exact, canonical synthetic decision. No appended authority or hidden claims.
    expected_decision=dict(GUARD,source_sha256=filehash(s),proposal_sha256=filehash(p))
    verify(r.read_bytes()==data(expected_decision),"GUARD")
    # Do not let a forged ACK, a changed WorkID, or bool-as-int pass replay.
    expected_receipt={"work_id":WORK,"result_sha256":filehash(r),
                      "model_calls":0,"receiver_ack":False}
    verify((target/"receipt.json").read_bytes()==data(expected_receipt),"RECEIPT")
    q=DueWorkQueue(str(target/"queue.sqlite3"))
    try:
        verify(q.enqueue(WORK,"SYNTHETIC_R0",filehash(s),DUE)=="REPLAY","IDENTITY")
        verify(q.claim_due(now=DUE+500,owner="RECOVER",limit=1)==[],"DUPLICATE")
        row=q.db.execute("SELECT state,result_sha256,epoch FROM work WHERE work_id=?",(WORK,)).fetchone()
        verify(row==("DONE",filehash(r),1),"FENCED_STATE")
    finally:q.close()
    return {"state":"PASS_SYNTHETIC_FRESH_PROCESS_REPLAY","new_model_calls":0,"external_effects":0,"nas_receiver_ack":False}

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.archive,self.pin=make(self.root)
        self.target=self.root/"restored"
    def test_fresh_process_and_replay(self):
        restore(self.archive,self.pin,self.target)
        for _ in range(2):
            run=subprocess.run([sys.executable,str(pathlib.Path(__file__).resolve()),"--replay",str(self.target)],
                               text=True,capture_output=True,timeout=10,check=True)
            self.assertEqual(json.loads(run.stdout)["new_model_calls"],0)
    def test_bad_archive_hash_holds(self):
        with self.assertRaisesRegex(ValueError,"HOLD_CAPSULE_HASH"):restore(self.archive,"0"*64,self.target)
    def test_no_clobber(self):
        self.target.mkdir()
        with self.assertRaisesRegex(ValueError,"HOLD_DEST_EXISTS"):restore(self.archive,self.pin,self.target)
    def test_tampered_decision_holds(self):
        restore(self.archive,self.pin,self.target)
        f=self.target/"decision.json";o=json.loads(f.read_bytes());o["receiver_ack"]=True;f.write_bytes(data(o))
        with self.assertRaisesRegex(ValueError,"HOLD_GUARD"):replay(self.target)
    def test_forged_receiver_ack_is_held(self):
        restore(self.archive,self.pin,self.target)
        f=self.target/"receipt.json"
        claim=json.loads(f.read_bytes());claim["receiver_ack"]=True
        f.write_bytes(data(claim))
        with self.assertRaisesRegex(ValueError,"HOLD_RECEIPT"):replay(self.target)

    def test_false_model_call_count_is_not_zero(self):
        restore(self.archive,self.pin,self.target)
        f=self.target/"receipt.json"
        claim=json.loads(f.read_bytes());claim["model_calls"]=False
        f.write_bytes(data(claim))
        with self.assertRaisesRegex(ValueError,"HOLD_RECEIPT"):replay(self.target)

    def test_wrong_receipt_workid_is_held(self):
        restore(self.archive,self.pin,self.target)
        f=self.target/"receipt.json"
        claim=json.loads(f.read_bytes());claim["work_id"]="other-work"
        f.write_bytes(data(claim))
        with self.assertRaisesRegex(ValueError,"HOLD_RECEIPT"):replay(self.target)

    def test_appended_authority_claim_with_matching_receipt_hash_is_held(self):
        restore(self.archive,self.pin,self.target)
        d=self.target/"decision.json";r=self.target/"receipt.json"
        claim=json.loads(d.read_bytes());claim["external_receiver_ack"]=True
        d.write_bytes(data(claim))
        receipt=json.loads(r.read_bytes());receipt["result_sha256"]=filehash(d)
        r.write_bytes(data(receipt))
        with self.assertRaisesRegex(ValueError,"HOLD_GUARD"):replay(self.target)

    def test_collision_held(self):
        restore(self.archive,self.pin,self.target)
        q=DueWorkQueue(str(self.target/"queue.sqlite3"))
        try:self.assertEqual(q.enqueue(WORK,"SYNTHETIC_R0","0"*64,DUE),"CONFLICT")
        finally:q.close()
if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--replay":
        print(json.dumps(replay(pathlib.Path(sys.argv[2])),sort_keys=True))
    else:unittest.main()
