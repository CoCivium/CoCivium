#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

HARD_ROUTE_HOLDS = {
    "CONFIDENTIALITY_COLLISION",
    "PUBLIC_SAFETY_HOLD",
    "RECEIVER_VISIBILITY_UNKNOWN",
    "CONFIDENTIALITY_REVIEW_REQUIRED",
}
NONCLAIMS = [
    "PACKET_NE_DELIVERY",
    "DELIVERY_NE_PICKUP",
    "PACKET_NE_TARGET_MUTATION",
    "PACKET_NE_PROVIDER_PUSH",
    "PACKET_NE_AUTHORITY_TRANSFER",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "MERGED_NE_CANON",
]

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha(data):
    return hashlib.sha256(data).hexdigest().upper()

def load(path):
    raw = Path(path).read_bytes()
    return json.loads(raw.decode("utf-8")), {"sha256": sha(raw), "bytes": len(raw)}

def delta_map(payload):
    if isinstance(payload, dict) and isinstance(payload.get("coevo_deltas"), list):
        rows = payload["coevo_deltas"]
    elif isinstance(payload, dict) and isinstance(payload.get("deltas"), list):
        rows = payload["deltas"]
    elif isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = [payload]
    else:
        raise ValueError("CoEvo input must be object/array/wrapper")
    out = {}
    for d in rows:
        if not isinstance(d, dict) or not d.get("delta_id"):
            continue
        if d["delta_id"] in out:
            raise ValueError("duplicate CoEvo delta_id: " + str(d["delta_id"]))
        out[d["delta_id"]] = d
    return out

def index_bindings(bindings):
    repo = {}
    for b in bindings.get("repository_receivers", []) or []:
        if not isinstance(b, dict) or not b.get("receiver_repo"):
            continue
        repo[b["receiver_repo"]] = b
    sessions = {}
    for b in bindings.get("session_receivers", []) or []:
        if not isinstance(b, dict) or not b.get("profile_id") or not b.get("instance_id"):
            continue
        sessions.setdefault(b["profile_id"], []).append(b)
    for p in sessions:
        sessions[p] = sorted(sessions[p], key=lambda x: x["instance_id"])
    return repo, sessions

def packetize(core):
    digest = sha(canonical(core).encode("utf-8"))
    out = dict(core)
    out["packet_id"] = "packet:" + digest[:24]
    out["packet_sha256"] = digest
    return out

