#!/usr/bin/env python3
"""CoPre+ R0 continuity guard: fail-closed sticky contract/readback and option map.

Only checks supplied, public-safe synthetic objects. No external device, runtime,
session, filesystem mutation, mirror publication, account action, or receiver ACK.
Declared failure-domain differences are NOT verified independence.
"""
import argparse
import copy
import json
from pathlib import Path

from CoPreContinuationR0 import SCHEMA, canonical, digest, compile_pack

STICKY = (
    "schema", "work_id", "sequence", "source_ref", "source_revision",
    "delta_ref", "parent_pack_sha256", "purpose", "observer", "receiver",
    "authority_ceiling", "confidentiality", "collision_domain",
    "wake_predicate", "stop_predicate", "budget", "evidence_refs",
    "next_deed", "verification", "recovery_ref", "failure_domain",
    "lineage_ref", "ownership", "lease", "delivery", "pickup",
    "integration", "effects", "outcome"
)
PACK_FIELDS = set(STICKY) | {"pack_sha256", "status", "footer"}
ROLES = {"MIRROR", "SHADOW", "CLONE", "COLD_START", "ALTERNATE_PROVIDER", "ACTUATOR"}
STATES = {"PROPOSED", "OBSERVED_CANDIDATE", "ELECTED_ACTIVE", "UNAVAILABLE"}


def truthy_string(x):
    return isinstance(x, str) and bool(x.strip())


def base_result(status, reason, pack=None, options=0, diversity=0, sticky_count=0):
    return {
        "schema": "CoCivium.CoPreInvariantGuard.R0",
        "status": status,
        "reason": reason,
        "work_id": pack.get("work_id") if isinstance(pack, dict) and pack.get("confidentiality") == "PUBLIC" else None,
        "contract_sha256": pack.get("pack_sha256") if status == "HOLD_RECEIVER_PROOF" else None,
        "sticky_field_count_verified": sticky_count,
        "option_candidates_reviewed": options,
        "distinct_declared_failure_and_trust_groups": diversity,
        "independent_failure_domains_verified": "UNPROVEN",
        "receiver_readproof": "UNPROVEN",
        "effects_performed": 0,
        "provider_sessions_touched": 0,
        "state_promotion": "NONE",
    }


def verify_pack(pack):
    if not isinstance(pack, dict) or pack.get("status") != "PACK_COMPILED_READ_ONLY":
        return "HOLD_INVALID_PACK"
    if set(pack) != PACK_FIELDS or any(k not in pack for k in STICKY):
        return "HOLD_SCHEMA_OR_FIELD_LOSS"
    if pack.get("schema") != SCHEMA or not truthy_string(pack.get("pack_sha256")):
        return "HOLD_SCHEMA_OR_FIELD_LOSS"
    if pack.get("confidentiality") != "PUBLIC" or pack.get("authority_ceiling") != "READ_ONLY":
        return "HOLD_PRIVACY_OR_AUTHORITY"
    if pack.get("effects") != 0 or pack.get("lease") != "NOT_ACQUIRED":
        return "HOLD_UNAUTHORIZED_EFFECT_OR_LEASE"
    if any(pack.get(k) != expected for k, expected in (
        ("delivery", "NOT_ATTEMPTED"), ("pickup", "UNPROVEN"),
        ("integration", "UNPROVEN"), ("outcome", "CANDIDATE_ONLY"),
        ("ownership", "WORK_ID_NOT_CHAT_SESSION"),
    )):
        return "HOLD_UNPROVEN_PROMOTION"
    if not isinstance(pack.get("sequence"), int) or isinstance(pack["sequence"], bool) or pack["sequence"] < 1:
        return "HOLD_INVALID_SEQUENCE"
    core = {k: pack[k] for k in STICKY}
    if digest(core) != pack["pack_sha256"]:
        return "HOLD_PACK_DIGEST_DRIFT"
    # The footer is a projection, not trusted proof. Never promote it.
    if not isinstance(pack.get("footer"), str):
        return "HOLD_UNTRUSTED_FOOTER"
    if not all(truthy_string(pack.get(k)) for k in (
        "work_id", "source_ref", "source_revision", "delta_ref",
        "recovery_ref", "receiver", "wake_predicate", "stop_predicate",
        "collision_domain", "failure_domain",
    )):
        return "HOLD_SCHEMA_OR_FIELD_LOSS"
    return "STRUCTURALLY_CONSISTENT_ONLY"


