#!/usr/bin/env python3
"""CoFlowBaseline R0: fixture-only benchmark evidence contract.

Does not inspect hardware, execute agent workloads, grant authority, or prove uptake.
"""
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONTEXT_FIELDS = ("workload_digest", "dataset_digest", "device_class", "quality_contract")


def canonical_bytes(item):
    return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def load_fixture(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("fixture_only") is not True or payload.get("schema") != "CoFlowBaseline.Fixture/0":
        raise ValueError("FIXTURE_ONLY_REQUIRED")
    if not isinstance(payload.get("observations"), list) or not payload["observations"]:
        raise ValueError("OBSERVATIONS_REQUIRED")
    return payload


def validated_run(row):
    if not isinstance(row, dict) or not isinstance(row.get("context"), dict):
        raise ValueError("INVALID_RUN")
    if set(row["context"]) != set(CONTEXT_FIELDS):
        raise ValueError("CONTEXT_FIELDS_MISMATCH")
    if any(not isinstance(row["context"][k], str) or not row["context"][k] for k in CONTEXT_FIELDS):
        raise ValueError("EMPTY_CONTEXT")
    if any(not isinstance(row.get(k), str) or not row[k] for k in ("run_id", "system")):
        raise ValueError("MISSING_RUN_ID_OR_SYSTEM")
    for key in ("emitted", "correct", "receiver_accepted"):
        if isinstance(row.get(key), bool) or not isinstance(row.get(key), int) or row[key] < 0:
            raise ValueError("INVALID_COUNT:" + key)
    if not (row["receiver_accepted"] <= row["correct"] <= row["emitted"]):
        raise ValueError("IMPOSSIBLE_COUNT_ORDER")
    sec = row.get("elapsed_seconds")
    if isinstance(sec, bool) or not isinstance(sec, (int, float)) or not math.isfinite(sec) or sec <= 0:
        raise ValueError("INVALID_ELAPSED")
    if type(row.get("quality_pass")) is not bool or type(row.get("currentness_pass")) is not bool:
        raise ValueError("MISSING_QUALITY_OR_CURRENTNESS")
    if row.get("receiver_receipt") not in ("SYNTHETIC_ACK", "NOT_OBSERVED"):
        raise ValueError("INVALID_RECEIPT_STATE")
    return row


def context_key(run):
    return tuple(run["context"][k] for k in CONTEXT_FIELDS)


def eligible(run):
    return (run["quality_pass"] is True and run["currentness_pass"] is True
            and run["receiver_receipt"] == "SYNTHETIC_ACK"
            and run["receiver_accepted"] > 0)


def measure(run):
    return round(run["receiver_accepted"] / run["elapsed_seconds"], 6)


def summarize(payload, reference_system="baseline", min_repeats=3):
    if min_repeats < 2:
        raise ValueError("INSUFFICIENT_REPETITIONS_CONTRACT")
    runs = [validated_run(row) for row in payload["observations"]]
    ids = [row["run_id"] for row in runs]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_RUN_ID")
    cohorts = defaultdict(list)
    for run in runs:
        cohorts[context_key(run)].append(run)
    result = []
    for key in sorted(cohorts):
        group = cohorts[key]
        valid = [r for r in group if eligible(r)]
        peaks = sorted(valid, key=lambda r: (-measure(r), r["run_id"]))
        record = ({"rate_per_second": measure(peaks[0]), "run_id": peaks[0]["run_id"],
                   "system": peaks[0]["system"]} if peaks else None)
        grouped = defaultdict(list)
        for r in valid:
            grouped[r["system"]].append(r)
        sustained = {}
        for system, observations in sorted(grouped.items()):
            if len(observations) < min_repeats:
                sustained[system] = {"state": "HOLD_REPETITIONS", "qualified_repeats": len(observations)}
                continue
            # Conservative observed minimum, not a statistical confidence bound.
            rates = sorted(measure(r) for r in observations)
            sustained[system] = {"state": "OBSERVED_REPEAT_MIN", "qualified_repeats": len(observations),
                                 "repeat_min_rate": rates[0], "repeat_median_rate": rates[len(rates)//2]}
        baseline = sustained.get(reference_system)
        for system, datum in sustained.items():
            if system == reference_system or datum["state"] != "OBSERVED_REPEAT_MIN":
                datum["promotion_vs_baseline"] = "NOT_EVALUATED"
            elif not baseline or baseline["state"] != "OBSERVED_REPEAT_MIN":
                datum["promotion_vs_baseline"] = "HOLD_NO_COMPARABLE_BASELINE"
            elif datum["repeat_min_rate"] > baseline["repeat_min_rate"]:
                datum["promotion_vs_baseline"] = "THROUGHPUT_GATE_PASS_ONLY"
            else:
                datum["promotion_vs_baseline"] = "THROUGHPUT_GATE_FAIL"
        result.append({"context": dict(zip(CONTEXT_FIELDS, key)), "qualified_runs": len(valid),
                       "unqualified_runs": len(group)-len(valid), "historical_record": record,
                       "sustained_candidates": sustained})
    return {"schema": "CoFlowBaseline.Summary/0", "synthetic_only": True,
            "warning": "Fixture observations do not establish real-world throughput or receiver acceptance.",
            "qualified_runs_total": sum(row["qualified_runs"] for row in result),
            "cohorts": result}


def build_events(summary):
    primary = next(x for x in summary["cohorts"] if x["context"]["device_class"] == "X2-SYNTHETIC")
    systems = primary["sustained_candidates"]
    checks = [
        ("CONTEXT_ISOLATION", "PASS", "Other-device peak does not replace X2-context record"),
        ("REPEATED_BASELINE", "PASS" if systems["baseline"]["state"] == "OBSERVED_REPEAT_MIN" else "FAIL", "Three baseline fixture repetitions required"),
        ("PEAK_IS_SUSTAINED_ASSUMPTION", "FAIL", "Historical peak from one burst cannot establish a sustained floor"),
        ("BURST_UNDER_REPEATED_GATE", "HOLD" if systems["burst"]["state"] == "HOLD_REPETITIONS" else "FAIL", "Single exceptional burst has no stable baseline"),
        ("NEW_CANDIDATE_COMPARABLE_GATE", "PASS" if systems["candidate"]["promotion_vs_baseline"] == "THROUGHPUT_GATE_PASS_ONLY" else "FAIL", "Synthetic throughput repeat-min improves; correctness/cost/etc. still require separate real gates"),
        ("MISLEADING_UNACKED_ROW", "PASS" if primary["unqualified_runs"] > 0 else "FAIL", "Run lacking a synthetic fixture ACK cannot set a record"),
        ("REAL_X2_OR_INDEPENDENT_RECEIVER", "NOT_RUN", "No real devices, people, network, energy meters or provider sessions used"),
    ]
    prior = "0"*64
    events = []
    for index, (check, state, detail) in enumerate(checks, 1):
        item = {"schema": "CoBenchmarkEvoEvent/Fixture0", "seq": index, "kind": check,
                "outcome": state, "detail": detail, "synthetic_only": True, "prev_hash": prior}
        item["event_hash"] = hashlib.sha256(canonical_bytes(item)).hexdigest()
        prior = item["event_hash"]
        events.append(item)
    return events, prior


def verify_events(events, expected_head):
    prior = "0"*64
    for index, event in enumerate(events, 1):
        if event.get("seq") != index or event.get("prev_hash") != prior:
            raise ValueError("BROKEN_CHAIN")
        payload = {k: v for k, v in event.items() if k != "event_hash"}
        if event.get("event_hash") != hashlib.sha256(canonical_bytes(payload)).hexdigest():
            raise ValueError("TAMPERED_EVENT")
        prior = event["event_hash"]
    if prior != expected_head:
        raise ValueError("HEAD_MISMATCH")
    return len(events)


def main():
    payload = load_fixture(BASE / "fixtures" / "observations.json")
    summary = summarize(payload)
    (BASE / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    events, head = build_events(summary)
    (BASE / "benchmark_evo.jsonl").write_text("".join(json.dumps(x, sort_keys=True)+"\n" for x in events), encoding="utf-8")
    (BASE / "HEAD.sha256").write_text(head+"\n", encoding="utf-8")
    assert verify_events(events, head) == len(events)
    print("PASS: {} fixture runs across {} context groups; {} hash-linked events; head {}".format(
        len(payload["observations"]), len(summary["cohorts"]), len(events), head))
    primary = next(x for x in summary["cohorts"] if x["context"]["device_class"] == "X2-SYNTHETIC")
    print("SYNTHETIC X2 context: record {} accepted-outcomes/s; repeated baseline {} accepted-outcomes/s".format(
        primary["historical_record"]["rate_per_second"], primary["sustained_candidates"]["baseline"]["repeat_min_rate"]))


if __name__ == "__main__":
    main()
