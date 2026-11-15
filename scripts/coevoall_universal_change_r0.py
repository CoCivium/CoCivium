"""Synthetic CoEvoAll universal-change eligibility evaluator R0.

No mutation, network, credentials, deletion, installation, or effect authority.
Returned source-level candidate verdicts are NOT independent review or runtime adoption.
"""
import json
import re
from pathlib import Path

_SHA = re.compile(r"^[0-9a-f]{64}$")
_SCOPE = re.compile(r"^[a-z][a-z0-9_-]{0,127}$")
POLICY = Path(__file__).resolve().parents[1] / "ai/evolution/universal-evolution-r0.json"


def load_policy(path=POLICY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != "CoAll.UniversalEvolution.R0.Candidate":
        raise ValueError("UNKNOWN_POLICY_SCHEMA")
    if data.get("permanent_exempt_scopes") != [] or data.get("domains_are_open_world") is not True:
        raise ValueError("PERMANENT_CHANGE_EXCLUSION_FORBIDDEN")
    if data.get("effect_authority") != "NONE_IN_THIS_SYNTHETIC_EVALUATOR":
        raise ValueError("EFFECT_AUTHORITY_MUST_BE_NONE")
    if data.get("history_policy") != "APPEND_ONLY_PREDECESSOR_AND_EXPLICIT_SUPERSESSION":
        raise ValueError("HISTORICAL_REWRITE_FORBIDDEN")
    if data.get("observation_can_advance_without_mutation") is not True:
        raise ValueError("OBSERVATION_MUST_NOT_FORCE_MUTATION")
    return data


def evaluate(subject, proposal, tick, policy):
    """One bounded synthetic observation, always zero real-world effects."""
    result = {
        "state": "HOLD",
        "effect_count": 0,
        "object_mutated": False,
        "receiver_ack": False,
        "external_authority": False,
        "observation_tick": tick,
        "new_revision_sha256": None,
    }
    if not isinstance(subject, dict) or not isinstance(tick, int) or isinstance(tick, bool):
        return {**result, "reason": "INVALID_SUBJECT_OR_TICK"}
    obj = subject.get("object_id")
    scope = subject.get("scope")
    previous = subject.get("revision_sha256")
    last_tick = subject.get("last_tick")
    if (not isinstance(obj, str) or not obj.strip()
            or not isinstance(scope, str) or not _SCOPE.fullmatch(scope)
            or not isinstance(previous, str) or not _SHA.fullmatch(previous)
            or not isinstance(last_tick, int) or isinstance(last_tick, bool)):
        return {**result, "reason": "SUBJECT_NOT_SOURCE_BOUND"}
    if tick <= last_tick:
        return {**result, "reason": "NON_MONOTONIC_OBSERVATION"}
    if policy.get("permanent_exempt_scopes") != [] or policy.get("domains_are_open_world") is not True:
        return {**result, "reason": "POLICY_EXEMPTS_FROM_CHANGE"}
    if policy.get("effect_authority") != "NONE_IN_THIS_SYNTHETIC_EVALUATOR":
        return {**result, "reason": "POLICY_EFFECT_AUTHORITY_UNSAFE"}
    if proposal is None:
        return {**result, "state": "OBSERVATION_REFRESH_ONLY",
                "reason": "TIME_AND_EVIDENCE_RELATION_REEVALUATED", "next_wake": "ON_MATERIAL_DELTA"}
    if not isinstance(proposal, dict):
        return {**result, "reason": "INVALID_CANDIDATE"}
    source = proposal.get("based_on_sha256")
    successor = proposal.get("successor_sha256")
    if source != previous:
        return {**result, "reason": "STALE_OR_CONFLICTING_PREDECESSOR"}
    if not isinstance(successor, str) or not _SHA.fullmatch(successor):
        return {**result, "reason": "INVALID_SUCCESSOR_DIGEST"}
    if successor == previous:
        return {**result, "state": "NO_MATERIAL_DELTA",
                "reason": "IDENTICAL_SOURCE_REBIND"}
    if proposal.get("overwrites_history") is not False:
        return {**result, "reason": "HISTORY_OVERWRITE_NOT_PERMITTED"}
    if proposal.get("requests_effect") is not False:
        return {**result, "reason": "EFFECT_REQUIRES_SEPARATE_AUTHORITY"}
    falsifier = proposal.get("falsifier")
    if not isinstance(falsifier, str) or len(falsifier.strip()) < 8:
        return {**result, "reason": "FALSIFIER_MISSING"}
    gain = proposal.get("synthetic_expected_gain")
    cost = proposal.get("synthetic_expected_cost")
    if (not isinstance(gain, (int, float)) or isinstance(gain, bool)
            or not isinstance(cost, (int, float)) or isinstance(cost, bool)
            or not (-1e6 <= gain <= 1e6 and 0 <= cost <= 1e6)
            or gain <= cost):
        return {**result, "reason": "NET_USEFUL_GAIN_UNQUALIFIED"}
    sensitive = set(policy.get("review_sensitive_domain_examples", []))
    if scope in sensitive and proposal.get("independent_review_requested") is not True:
        return {**result, "reason": "SENSITIVE_SCOPE_REVIEW_NOT_REQUESTED"}
    return {
        **result, "state": "CANDIDATE_FOR_INDEPENDENT_REVIEW",
        "reason": "SYNTHETIC_POSITIVE_DELTA_ONLY__NOT_ACCEPTED",
        "scope_change_eligible": True,
        "proposed_successor_sha256": successor,
        "independent_review_received": False,
    }


if __name__ == "__main__":
    load_policy()
    print("PASS_COEVOALL_UNIVERSAL_CHANGE_POLICY_SOURCE_ONLY")
