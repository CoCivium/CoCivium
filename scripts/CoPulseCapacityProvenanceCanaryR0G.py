#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

def sha_path(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def load(p): return json.loads(Path(p).read_text())
def run_json(cmd, expect_ok=True):
    cp=subprocess.run(cmd,capture_output=True,text=True)
    if expect_ok and cp.returncode!=0: raise RuntimeError(cp.stderr+cp.stdout)
    if not expect_ok: return cp
    return json.loads(cp.stdout.strip().splitlines()[-1])

def pulse(pid,cursor,delivery,domain):
    return {"pulse_id":pid,"cursor":cursor,"delivery_class":delivery,"digest_state":"DIGEST_CLASS__NOT_YET_COMPACTED" if delivery=="DIGEST" else None,"subject":pid,"relation_type":"relates_to","epistemic_class":"OBSERVED","domains":[domain],"topics":["r0g-fixture"],"evidence_refs":["fixture://"+pid],"source_identity":"fixture-source:"+pid,"authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PUBLIC","wake_conditions":[]}

def packet(receiver,last_ack,field,field_sha):
    sel=[x for x in field if x["cursor"]>last_ack]
    counts={"HOT":0,"WARM":0,"DIGEST":0,"SLEEP":0,"OLDER_OR_ACKED":len(field)-len(sel)}
    for x in sel: counts[x["delivery_class"]]+=1
    return {"schema":"CoPulseSubscriptionPacket.R0A.v0.1-candidate","state":"PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP","packet_id":"copulsepacket:r0g:"+receiver,"receiver_id":receiver,"profile_id":"CoGeneralist","source_bindings":{"pulses_sha256":field_sha},"cursor":{"last_acked_cursor":last_ack,"max_seen_cursor":6,"candidate_delivered_cursor":6,"ack_cursor_unchanged":last_ack},"counts":counts,"selected_pulses":sel,"effects":{"receiver_context_mutation":0,"provider_session_mutation":0,"authority_change":0,"public_outreach":0},"next":"RECEIVER_EXACT_PACKET_READPROOF_BEFORE_ACK_CURSOR_ADVANCE","nonclaims":["DELIVERY_NE_PICKUP"]}

def main():
    p=argparse.ArgumentParser()
    for name in ["worker","gate","freshness","budget","compactor","replay"]: p.add_argument("--"+name,required=True)
    p.add_argument("--out-root",required=True); a=p.parse_args()
    root=Path(a.out_root)
    if root.exists(): raise SystemExit("FAIL_CLOSED__NO_CLOBBER")
    root.mkdir(parents=True)
    field=[pulse("pulse.hot.001",1,"HOT","CoUX+/CoSurface+"),pulse("pulse.warm.002",2,"WARM","CoLex+"),pulse("pulse.digest.003",3,"DIGEST","CoHumour+"),pulse("pulse.digest.004",4,"DIGEST","CoTheoryAll+"),pulse("pulse.digest.005",5,"DIGEST","CoHumour+"),pulse("pulse.digest.006",6,"DIGEST","CoTheoryAll+")]
    field_path=root/"field.json"; field_path.write_text(json.dumps(field,indent=2)+"\n"); field_sha=sha_path(field_path)
    specs=[("A","VirtualReceiver-R0G-A",2,6,"challenge-r0g-a"),("B","VirtualReceiver-R0G-B",0,3,"challenge-r0g-b")]
    records=[]; procs=[]
    try:
      for suffix,receiver,last_ack,capacity,challenge in specs:
        wdir=root/("worker-"+suffix)
        proc=subprocess.Popen([sys.executable,a.worker,"--receiver-id",receiver,"--virtual-session-id","virtual:r0g:"+suffix,"--participant-id","participant:r0g:"+suffix,"--challenge",challenge,"--capacity",str(capacity),"--sampled-at","2026-09-23T12:51:00Z","--observed-at","2026-09-23T12:51:01Z","--out-dir",str(wdir)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        procs.append(proc); hello=json.loads(proc.stdout.readline()); assert proc.poll() is None
        proc.stdin.write("ACK "+challenge+"\n"); proc.stdin.flush(); ack=json.loads(proc.stdout.readline()); assert ack["state"]=="ACK_CHALLENGE_CONFIRMED" and proc.poll() is None
        pkt=packet(receiver,last_ack,field,field_sha); pkt_path=root/("packet-"+suffix+".json"); pkt_path.write_text(json.dumps(pkt,indent=2)+"\n")
        gate_path=root/("gate-"+suffix+".json")
        gate_term=run_json([sys.executable,a.gate,"--binding",hello["binding_path"],"--pressure",hello["pressure_path"],"--attestation",hello["attestation_path"],"--challenge",challenge,"--output",str(gate_path)])
        assert proc.poll() is None
        fresh_path=root/("fresh-"+suffix+".json")
        fresh_term=run_json([sys.executable,a.freshness,"--pressure",hello["pressure_path"],"--evaluated-at","2026-09-23T12:52:00Z","--max-age-seconds","300","--max-future-skew-seconds","30","--output",str(fresh_path)])
        assert fresh_term["STATE"]=="PASS_FRESH_PRESSURE_SAMPLE"
        election_path=root/("election-"+suffix+".json")
        elect=run_json([sys.executable,a.budget,"--packet",str(pkt_path),"--pressure",hello["pressure_path"],"--output",str(election_path)])
        comp_path=root/("comp-"+suffix+".json"); comp=run_json([sys.executable,a.compactor,"--packet",str(pkt_path),"--digest-budget",str(elect["ELECTED_DIGEST_BUDGET"]),"--output",str(comp_path)])
        replay_path=root/("replay-"+suffix+".json"); rep=run_json([sys.executable,a.replay,"--compacted",str(comp_path),"--source-packet",str(pkt_path),"--output",str(replay_path)])
        records.append({"receiver_id":receiver,"pid":hello["pid"],"worker_alive_during_gate":True,"binding_id":hello["binding_id"],"gate_sha256":load(gate_path)["gate_sha256"],"pressure_sha256":sha_path(hello["pressure_path"]),"capacity":capacity,"last_acked_cursor":last_ack,"elected_budget":elect["ELECTED_DIGEST_BUDGET"],"replayed_digest_count":rep["REPLAYED_DIGEST"],"exact_replay":rep["EXACT_OBJECT_EQUALITY"]})
      assert records[0]["pid"]!=records[1]["pid"] and records[0]["elected_budget"]==4 and records[1]["elected_budget"]==1
      tampered=root/"tampered-pressure.json"; x=load(root/"worker-A"/"pressure.json"); x["max_currentness_items"]=99; tampered.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
      bad=run_json([sys.executable,a.gate,"--binding",str(root/"worker-A"/"binding.json"),"--pressure",str(tampered),"--attestation",str(root/"worker-A"/"attestation.json"),"--challenge","challenge-r0g-a","--output",str(root/"tampered-gate.json")],expect_ok=False)
      if bad.returncode==0 or "PRESSURE_SHA_MISMATCH" not in (bad.stdout+bad.stderr): raise SystemExit("FAIL_CLOSED__TAMPER_NOT_REJECTED")
      result={"schema":"CoPulseCapacityProvenanceLiveReceiverCanary.R0G.v0.1-candidate","state":"PASS_R0G_LIVE_RECEIVER_PROCESS_BINDING__CAPACITY_SOURCE_PROVENANCE__TAMPER_REJECTED__EXACT_REPLAY","shared_pulse_field_sha256":field_sha,"receivers":records,"checks":{"distinct_live_processes":True,"live_during_provenance_gate":True,"capacity_sample_hash_bound":True,"tampered_capacity_rejected":True,"divergent_budgets":[4,1],"independent_ack":[2,0],"exact_replay":True},"effects":{"provider_session_mutation":0,"x2_mutation":0,"ack_cursor_mutation":0,"authority_change":0,"source_deletion":0},"next":"R0H_AUTHENTIC_CAPACITY_MEASUREMENT_OR_X2_LIVE_RECEIVER_BINDING","nonclaims":["LOCAL_PROCESS_CANARY_NE_X2_LIVE_RECEIVER","PROVENANCE_NE_ACCURACY","LIVENESS_NE_PERSISTENCE","PROCESS_PID_NE_IDENTITY","LOCAL_CANARY_NE_CROSS_FAILURE_DOMAIN"]}
      rp=root/"r0g-result.json"; enc=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode(); rp.write_bytes(enc)
      print(json.dumps({"STATE":result["state"],"OUTPUT":str(rp),"OUTPUT_SHA256":hashlib.sha256(enc).hexdigest().upper(),"PIDS":[records[0]["pid"],records[1]["pid"]],"BUDGETS":[4,1],"TAMPER_REJECTED":True,"NEXT":result["next"]},separators=(",",":")))
    finally:
      for proc in procs:
        if proc.poll() is None:
          try: proc.stdin.write("EXIT\n"); proc.stdin.flush(); proc.stdout.readline(); proc.wait(timeout=3)
          except Exception: proc.kill()
if __name__=="__main__": main()
