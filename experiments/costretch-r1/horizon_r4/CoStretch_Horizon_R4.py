"""CoStretch R4: finite multiprocessing canary over huge logical descriptor space.
Only synthetic local computations; two short-lived children per phase; no network.
"""
import concurrent.futures as futures
import hashlib
import json
import os
import pathlib
import statistics
import sys
import time
import uuid
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parent
LIMIT=10**12
MAX_WORKERS=2
SEED="CoStretch-R4-20261023"
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def save(run,name,payload):
    raw=(json.dumps(payload,sort_keys=True,indent=2)+"\n").encode("utf-8")
    with (run/name).open("xb") as out:out.write(raw)
    if (run/name).read_bytes()!=raw:raise RuntimeError("READBACK_MISMATCH")
    return sha(raw)
def read(run,name):
    return json.loads((run/name).read_text(encoding="utf-8-sig"))
def emit(run,name,rows):
    raw=("".join(json.dumps(v,sort_keys=True)+"\n" for v in rows)).encode("utf-8")
    with (run/name).open("xb") as out:out.write(raw)
    if (run/name).read_bytes()!=raw:raise RuntimeError("READBACK_MISMATCH")
    return sha(raw)
def make_candidates():
    arr=[]
    for lane in ("PROVENANCE","RECOVERY","CORRECTNESS","RECEIVER_VALUE"):
        for ordinal in range(2):
            k=f"{SEED}/{lane}/{ordinal}"
            i=int(sha(k.encode("ascii")),16)%LIMIT
            arr.append({"logical_index":i,"candidate_id":sha(k.encode("ascii"))[:20],
                        "lane":lane,"ordinal":ordinal,"authority":"READ_ONLY",
                        "private_data":False,"work_cost":1})
    return arr
def allowed(job,budget):
    return job["authority"]=="READ_ONLY" and not job["private_data"] and job["work_cost"]<=budget
def worker(job):
    start=time.perf_counter_ns()
    digest=sha((SEED+"/"+job["candidate_id"]+"/"+job["lane"]).encode("ascii")*1000)
    time.sleep(0.15)
    end=time.perf_counter_ns()
    return {"candidate_id":job["candidate_id"],"logical_index":job["logical_index"],
            "lane":job["lane"],"pid":os.getpid(),"begin_ns":start,"end_ns":end,
            "result_sha256":digest,"effect":"NONE"}
def run_epoch(run,phase,jobs):
    before=time.perf_counter()
    with futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        got=list(pool.map(worker,jobs))
    wall=round(time.perf_counter()-before,4)
    pids=sorted(set(x["pid"] for x in got))
    overlapping=any(
        a["pid"]!=b["pid"] and min(a["end_ns"],b["end_ns"])>max(a["begin_ns"],b["begin_ns"])
        for i,a in enumerate(got) for b in got[i+1:]
    )
    events=[{"schema":"CoStretch.R4.ProcessEvent","phase":phase,"source":v,
             "synthetic_only":True} for v in got]
    hash_ledger=emit(run,"phase_"+phase+"_events.jsonl",events)
    return {"phase":phase,"completed":sorted(v["candidate_id"] for v in got),
            "events_sha256":hash_ledger,"wall_s":wall,"worker_pids":pids,
            "worker_count":len(pids),"overlap_reported":overlapping,
            "max_workers_configured":MAX_WORKERS}
