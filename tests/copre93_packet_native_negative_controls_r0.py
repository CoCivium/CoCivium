#!/usr/bin/env python3
"""CoPre9.3 packet safety negative controls. Source-only, zero delivery.

Default emits REPORT_ONLY with true contract failures but exits zero.
--strict returns exit 2 on any contract failure; a source-pin mismatch
always HOLDS with exit 3. Never interpret REPORT_ONLY exit 0 as safety.
Adapted from the prior privately preserved review-harness evidence under
CO-SESSION-RECOVERY / CoShareHub #64. Not an issuer/receiver verifier.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ORIGINAL_SOURCE_BLOB = "208e3db1ea6b25df68568bb2e3f770d3b8fe0b7a"


def source_git_blob(raw):
    return hashlib.sha1(("blob %d\0" % len(raw)).encode() + raw).hexdigest()


def load_exact(path, expected_blob):
    raw = path.read_bytes()
    found = source_git_blob(raw)
    if found != expected_blob:
        raise ValueError("HOLD_SOURCE_PIN_MISMATCH:" + found)
    spec = importlib.util.spec_from_file_location("packet_canary_target", path)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    if not callable(getattr(module, "index_bindings", None)) or not callable(getattr(module, "compile_packets", None)):
        raise ValueError("HOLD_SOURCE_SHAPE_CHANGED")
    return module, found, hashlib.sha256(raw).hexdigest()


def fixture():
    delta = {
        "delta_id": "synthetic:control", "confidentiality": "PUBLIC",
        "public_safety": "PUBLIC_SAFE", "mutation_class": "PROPOSE",
        "authority_ceiling": "CANDIDATE_ONLY",
        "subject": "fixture", "relation": "tests",
    }
    route = {
        "route_id": "fixture:route", "delta_id": delta["delta_id"],
        "receiver_repo": "CoCivium/CoCivium",
        "bound_target_head": "H1", "holds": [],
        "route_state": "CANDIDATE_ROUTE_CURRENTNESS_BOUND",
        "proposed_action": "LAND_CANDIDATE_DELTA_OR_BRANCH",
        "receiver_readproof_gate": "EXACT", "next_gate": "REVIEW",
        "evidence_refs": [],
    }
    binding = {
        "receiver_repo": "CoCivium/CoCivium",
        "receiver_id": "github:CoCivium/CoCivium",
        "current_head": "H1",
    }
    return delta, route, binding


def expected_duplicate(exc):
    return isinstance(exc, ValueError) and re.search(
        r"duplicat|collis|ambig", str(exc), re.I
    ) is not None


def run_case(name, fn, records):
    try:
        okay, observation = fn()
        records.append({"case": name, "contract_pass": bool(okay), "observed": observation})
    except Exception as exc:
        records.append({"case": name, "contract_pass": False,
                        "observed": "UNEXPECTED_" + type(exc).__name__})


def run(module):
    tests = []
    delta, route, binding = fixture()
    plan = {"route_proposals": [copy.deepcopy(route)],
            "subscription_proposals": [], "currentness_flags": []}
    payload = {"coevo_deltas": [copy.deepcopy(delta)]}
    bindings = {"repository_receivers": [copy.deepcopy(binding)], "session_receivers": []}

    def control():
        result = module.compile_packets(copy.deepcopy(plan), copy.deepcopy(payload), copy.deepcopy(bindings))
        packets = result["repository_packets"]
        effects = result["effects"]
        good = len(packets) == 1 and packets[0].get("delivery_state") == "PACKET_COMPILED__NOT_DELIVERED" and all(x == 0 for x in effects.values())
        return good, {"candidates": len(packets), "all_effects_zero": all(x == 0 for x in effects.values())}
    run_case("unique_public_control", control, tests)

    def duplicate_repo(reverse):
        b2 = dict(binding, current_head="H2", receiver_id="github:Other")
        rows = [copy.deepcopy(binding), b2]
        if reverse:
            rows.reverse()
        try:
            repo_map, _ = module.index_bindings({"repository_receivers": rows})
        except Exception as exc:
            good = expected_duplicate(exc)
            return good, {"collision_rejected": good, "exception": type(exc).__name__}
        return False, {"last_wins_binding": repo_map.get(binding["receiver_repo"], {}).get("current_head")}
    run_case("duplicate_repo_forward", lambda: duplicate_repo(False), tests)
    run_case("duplicate_repo_reverse", lambda: duplicate_repo(True), tests)

    def duplicate_session():
        s1 = {"profile_id": "Ops", "instance_id": "session:1",
              "currentness_cursor": "A", "confidentiality_capabilities": ["PUBLIC"]}
        s2 = dict(s1, currentness_cursor="B", confidentiality_capabilities=["PRIVATE"])
        try:
            _, session_map = module.index_bindings({"session_receivers": [s1, s2]})
        except Exception as exc:
            good = expected_duplicate(exc)
            return good, {"collision_rejected": good, "exception": type(exc).__name__}
        return False, {"same_instance_records_admitted": len(session_map.get("Ops", []))}
    run_case("duplicate_session_instance", duplicate_session, tests)

    def stripped_holds():
        private = dict(delta, confidentiality="PRIVATE",
                       public_safety="PRIVATE_ONLY", mutation_class="EFFECT_GATED")
        held = dict(route, route_state="HOLD_CONFIDENTIALITY_COLLISION", holds=[])
        altered = dict(plan, route_proposals=[held])
        result = module.compile_packets(altered, {"coevo_deltas": [private]}, copy.deepcopy(bindings))
        packet_count = len(result["repository_packets"])
        reasons = [reason for row in result.get("holds", [])
                   for reason in row.get("reasons", [])]
        good = packet_count == 0 and bool(reasons) and all(x == 0 for x in result["effects"].values())
        return good, {"candidate_packets": packet_count, "hold_reasons": reasons,
                      "all_effects_zero": all(x == 0 for x in result["effects"].values())}
    run_case("held_private_route_stripped_holds", stripped_holds, tests)

    return tests


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--expected-git-blob", default=ORIGINAL_SOURCE_BLOB)
    p.add_argument("--strict", action="store_true")
    a = p.parse_args(argv)
    try:
        module, blob, digest = load_exact(a.target, a.expected_git_blob)
    except (ValueError, OSError, ImportError) as exc:
        print(json.dumps({"state": "HOLD_SOURCE", "reason": str(exc)}, sort_keys=True))
        return 3
    checks = run(module)
    passed = sum(bool(x["contract_pass"]) for x in checks)
    out = {
        "schema": "CoPre93.PacketNativeNegativeControls.R0",
        "work_id": "CoPre93.PacketNativeNegativeControls.ReviewOnly.20261120.R0",
        "source_git_blob": blob,
        "source_sha256": digest,
        "mode": "STRICT" if a.strict else "REPORT_ONLY",
        "tests": checks,
        "tests_total": len(checks),
        "contracts_passed": passed,
        "contracts_failed": len(checks) - passed,
        "state": "CONTRACT_PASS_REVIEW_ONLY" if passed == len(checks) else "CONTRACT_FAIL_REVIEW_REQUIRED",
        "effects": {"deliveries": 0, "remote_actions": 0, "site_releases": 0},
        "gates": ["NO_RECEIVER_ORIGIN_ACK", "NO_3IND",
                  "NO_PUBLIC_RELEASE", "NO_RUNTIME_INSTALL"],
    }
    print(json.dumps(out, sort_keys=True, indent=2))
    return 2 if a.strict and passed != len(checks) else 0


if __name__ == "__main__":
    sys.exit(main())
