#!/usr/bin/env python3
"""CoPre+ R0 read-only NEXT -> CoPrePack compiler. No effect execution.

Source-bound, deterministic, versioned, no provider session wake or receipt claim.
"""
import argparse
import hashlib
import json
from pathlib import Path

SCHEMA="CoCivium.CoPreContinuation.R0"
FORBIDDEN={"RUNTIME","PUBLIC_OUTREACH","CREDENTIAL","FINANCIAL","DELETE","CANON","AUTHORITY_CHANGE","PRIVACY_BOUNDARY"}
NEEDED=("work_id","source_ref","source_revision","purpose","delta_ref","observer",
        "authority_ceiling","confidentiality","collision_domain","receiver",
        "wake_predicate","stop_predicate","budget","evidence_refs","next_deed",
        "verification","recovery_ref","failure_domain")


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def text(value):
    return isinstance(value,str) and bool(value.strip())


def compile_pack(observation, previous=None):
    if not isinstance(observation,dict):
        return {"status":"HOLD","reason":"INVALID_INPUT","effects":0}
    missing=[k for k in NEEDED if k not in observation or observation[k] in (None,"",[],{})]
    if missing:
        return {"status":"HOLD","reason":"MISSING_REQUIRED_FIELDS","missing":sorted(missing),"effects":0}
    if not all(text(observation[k]) for k in (
       "work_id","source_ref","source_revision","purpose","delta_ref","observer",
       "authority_ceiling","confidentiality","collision_domain","receiver",
       "wake_predicate","stop_predicate","next_deed","verification","recovery_ref","failure_domain")):
        return {"status":"HOLD","reason":"INVALID_TYPE","effects":0}
    if not isinstance(observation["evidence_refs"],list) or not all(text(x) for x in observation["evidence_refs"]):
        return {"status":"HOLD","reason":"INVALID_EVIDENCE","effects":0}
    if not isinstance(observation["budget"],dict) or not isinstance(observation["budget"].get("max_work_units"),int) or not 1<=observation["budget"]["max_work_units"]<=8:
        return {"status":"HOLD","reason":"INVALID_BUDGET","effects":0}
    if observation["confidentiality"]!="PUBLIC" or observation["authority_ceiling"]!="READ_ONLY":
        return {"status":"HOLD","reason":"PRIVACY_OR_AUTHORITY_BOUNDARY","effects":0}
    if set(observation.get("requested_effects",[]))&FORBIDDEN or observation.get("requested_effects",[]) not in ([],["NONE"]):
        return {"status":"HOLD","reason":"EFFECT_REQUIRES_SEPARATE_GATE","effects":0}
    if not observation.get("material_delta",False):
        return {"status":"QUIESCENT","reason":"NO_MATERIAL_DELTA","effects":0,"work_id":observation["work_id"]}
    if previous is not None:
        if previous.get("work_id")!=observation["work_id"]:
            return {"status":"HOLD","reason":"WORK_ID_CHANGED","effects":0}
        if previous.get("source_revision")==observation["source_revision"] and previous.get("delta_ref")==observation["delta_ref"]:
            return {"status":"QUIESCENT","reason":"IDENTICAL_DELTA_ALREADY_BOUND","effects":0,"work_id":observation["work_id"]}
        if previous.get("pack_sha256") != observation.get("expected_previous_pack_sha256"):
            return {"status":"HOLD","reason":"STALE_PREDECESSOR_OR_COLLISION","effects":0}
    if observation.get("wake_is_bound") is not True:
        return {"status":"HOLD","reason":"WAKE_IS_GENERIC_OR_UNBOUND","effects":0}
    if observation.get("source_currentness")!="VERIFIED":
        return {"status":"HOLD","reason":"SOURCE_CURRENTNESS_UNVERIFIED","effects":0}
    sequence=(previous or {}).get("sequence",0)+1
    core={
      "schema":SCHEMA,"work_id":observation["work_id"],"sequence":sequence,
      "source_ref":observation["source_ref"],"source_revision":observation["source_revision"],
      "delta_ref":observation["delta_ref"],"parent_pack_sha256":(previous or {}).get("pack_sha256"),
      "purpose":observation["purpose"],"observer":observation["observer"],
      "receiver":observation["receiver"],"authority_ceiling":"READ_ONLY",
      "confidentiality":"PUBLIC","collision_domain":observation["collision_domain"],
      "wake_predicate":observation["wake_predicate"],"stop_predicate":observation["stop_predicate"],
      "budget":observation["budget"],"evidence_refs":observation["evidence_refs"],
      "next_deed":observation["next_deed"],"verification":observation["verification"],
      "recovery_ref":observation["recovery_ref"],"failure_domain":observation["failure_domain"],
      "lineage_ref":"docs/cluster/CoPre_Seed_002.json",
      "ownership":"WORK_ID_NOT_CHAT_SESSION","lease":"NOT_ACQUIRED",
      "delivery":"NOT_ATTEMPTED","pickup":"UNPROVEN","integration":"UNPROVEN",
      "effects":0,"outcome":"CANDIDATE_ONLY"}
    ident=digest(core)
    core["pack_sha256"]=ident
    core["status"]="PACK_COMPILED_READ_ONLY"
    core["footer"]="CoPre+"+" | "+observation["work_id"]+" #"+str(sequence)+" | "+observation["next_deed"]+" | Trigger: "+observation["wake_predicate"]+" | Test: "+observation["verification"]+" | CoPrePack sha256:"+ident[:16]+" | HELD from execution"
    return core