def evaluate(pack, worker_readback, alternatives):
    verdict = verify_pack(pack)
    if verdict != "STRUCTURALLY_CONSISTENT_ONLY":
        return base_result("HOLD", verdict, pack)
    if not isinstance(worker_readback, dict):
        return base_result("HOLD", "MISSING_WORKER_READBACK", pack)
    if not truthy_string(worker_readback.get("worker_id")):
        return base_result("HOLD", "MISSING_WORKER_ID", pack)
    if worker_readback.get("pack_sha256") != pack["pack_sha256"]:
        return base_result("HOLD", "STALE_OR_WRONG_WORKER_PACK", pack)
    observed = worker_readback.get("sticky")
    if not isinstance(observed, dict) or set(observed) != set(STICKY):
        return base_result("HOLD", "WORKER_LOST_STICKY_FIELDS", pack)
    if any(canonical(observed[k]) != canonical(pack[k]) for k in STICKY):
        return base_result("HOLD", "WORKER_STICKY_VALUE_DRIFT", pack)
    if not isinstance(alternatives, list) or len(alternatives) > 16:
        return base_result("HOLD", "INVALID_OPTIONALITY_BOUND", pack, sticky_count=len(STICKY))

    options = {}
    for item in alternatives:
        if not isinstance(item, dict) or not all(truthy_string(item.get(k)) for k in (
                "option_id", "role", "failure_domain_ref", "trust_root_ref", "state", "pack_sha256")):
            return base_result("HOLD", "INCOMPLETE_RECOVERY_OPTION", pack, sticky_count=len(STICKY))
        if item["role"] not in ROLES or item["state"] not in STATES:
            return base_result("HOLD", "INVALID_RECOVERY_OPTION_TYPE", pack, sticky_count=len(STICKY))
        if item["pack_sha256"] != pack["pack_sha256"]:
            return base_result("HOLD", "RECOVERY_OPTION_PACK_DRIFT", pack, sticky_count=len(STICKY))
        key = item["option_id"]
        if key in options and canonical(options[key]) != canonical(item):
            return base_result("HOLD", "OPTION_ID_COLLISION", pack, sticky_count=len(STICKY))
        options[key] = item

    if sum(1 for x in options.values() if x["role"] == "ACTUATOR" and x["state"] == "ELECTED_ACTIVE") > 1:
        return base_result("HOLD", "MULTIPLE_ELECTED_ACTUATORS", pack, len(options), sticky_count=len(STICKY))
    # User-entered labels are *claims*. We count groups only as options to test,
    # never as independent, restored, or currently healthy receivers.
    candidates = [x for x in options.values() if x["state"] in {"PROPOSED", "OBSERVED_CANDIDATE", "ELECTED_ACTIVE"}]
    domains = {(x["failure_domain_ref"], x["trust_root_ref"]) for x in candidates}
    return base_result(
        "HOLD_RECEIVER_PROOF", "EXACT_STICKY_MATCH_BUT_NO_INDEPENDENT_READPROOF",
        pack, len(options), len(domains), len(STICKY))


