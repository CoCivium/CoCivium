#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

LOW_AUTH = {"OBSERVE_ONLY", "OBSERVE_AND_PROPOSE_ONLY"}

def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def review_fixture(pack: dict) -> dict:
    encounters = pack.get("encounters")
    if not isinstance(encounters, list) or len(encounters) != 3:
        raise ValueError("EXPECTED_THREE_ENCOUNTERS")

    ids = set()
    evidence_count = 0
    null_count = 0
    benefit_count = 0
    open_relations = []
    unauthorized_wake_routes = 0

    for encounter in encounters:
        eid = encounter["encounter_id"]
        if eid in ids:
            raise ValueError("DUPLICATE_ENCOUNTER_ID")
        ids.add(eid)

        if encounter.get("authority_ceiling") not in LOW_AUTH:
            raise ValueError("AUTHORITY_INFLATION:" + eid)

        yields = encounter.get("yields") or []
        if not yields:
            raise ValueError("NO_YIELD:" + eid)
        evidence_count += len(yields)

        if encounter.get("encounter_mode") == "EVIDENCED_NULL":
            null_count += 1
            if encounter.get("contribution_delta_refs"):
                raise ValueError("NULL_WITH_CONTRIBUTION:" + eid)
            if not any(y.get("yield_type") == "EVIDENCED_NULL" for y in yields):
                raise ValueError("NULL_WITHOUT_NULL_YIELD:" + eid)

        for benefit in encounter.get("benefit_observations") or []:
            benefit_count += 1
            if "counterfactual_confidence" not in benefit:
                raise ValueError("BENEFIT_COUNTERFACTUAL_MISSING:" + eid)
            if "attribution_uncertainty" not in benefit:
                raise ValueError("BENEFIT_ATTRIBUTION_UNCERTAINTY_MISSING:" + eid)

        for wake in encounter.get("wake_relations") or []:
            if wake.get("participant_notification_authorized") is False:
                unauthorized_wake_routes += 1
                if wake.get("communication_route_ref") is not None:
                    raise ValueError("UNAUTHORIZED_NOTIFICATION_ROUTE:" + eid)

        for relation in encounter.get("open_relations") or []:
            open_relations.append({
                "encounter_id": eid,
                "relation": copy.deepcopy(relation),
            })

    if null_count != 1:
        raise ValueError("EXPECTED_ONE_EVIDENCED_NULL")
    if benefit_count != 1:
        raise ValueError("EXPECTED_ONE_BENEFIT_OBSERVATION")
    if unauthorized_wake_routes < 1:
        raise ValueError("EXPECTED_UNAUTHORIZED_WAKE_HOLD")

    return {
        "encounters_reviewed": len(encounters),
        "yield_records_reviewed": evidence_count,
        "evidenced_null_count": null_count,
        "benefit_observation_count": benefit_count,
        "unauthorized_wake_routes_held": unauthorized_wake_routes,
        "open_relations": open_relations,
    }

def profile_index(profiles: dict) -> dict:
    return {row["profile_id"]: row for row in profiles.get("profiles", [])}

def subscribed(profile: dict, domain: str, allowed_tiers: set[str]) -> tuple[bool, str | None]:
    for tier in ("hot", "warm", "digest"):
        if tier in allowed_tiers and domain in (profile.get(tier) or []):
            return True, tier.upper()
    return False, None

def route_open_relations(review: dict, profiles: dict, policy: dict) -> dict:
    idx = profile_index(profiles)
    capmap = {row["capability_hint"]: row for row in policy.get("capability_routes", [])}
    allowed = set(policy["route_policy"]["allowed_subscription_tiers"])

    routed = []
    held = []

    for item in review["open_relations"]:
        rel = item["relation"]
        relation_id = rel["relation_id"]
        hint = rel.get("capability_hint")

        if rel.get("status") != "OPEN":
            held.append({"relation_id": relation_id, "state": "HELD_NOT_OPEN"})
            continue

        if rel.get("consent_required"):
            held.append({"relation_id": relation_id, "state": "HELD_FOR_CONSENT"})
            continue

        route = capmap.get(hint)
        if route is None:
            held.append({"relation_id": relation_id, "state": "HELD_NO_CAPABILITY_ROUTE"})
            continue

        matches = []
        for profile_id in route.get("candidate_profiles", []):
            profile = idx.get(profile_id)
            if profile is None:
                continue
            ok, tier = subscribed(profile, route["domain_hint"], allowed)
            if ok:
                matches.append({
                    "profile_id": profile_id,
                    "subscription_tier": tier,
                    "domain_hint": route["domain_hint"],
                })

        if not matches:
            held.append({"relation_id": relation_id, "state": policy["route_policy"]["unmatched_state"]})
            continue

        routed.append({
            "encounter_id": item["encounter_id"],
            "relation_id": relation_id,
            "need": rel["need"],
            "capability_hint": hint,
            "authority_required": rel["authority_required"],
            "state": policy["route_policy"]["route_state"],
            "candidate_receivers": matches,
        })

    return {"route_candidates": routed, "held_relations": held}