def compile_packets(plan, coevo_payload, bindings):
    deltas = delta_map(coevo_payload)
    repo_bindings, session_bindings = index_bindings(bindings)
    source_bad = {x.get("delta_id") for x in (plan.get("currentness_flags") or []) if x.get("delta_id")}
    repo_packets, session_packets, holds = [], [], []

    for route in sorted(plan.get("route_proposals") or [], key=lambda x: (str(x.get("receiver_repo")), str(x.get("delta_id")), str(x.get("route_id")))):
        did, receiver, rid = route.get("delta_id"), route.get("receiver_repo"), route.get("route_id")
        delta = deltas.get(did)
        binding = repo_bindings.get(receiver)
        reasons = []
        if delta is None:
            reasons.append("SOURCE_DELTA_MISSING")
        if did in source_bad:
            reasons.append("SOURCE_CURRENTNESS_FAILURE")
        hard = sorted(set(route.get("holds") or []).intersection(HARD_ROUTE_HOLDS))
        reasons.extend(hard)
        if binding is None:
            reasons.append("REPOSITORY_RECEIVER_UNBOUND")
        else:
            if not binding.get("receiver_id"):
                reasons.append("REPOSITORY_RECEIVER_ID_UNBOUND")
            if not binding.get("current_head"):
                reasons.append("TARGET_CURRENT_HEAD_UNBOUND")
            planned = route.get("bound_target_head")
            actual = binding.get("current_head")
            if planned and actual and planned != actual:
                reasons.append("TARGET_HEAD_MOVED_SINCE_PLAN")
        if reasons:
            holds.append({"packet_class":"REPOSITORY","delta_id":did,"route_id":rid,"receiver":receiver,"reasons":sorted(set(reasons))})
            continue
        downstream = [h for h in route.get("holds") or [] if h not in HARD_ROUTE_HOLDS]
        core = {
            "packet_class":"REPOSITORY_CANDIDATE",
            "delta_id":did,
            "receiver_id":binding["receiver_id"],
            "receiver_repo":receiver,
            "expected_target_head":binding["current_head"],
            "route_id":rid,
            "route_state":route.get("route_state"),
            "proposed_action":route.get("proposed_action"),
            "downstream_gates":sorted(set(downstream)),
            "receiver_readproof_gate":route.get("receiver_readproof_gate"),
            "next_gate":route.get("next_gate"),
            "coevo_delta":delta,
            "evidence_refs":sorted(set(route.get("evidence_refs") or [])),
            "delivery_state":"PACKET_COMPILED__NOT_DELIVERED",
            "effects":{"target_mutation":0,"branch_creation":0,"pull_request_creation":0,"publication":0,"receiver_pickup_claim":0},
            "nonclaims":NONCLAIMS,
        }
        repo_packets.append(packetize(core))

    for sub in sorted(plan.get("subscription_proposals") or [], key=lambda x: (str(x.get("profile_id")), str(x.get("delta_id")), str(x.get("subscription_id")))):
        did, profile, sid = sub.get("delta_id"), sub.get("profile_id"), sub.get("subscription_id")
        delta = deltas.get(did)
        candidates = session_bindings.get(profile, [])
        if not candidates:
            holds.append({"packet_class":"SESSION","delta_id":did,"subscription_id":sid,"receiver":profile,"reasons":["SESSION_INSTANCE_UNBOUND"]})
            continue
        for binding in candidates:
            reasons = []
            if delta is None:
                reasons.append("SOURCE_DELTA_MISSING")
            if did in source_bad:
                reasons.append("SOURCE_CURRENTNESS_FAILURE")
            if not binding.get("currentness_cursor"):
                reasons.append("CURRENTNESS_CURSOR_UNBOUND")
            confidentiality = str(sub.get("confidentiality") or (delta or {}).get("confidentiality") or "UNKNOWN")
            capabilities = set(binding.get("confidentiality_capabilities") or [])
            if confidentiality not in capabilities:
                reasons.append("CONFIDENTIALITY_CAPABILITY_MISSING")
            if reasons:
                holds.append({"packet_class":"SESSION","delta_id":did,"subscription_id":sid,"receiver":binding.get("instance_id"),"reasons":sorted(set(reasons))})
                continue
            core = {
                "packet_class":"SESSION_CURRENTNESS_CANDIDATE",
                "delta_id":did,
                "receiver_instance_id":binding["instance_id"],
                "profile_id":profile,
                "currentness_cursor":binding["currentness_cursor"],
                "subscription_id":sid,
                "temperature":sub.get("temperature"),
                "delivery_class":sub.get("delivery_class"),
                "matched_domains":sub.get("matched_domains") or [],
                "coevo_delta":delta,
                "delivery_state":"PACKET_COMPILED__NOT_DELIVERED",
                "effects":{"provider_session_push":0,"session_mutation":0,"authority_transfer":0,"receiver_pickup_claim":0},
                "nonclaims":NONCLAIMS + ["PROFILE_NE_SESSION_INSTANCE","SUBSCRIPTION_NE_AUTHORITY"],
            }
            session_packets.append(packetize(core))

    repo_packets.sort(key=lambda x: x["packet_id"])
    session_packets.sort(key=lambda x: x["packet_id"])
    holds.sort(key=lambda x: (x["packet_class"], str(x.get("delta_id")), str(x.get("route_id") or x.get("subscription_id")), str(x.get("receiver"))))
    result = {
        "compiler":"CoEvoReceiverPacketCompiler.R0",
        "coverage":{
            "repository_route_proposals":len(plan.get("route_proposals") or []),
            "session_subscription_proposals":len(plan.get("subscription_proposals") or []),
            "repository_bindings":len(repo_bindings),
            "session_instance_bindings":sum(len(v) for v in session_bindings.values()),
            "repository_packets":len(repo_packets),
            "session_packets":len(session_packets),
            "holds":len(holds),
        },
        "repository_packets":repo_packets,
        "session_packets":session_packets,
        "holds":holds,
        "effects":{
            "deliveries_executed":0,
            "target_mutations":0,
            "branches_created":0,
            "pull_requests_created":0,
            "provider_session_pushes":0,
            "receiver_pickup_claims":0,
            "canon_changes":0,
        },
        "next":"DELIVER_ONLY_THROUGH_PROVEN_RECEIVER_ADAPTER_THEN_REQUIRE_EXACT_PACKET_READPROOF",
        "nonclaims":NONCLAIMS,
    }
    result["bundle_sha256"] = sha(canonical(result).encode("utf-8"))
    return result