def selftest():
    original = {
        "work_id": "CoPre.synthetic", "source_ref": "fixture:source",
        "source_revision": "fixture:sha1", "delta_ref": "fixture:delta-a",
        "purpose": "prove sticky invariant preservation", "observer": "test",
        "authority_ceiling": "READ_ONLY", "confidentiality": "PUBLIC",
        "collision_domain": "test-local", "receiver": "fixture:receiver",
        "wake_predicate": "exact source change", "stop_predicate": "no delta",
        "budget": {"max_work_units": 1}, "evidence_refs": ["fixture:evidence"],
        "next_deed": "reconstruct pack", "verification": "exact typed readback",
        "recovery_ref": "fixture:recovery", "failure_domain": "fixture:host",
        "requested_effects": ["NONE"], "material_delta": True,
        "wake_is_bound": True, "source_currentness": "VERIFIED",
    }
    p = compile_pack(original)
    assert verify_pack(p) == "STRUCTURALLY_CONSISTENT_ONLY"
    view = {
        "worker_id": "synthetic:worker-A", "pack_sha256": p["pack_sha256"],
        "sticky": {k: copy.deepcopy(p[k]) for k in STICKY},
    }
    def option(key, domain, trust, role="MIRROR", state="PROPOSED"):
        return {
            "option_id": key, "role": role, "failure_domain_ref": domain,
            "trust_root_ref": trust, "state": state, "pack_sha256": p["pack_sha256"],
        }
    one = option("a", "host-1", "account-x")
    same = option("b", "host-1", "account-x", "SHADOW")
    other = option("c", "host-2", "account-y", "COLD_START")
    checks = 0
    def check(pack, worker, alt, status, reason=None):
        nonlocal checks
        v = evaluate(pack, worker, alt)
        assert v["status"] == status, (v, status)
        if reason:
            assert v["reason"] == reason, (v, reason)
        assert v["effects_performed"] == v["provider_sessions_touched"] == 0
        assert v["receiver_readproof"] == "UNPROVEN"
        assert v["independent_failure_domains_verified"] == "UNPROVEN"
        checks += 1
        return v

    check(p, view, [], "HOLD_RECEIVER_PROOF")
    matched = check(p, view, [one, same], "HOLD_RECEIVER_PROOF")
    assert matched["distinct_declared_failure_and_trust_groups"] == 1
    checks += 1
    diverse = check(p, view, [one, other], "HOLD_RECEIVER_PROOF")
    assert diverse["distinct_declared_failure_and_trust_groups"] == 2
    checks += 1
    check(p, view, [one, one], "HOLD_RECEIVER_PROOF")
    check(p, view, None, "HOLD", "INVALID_OPTIONALITY_BOUND")
    check(p, None, [one], "HOLD", "MISSING_WORKER_READBACK")
    for fld in ("source_ref", "authority_ceiling", "receiver", "recovery_ref", "work_id", "wake_predicate", "collision_domain"):
        v = copy.deepcopy(view)
        v["sticky"].pop(fld)
        check(p, v, [one], "HOLD", "WORKER_LOST_STICKY_FIELDS")
    for fld in ("source_revision", "parent_pack_sha256", "budget", "next_deed", "confidentiality", "stop_predicate"):
        v = copy.deepcopy(view)
        v["sticky"][fld] = "tampered"
        check(p, v, [one], "HOLD", "WORKER_STICKY_VALUE_DRIFT")
    bad = copy.deepcopy(p)
    bad.pop("authority_ceiling")
    check(bad, view, [one], "HOLD", "HOLD_SCHEMA_OR_FIELD_LOSS")
    bad = copy.deepcopy(p)
    bad["source_revision"] = "some newer unbound source"
    check(bad, view, [one], "HOLD", "HOLD_PACK_DIGEST_DRIFT")
    bad = copy.deepcopy(p)
    bad["pickup"] = "ACKED"
    check(bad, view, [one], "HOLD", "HOLD_UNPROVEN_PROMOTION")
    v = copy.deepcopy(view)
    v["pack_sha256"] = "stale"
    check(p, v, [one], "HOLD", "STALE_OR_WRONG_WORKER_PACK")
    bad_option = copy.deepcopy(other)
    bad_option["pack_sha256"] = "wrong"
    check(p, view, [one, bad_option], "HOLD", "RECOVERY_OPTION_PACK_DRIFT")
    collide = copy.deepcopy(one)
    collide["trust_root_ref"] = "different"
    check(p, view, [one, collide], "HOLD", "OPTION_ID_COLLISION")
    check(p, view, [option("a", "h1", "r", "ACTUATOR", "ELECTED_ACTIVE"),
                    option("b", "h2", "s", "ACTUATOR", "ELECTED_ACTIVE")],
          "HOLD", "MULTIPLE_ELECTED_ACTUATORS")
    check(p, view, [one] * 17, "HOLD", "INVALID_OPTIONALITY_BOUND")
    check(p, view, [option("a", "h1", "root", state="UNAVAILABLE")], "HOLD_RECEIVER_PROOF")
    check(p, view, [one, other], "HOLD_RECEIVER_PROOF")
    print(json.dumps({
        "schema": "CoPreInvariantGuardSyntheticR0", "cases": checks,
        "passed": checks, "scope": "SYNTHETIC_ONLY",
        "real_receiver_ack": "UNPROVEN", "independent_recovery": "UNPROVEN",
        "effects": 0}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--input")
    args = parser.parse_args()
    if args.selftest:
        selftest()
    elif args.input:
        row = json.loads(Path(args.input).read_text(encoding="utf-8"))
        print(json.dumps(evaluate(row.get("pack"), row.get("worker_readback"), row.get("alternatives")), indent=2, sort_keys=True))
    else:
        parser.error("specify --selftest or --input")