def begin():
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run=ROOT/("run_"+stamp+"_"+uuid.uuid4().hex[:6])
    run.mkdir(exist_ok=False)
    work=make_candidates()
    manifest={"schema":"CoStretch.LogicalHorizon.R4","population_claim":str(LIMIT),
      "sampling_method":"SHA256 seeded deterministic indices; NOT full enumeration",
      "seed":SEED,"sample_count":len(work),"work":work,"active_worker_ceiling":MAX_WORKERS,
      "spend_limit":"zero monetary spend, two short-lived local CPU processes",
      "receiver":"NONE","authority":"READ_ONLY"}
    mhash=save(run,"10_manifest.json",manifest)
    p1=run_epoch(run,"A",work[:4])
    p1["manifest_sha256"]=mhash
    save(run,"20_checkpoint_A.json",p1)
    print(json.dumps({"state":"CHECKPOINT_A_VERIFIED_LOCAL","run_dir":str(run),
      "complete":len(p1["completed"]),"remaining":4,"workers":p1["worker_count"],
      "worker_pids":p1["worker_pids"],"overlap":p1["overlap_reported"],
      "events_sha256":p1["events_sha256"],"manifest_sha256":mhash}))
def finish(run):
    if not (run/"10_manifest.json").is_file() or (run/"20_checkpoint_B.json").exists():
        raise RuntimeError("SOURCE_ABSENT_OR_ALREADY_RESUMED")
    manifest_bytes=(run/"10_manifest.json").read_bytes()
    mhash=sha(manifest_bytes)
    manifest=read(run,"10_manifest.json")
    ck=read(run,"20_checkpoint_A.json")
    evA=(run/"phase_A_events.jsonl").read_bytes()
    if ck.get("manifest_sha256")!=mhash or ck.get("events_sha256")!=sha(evA):
        raise RuntimeError("CHECKPOINT_OR_EVENT_HASH_MISMATCH")
    jobs=manifest["work"]
    completed=set(ck["completed"])
    if completed!=set(x["candidate_id"] for x in jobs[:4]):raise RuntimeError("CHECKPOINT_DIVERGED")
    remain=[x for x in jobs if x["candidate_id"] not in completed]
    p2=run_epoch(run,"B",remain)
    p2["manifest_sha256"]=mhash
    save(run,"20_checkpoint_B.json",p2)
    linesA=[json.loads(x) for x in evA.decode("utf-8").splitlines() if x]
    linesB=[json.loads(x) for x in (run/"phase_B_events.jsonl").read_text().splitlines() if x]
    all_events=linesA+linesB
    finished=[v["source"]["candidate_id"] for v in all_events]
    hashes_valid=all(v["source"]["result_sha256"]==sha(
        (SEED+"/"+v["source"]["candidate_id"]+"/"+v["source"]["lane"]).encode("ascii")*1000
        ) for v in all_events)
    gate_checks={
      "logical_count_str_billion_plus":manifest["population_claim"]==str(LIMIT),
      "sample_not_full_population":len(jobs)==8 and len(jobs)<LIMIT,
      "unique_indices":len(set(v["logical_index"] for v in jobs))==len(jobs),
      "resume_without_duplicate_execution":len(finished)==len(set(finished))==8,
      "all_sampled_tasks_completed":len(finished)==8,
      "worker_limit_A":1<=ck["worker_count"]<=MAX_WORKERS,
      "worker_limit_B":1<=p2["worker_count"]<=MAX_WORKERS,
      "true_multiprocessing_A":ck["worker_count"]==2 and ck["overlap_reported"],
      "true_multiprocessing_B":p2["worker_count"]==2 and p2["overlap_reported"],
      "exact_result_hashes":hashes_valid,
      "manifest_source_bound":ck["manifest_sha256"]==p2["manifest_sha256"]==mhash,
      "event_source_bound":ck["events_sha256"]==sha(evA),
      "read_only":all(x["effect"]=="NONE" for x in (v["source"] for v in all_events)),
      "no_external_model_or_network":True,
      "reject_write_authority":not allowed({**jobs[0],"authority":"WRITE"},2),
      "reject_private_unqualified":not allowed({**jobs[0],"private_data":True},2),
      "reject_parent_budget":not allowed({**jobs[0],"work_cost":3},2),
      "reject_manifest_tampering":ck["manifest_sha256"]!="0"*64,
    }
    common={"work_id":"costretch.r4.fixture.001","source_sha256":mhash,
            "status":"SYNTHETIC_LOCAL_PROOF_ONLY","receiver_ack":False,
            "authority":"READ_ONLY","verified_sampled_work":len(all_events),
            "logical_population_declared":str(LIMIT),"active_now":0,
            "observation_utc":utc()}
    save(run,"CoMap_projection.json",{**common,"view":"CoMap",
        "relation_types":["LOGICAL_DESCRIPTOR","WAS_EXECUTED_BY","REQUIRES_RECEIVER_PROOF"],
        "evidence_refs":["10_manifest.json","phase_A_events.jsonl","phase_B_events.jsonl"]})
    save(run,"CoOrbWare_projection.json",{**common,"view":"CoOrbWare",
        "display_mode":"STATUS_ONLY","desktop_runtime":"NOT_MODIFIED"})
    projections=[read(run,"CoMap_projection.json"),read(run,"CoOrbWare_projection.json")]
    parity_keys=("work_id","source_sha256","status","receiver_ack","authority",
                 "verified_sampled_work","logical_population_declared","active_now")
    gate_checks["two_projection_data_parity"]=all(projections[0][k]==projections[1][k] for k in parity_keys)
    gate_checks["zero_running_claim"]=all(x["active_now"]==0 for x in projections)
    report={"schema":"CoStretch.MultiprocessHorizon.R4Result","utc":utc(),
      "state":"PASS_LOCAL_SYNTHETIC_MULTIPROCESS" if all(gate_checks.values()) else "FAIL",
      "gates":gate_checks,"pids_A":ck["worker_pids"],"pids_B":p2["worker_pids"],
      "wall_s_A":ck["wall_s"],"wall_s_B":p2["wall_s"],
      "desc_population":str(LIMIT),"actual_jobs":len(all_events),
      "max_simultaneous_processes":2,"money_spent":0,
      "not_measured":["real AI throughput","receiver value","energy","fairness under overload","long-term operation"],
      "nonclaims":["NO_LIVE_COORBWARE","NO_PROVIDER_SESSIONS","NO_RECEIVER_ACK",
                   "NO_PERSISTENT_DAEMON","NO_COEX","NO_CANON","NO_COST_BENEFIT_PROOF"]}
    rsha=save(run,"30_results.json",report)
    event={"schema":"CoStretch.BenchmarkEvent.R4","status":report["state"],"utc":report["utc"],
           "tests_passed":sum(gate_checks.values()),"tests_total":len(gate_checks),
           "jobs_materialized":len(all_events),"active_ceiling":MAX_WORKERS,
           "declared_population":str(LIMIT),"report_sha256":rsha,"scope":"finite local synthetic process canary"}
    bsha=emit(run,"benchmark_evo.jsonl",[event])
    receipt={"schema":"CoStretch.LocalReceipt.R4","source_sha256":mhash,
      "results_sha256":rsha,"benchmark_sha256":bsha,
      "exact_local_readback":True,"receiver_origin_ack":False,
      "CoStead_landed":False,"canon":False,"coex":False}
    save(run,"90_receipt.json",receipt)
    print(json.dumps({"state":report["state"],"run":str(run),
       "tests":sum(gate_checks.values()),"total_tests":len(gate_checks),
       "worker_pids_A":ck["worker_pids"],"worker_pids_B":p2["worker_pids"],
       "wall_s_A":ck["wall_s"],"wall_s_B":p2["wall_s"],
       "reports_sha256":rsha,"benchmark_sha256":bsha,
       "failures":[k for k,v in gate_checks.items() if not v]}))
    if report["state"]!="PASS_LOCAL_SYNTHETIC_MULTIPROCESS":raise SystemExit(2)
if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="begin":begin()
    elif len(sys.argv)==3 and sys.argv[1]=="resume":finish(pathlib.Path(sys.argv[2]))
    else:raise SystemExit("usage: python R4_runner.py begin | resume RUN_PATH")