def selftest():
    coevo={"coevo_deltas":[
        {"delta_id":"a","session_id":"A","observed_at":"2026-09-23T11:50:00Z","domain":["CoLex+"],"subject":"x","relation":"links","epistemic_class":"INFERRED","source_refs":[],"target_surfaces":[],"mutation_class":"PROPOSE","authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PUBLIC","public_safety":"PUBLIC_SAFE","next_receiver":"fan"},
        {"delta_id":"b","session_id":"B","observed_at":"2026-09-23T11:51:00Z","domain":["CoOps+"],"subject":"y","relation":"links","epistemic_class":"PLANNED","source_refs":[],"target_surfaces":[],"mutation_class":"PROPOSE","authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PRIVATE","public_safety":"PRIVATE_ONLY","next_receiver":"fan"}
    ]}
    plan={
        "route_proposals":[
            {"route_id":"route:a","delta_id":"a","receiver_repo":"CoCivium/CoCivium","holds":[],"bound_target_head":None,"route_state":"CANDIDATE_ROUTE_REQUIRES_TARGET_CURRENTNESS","proposed_action":"LAND_CANDIDATE_DELTA_OR_BRANCH","receiver_readproof_gate":"EXACT","next_gate":"REVIEW","evidence_refs":[]},
            {"route_id":"route:b","delta_id":"b","receiver_repo":"CoCivium/CoToolbelt","holds":[],"bound_target_head":"H2","route_state":"CANDIDATE_ROUTE_CURRENTNESS_BOUND","proposed_action":"LAND_CANDIDATE_DELTA_OR_BRANCH","receiver_readproof_gate":"EXACT","next_gate":"REVIEW","evidence_refs":[]},
            {"route_id":"route:b-public","delta_id":"b","receiver_repo":"CoCivium/CoStacks","holds":["CONFIDENTIALITY_COLLISION","PUBLIC_SAFETY_HOLD"],"bound_target_head":None,"route_state":"HOLD_CONFIDENTIALITY_COLLISION","proposed_action":"LAND_CANDIDATE_DELTA_OR_BRANCH","receiver_readproof_gate":"EXACT","next_gate":"REVIEW","evidence_refs":[]}
        ],
        "subscription_proposals":[
            {"subscription_id":"sub:a","delta_id":"a","profile_id":"CoLanguage","temperature":"HOT","delivery_class":"CURRENT_DELTA_PACKET","matched_domains":["CoLex+"],"confidentiality":"PUBLIC"},
            {"subscription_id":"sub:b","delta_id":"b","profile_id":"CoOps","temperature":"HOT","delivery_class":"CURRENT_DELTA_PACKET","matched_domains":["CoOps+"],"confidentiality":"PRIVATE"}
        ],
        "currentness_flags":[]
    }
    bindings={
        "repository_receivers":[
            {"receiver_repo":"CoCivium/CoCivium","receiver_id":"github:CoCivium/CoCivium","current_head":"H1"},
            {"receiver_repo":"CoCivium/CoToolbelt","receiver_id":"github:CoCivium/CoToolbelt","current_head":"H2"},
            {"receiver_repo":"CoCivium/CoStacks","receiver_id":"github:CoCivium/CoStacks","current_head":"H3"}
        ],
        "session_receivers":[
            {"profile_id":"CoLanguage","instance_id":"session:lang-1","currentness_cursor":"cursor:1","confidentiality_capabilities":["PUBLIC"]},
            {"profile_id":"CoOps","instance_id":"session:ops-1","currentness_cursor":"cursor:2","confidentiality_capabilities":["PUBLIC","PRIVATE"]}
        ]
    }
    out=compile_packets(plan,coevo,bindings)
    assert out["coverage"]["repository_packets"]==2
    assert out["coverage"]["session_packets"]==2
    assert out["coverage"]["holds"]==1
    assert all(v==0 for v in out["effects"].values())
    assert all(p["delivery_state"]=="PACKET_COMPILED__NOT_DELIVERED" for p in out["repository_packets"]+out["session_packets"])
    print("SELFTEST=PASS_REPO_PACKETS_2__SESSION_PACKETS_2__HOLDS_1__ZERO_DELIVERY_EFFECTS")
    print("BUNDLE_SHA256="+out["bundle_sha256"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--plan")
    p.add_argument("--coevo")
    p.add_argument("--bindings")
    p.add_argument("--output")
    a=p.parse_args()
    if a.selftest:
        return selftest()
    if not all([a.plan,a.coevo,a.bindings,a.output]):
        raise SystemExit("FAIL_CLOSED__PLAN_COEVO_BINDINGS_OUTPUT_REQUIRED")
    plan,pm=load(a.plan); coevo,cm=load(a.coevo); bindings,bm=load(a.bindings)
    out=compile_packets(plan,coevo,bindings)
    out["inputs"]={"plan":pm,"coevo":cm,"bindings":bm}
    out["bundle_sha256"]=sha(canonical({k:v for k,v in out.items() if k!="bundle_sha256"}).encode("utf-8"))
    target=Path(a.output)
    if target.exists():
        raise SystemExit("FAIL_CLOSED__NO_CLOBBER="+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    c=out["coverage"]
    print("STATE=PASS_COEVO_RECEIVER_PACKETS_COMPILED__NOT_DELIVERED")
    print("OUTPUT="+str(target))
    print("BUNDLE_SHA256="+out["bundle_sha256"])
    print("REPOSITORY_PACKETS="+str(c["repository_packets"]))
    print("SESSION_PACKETS="+str(c["session_packets"]))
    print("HOLDS="+str(c["holds"]))
    print("DELIVERIES_EXECUTED=0")

if __name__=="__main__":
    main()