def negative_tests(pack: dict, profiles: dict, policy: dict) -> dict:
    out = {}

    bad_auth = copy.deepcopy(pack)
    bad_auth["encounters"][0]["authority_ceiling"] = "EXECUTE_WITHOUT_GATE"
    try:
        review_fixture(bad_auth)
        out["authority_inflation_rejected"] = False
    except ValueError:
        out["authority_inflation_rejected"] = True

    bad_wake = copy.deepcopy(pack)
    bad_wake["encounters"][0]["wake_relations"][0]["communication_route_ref"] = "mail:anywhere"
    try:
        review_fixture(bad_wake)
        out["unauthorized_notification_route_rejected"] = False
    except ValueError:
        out["unauthorized_notification_route_rejected"] = True

    review = review_fixture(pack)
    consent_review = copy.deepcopy(review)
    consent_review["open_relations"][0]["relation"]["consent_required"] = True
    consent_routing = route_open_relations(consent_review, profiles, policy)
    out["consent_required_relation_held"] = (
        len(consent_routing["route_candidates"]) == 0
        and any(x["state"] == "HELD_FOR_CONSENT" for x in consent_routing["held_relations"])
    )

    unknown_review = copy.deepcopy(review)
    unknown_review["open_relations"][0]["relation"]["capability_hint"] = "unknown/capability"
    unknown_routing = route_open_relations(unknown_review, profiles, policy)
    out["unknown_capability_relation_held"] = (
        len(unknown_routing["route_candidates"]) == 0
        and any(x["state"] == "HELD_NO_CAPABILITY_ROUTE" for x in unknown_routing["held_relations"])
    )

    if not all(out.values()):
        raise ValueError("NEGATIVE_TEST_FAILED:" + json.dumps(out, sort_keys=True))
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--source-proof", required=True)
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    fixture_path = Path(args.fixture)
    proof_path = Path(args.source_proof)
    profiles_path = Path(args.profiles)
    policy_path = Path(args.policy)
    out_path = Path(args.output)

    if out_path.exists():
        raise SystemExit("FAIL_CLOSED__NO_CLOBBER=" + str(out_path))

    fixture_raw = fixture_path.read_bytes()
    proof_raw = proof_path.read_bytes()
    fixture = json.loads(fixture_raw.decode("utf-8"))
    proof = json.loads(proof_raw.decode("utf-8"))
    profiles = load_json(profiles_path)
    policy = load_json(policy_path)

    expected_fixture_sha = proof["local_sha256"]["fixture"]
    actual_fixture_sha = sha256(fixture_raw)
    if actual_fixture_sha != expected_fixture_sha:
        raise SystemExit("FAIL_CLOSED__R0A_FIXTURE_HASH_MISMATCH")

    review = review_fixture(fixture)
    routing = route_open_relations(review, profiles, policy)
    negatives = negative_tests(fixture, profiles, policy)

    if len(routing["route_candidates"]) != 1:
        raise SystemExit("FAIL_CLOSED__EXPECTED_ONE_OPEN_RELATION_ROUTE_CANDIDATE")
    if routing["route_candidates"][0]["relation_id"] != "open:plain-language-role-identity":
        raise SystemExit("FAIL_CLOSED__UNEXPECTED_ROUTED_RELATION")

    result = {
        "schema": "CoEncounterYieldIndependentReview.R0B.v0.1",
        "state": "PASS_R0B_INDEPENDENT_DETERMINISTIC_REVIEW__OPEN_RELATION_ROUTE_CANDIDATE__NO_ASSIGNMENT_NO_DELIVERY_NO_AUTHORITY",
        "execution_expectation": "GITHUB_ACTIONS_DISTINCT_FROM_R0A_OPENAI_TASK_CONTAINER",
        "source_bindings": {
            "fixture_sha256": actual_fixture_sha,
            "source_proof_sha256": sha256(proof_raw),
            "source_proof_state": proof.get("state"),
        },
        "independence": {
            "semantic_review_input": policy["independence_policy"]["semantic_review_input"],
            "prior_result_assertions_used": False,
            "routing_phase_after_semantic_review": True,
            "ignored_for_route_election": policy["independence_policy"]["ignored_for_route_election"],
        },
        "review": {k: v for k, v in review.items() if k != "open_relations"},
        "routing": routing,
        "negative_tests": negatives,
        "effects": {
            "assignments": 0,
            "deliveries": 0,
            "participant_notifications": 0,
            "repo_mutations_by_reviewer": 0,
            "authority_changes": 0,
        },
        "external_alignment": policy["external_donors"],
        "next": "R0C_HETEROGENEOUS_RECEIVER_REVIEW_OR_PUBLIC_OPEN_RELATION_UX_CANARY__ONLY_IF_MATERIAL",
        "rails": policy["rails"],
        "nonclaims": [
            "INDEPENDENT_DETERMINISTIC_REVIEW_NE_HETEROGENEOUS_MODEL_REVIEW",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "ROUTE_CANDIDATE_NE_ASSIGNMENT",
            "ROUTE_CANDIDATE_NE_DELIVERY",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_RUNTIME_INTEGRATION",
            "NO_COEX",
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2) + "\n").encode("utf-8")
    out_path.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(out_path),
        "OUTPUT_SHA256": sha256(encoded),
        "FIXTURE_SHA256": actual_fixture_sha,
        "ROUTE_CANDIDATES": len(routing["route_candidates"]),
        "HELD_RELATIONS": len(routing["held_relations"]),
        "NEGATIVE_TESTS": negatives,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
