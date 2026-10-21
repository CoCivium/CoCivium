#!/usr/bin/env python3
"""Read-only audit of supplied session evidence; no live probes or authority changes."""
import argparse
import json
import math
from datetime import datetime, timezone

REQUIRED = ("currentness", "checkpoint", "capabilities", "authority", "work_frontier", "continuation_owner")
NONCLAIMS = ["NO_SENTIENCE_OR_SANITY_MEASUREMENT", "NO_LIVE_CAPABILITY_PROBE",
             "REPORTED_EVIDENCE_NOT_INDEPENDENT_VERIFICATION", "NO_RUNTIME_DEPLOYMENT"]

def stamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timezone required")
    return value

def audit(snapshot, now):
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    rows = []
    checks = snapshot.get("checks", {})
    if not isinstance(checks, dict):
        raise ValueError("checks must be an object")
    for name in REQUIRED:
        check = checks.get(name)
        row = {"check": name, "state": "UNKNOWN", "reason": "MISSING_EVIDENCE"}
        if isinstance(check, dict):
            ref = check.get("evidence_ref")
            row["evidence_ref"] = ref if isinstance(ref, str) else None
            try:
                observed = stamp(check.get("observed_at"))
                age = (now - observed).total_seconds()
                limit = check.get("max_age_seconds")
                if isinstance(limit, bool) or not isinstance(limit, (int, float)):
                    raise ValueError("numeric finite freshness limit required")
                if not math.isfinite(limit) or limit <= 0:
                    raise ValueError("positive finite freshness limit required")
                if age < 0:
                    raise ValueError("future evidence")
                row["age_seconds"] = round(age, 3)
                reported = check.get("reported_state")
                if not isinstance(ref, str) or not ref.strip():
                    raise ValueError("evidence reference required")
                if reported not in ("OK", "FAILED", "UNKNOWN"):
                    raise ValueError("invalid reported state")
                if age > limit:
                    row.update(state="STALE", reason="FRESHNESS_EXPIRED")
                elif reported == "FAILED":
                    row.update(state="REPORTED_FAILURE", reason="SOURCE_REPORTS_FAILURE")
                elif reported == "OK":
                    row.update(state="EVIDENCE_REPORTED_CURRENT", reason="NOT_INDEPENDENTLY_VERIFIED")
                else:
                    row.update(reason="SOURCE_REPORTS_UNKNOWN")
            except (ValueError, TypeError, OverflowError) as exc:
                row.update(state="UNKNOWN", reason=str(exc))
        rows.append(row)
    counts = {state: sum(r["state"] == state for r in rows)
              for state in ("UNKNOWN", "STALE", "REPORTED_FAILURE", "EVIDENCE_REPORTED_CURRENT")}
    return {"schema": "CoCivium.SessionEvidenceAudit.R0",
            "session_id": snapshot.get("session_id"),
            "audited_at": now.isoformat(), "checks": rows, "counts": counts,
            "assessment": "FOLLOWUP_REQUIRED" if any(counts[s] for s in ("UNKNOWN", "STALE", "REPORTED_FAILURE"))
                          else "SUPPLIED_EVIDENCE_CURRENT__CAPABILITY_ACCEPTANCE_UNPROVEN",
            "nonclaims": NONCLAIMS,
            "next_action": "Resolve the first relevant evidence gap using an authorized read-only check; do not infer broader access."}

def self_test():
    import copy
    now = stamp("2026-10-21T15:00:00Z")
    check = {"reported_state": "OK", "observed_at": "2026-10-21T14:59:00Z",
             "max_age_seconds": 60, "evidence_ref": "fixture:observed-result"}
    valid = {"session_id": "FIXTURE_ONLY", "checks": {k: copy.deepcopy(check) for k in REQUIRED}}
    assert audit({}, now)["counts"]["UNKNOWN"] == 6
    assert audit(valid, now)["counts"]["EVIDENCE_REPORTED_CURRENT"] == 6
    cases = [
        ({"observed_at": "2026-10-21T14:58:59Z"}, "STALE"),
        ({"observed_at": "2026-10-21T15:00:01Z"}, "UNKNOWN"),
        ({"observed_at": "2026-10-21T14:59:00"}, "UNKNOWN"),
        ({"evidence_ref": ""}, "UNKNOWN"),
        ({"max_age_seconds": True}, "UNKNOWN"),
        ({"max_age_seconds": float("inf")}, "UNKNOWN"),
        ({"reported_state": "FAILED"}, "REPORTED_FAILURE"),
        ({"reported_state": "UNKNOWN"}, "UNKNOWN"),
    ]
    for patch, expected in cases:
        item = copy.deepcopy(valid)
        item["checks"]["currentness"].update(patch)
        assert audit(item, now)["checks"][0]["state"] == expected
    for invalid in ([], {"checks": []}):
        try:
            audit(invalid, now)
            raise AssertionError("malformed input accepted")
        except ValueError:
            pass
    print(json.dumps({"fixture_cases_passed": 12, "live_sessions_tested": 0, "nonclaims": NONCLAIMS}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?")
    parser.add_argument("--now", help="explicit timezone-qualified audit time; default UTC now")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        if not args.snapshot:
            parser.error("snapshot path required")
        with open(args.snapshot, encoding="utf-8") as handle:
            result = audit(json.load(handle), stamp(args.now) if args.now else datetime.now(timezone.utc))
        print(json.dumps(result, indent=2, allow_nan=False))
