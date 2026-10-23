#!/usr/bin/env python3
"""Validate CoStretch evidence JSONL and guarded paired comparisons.

No network, disk mutation, package dependencies, or model calls. This validator
checks record structure and honesty rails, not semantic correctness of claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "CoStretch.BenchmarkEvo.R0"
RESULTS = {"PASS", "FAIL", "HOLD"}
EVIDENCE = {"SYNTHETIC_FIXTURE", "DETERMINISTIC_LOCAL", "HISTORICAL_REPLAY", "MODEL_RUN", "HUMAN_REVIEW"}
STAGES = {"LOGICAL_ONLY", "VERIFIED_LOCAL", "LANDED", "PICKED_UP", "INTEGRATED"}
HEX = set("0123456789abcdef")
METERS = ("wall_ms", "cpu_ms", "energy_j", "token_count", "peak_memory_bytes", "cost_usd", "reviewer_minutes")


class EvidenceError(ValueError):
    pass


def _require(test: bool, reason: str):
    if not test:
        raise EvidenceError(reason)


def _hash(text: Any) -> bool:
    return isinstance(text, str) and len(text) == 64 and all(c in HEX for c in text)


def _timestamp(s: Any) -> bool:
    if not isinstance(s, str) or not s.endswith("Z"):
        return False
    try:
        return datetime.fromisoformat(s[:-1] + "+00:00").utcoffset().total_seconds() == 0
    except ValueError:
        return False


def validate_one(r: Any) -> None:
    _require(isinstance(r, dict), "record must be an object")
    required = {"schema", "event_id", "run_id", "task_id", "created_utc", "evidence_class", "task_sha256", "fixture_sha256", "method", "verdict", "checks", "authority", "lifecycle", "resource", "receiver", "nonclaims"}
    _require(required <= r.keys(), "missing required keys: " + ",".join(sorted(required - r.keys())))
    allowed = required | {"source_ref", "model", "historical", "notes", "comparison_group"}
    _require(set(r) <= allowed, "unknown keys: " + ",".join(sorted(set(r) - allowed)))
    _require(r["schema"] == SCHEMA, "wrong schema")
    for key in ("event_id", "run_id", "task_id", "method"):
        _require(isinstance(r[key], str) and 0 < len(r[key]) <= 160 and r[key].strip() == r[key], "invalid " + key)
    _require(_timestamp(r["created_utc"]), "timestamp must be UTC RFC3339 Z")
    _require(r["evidence_class"] in EVIDENCE, "invalid evidence_class")
    _require(_hash(r["task_sha256"]) and _hash(r["fixture_sha256"]), "invalid content sha256")
    _require(r["verdict"] in RESULTS, "invalid verdict")
    _require(isinstance(r["checks"], list) and r["checks"], "checks must be nonempty")
    _require(all(isinstance(c, dict) and set(c) == {"name", "outcome"} and isinstance(c["name"], str) and c["outcome"] in RESULTS for c in r["checks"]), "malformed check")
    names = [c["name"] for c in r["checks"]]
    _require(len(names) == len(set(names)), "duplicate check")
    _require(not (r["verdict"] == "PASS" and any(c["outcome"] != "PASS" for c in r["checks"])), "PASS conceals a failed or held check")
    auth = r["authority"]
    _require(isinstance(auth, dict) and set(auth) == {"effect_scope", "consent_state"}, "invalid authority")
    _require(auth["effect_scope"] in ("NONE", "READ_ONLY", "BOUNDED_AUTHORIZED") and auth["consent_state"] in ("NOT_REQUIRED", "VERIFIED", "UNKNOWN"), "invalid authority values")
    lifecycle = r["lifecycle"]
    _require(isinstance(lifecycle, dict) and set(lifecycle) == {"stage", "landing_receipt_sha256", "receiver_ack_sha256", "integration_receipt_sha256"}, "invalid lifecycle")
    _require(lifecycle["stage"] in STAGES, "invalid stage")
    for k in ("landing_receipt_sha256", "receiver_ack_sha256", "integration_receipt_sha256"):
        _require(lifecycle[k] is None or _hash(lifecycle[k]), "bad optional receipt hash")
    st = lifecycle["stage"]
    if st in {"LANDED", "PICKED_UP", "INTEGRATED"}:
        _require(_hash(lifecycle["landing_receipt_sha256"]), "landing proof missing")
    if st in {"PICKED_UP", "INTEGRATED"}:
        _require(_hash(lifecycle["receiver_ack_sha256"]), "receiver proof missing")
    if st == "INTEGRATED":
        _require(_hash(lifecycle["integration_receipt_sha256"]), "integration proof missing")
    receiver = r["receiver"]
    _require(isinstance(receiver, dict) and set(receiver) == {"id", "origin_verified"}, "invalid receiver")
    _require(receiver["id"] is None or (isinstance(receiver["id"], str) and receiver["id"]), "invalid receiver id")
    _require(type(receiver["origin_verified"]) is bool, "invalid receiver verification")
    if st in {"PICKED_UP", "INTEGRATED"}:
        _require(receiver["origin_verified"] is True and receiver["id"] is not None, "receiver origin not verified")
    resource = r["resource"]
    _require(isinstance(resource, dict) and set(resource) == set(METERS), "resource meters missing or extra")
    for k in METERS:
        v = resource[k]
        _require(v is None or (type(v) in (int, float) and v >= 0 and v < 1e15), "invalid meter " + k)
    _require(isinstance(r["nonclaims"], list) and len(r["nonclaims"]) > 0 and all(isinstance(n, str) and n for n in r["nonclaims"]), "nonclaims missing")
    if r["evidence_class"] == "SYNTHETIC_FIXTURE":
        _require(auth == {"effect_scope": "NONE", "consent_state": "NOT_REQUIRED"}, "synthetic fixture cannot have effect authority")
        _require(st == "LOGICAL_ONLY", "synthetic fixture cannot claim physical custody")
        _require(all(resource[k] is None for k in METERS), "synthetic logical fixture cannot claim measured usage")
        _require(receiver == {"id": None, "origin_verified": False}, "synthetic fixture cannot claim receiver")
    if r["evidence_class"] == "MODEL_RUN":
        model = r.get("model")
        _require(isinstance(model, dict) and {"provider", "name", "version", "run_receipt_sha256"} == set(model), "model run provenance missing")
        _require(all(isinstance(model[k], str) and model[k] and model[k] != "UNKNOWN" for k in ("provider", "name", "version")), "model provenance unknown")
        _require(_hash(model["run_receipt_sha256"]), "model run receipt absent")
    if r["evidence_class"] == "HISTORICAL_REPLAY":
        historical = r.get("historical")
        _require(isinstance(historical, dict) and set(historical) == {"original_sha256", "original_model_id"}, "historical source record absent")
        _require(_hash(historical["original_sha256"]), "unverified historical original")
        _require(isinstance(historical["original_model_id"], str) and historical["original_model_id"], "invalid old model reference")
    if "comparison_group" in r:
        _require(isinstance(r["comparison_group"], str) and 0 < len(r["comparison_group"]) <= 160, "invalid comparison group")


def validate_jsonl(text: str) -> dict:
    events, ids = [], set()
    _require(text.strip() != "", "empty ledger")
    for i, line in enumerate(text.splitlines(), 1):
        _require(line.strip() != "", "blank line at " + str(i))
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            raise EvidenceError(f"malformed JSON at line {i}: {e}") from e
        try:
            validate_one(item)
        except EvidenceError as e:
            raise EvidenceError(f"line {i}: {e}") from e
        _require(item["event_id"] not in ids, "duplicate event id")
        ids.add(item["event_id"])
        events.append(item)
    by_group = defaultdict(list)
    for e in events:
        if "comparison_group" in e:
            by_group[e["comparison_group"]].append(e)
    comparable = []
    for group, rows in sorted(by_group.items()):
        _require(len(rows) >= 2, f"comparison {group}: fewer than 2 candidates")
        _require(len({r["method"] for r in rows}) == len(rows), f"comparison {group}: duplicate method")
        _require(len({r["task_sha256"] for r in rows}) == 1, f"comparison {group}: task drift")
        _require(len({r["fixture_sha256"] for r in rows}) == 1, f"comparison {group}: fixture drift")
        _require(len({r["evidence_class"] for r in rows}) == 1, f"comparison {group}: mixed evidence classes")
        comparable.append(group)
    return {"schema": "CoStretch.BenchmarkEvoValidation.R0", "state": "SCHEMA_PASS__OUTCOME_TRUTH_UNASSESSED", "records": len(events), "pass": sum(r["verdict"] == "PASS" for r in events), "fail": sum(r["verdict"] == "FAIL" for r in events), "hold": sum(r["verdict"] == "HOLD" for r in events), "comparable_groups": comparable, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "nonclaims": ["STRUCTURAL_VALIDATION_NE_SCIENTIFIC_VALIDATION", "HASH_POINTER_NE_AUTHENTICATED_PROOF", "SYNTHETIC_FIXTURE_NE_MODEL_RUN", "VALIDATION_NE_RECEIVER_ACCEPTANCE"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", type=Path)
    p.add_argument("--report", type=Path, help="create report only if destination absent")
    a = p.parse_args()
    try:
        report = validate_jsonl(a.file.read_text(encoding="utf-8"))
        body = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if a.report:
            with a.report.open("x", encoding="utf-8") as f:
                f.write(body)
        else:
            print(body, end="")
    except (OSError, EvidenceError) as e:
        p.exit(2, "FAIL: " + str(e) + "\n")


if __name__ == "__main__":
    main()
