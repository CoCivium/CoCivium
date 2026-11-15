"""CoEvoAll hypothetical policy comparison over immutable synthetic fixtures.

This module does not alter local or external state, and contains no scheduler.
Its modeled "applied" transitions are counterfactual only: they are NEVER authority.
"""
import hashlib
import json
import math
from pathlib import Path

from coevoall_universal_change_r0 import evaluate, load_policy

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "ai/fixtures/coevoall_policy_comparison_r0.json"
SCHEMA = "CoAll.CoEvoAll.PolicyComparison.R0.SyntheticFixture"
POLICIES = ("frozen", "forced", "evidence_qualified")
SENSITIVE = frozenset({"privacy", "authority", "safety", "governance", "identity",
                       "evolution_rule", "deletion", "consent", "proof"})


def fixture_read(path=FIXTURE):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(data)
    return data


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and abs(value) <= 1e6


def validate(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("UNSUPPORTED_FIXTURE_SCHEMA")
    if data.get("scope") != "COUNTERFACTUAL_ONLY_NOT_ACTUAL_AUTHORITY":
        raise ValueError("EFFECT_SCOPE_MUST_BE_SYNTHETIC")
    if not number(data.get("observation_cost")) or data["observation_cost"] < 0:
        raise ValueError("BAD_OBSERVATION_COST")
    if set(data.get("nonclaims", [])) != {
        "COUNTERFACTUAL_SCORE_NE_ACTUAL_BENEFIT",
        "MOCK_REVIEW_NE_INDEPENDENT_AUTHORITY",
        "FORCED_MUTATION_IS_SIMULATED_ONLY",
        "SYNTHETIC_WINNER_NE_REAL_WORLD_BEST",
        "NO_LOCAL_OR_EXTERNAL_EFFECTS",
    }:
        raise ValueError("NONCLAIMS_NOT_PINNED")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not (3 <= len(scenarios) <= 8):
        raise ValueError("SCENARIOS_NOT_BOUNDED")
    scenario_ids = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != {"id", "events"}:
            raise ValueError("SCENARIO_SCHEMA_UNSAFE")
        sid = scenario["id"]
        if not isinstance(sid, str) or not sid.isidentifier() or sid in scenario_ids:
            raise ValueError("SCENARIO_ID_CONFLICT")
        scenario_ids.add(sid)
        events = scenario["events"]
        if not isinstance(events, list) or not (1 <= len(events) <= 30):
            raise ValueError("EVENT_COUNT_UNSAFE")
        event_ids = set()
        for e in events:
            if not isinstance(e, dict) or set(e) != {
                "id", "scope", "actual_gain", "estimated_gain",
                "change_cost", "synthetic_review_confirmed",
            }:
                raise ValueError("EVENT_SCHEMA_UNSAFE")
            eid = e["id"]
            if not isinstance(eid, str) or not eid.isidentifier() or eid in event_ids:
                raise ValueError("EVENT_ID_CONFLICT")
            event_ids.add(eid)
            if not isinstance(e["scope"], str) or not e["scope"].isidentifier():
                raise ValueError("SCOPE_NOT_VALID")
            for key in ("actual_gain", "estimated_gain", "change_cost"):
                if not number(e[key]):
                    raise ValueError("INVALID_QUANTITY_" + key)
            if e["change_cost"] < 0 or type(e["synthetic_review_confirmed"]) is not bool:
                raise ValueError("INVALID_COST_OR_REVIEW")


def digest(value):
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def project(data, policy=None):
    """Compare hypothetical strategies. No return field grants or creates effects."""
    validate(data)
    policy = policy or load_policy()
    if (policy.get("effect_authority") != "NONE_IN_THIS_SYNTHETIC_EVALUATOR"
            or policy.get("permanent_exempt_scopes") != []):
        raise ValueError("UNSAFE_EVALUATION_POLICY")
    records = []
    overhead = data["observation_cost"]
    for scenario in data["scenarios"]:
        candidates = {}
        events = scenario["events"]
        for strategy in POLICIES:
            score = 0.0
            changed = 0
            helpful = 0
            harmful = 0
            misses = 0
            unreviewed = 0
            proposals = 0
            reject = 0
            for step, e in enumerate(events, start=1):
                positive = e["actual_gain"] > e["change_cost"]
                if strategy == "frozen":
                    chosen = False
                elif strategy == "forced":
                    chosen = True  # Simulated, explicitly *not* authorized.
                else:
                    score -= overhead
                    base = digest(scenario["id"] + "/" + e["id"] + "/before")
                    after = digest(scenario["id"] + "/" + e["id"] + "/after")
                    subject = {"object_id": "synthetic:" + e["id"],
                               "scope": e["scope"], "revision_sha256": base,
                               "last_tick": step - 1}
                    proposal = {
                        "based_on_sha256": base,
                        "successor_sha256": after,
                        "overwrites_history": False,
                        "requests_effect": False,
                        "falsifier": "Reject if isolated fixture observation does not replicate",
                        "synthetic_expected_gain": e["estimated_gain"],
                        "synthetic_expected_cost": e["change_cost"],
                        "independent_review_requested": True,
                    }
                    verdict = evaluate(subject, proposal, step, policy)
                    proposed = verdict["state"] == "CANDIDATE_FOR_INDEPENDENT_REVIEW"
                    proposals += int(proposed)
                    # The reviewer is just fixture data, NOT a real approval.
                    chosen = proposed and e["synthetic_review_confirmed"]
                    reject += int(proposed and not e["synthetic_review_confirmed"])
                if chosen:
                    changed += 1
                    score += e["actual_gain"] - e["change_cost"]
                    helpful += int(positive)
                    harmful += int(not positive)
                    unreviewed += int(not e["synthetic_review_confirmed"])
                elif positive:
                    misses += 1
            candidates[strategy] = {
                "counterfactual_utility": round(score, 4),
                "projected_changes": changed,
                "projected_beneficial_changes": helpful,
                "projected_harmful_changes": harmful,
                "missed_positive_opportunities": misses,
                "unreviewed_projected_changes": unreviewed,
                "review_proposals": proposals,
                "mock_review_rejections": reject,
                "real_effect_count": 0,
            }
        # Winner is score only; a high score cannot override review limitations.
        winner = max(POLICIES, key=lambda s: candidates[s]["counterfactual_utility"])
        records.append({"scenario": scenario["id"], "winner_by_toy_score": winner,
                        "strategies": candidates, "real_effect_count": 0})
    return {
        "schema": "CoAll.CoEvoAll.PolicyComparison.R0.Report",
        "state": "SYNTHETIC_COMPARISON_ONLY_NO_REAL_ACTION",
        "records": records,
        "strategy_count": len(POLICIES),
        "scenario_count": len(records),
        "real_effect_count": 0,
        "external_receiver_ack": False,
        "nonclaims": data["nonclaims"],
    }


if __name__ == "__main__":
    print(json.dumps(project(fixture_read()), sort_keys=True, indent=2))
