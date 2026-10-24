#!/usr/bin/env python3
"""CoNex R0: finite, reproducible counterfactual expansion of CoDoodle seeds.

No network, external action, model usage, credential access, event capture, or
workers. The pseudo-random order is SHA256-derived and stable with a supplied
integer seed. Output is an unscheduled set of proposed tests, not test results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import codoodle

SCHEMA = "CoNex.SeededVariation.R0"
MAX_SEED = (1 << 64) - 1
MAX_FANOUT = 3
MAX_TOTAL = 24
BRANCHES = (
    "ELSE", "FAULT", "REPLAY", "TIME_SHIFT", "OUTSIDE_PRIOR",
    "NULL_SCOPE", "WEIRD_HYPOTHESIS",
)
BRANCH_POLICY = {
    "NOT_ELSE": (
        "Try a counterexample to the proposed conclusion.",
        "Provide a scoped falsifying witness or report UNKNOWN, never universal absence.",
    ),
    "ELSE": (
        "Compare one simpler alternative with the baseline.",
        "Use identical task, evidence boundary, and resource budget.",
    ),
    "FAULT": (
        "What if the original source, input, or receiver is unavailable?",
        "Inject a synthetic missing-input/failure state without mutating real receivers.",
    ),
    "REPLAY": (
        "Would the earlier result reproduce on pinned historical inputs?",
        "Preserve an original snapshot and compare exact source-bound differences.",
    ),
    "TIME_SHIFT": (
        "Would a past/future projection change a useful prediction?",
        "Clearly separate observation time, counterfactual time, and forecast status.",
    ),
    "OUTSIDE_PRIOR": (
        "Does an independent outside explanation solve this better?",
        "Find source/rights/currentness and compare with a reproducible baseline.",
    ),
    "NULL_SCOPE": (
        "Is the missing connection UNKNOWN, observed absent, or intentionally private?",
        "Demand scoped observation before negative quantification; preserve private redaction.",
    ),
    "WEIRD_HYPOTHESIS": (
        "Which unusual framing could expose a testable assumption?",
        "Label it speculative and require independent measurable predictions before promotion.",
    ),
}
NONCLAIMS = (
    "SEEDED_VARIATION_NE_INDEPENDENT_EVIDENCE",
    "DESCRIPTOR_NE_EXECUTED_EXPERIMENT",
    "PSEUDORANDOM_NE_CRYPTOSYSTEM",
    "SOURCE_CATALOG_NE_LIVE_FEED",
    "ET_SIGNAL_CANDIDATE_NE_ET_CONFIRMATION",
    "GD_PHILOSOPHY_NE_GD_PHYSICAL_SENSOR",
    "MANY_VIRTUAL_CANDIDATES_NE_MANY_LIVE_WORKERS",
    "NO_EFFECT_WITHOUT_SEPARATE_AUTHORITY",
    "GITHUB_PR_NE_DEVICE_RUNTIME",
)


def _score(source_sha: str, seed: int, nexus_id: str, branch: str) -> str:
    data = f"CoNexR0|{source_sha}|{seed}|{nexus_id}|{branch}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def expand(seeds: dict[str, Any], seed: int, *, fanout: int = 2,
           max_total: int = 12) -> dict[str, Any]:
    if not isinstance(seeds, dict) or seeds.get("schema") != codoodle.SCHEMA:
        raise ValueError("requires CoDoodle R0 candidate report")
    source = seeds.get("source")
    if not isinstance(source, dict):
        raise ValueError("source missing")
    source_sha = source.get("sha256")
    if not isinstance(source_sha, str) or len(source_sha) != 64 or any(c not in "0123456789abcdef" for c in source_sha):
        raise ValueError("invalid source digest")
    if seeds.get("state") != "LEXICAL_CANDIDATES__ZERO_EXECUTION":
        raise ValueError("cannot elevate non-shadow input")
    if type(seed) is not int or not 0 <= seed <= MAX_SEED:
        raise ValueError("seed must be uint64 (not bool)")
    if type(fanout) is not int or not 1 <= fanout <= MAX_FANOUT:
        raise ValueError("fanout must be 1..3")
    if type(max_total) is not int or not 1 <= max_total <= MAX_TOTAL:
        raise ValueError("max_total must be 1..24")
    parents = seeds.get("candidates")
    if not isinstance(parents, list) or len(parents) > codoodle.MAX_CANDIDATES:
        raise ValueError("candidate count out of bounds")
    if seeds.get("candidate_count") != len(parents):
        raise ValueError("candidate count mismatch")
    if any(p.get("experiment_executed") is not False for p in parents if isinstance(p, dict)):
        raise ValueError("candidate contains execution claim")
    if any(not isinstance(p, dict) for p in parents):
        raise ValueError("invalid candidate type")
    emitted: list[dict[str, Any]] = []
    # One initial inverse/counterexample per matched nexus, then bounded rounds
    # of seeded alternative lenses. This avoids a single busy nexus consuming
    # the entire global budget before quiet nexuses have any representation.
    for branch_round in range(fanout):
        for parent in parents:
            if len(emitted) == max_total:
                break
            cid = parent.get("candidate_id")
            if not isinstance(cid, str) or not cid.startswith("codoodle:" + source_sha[:16] + ":"):
                raise ValueError("candidate source identity mismatch")
            if parent.get("readiness") != "DESCRIPTOR_ONLY_NEEDS_PRIORS_AND_EVIDENCE":
                raise ValueError("candidate evidence gate lost")
            if parent.get("effect_boundary") not in ("LOCAL_SHADOW_ONLY", "EXTERNAL_ACTION_HELD"):
                raise ValueError("candidate effect boundary unsupported")
            order = sorted(BRANCHES, key=lambda b: _score(source_sha, seed, cid, b))
            chosen = "NOT_ELSE" if branch_round == 0 else order[branch_round - 1]
            q, test = BRANCH_POLICY[chosen]
            # Do not paste the source's matched raw text into variants. A short
            # source span, original family, and exact source digest suffice.
            span = parent.get("source_span_chars")
            if not isinstance(span, list) or len(span) != 2 or any(type(i) is not int for i in span):
                raise ValueError("missing source span")
            trace = _score(source_sha, seed, cid, chosen)
            emitted.append({
                "id": "conex:" + trace[:24],
                "nexus_parent_id": cid,
                "source_sha256": source_sha,
                "source_span_chars": span,
                "original_family": parent.get("concept_family"),
                "original_epistemic_class": parent.get("evidence_class"),
                "branch": chosen,
                "question_lens": q,
                "bounded_disconfirmation": test,
                "next_gate": "PRIORS_AND_SOURCE_SCOPE_REVIEW_BEFORE_COEXPERIMENTSELECTOR",
                "suggested_lane": parent.get("suggested_lane"),
                "effect_boundary": "EXTERNAL_ACTION_HELD" if parent.get("effect_boundary") == "EXTERNAL_ACTION_HELD" else "LOCAL_SHADOW_ONLY",
                "readiness": "PROPOSAL_ONLY_UNSCORED",
                "executed": False,
                "selection_trace_sha256": trace,
            })
        if len(emitted) == max_total:
            break
    return {
        "schema": SCHEMA,
        "state": "SEEDED_VARIANTS__ZERO_EXECUTION",
        "parent_source_sha256": source_sha,
        "seed_u64": seed,
        "algorithm": "SHA256_LEXICOGRAPHIC_ORDER_R0_NOT_SECURITY_RANDOM",
        "nexuses": len(parents),
        "fanout_per_nexus_requested": fanout,
        "global_variant_cap": max_total,
        "possible_before_global_cap": len(parents) * fanout,
        "emitted": len(emitted),
        "held_for_budget": len(parents) * fanout - len(emitted),
        "variants": emitted,
        "required_evidence": "EVIDENCED_PRIORS_AND_METRICS_BEFORE_SELECTOR; REVIEW_BEFORE_ANY_EFFECT",
        "effects": {"workers_started": 0, "provider_calls": 0, "external_sends": 0,
                    "experiments_executed": 0, "device_io": 0, "authority_granted": 0},
        "nonclaims": NONCLAIMS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="CoDoodle R0 JSON report, generated from explicitly supplied text")
    parser.add_argument("--seed", type=int, required=True,
                        help="Non-secret reproducible integer in uint64 range")
    parser.add_argument("--fanout", type=int, default=2)
    parser.add_argument("--max-total", type=int, default=12)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.input.is_symlink() or args.input.stat().st_size > 65536:
            raise ValueError("input symlink or size rejected")
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = expand(payload, args.seed, fanout=args.fanout,
                        max_total=args.max_total)
        serial = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            # Exclusive creation, never overwrite the user's original text.
            with args.output.open("x", encoding="utf-8") as f:
                f.write(serial)
        else:
            print(serial, end="")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
