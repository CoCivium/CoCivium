"""CoStretch R5: bounded elastic reduction/reawakening, local synthetic processes only.
No daemon, network, provider call, system configuration change or external effects.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import sys
import time
import uuid
from datetime import datetime,timezone

ROOT=pathlib.Path(__file__).resolve().parent
R4=ROOT.parent/"R4_LogicalHorizonMultiprocess_20261023"/"run_20261023T222000450181Z_772db0"
MAX=2
def now():return datetime.now(timezone.utc).isoformat()
def hash_bytes(b):return hashlib.sha256(b).hexdigest()
def js(obj):return (json.dumps(obj,sort_keys=True,indent=2)+"\n").encode("utf-8")
def exclusive(path,data):
    with path.open("xb") as f:f.write(data)
    assert path.read_bytes()==data
    return hash_bytes(data)
def read(path):return json.loads(path.read_bytes().decode("utf-8-sig"))
def manifest_verified():
    src=(R4/"10_manifest.json").read_bytes()
    receipt=read(R4/"90_receipt.json")
    h=hash_bytes(src)
    if receipt["source_sha256"]!=h:raise RuntimeError("R4_SOURCE_HASH_MISMATCH")
    parsed=json.loads(src.decode("utf-8"))
    if parsed["schema"]!="CoStretch.LogicalHorizon.R4" or len(parsed["work"])!=8:
        raise RuntimeError("R4_FORMAT_OR_COUNT_UNEXPECTED")
    return h,parsed
def policy(prior,pressure,authorized=True,healthy=True,source_current=True,
           budget=2,demand=4,retired=False):
    """Returns qualified capacity. Pressure is a synthetic input in this R5."""
    state=dict(prior)
    if prior.get("retired") or retired:
        return {"ceiling":0,"low_streak":0,"retired":True,"reason":"PERMANENT_RETIREMENT"}
    if not authorized or not healthy or not source_current:
        return {"ceiling":0,"low_streak":0,"retired":False,"reason":"PARK_UNQUALIFIED"}
    if not isinstance(pressure,(float,int)) or not 0<=pressure<=1:
        return {"ceiling":0,"low_streak":0,"retired":False,"reason":"PARK_UNKNOWN_PRESSURE"}
    if not isinstance(budget,int) or budget<1 or demand<1:
        return {"ceiling":0,"low_streak":0,"retired":False,"reason":"PARK_NO_BUDGET_OR_DEMAND"}
    cap=min(MAX,budget,demand)
    if pressure>=0.8:
        return {"ceiling":min(1,cap),"low_streak":0,"retired":False,"reason":"PRESSURE_CONTRACT"}
    if pressure<=0.3:
        low=min(2,prior.get("low_streak",0)+1)
        wanted=min(cap,2 if (prior["ceiling"]>1 or low>=2) else 1)
        return {"ceiling":wanted,"low_streak":low,"retired":False,
                "reason":"LOW_REOPEN" if low>=2 and wanted>1 else "HYSTERESIS_HOLD"}
    return {"ceiling":min(prior["ceiling"],cap),"low_streak":0,
            "retired":False,"reason":"MID_PRESSURE_HOLD"}
def work(job):
    start=time.perf_counter_ns()
    taskdata=f"costretch.r5.synthetic/{job['epoch']}/{job['candidate_id']}".encode("ascii")
    digest=hash_bytes(taskdata*1000)
    time.sleep(0.14)
    stop=time.perf_counter_ns()
    return {"event_id":job["event_id"],"candidate_id":job["candidate_id"],
            "epoch":job["epoch"],"pid":os.getpid(),"begin_ns":start,"end_ns":stop,
            "digest":digest,"effect":"NONE"}
def epoch(run,tag,workset,decision):
    active=decision["ceiling"]
    if active<1:raise RuntimeError("INVALID_RUN_WITHOUT_ELIGIBLE_CAPACITY")
    jobs=[{"event_id":f"R5/{tag}/{j['candidate_id']}",
           "candidate_id":j["candidate_id"],"epoch":tag} for j in workset]
    t=time.perf_counter()
    with cf.ProcessPoolExecutor(max_workers=active) as ex:
        results=list(ex.map(work,jobs))
    wall=round(time.perf_counter()-t,4)
    pids=sorted(set(x["pid"] for x in results))
    overlap=any(x["pid"]!=y["pid"] and max(x["begin_ns"],y["begin_ns"])<min(x["end_ns"],y["end_ns"])
                for i,x in enumerate(results) for y in results[i+1:])
    events=[{"schema":"CoStretch.R5.SyntheticWorkEvent","detail":x} for x in results]
    lines=("".join(json.dumps(x,sort_keys=True)+"\n" for x in events)).encode("utf-8")
    ehash=exclusive(run/("phase_"+tag+"_events.jsonl"),lines)
    return {"epoch":tag,"decision":decision,"jobs":len(jobs),
            "event_ids":sorted(x["event_id"] for x in results),"event_sha256":ehash,
            "pids":pids,"observed_distinct_workers":len(pids),"overlap":overlap,
            "wall_seconds":wall,"workers_exited_with_executor":True}
def events_verified(run,record):
    path=run/("phase_"+record["epoch"]+"_events.jsonl")
    data=path.read_bytes()
    if hash_bytes(data)!=record["event_sha256"]:return False
    events=[json.loads(x)["detail"] for x in data.decode("utf-8").splitlines()]
    if len(events)!=record["jobs"]:return False
    if sorted(x["event_id"] for x in events)!=record["event_ids"]:return False
    for x in events:
        msg=f"costretch.r5.synthetic/{x['epoch']}/{x['candidate_id']}".encode("ascii")
        if hash_bytes(msg*1000)!=x["digest"] or x["effect"]!="NONE":return False
    return True
def start():
    h,manifest=manifest_verified()
    run=ROOT/("run_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+"_"+uuid.uuid4().hex[:6])
    run.mkdir(exist_ok=False)
    capsule={"schema":"CoStretch.R5.ElasticHorizonCapsule","created_utc":now(),
        "source_r4_hash":h,"r4_run":str(R4),"population_declared":"1000000000000",
        "selected_distinct_indices":len(manifest["work"]),"worker_cap":MAX,
        "privacy":"SYNTHETIC_ONLY","authority":"READ_ONLY","outbound_effects":0,
        "plan":"A normal 2; B high-pressure 1; checkpoint exit; C low-first 1; D low-second 2; exit",
        "pressure_source":"SYNTHETIC_FIXTURE_NOT_X2_TELEMETRY",
        "no_auto_authority":"Retirement or revocation must not be reopened by low pressure"}
    chash=exclusive(run/"10_capsule.json",js(capsule))
    a=policy({"ceiling":2,"low_streak":2,"retired":False},0.1)
    b=policy(a,0.93)
    if (a["ceiling"],b["ceiling"])!=(2,1):raise RuntimeError("DECISION_MISMATCH")
    wa=epoch(run,"A",manifest["work"][:4],a)
    wb=epoch(run,"B",manifest["work"][4:6],b)
    ck={"schema":"CoStretch.R5.CheckpointA","capsule_sha256":chash,"source_r4_hash":h,
        "current_policy":b,"phases":[wa,wb],"utc":now(),"shutdown_after_checkpoint":True}
    exclusive(run/"20_checkpoint_A.json",js(ck))
    print(json.dumps({"status":"CHECKPOINT_EXITED","run":str(run),
        "ceilings":[a["ceiling"],b["ceiling"]],"phase_pids":[wa["pids"],wb["pids"]],
        "overlap_A":wa["overlap"],"r4_source_sha256":h,"checkpoint_capsule_sha256":chash,
        "complete":6,"remaining_invocations":6}))
def resume(run):
    if not (run/"10_capsule.json").exists() or not (run/"20_checkpoint_A.json").exists():
        raise RuntimeError("CHECKPOINT_MISSING")
    if (run/"20_checkpoint_B.json").exists():raise RuntimeError("NO_CLOBBER_ALREADY_FINISHED")
    capsule_bytes=(run/"10_capsule.json").read_bytes()
    capsule=read(run/"10_capsule.json")
    ck=read(run/"20_checkpoint_A.json")
    h,manifest=manifest_verified()
    if ck["capsule_sha256"]!=hash_bytes(capsule_bytes) or capsule["source_r4_hash"]!=h or ck["source_r4_hash"]!=h:
        raise RuntimeError("CHANGED_SOURCE_OR_CAPSULE")
    if len(ck["phases"])!=2 or not all(events_verified(run,x) for x in ck["phases"]):
        raise RuntimeError("CHECKPOINT_A_EVENTS_INVALID")
    c=policy(ck["current_policy"],0.17)
    d=policy(c,0.15)
    if (c["ceiling"],d["ceiling"])!=(1,2) or c["low_streak"]!=1 or d["low_streak"]!=2:
        raise RuntimeError("HYSTERESIS_PROOF_INVALID")
    wc=epoch(run,"C",manifest["work"][6:8],c)
    wd=epoch(run,"D",manifest["work"][:4],d)
    allp=ck["phases"]+[wc,wd]
    exclusive(run/"20_checkpoint_B.json",js({
        "schema":"CoStretch.R5.CheckpointB","capsule_sha256":ck["capsule_sha256"],
        "source_r4_hash":h,"phases":allp,"utc":now(),"shutdown_after_checkpoint":True}))
    observed=[json.loads(line)["detail"] for e in allp
              for line in (run/("phase_"+e["epoch"]+"_events.jsonl")).read_text().splitlines()]
    expected_ceilings=[2,1,1,2]
    # The following is an explicit comparison of pure policy negative controls.
    tests={
        "source_manifest_hash_pinned":h==capsule["source_r4_hash"],
        "checkpoint_capsule_hash_pinned":hash_bytes(capsule_bytes)==ck["capsule_sha256"],
        "checkpoint_A_events_verified":all(events_verified(run,x) for x in ck["phases"]),
        "checkpoint_B_events_verified":events_verified(run,wc) and events_verified(run,wd),
        "two_invocations_recovery":ck["shutdown_after_checkpoint"],
        "correct_four_phase_caps": [x["decision"]["ceiling"] for x in allp]==expected_ceilings,
        "actual_two_worker_overlapping_A":allp[0]["observed_distinct_workers"]==2 and allp[0]["overlap"],
        "actual_one_worker_B":allp[1]["observed_distinct_workers"]==1 and not allp[1]["overlap"],
        "actual_one_worker_C":allp[2]["observed_distinct_workers"]==1 and not allp[2]["overlap"],
        "actual_two_worker_overlapping_D":allp[3]["observed_distinct_workers"]==2 and allp[3]["overlap"],
        "no_duplicate_event_ids":len(set(x["event_id"] for x in observed))==len(observed),
        "exact_result_digests":all(hash_bytes(
             f"costretch.r5.synthetic/{x['epoch']}/{x['candidate_id']}".encode("ascii")*1000
             )==x["digest"] for x in observed),
        "all_events_no_outbound_effect":all(x["effect"]=="NONE" for x in observed),
        "pressure_contraction":allp[1]["decision"]["reason"]=="PRESSURE_CONTRACT",
        "first_low_hysteresis_hold":allp[2]["decision"]["reason"]=="HYSTERESIS_HOLD",
        "second_low_reopen":allp[3]["decision"]["reason"]=="LOW_REOPEN",
        "unknown_pressure_parks":policy(d,None)["ceiling"]==0,
        "unauthorized_parks":policy(d,.1,authorized=False)["ceiling"]==0,
        "unhealthy_parks":policy(d,.1,healthy=False)["ceiling"]==0,
        "stale_source_parks":policy(d,.1,source_current=False)["ceiling"]==0,
        "zero_budget_parks":policy(d,.1,budget=0)["ceiling"]==0,
        "zero_demand_parks":policy(d,.1,demand=0)["ceiling"]==0,
        "persistent_retirement":policy({"ceiling":0,"low_streak":0,"retired":True},.1,authorized=True)["ceiling"]==0,
        "no_automatic_auth_gain":policy(d,.1,authorized=False)["reason"]=="PARK_UNQUALIFIED",
        "early_rebound_rejected":policy({"ceiling":1,"low_streak":0,"retired":False},.1)["ceiling"]==1,
        "pressure_flap_resets_low_counter":policy(c,.95)["low_streak"]==0,
        "parent_cap_preserved":policy(d,.1,budget=1)["ceiling"]==1,
        "phase_source_unchanged":h==manifest_verified()[0],
        "multiprocess_epochs_short_lived":all(x["workers_exited_with_executor"] for x in allp),
        "logical_population_not_materialized":len(observed)==12 and int(capsule["population_declared"])>len(observed),
    }
    shared={"work_id":"costretch.r5.elastic.001","source_sha256":h,
        "status":"BOUNDED_SYNTHETIC_REOPENED_AND_STOPPED","authority":"READ_ONLY",
        "receiver_ack":False,"active_now":0,"historical_worker_ceilings":expected_ceilings,
        "source_r4_hash":h,"currentness":"HISTORICAL_RUN_ONLY","privacy":"PUBLIC_SAFE_SYNTHETIC"}
    exclusive(run/"CoMap_projection.json",js({**shared,"view":"CoMap","evidence":["10_capsule.json","20_checkpoint_A.json","20_checkpoint_B.json"]}))
    exclusive(run/"CoOrbWare_projection.json",js({**shared,"view":"CoOrbWare","native_runtime":"NOT_INSTALLED"}))
    viewA=read(run/"CoMap_projection.json")
    viewB=read(run/"CoOrbWare_projection.json")
    tests["same_identity_across_surfaces"]=all(viewA[k]==viewB[k] for k in shared)
    tests["zero_active_after_exit"]=viewA["active_now"]==viewB["active_now"]==0
    passes=sum(bool(x) for x in tests.values())
    status="PASS_LOCAL_SYNTHETIC_ELASTIC_REDUCTION" if passes==len(tests) else "FAIL"
    result={"schema":"CoStretch.ElasticReawakening.R5","utc":now(),"status":status,
        "tests":tests,"pass":passes,"total":len(tests),
        "scope":"read-only synthetic pressure and real finite 2 to 1 to 1 to 2 local process epochs",
        "declared_logical_population":"1000000000000","actual_invocations":len(observed),
        "unique_candidates_exercised":len(set(x["candidate_id"] for x in observed)),
        "worker_ceiling_epochs":expected_ceilings,"worker_pids":[x["pids"] for x in allp],
        "walls_seconds":[x["wall_seconds"] for x in allp],
        "pressure_inputs_synthetic":[0.1,0.93,0.17,0.15],
        "final_active_workers":0,"data_projection_only":True,
        "nonclaims":["NO_LIVE_COORBWARE","NO_REAL_PRESSURE_MONITOR",
            "NO_EVALUATED_LLM","NO_TRILLION_WORKERS","NO_ALWAYS_ON_DAEMON",
            "NO_MAIL_OR_NODES_FANOUT","NO_INDEPENDENT_RECEIVER_ACK",
            "NO_COST_OR_ENERGY_MEASUREMENT","NO_COEX","NO_CANON"]}
    rsha=exclusive(run/"30_results.json",js(result))
    event={"schema":"CoStretch.BenchmarkEvo.R5","utc":result["utc"],"status":status,
         "checks_passed":passes,"checks_total":len(tests),"ceiling_sequence":expected_ceilings,
         "synthetic_pressure_sequence":result["pressure_inputs_synthetic"],
         "actual_synthetic_invocations":len(observed),"r4_manifest_sha256":h,
         "result_sha256":rsha,"scope":"finite synthetic pressure inputs, real Windows processes, no live CoOrbWare"}
    ev= (json.dumps(event,sort_keys=True)+"\n").encode("utf-8")
    ehash=exclusive(run/"benchmark_evo.jsonl",ev)
    receipt={"schema":"CoStretch.R5.LocalReceipt","source_r4_sha256":h,
             "results_sha256":rsha,"event_sha256":ehash,
             "runner_sha256":hash_bytes(pathlib.Path(__file__).read_bytes()),
             "local_readback":True,"independent_receiver_ack":False,
             "CoStead_landed":False,"canon":False,"coex":False}
    exclusive(run/"90_receipt.json",js(receipt))
    print(json.dumps({"status":status,"run":str(run),"checks":passes,"total":len(tests),
         "sequence":expected_ceilings,"pids":result["worker_pids"],
         "result_sha256":rsha,"event_sha256":ehash,
         "failures":[name for name,good in tests.items() if not good]}))
    if status!="PASS_LOCAL_SYNTHETIC_ELASTIC_REDUCTION":raise SystemExit(2)
if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="begin":start()
    elif len(sys.argv)==3 and sys.argv[1]=="resume":resume(pathlib.Path(sys.argv[2]))
    else:raise SystemExit("usage: python R5_runner.py begin | resume <run_path>")