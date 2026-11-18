#!/usr/bin/env python3
"""CoEx wave endcap R0: read-only, source-bound BEGIN/END render + effect gate.

The executable validates an external landing plan; only an already-authorized
surface adapter can actually perform a mutation. Does not publish, deploy, wake
other sessions, read private systems, or certify CoEx.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

SCHEMA = "CoCivium.CoExWaveEndcaps.R0.v0.1"
PHASES = ("BEGIN", "END")
SURFACES = {
    "GITHUB_DRAFT_SOURCE",
    "PUBLIC_WEB",
    "PRIVATE_CUSTODY",
    "AUTHORIZED_DEVICE",
    "RECEIVER_APP",
    "PROVIDER_SESSION",
}
OUTCOMES = {"INTENT_RECORDED", "VERIFIED_SOURCE", "HELD", "FAILED", "INCOMPLETE"}
EFFECTS = {
    "SOURCE_WRITE", "SCRIPT_LANDING", "BRANCH_PATCH", "PUBLICATION",
    "DEPLOYMENT", "DEVICE_MUTATION", "SESSION_MUTATION", "PRIVATE_TRANSFER",
}
DANGEROUS = {"PUBLICATION", "DEPLOYMENT", "DEVICE_MUTATION", "SESSION_MUTATION", "PRIVATE_TRANSFER"}


def sha256(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def present(s):
    return isinstance(s, str) and bool(s.strip())


def check_cap(cap, phase, render):
    if not isinstance(cap, dict) or cap.get("phase") != phase:
        return "HOLD_BAD_PHASE"
    required = (
        "work_id", "wave_id", "source_ref", "source_revision",
        "render_kind", "render_sha256", "effect_intent", "surface",
        "target_ref", "authority_scope", "confidentiality",
        "receipt_ref", "status", "next_wake",
    )
    if any(not present(cap.get(k)) for k in required):
        return "HOLD_MISSING_ENDCAP_BINDING"
    if cap["render_kind"] != "MARKDOWN_SOURCE_RENDER":
        return "HOLD_UNSUPPORTED_RENDER_PROOF"
    if not isinstance(render, str) or cap["render_sha256"] != sha256(render):
        return "HOLD_RENDER_MISMATCH"
    if cap["surface"] not in SURFACES or cap["effect_intent"] not in EFFECTS:
        return "HOLD_BAD_TARGET_OR_EFFECT"
    if cap["confidentiality"] != "PUBLIC":
        return "HOLD_PRIVATE_BOUNDARY"
    if cap["status"] not in OUTCOMES:
        return "HOLD_INVALID_RESULT"
    if phase == "BEGIN" and cap["status"] != "INTENT_RECORDED":
        return "HOLD_BEGIN_IS_NOT_RESULT"
    if phase == "END" and cap["status"] == "INTENT_RECORDED":
        return "HOLD_END_IS_NOT_RESULT"
    if cap.get("coex_claim") is True and not (
        cap.get("receiver_readproof") == "VERIFIED"
        and present(cap.get("receiver_receipt_ref"))
        and present(cap.get("receiver_identity"))
    ):
        return "HOLD_FALSE_COEX"
    if cap.get("landing_status") == "LANDED" and not (
        present(cap.get("landed_blob_sha"))
        and present(cap.get("landing_readback_ref"))
    ):
        return "HOLD_FALSE_LANDING"
    return "SOURCE_BOUND_CAP"


def review(begin, end, begin_render, end_render):
    a = check_cap(begin, "BEGIN", begin_render)
    if a != "SOURCE_BOUND_CAP":
        return {"status": "HOLD", "reason": a, "effects_performed": 0}
    b = check_cap(end, "END", end_render)
    if b != "SOURCE_BOUND_CAP":
        return {"status": "HOLD", "reason": b, "effects_performed": 0}
    if any(begin.get(k) != end.get(k) for k in ("work_id", "wave_id", "confidentiality")):
        return {"status": "HOLD", "reason": "MISMATCHED_WAVE_IDENTITY", "effects_performed": 0}
    if end.get("begin_render_sha256") != begin["render_sha256"]:
        return {"status": "HOLD", "reason": "BROKEN_BEGIN_END_CHAIN", "effects_performed": 0}
    if begin.get("landing_status") == "LANDED" and begin.get("landed_blob_sha") == end.get("landed_blob_sha"):
        return {"status": "HOLD", "reason": "BEGIN_END_NOT_SEPARATE_LANDINGS", "effects_performed": 0}
    targets = [begin, end]
    if any(c["effect_intent"] in DANGEROUS or c["surface"] != "GITHUB_DRAFT_SOURCE" for c in targets):
        return {"status": "HOLD_EFFECT_GATE", "reason": "SURFACE_REQUIRES_SEPARATE_ADAPTER_AUTHORITY", "effects_performed": 0}
    if any(c.get("authority_scope") != "PUBLIC_DRAFT_BRANCH_ONLY" for c in targets):
        return {"status": "HOLD_EFFECT_GATE", "reason": "NO_DRAFT_WRITE_SCOPE", "effects_performed": 0}
    # This is an external-writer *plan*. CI has no write token and takes no action.
    return {
        "schema": SCHEMA, "status": "REVIEW_SOURCE_LANDING_ONLY",
        "begin_sha256": begin["render_sha256"],
        "end_sha256": end["render_sha256"],
        "separate_landing_records": 2,
        "requested_effects": [c["effect_intent"] for c in targets],
        "effects_performed": 0,
        "external_writer_required": True,
        "receiver_readproof": "UNPROVEN",
        "coex": "NOT_CERTIFIED",
    }


def selftest():
    render_a = "# BEGIN\nSource-bound plan; no result.\n"
    render_b = "# END\nMeasured results, including held work.\n"
    def cap(phase, content):
        return {
            "phase": phase, "work_id": "fixture:work", "wave_id": "fixture:wave",
            "source_ref": "fixture:source", "source_revision": "fixture:sha",
            "render_kind": "MARKDOWN_SOURCE_RENDER", "render_sha256": sha256(content),
            "effect_intent": "SOURCE_WRITE", "surface": "GITHUB_DRAFT_SOURCE",
            "target_ref": "fixture:branch", "authority_scope": "PUBLIC_DRAFT_BRANCH_ONLY",
            "confidentiality": "PUBLIC", "receipt_ref": "fixture:receipt",
            "status": "INTENT_RECORDED" if phase == "BEGIN" else "HELD",
            "next_wake": "fixture:source_changes", "coex_claim": False,
            "landing_status": "PROPOSED",
        }
    a, b = cap("BEGIN",render_a), cap("END",render_b)
    b["begin_render_sha256"] = a["render_sha256"]
    cases = 0
    def check(aa, bb, ra, rb, status, reason=None):
        nonlocal cases
        ans = review(aa, bb, ra, rb)
        assert ans["status"] == status, (ans,status)
        if reason: assert ans["reason"] == reason, (ans,reason)
        assert ans["effects_performed"] == 0
        cases += 1
        return ans
    check(a,b,render_a,render_b,"REVIEW_SOURCE_LANDING_ONLY")
    check(a,b,render_a,render_b + "tampered","HOLD","HOLD_RENDER_MISMATCH")
    w=copy.deepcopy(a);w["status"]="VERIFIED_SOURCE"
    check(w,b,render_a,render_b,"HOLD","HOLD_BEGIN_IS_NOT_RESULT")
    w=copy.deepcopy(b);w["status"]="INTENT_RECORDED"
    check(a,w,render_a,render_b,"HOLD","HOLD_END_IS_NOT_RESULT")
    w=copy.deepcopy(b);w["begin_render_sha256"]="wrong"
    check(a,w,render_a,render_b,"HOLD","BROKEN_BEGIN_END_CHAIN")
    w=copy.deepcopy(b);w["work_id"]="new"
    check(a,w,render_a,render_b,"HOLD","MISMATCHED_WAVE_IDENTITY")
    w=copy.deepcopy(b);w["effect_intent"]="DEPLOYMENT"
    check(a,w,render_a,render_b,"HOLD_EFFECT_GATE")
    w=copy.deepcopy(b);w["surface"]="PROVIDER_SESSION"
    check(a,w,render_a,render_b,"HOLD_EFFECT_GATE")
    w=copy.deepcopy(b);w["authority_scope"]="EVERYWHERE"
    check(a,w,render_a,render_b,"HOLD_EFFECT_GATE")
    w=copy.deepcopy(b);w["coex_claim"]=True
    check(a,w,render_a,render_b,"HOLD","HOLD_FALSE_COEX")
    w=copy.deepcopy(b);w["landing_status"]="LANDED"
    check(a,w,render_a,render_b,"HOLD","HOLD_FALSE_LANDING")
    w=copy.deepcopy(b);w["confidentiality"]="PRIVATE"
    check(a,w,render_a,render_b,"HOLD","HOLD_PRIVATE_BOUNDARY")
    w=copy.deepcopy(b);w.pop("target_ref")
    check(a,w,render_a,render_b,"HOLD","HOLD_MISSING_ENDCAP_BINDING")
    print(json.dumps({"schema": SCHEMA,"synthetic_cases":cases,"passed":cases,
       "effects_performed":0,"coex":"NOT_CERTIFIED",
       "scope":"SYNTHETIC_ONLY"},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--manifest")
    p.add_argument("--repo-root",default=".")
    args=p.parse_args()
    if args.selftest:
        selftest()
    elif args.manifest:
        root=Path(args.repo_root).resolve()
        file=(root/args.manifest).resolve()
        assert file.is_relative_to(root)
        m=json.loads(file.read_text(encoding="utf-8"))
        assert m["schema"]==SCHEMA
        def read(rel):
            path=(root/rel).resolve()
            assert path.is_relative_to(root)
            return path.read_text(encoding="utf-8")
        result=review(m["begin"],m["end"],read(m["begin_render_path"]),read(m["end_render_path"]))
        print(json.dumps(result,sort_keys=True,indent=2))
        if result["status"]!="REVIEW_SOURCE_LANDING_ONLY":
            raise SystemExit(2)
    else:
        p.error("use --selftest or --manifest PATH")


if __name__=="__main__":
    main()
