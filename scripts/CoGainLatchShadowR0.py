#!/usr/bin/env python3
"""CoGainLatch+ R0: deterministic, no-effect gain promotion and routing planner.

All outputs are candidate assessments. No runtime or external receiver is contacted.
Use evidence from independent measurements, not synthetic PASS labels, for real promotion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENVELOPE = ("workload_id", "environment", "receiver_class", "authority_ceiling", "privacy_class", "measurement_protocol")
RAILS = [
    "SHADOW_PASS_NE_RUNTIME_PROMOTION", "GITHUB_BRANCH_NE_RECEIVER_PICKUP",
    "PROPOSAL_NE_BROADCAST", "REMOTE_ROUTE_OFFLINE_NE_DEVICE_OFF",
    "MORE_PARALLELISM_NE_MORE_VALUE", "GROWTH_RATE_NE_EXPONENTIAL_PROOF",
    "METRIC_NE_USER_VALUE", "ROLLBACK_POINTER_NE_RECOVERY_PROOF",
    "SOURCE_REF_NE_INDEPENDENT_REPLICATION", "INVERSION_CANDIDATE_NE_EXECUTION",
    "NO_PUBLICATION_OR_EXTERNAL_EFFECT", "RICK_NE_HEARTBEAT",
    "SELF_REPORTED_TIME_NE_EVALUATOR_TIME", "TYPED_METRIC_DOMAINS_REQUIRED",
]


def digest(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def instant(raw: Any) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        val = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return val.astimezone(timezone.utc) if val.tzinfo is not None else None
    except ValueError:
        return None


def numeric(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def sha256_ok(value: Any) -> bool:
    """Require a canonical lowercase SHA-256 hex digest, not 64 arbitrary chars."""
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def metric_in_domain(value: Any, domain: Any) -> bool:
    if not numeric(value) or not isinstance(domain, dict):
        return False
    if not set(domain).issubset({"min", "max"}) or not domain:
        return False
    if any(not numeric(bound) for bound in domain.values()):
        return False
    if "min" in domain and value < domain["min"]:
        return False
    if "max" in domain and value > domain["max"]:
        return False
    return True


def refs_ok(obj: Any) -> bool:
    return isinstance(obj, list) and bool(obj) and all(isinstance(x, str) and x.strip() for x in obj) and len(set(obj)) == len(obj)


def assessment(incumbent: dict, challenger: dict, policy: dict, asof: datetime) -> dict:
    cid = challenger.get("candidate_id", "UNIDENTIFIED") if isinstance(challenger, dict) else "INVALID"
    holds = []
    if not isinstance(challenger, dict):
        return {"candidate_id": cid, "state": "HOLD", "holds": ["CANDIDATE_NOT_OBJECT"]}
    if not isinstance(incumbent, dict):
        return {"candidate_id": cid, "state": "HOLD", "holds": ["INCUMBENT_NOT_OBJECT"]}
    if not isinstance(cid, str) or not cid:
        holds.append("CANDIDATE_ID_REQUIRED")
    if any(challenger.get(k) != incumbent.get(k) or challenger.get(k) is None for k in ENVELOPE):
        holds.append("DIFFERENT_COMPARABILITY_ENVELOPE__SIBLING_EVALUATION_REQUIRED")
    if challenger.get("incumbent_id") != incumbent.get("candidate_id"):
        holds.append("PREDECESSOR_ID_MISMATCH")
    if not sha256_ok(incumbent.get("config_sha256")):
        holds.append("INCUMBENT_CONFIG_DIGEST_INVALID")
    if not sha256_ok(challenger.get("predecessor_config_sha256")):
        holds.append("PREDECESSOR_DIGEST_INVALID")
    if challenger.get("predecessor_config_sha256") != incumbent.get("config_sha256"):
        holds.append("PREDECESSOR_DIGEST_MISMATCH")
    if not sha256_ok(challenger.get("config_sha256")):
        holds.append("CONFIG_DIGEST_REQUIRED")
    if challenger.get("config_sha256") == incumbent.get("config_sha256"):
        holds.append("NO_NEW_CONFIGURATION")
    if challenger.get("measurement_state") != "PASS":
        holds.append("MEASUREMENT_NOT_PASS")
    if not refs_ok(challenger.get("source_refs")):
        holds.append("SOURCE_REFS_MISSING")
    if not refs_ok(challenger.get("independent_challenge_refs")):
        holds.append("INDEPENDENT_CHALLENGE_UNBOUND")
    if not refs_ok(challenger.get("inverse_falsifier_refs")):
        holds.append("INVERSE_FALSIFIER_UNBOUND")
    if not challenger.get("rollback") or not isinstance(challenger.get("rollback"), dict):
        holds.append("ROLLBACK_PLAN_MISSING")
    else:
        rb = challenger["rollback"]
        if not sha256_ok(rb.get("config_sha256")):
            holds.append("ROLLBACK_CONFIG_DIGEST_INVALID")
        if rb.get("config_sha256") != incumbent.get("config_sha256") or not rb.get("recovery_test_ref"):
            holds.append("ROLLBACK_TARGET_OR_TEST_UNBOUND")
    observed = instant(challenger.get("observed_at"))
    if observed is None:
        holds.append("INVALID_OBSERVED_AT")
    elif (asof - observed).total_seconds() > policy["freshness_hours"] * 3600 or observed > asof:
        holds.append("STALE_OR_FUTURE_OBSERVATION")
    directions = policy["metric_directions"]
    floors = policy["hard_floors"]
    domains = policy["metric_domains"]
    cm, im = challenger.get("metrics"), incumbent.get("metrics")
    if not isinstance(cm, dict) or not isinstance(im, dict):
        holds.append("METRIC_VECTOR_MISSING")
    elif any(not numeric(cm.get(m)) or not numeric(im.get(m)) for m in directions):
        holds.append("INVALID_OR_INCOMPLETE_METRICS")
    else:
        for metric in directions:
            if not metric_in_domain(cm[metric], domains[metric]):
                holds.append("METRIC_DOMAIN_VIOLATION_CHALLENGER:" + metric)
            if not metric_in_domain(im[metric], domains[metric]):
                holds.append("METRIC_DOMAIN_VIOLATION_INCUMBENT:" + metric)
        for metric, threshold in floors.items():
            if not numeric(cm.get(metric)):
                holds.append("HARD_FLOOR_METRIC_MISSING:" + metric)
            elif directions.get(metric) == "max" and cm[metric] < threshold:
                holds.append("HARD_FLOOR_FAIL:" + metric)
            elif directions.get(metric) == "min" and cm[metric] > threshold:
                holds.append("HARD_CEILING_FAIL:" + metric)
        strict_gain = False
        for metric, direction in directions.items():
            if direction == "max":
                if cm[metric] < im[metric]:
                    holds.append("REGRESSION:" + metric)
                strict_gain |= cm[metric] > im[metric]
            elif direction == "min":
                if cm[metric] > im[metric]:
                    holds.append("REGRESSION:" + metric)
                strict_gain |= cm[metric] < im[metric]
            else:
                holds.append("INVALID_DIRECTION:" + metric)
        if not strict_gain:
            holds.append("NO_STRICT_MEASURED_GAIN")
    # A fixture, attestation or local PASS label cannot certify third-party measurements.
    evidence = challenger.get("evidence_class")
    if evidence not in ("RECEIVER_VERIFIED", "REPLAYABLE_BENCHMARK"):
        holds.append("EVIDENCE_CLASS_NOT_PROMOTABLE")
    return {
        "candidate_id": cid,
        "state": "ELIGIBLE_SHADOW_PROMOTION_PROPOSAL" if not holds else "HOLD",
        "holds": sorted(set(holds)),
        "evidence_class": evidence or "UNKNOWN",
        "measured_claim_boundary": "SOURCE_ATTESTATIONS_UNAUTHENTICATED__INDEPENDENT_RECEIVER_CHECK_REQUIRED",
        "predecessor_preserved": incumbent.get("candidate_id"),
        "config_sha256_claimed": challenger.get("config_sha256"),
        "recommended_operation": "REVIEW_THEN_BOUNDED_CANARY" if not holds else "NO_MUTATION",
    }


def run(packet: dict, evaluation_time: datetime | None = None) -> dict:
    """Wall-clock freshness comes from the host, never from packet['as_of'].

    evaluation_time is injectable only by a trusted caller (e.g. deterministic tests).
    It must not be populated from user-supplied packet data in a production caller.
    """
    if not isinstance(packet, dict) or packet.get("schema") != "CoGainLatch.ShadowInput.R0":
        raise ValueError("WRONG_INPUT_SCHEMA")
    asof = instant(packet.get("as_of"))
    if asof is None:
        raise ValueError("INVALID_AS_OF")
    clock_source = "HOST_UTC_CLOCK" if evaluation_time is None else "TRUSTED_CALLER_INJECTION"
    checked_at = datetime.now(timezone.utc) if evaluation_time is None else evaluation_time
    if not isinstance(checked_at, datetime) or checked_at.tzinfo is None or checked_at.utcoffset() is None:
        raise ValueError("UNTRUSTED_EVALUATION_CLOCK")
    checked_at = checked_at.astimezone(timezone.utc)
    policy = packet.get("policy")
    if not isinstance(policy, dict) or not numeric(policy.get("freshness_hours")) or policy["freshness_hours"] <= 0:
        raise ValueError("INVALID_POLICY")
    dirs, floors, domains = policy.get("metric_directions"), policy.get("hard_floors"), policy.get("metric_domains")
    if not isinstance(dirs, dict) or not dirs or not isinstance(floors, dict) or not isinstance(domains, dict):
        raise ValueError("INVALID_METRIC_POLICY")
    if any(x not in ("min", "max") for x in dirs.values()) or any(k not in dirs or not numeric(v) for k, v in floors.items()):
        raise ValueError("INVALID_METRIC_POLICY_DIRECTIONS")
    if set(domains) != set(dirs) or any(
        not isinstance(d, dict) or not d or not set(d).issubset({"min", "max"})
        or any(not numeric(bound) for bound in d.values())
        or ("min" in d and "max" in d and d["min"] > d["max"])
        for d in domains.values()
    ):
        raise ValueError("INVALID_METRIC_DOMAINS")
    incumbent = packet.get("incumbent", {})
    candidates = packet.get("challengers", [])
    if not isinstance(candidates, list) or len(candidates) > 100:
        raise ValueError("CHALLENGER_LIMIT")
    assessed = [assessment(incumbent, c, policy, checked_at) for c in candidates]
    unique_ids = [r["candidate_id"] for r in assessed]
    if len(unique_ids) != len(set(unique_ids)):
        raise ValueError("DUPLICATE_CANDIDATE_ID")
    eligible = [r["candidate_id"] for r in assessed if r["state"] == "ELIGIBLE_SHADOW_PROMOTION_PROPOSAL"]
    receivers = []
    for target in packet.get("receiver_candidates", []):
        if not isinstance(target, dict) or not target.get("receiver_id"):
            raise ValueError("INVALID_RECEIVER")
        online = target.get("observer_route")
        if online == "OFFLINE":
            state = "HOLD_OBSERVER_ROUTE_OFFLINE"
        elif online == "ONLINE" and target.get("currentness_verified") is True and target.get("capability_verified") is True:
            state = "CANDIDATE_ROUTE__RECEIVER_READPROOF_REQUIRED"
        else:
            state = "HOLD_RECEIVER_CURRENTNESS_OR_CAPABILITY_UNKNOWN"
        receivers.append({"receiver_id": target["receiver_id"], "state": state,
                          "eligible_candidate_ids": eligible, "pickup": "UNPROVEN", "applied": False,
                          "fanout_effect": "NONE"})
    return {
        "schema": "CoGainLatch.ShadowReport.R0", "as_of": packet["as_of"],
        "evaluated_at": checked_at.isoformat(), "evaluation_clock_source": clock_source,
        "packet_time_authority": "SELF_REPORTED__NOT_USED_FOR_FRESHNESS",
        "coverage": "BOUNDED_PACKET_ONLY__NOT_GLOBAL_FLEET",
        "input_sha256": digest(packet), "incumbent_id": incumbent.get("candidate_id"),
        "assessments": assessed, "eligible_shadow_proposals": eligible,
        "receiver_route_proposals": receivers,
        "growth_claim": "UNPROVEN__REQUIRES_MULTIWINDOW_COMPARABLE_TIME_SERIES",
        "runtime_status": "NOT_INSTALLED__NO_X2_ACTION", "effects": {
            "external_messages": 0, "device_mutations": 0, "provider_mutations": 0,
            "auto_merge": 0, "recipient_acknowledgments": 0},
        "rails": RAILS,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    report = run(json.loads(args.input.read_text(encoding="utf-8")))
    value = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.write_text(value, encoding="utf-8")
    else:
        print(value, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