def render_continuation_input(packet):
    """Explicit user-turn projection; not a provider composer mutation."""
    if not isinstance(packet, dict) or packet.get("status") != "PACK_COMPILED_READ_ONLY":
        return None
    parts = [
        "CoPre+ | CONTINUATION REQUEST | NOT AN AUTHORITY GRANT",
        "WorkID: " + packet["work_id"] + " | Wave: " + str(packet["sequence"]),
        "Purpose: " + packet["purpose"],
        "Source: " + packet["source_ref"] + " @ " + packet["source_revision"],
        "Delta: " + packet["delta_ref"],
        "CoPrePack SHA-256: " + packet["pack_sha256"],
        "Parent: " + str(packet["parent_pack_sha256"]),
        "Evidence: " + "; ".join(packet["evidence_refs"]),
        "Receiver: " + packet["receiver"] + " | Observer: " + packet["observer"],
        "Authority: READ_ONLY | Effects: NONE | Confidentiality: PUBLIC",
        "Collision: " + packet["collision_domain"] + " | Failure domain: " + packet["failure_domain"],
        "Bound: " + str(packet["budget"]["max_work_units"]) + " work units",
        "NEXT: " + packet["next_deed"],
        "Verify/falsify: " + packet["verification"],
        "Wake only on: " + packet["wake_predicate"],
        "Stop on: " + packet["stop_predicate"],
        "Recovery: " + packet["recovery_ref"],
        "FIRST: Verify exact source and pack identity. Reconcile latest WorkID state,",
        "challenge with inverse/in-between and external alternatives, then elect one",
        "bounded reversible deed. No ACK, deployment, canon, session access or",
        "additional permissions follow from this message. On no delta: QUIESCENT.",
    ]
    return "\n".join(parts)


def selftest():
    base={
      "work_id":"CoPre.test","source_ref":"github:example@blob",
      "source_revision":"sha:one","purpose":"find missing receiver edge",
      "delta_ref":"delta:one","observer":"synthetic-test","authority_ceiling":"READ_ONLY",
      "confidentiality":"PUBLIC","collision_domain":"test-only","receiver":"synthetic-review",
      "wake_predicate":"exact source delta updated","stop_predicate":"no independent evidence",
      "budget":{"max_work_units":1},"evidence_refs":["fixture:one"],
      "next_deed":"inspect first missing receipt","verification":"exact byte readback",
      "recovery_ref":"fixture:replay","failure_domain":"synthetic-host",
      "requested_effects":["NONE"],"material_delta":True,"wake_is_bound":True,"source_currentness":"VERIFIED"
    }
    import copy
    checks=0
    first=compile_pack(base)
    assert first["status"]=="PACK_COMPILED_READ_ONLY" and first["sequence"]==1
    assert digest({k:v for k,v in first.items() if k not in ("pack_sha256","status","footer")})==first["pack_sha256"]
    checks+=2
    assert compile_pack(base)==first;checks+=1
    user_turn=render_continuation_input(first)
    assert "CoPrePack SHA-256: " + first["pack_sha256"] in user_turn
    assert "NEXT: " + base["next_deed"] in user_turn
    assert "Verify/falsify: " + base["verification"] in user_turn
    assert "Authority: READ_ONLY | Effects: NONE" in user_turn
    assert render_continuation_input({"status":"HOLD"}) is None
    checks+=5
    for changes,reason in [
       ({"material_delta":False},"QUIESCENT"),
       ({"wake_is_bound":False},"HOLD"),
       ({"source_currentness":"UNKNOWN"},"HOLD"),
       ({"confidentiality":"PRIVATE"},"HOLD"),
       ({"authority_ceiling":"WRITE"},"HOLD"),
       ({"requested_effects":["PUBLIC_OUTREACH"]},"HOLD"),
       ({"budget":{"max_work_units":900}},"HOLD"),
       ({"receiver":""},"HOLD"),
       ({"evidence_refs":[""]},"HOLD"),
    ]:
       o=copy.deepcopy(base);o.update(changes)
       assert compile_pack(o)["status"]==reason, changes
       checks+=1
    assert compile_pack(base,first)["status"]=="QUIESCENT";checks+=1
    nexto=copy.deepcopy(base);nexto.update({"source_revision":"sha:two","delta_ref":"delta:two","next_deed":"challenge alternative"})
    assert compile_pack(nexto,first)["reason"]=="STALE_PREDECESSOR_OR_COLLISION";checks+=1
    nexto["expected_previous_pack_sha256"]=first["pack_sha256"]
    second=compile_pack(nexto,first)
    assert second["sequence"]==2 and second["pack_sha256"]!=first["pack_sha256"] and second["parent_pack_sha256"]==first["pack_sha256"];checks+=1
    nexto["work_id"]="CoPre.different"
    assert compile_pack(nexto,first)["reason"]=="WORK_ID_CHANGED";checks+=1
    print(json.dumps({"schema":"CoPreR0Selftest","passed":checks,"scope":"SYNTHETIC_ONLY","effects":0,"session_wakes":0},sort_keys=True))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--selftest",action="store_true")
    parser.add_argument("--input")
    parser.add_argument("--emit-prompt",action="store_true",help="Render explicit user-turn text; cannot edit any provider input field")
    args=parser.parse_args()
    if args.selftest:
        selftest()
    elif args.input:
        result=compile_pack(json.loads(Path(args.input).read_text(encoding="utf-8")))
        if args.emit_prompt and result.get("status")=="PACK_COMPILED_READ_ONLY":
            print(render_continuation_input(result))
        else:
            print(json.dumps(result,indent=2,sort_keys=True))
    else:
        parser.error("Specify --selftest or --input")
