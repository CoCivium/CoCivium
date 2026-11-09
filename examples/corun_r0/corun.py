#!/usr/bin/env python3
"""CoRun+ R0: permissionless/read-only, finite DAG vs serial baseline.

No shell, subprocess, network, model calls, device access, imports from input, or
remote writes.  Source input is treated as data, not instruction.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from dataclasses import dataclass
from typing import Any

SCHEMA = "CoCivium.CoRunPlus.Runset.R0"
SOURCE_SCHEMA = "CoCivium.CoFlowAnchorDeltaRetrospective.R1"
CODE_VERSION = "0.1.0"
WORK_ID = "corun-coflow-priorgraph-r0"
MAX_WORKERS = 8
MAX_CASES = 64
MAX_INPUT_BYTES = 2_000_000
ALLOWED_STATUSES = {"PASS", "FAIL", "HELD", "PARTIAL"}
ALLOWED_STRATA = {"WORKED_SCOPED", "PARTIAL_OR_BLOCKED", "FAILED_HISTORICAL_REPAIRED", "FAILED_STILL_OBSERVED"}
SAFE_ID = re.compile(r"^[A-Z][A-Z0-9_-]{1,31}$")


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def fail(message: str) -> None:
    raise ValueError(message)


def load_source(path: Path, expected_git_blob: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if not path.is_file():
        fail("source missing")
    if path.stat().st_size > MAX_INPUT_BYTES:
        fail("source exceeds finite budget")
    b = path.read_bytes()
    digest, blob = sha(b), git_blob(b)
    if expected_git_blob is not None and blob != expected_git_blob.lower():
        fail("source Git-blob pin mismatch; refuse silent substitution")
    try:
        value = json.loads(b)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        fail("invalid JSON source: " + type(e).__name__)
    if not isinstance(value, dict) or value.get("schema") != SOURCE_SCHEMA:
        fail("unexpected source schema")
    cases = value.get("cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
        fail("source must have 1..64 cases")
    ids = set()
    for entry in cases:
        if not isinstance(entry, dict):
            fail("invalid case")
        cid = entry.get("id")
        if not isinstance(cid, str) or not SAFE_ID.fullmatch(cid) or cid in ids:
            fail("duplicate/unsafe case id")
        ids.add(cid)
        if entry.get("stratum") not in ALLOWED_STRATA:
            fail("unrecognized stratum")
        if entry.get("ledger_status") not in ALLOWED_STATUSES:
            fail("unrecognized ledger status")
        for key in ("record_id", "observed_at", "epistemic_boundary", "release_test"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                fail("missing required evidence field: " + key)
        if entry.get("paired_case_id") is not None and not isinstance(entry["paired_case_id"], str):
            fail("invalid pair")
    for entry in cases:
        pid = entry.get("paired_case_id")
        if pid and pid not in ids:
            fail("paired case absent")
    return value, {"bytes": len(b), "sha256": digest, "git_blob_sha1": blob, "path": path.as_posix()}


@dataclass(frozen=True)
class Node:
    id: str
    op: str
    deps: tuple[str, ...]
    source_id: str | None = None


def build_graph(source: dict[str, Any]) -> list[Node]:
    nodes = [Node("source", "source", ())]
    cases = sorted(source["cases"], key=lambda c: c["id"])
    for c in cases:
        nodes.append(Node("case:" + c["id"], "case", ("source",), c["id"]))
    pairs = set()
    for c in cases:
        if c.get("paired_case_id"):
            pairs.add(tuple(sorted([c["id"], c["paired_case_id"]])))
    for a, b in sorted(pairs):
        nodes.append(Node("pair:" + a + ":" + b, "pair", ("case:" + a, "case:" + b)))
    deps = tuple(n.id for n in nodes if n.op in ("case", "pair"))
    nodes.append(Node("aggregate", "aggregate", deps))
    nodes.append(Node("challenge", "challenge", ("aggregate",)))
    nodes.append(Node("deliverable", "deliverable", ("source", "aggregate", "challenge")))
    validate_graph(nodes)
    return nodes


def validate_graph(nodes: list[Node]) -> None:
    names = [n.id for n in nodes]
    if len(names) != len(set(names)):
        fail("duplicate DAG node")
    refs = set(names)
    for n in nodes:
        if n.id in n.deps or any(d not in refs for d in n.deps):
            fail("invalid dependency")
    visited, visiting = set(), set()
    index = {n.id: n for n in nodes}

    def visit(nid: str) -> None:
        if nid in visiting:
            fail("cycle")
        if nid in visited:
            return
        visiting.add(nid)
        for dep in index[nid].deps:
            visit(dep)
        visiting.remove(nid)
        visited.add(nid)

    for node in nodes:
        visit(node.id)


def task(node: Node, source: dict[str, Any], done: dict[str, dict[str, Any]], delay_ms: int, inject_fail: str | None) -> dict[str, Any]:
    if inject_fail == node.id:
        fail("injected fault " + node.id)
    if delay_ms:
        time.sleep(delay_ms / 1000)
    by_id = {c["id"]: c for c in source["cases"]}
    if node.op == "source":
        return {"schema": source["schema"], "selection_bias": source.get("sample_design", {}).get("selection_bias", "UNKNOWN"), "case_count": len(by_id), "source_state": source.get("state", "UNKNOWN")}
    if node.op == "case":
        c = by_id[node.source_id]
        return {"id": c["id"], "stratum": c["stratum"], "ledger_status": c["ledger_status"], "observed_at": c["observed_at"], "record_id": c["record_id"], "release_test": c["release_test"], "epistemic_boundary": c["epistemic_boundary"], "paired_case_id": c.get("paired_case_id"), "receiver_acceptance": "UNKNOWN"}
    if node.op == "pair":
        a_id, b_id = node.deps
        a, b = done[a_id], done[b_id]
        reverse = a["paired_case_id"] == b["id"] and b["paired_case_id"] == a["id"]
        return {"members": sorted([a["id"], b["id"]]), "reciprocal_references": reverse, "statuses": {a["id"]: a["ledger_status"], b["id"]: b["ledger_status"]}, "causal_claim": "NOT_PROVEN"}
    if node.op == "aggregate":
        cs = [v for k, v in sorted(done.items()) if k.startswith("case:")]
        pairs = [v for k, v in sorted(done.items()) if k.startswith("pair:")]
        counts: dict[str, int] = {}
        for c in cs:
            counts[c["stratum"]] = counts.get(c["stratum"], 0) + 1
        return {"cases": cs, "pairs": pairs, "strata_counts": counts, "historical_sample_only": True}
    if node.op == "challenge":
        agg = done["aggregate"]
        alerts = ["PURPOSIVE_SAMPLE_NOT_PROSPECTIVE_OR_CAUSAL", "SCOPED_PASS_NOT_RECEIVER_ADOPTION", "ONE_PIPELINE_NOT_INDEPENDENT_REPLICATION"]
        if any(not p["reciprocal_references"] for p in agg["pairs"]):
            alerts.append("NONRECIPROCAL_PAIR_REFERENCE")
        return {"warnings": alerts, "independence": "NOT_ESTABLISHED", "human_minutes": None, "proposed_discriminators": ["independent receiver readproof", "prospective A/B task completion", "record human active minutes and corrections", "cold reconstruction under independent failure domain"]}
    if node.op == "deliverable":
        return {"work_id": WORK_ID, "source": done["source"], "audit": done["aggregate"], "counterevidence": done["challenge"], "effect_class": "READ_ONLY_LOCAL", "promotion": "HELD_PENDING_PROSPECTIVE_HUMAN_BENEFIT"}
    fail("unregistered operator")


def execute(source: dict[str, Any], workers: int, delay_ms: int = 0, inject_fail: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if not 1 <= workers <= MAX_WORKERS or not 0 <= delay_ms <= 500:
        fail("invalid worker/latency budget")
    nodes = build_graph(source)
    indexed = {n.id: n for n in nodes}
    done: dict[str, dict[str, Any]] = {}
    unstarted = set(indexed)
    active = {}
    peak = 0
    started_ns = time.perf_counter_ns()
    # Exactly one elected dispatcher; worker functions have no effects.
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        while unstarted or active:
            ready = [indexed[nid] for nid in sorted(unstarted) if all(d in done for d in indexed[nid].deps)]
            for node in ready[:max(0, workers - len(active))]:
                unstarted.remove(node.id)
                deps_snapshot = {k: done[k] for k in node.deps}
                future = executor.submit(task, node, source, deps_snapshot, delay_ms, inject_fail)
                active[future] = node.id
            peak = max(peak, len(active))
            if not active:
                fail("scheduler deadlock or graph incomplete")
            finished, _ = concurrent.futures.wait(active, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in finished:
                node_id = active.pop(future)
                try:
                    done[node_id] = future.result()
                except Exception as e:
                    for f in active:
                        f.cancel()
                    fail("node " + node_id + " failed closed: " + str(e))
    elapsed_ns = time.perf_counter_ns() - started_ns
    if len(done) != len(indexed):
        fail("incomplete DAG")
    # Per-node hashes and output hash are independent of scheduling and wall time.
    evidence = {name: sha(canonical_bytes(done[name])) for name in sorted(done)}
    return done["deliverable"], {"worker_limit": workers, "peak_active": peak, "nodes_completed": len(done), "elapsed_ns": elapsed_ns, "node_sha256": evidence}


def compare(source: dict[str, Any], source_meta: dict[str, Any], workers: int, delay_ms: int = 0) -> dict[str, Any]:
    a, a_metrics = execute(source, 1, delay_ms)
    b, b_metrics = execute(source, workers, delay_ms)
    digest_a = sha(canonical_bytes(a))
    digest_b = sha(canonical_bytes(b))
    if digest_a != digest_b:
        fail("A/B output disagreement; no promotion")
    if a["audit"]["strata_counts"] != b["audit"]["strata_counts"]:
        fail("semantic disagreement")
    winner = "B_FASTER_WITHIN_THIS_TEST" if b_metrics["elapsed_ns"] < a_metrics["elapsed_ns"] else "A_FASTER_OR_EQUAL_WITHIN_THIS_TEST"
    return {"schema": SCHEMA, "version": CODE_VERSION, "work_id": WORK_ID, "source": source_meta, "arms": {"A_SERIAL": a_metrics, "B_BOUNDED_PARALLEL": b_metrics}, "output_sha256": digest_a, "outputs_equal": True, "comparison": {"observed_latency_winner": winner, "measured_wall_ns_A": a_metrics["elapsed_ns"], "measured_wall_ns_B": b_metrics["elapsed_ns"], "injected_latency_ms_per_task": delay_ms, "classification": "SYNTHETIC_DELAY_CONTROL" if delay_ms else "LOCAL_STRUCTURAL_PROBE", "human_time_saved": None, "independent_receiver_value": "UNKNOWN", "production_promotion": "HELD"}, "deliverable": a, "nonclaims": ["LOCAL_RUN_NE_DEVICE_RUNTIME", "THREAD_COUNT_NE_AUTONOMOUS_AGENTS", "SOURCE_CHECK_NE_RECEIVER_ACK", "TWO_ARMS_ONE_IMPLEMENTATION_NE_INDEPENDENT_REPLICATION", "SIMULATED_LATENCY_NE_REAL_WORLD_THROUGHPUT", "GIT_PR_NE_PUBLIC_PRODUCT_RELEASE"]}


def exclusive_write(out: Path, obj: dict[str, Any]) -> tuple[Path, Path]:
    if out.exists():
        fail("output exists; no silent overwrite")
    out.mkdir(parents=True, exist_ok=False)
    report = canonical_bytes(obj)
    rp = out / "runset.json"
    with rp.open("xb") as fh:
        fh.write(report)
    receipt = {"schema": "CoCivium.CoRunPlus.Receipt.R0", "work_id": WORK_ID, "runset_sha256": sha(report), "runset_bytes": len(report), "state": "PASS_LOCAL_AB_EXACT_OUTPUT_ONLY", "external_receiver": "UNKNOWN", "human_time": "UNMEASURED", "external_effects": "NONE"}
    rec = out / "receipt.json"
    with rec.open("xb") as fh:
        fh.write(canonical_bytes(receipt))
    return rp, rec


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="CoRun+ R0 bounded A/B prior-graph harness (no external effects)")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--expected-git-blob", default=None)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--simulated-io-ms", type=int, default=0)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        source, provenance = load_source(args.input, args.expected_git_blob)
        result = compare(source, provenance, args.workers, args.simulated_io_ms)
        rp, rec = exclusive_write(args.out, result)
    except (OSError, ValueError) as e:
        print("FAIL_CLOSED: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps({"status": "PASS_LOCAL_AB_EXACT_OUTPUT_ONLY", "source_git_blob": provenance["git_blob_sha1"], "A_wall_ns": result["comparison"]["measured_wall_ns_A"], "B_wall_ns": result["comparison"]["measured_wall_ns_B"], "classification": result["comparison"]["classification"], "report": str(rp), "receipt": str(rec)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
