#!/usr/bin/env python3
"""Evidence-typed relational fanout for a CoPreCursor CI-only handoff.

Inputs: two producer files and two receiver files from separate GitHub Actions
jobs. Recompute exact object identity, refuse forged promotion, retain source
dependence, then generate a bounded graph, option set and SHA-256 receipt.

This job does not perform external research, write source, certify any durable
destination, authorize an actor, or claim human first-use acceptance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import zipfile

PIN = "773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101"
READBACK_SCOPE = "ISOLATED_GITHUB_ACTIONS_JOB_NO_REPOSITORY_CHECKOUT"
REQUIRED_NONCLAIMS = (
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
)


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def gitblob(raw):
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\x00" + raw
    ).hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError("HELD_" + reason)


def analyze(bundle, producer, report_raw, receiver, receiver_receipt):
    """Independently verify source, capsule, producer/receiver and browser scope."""
    need(0 < len(bundle) < 2_500_000, "CAPSULE_SIZE")
    need(producer.get("schema") == "CoCivium.CoPreCursor.CapsuleProducerReceipt.R0",
         "PRODUCER_SCHEMA")
    need(sha(bundle) == producer.get("capsule_sha256"), "PRODUCER_CAPSULE_HASH")
    need(producer.get("capsule_bytes") == len(bundle), "PRODUCER_CAPSULE_SIZE")
    need(producer.get("result") == "PACKAGE_CREATED_NOT_LANDED",
         "PRODUCER_COMPLETION_SCOPE")
    need(producer.get("receiver_ack") is False
         and producer.get("coex") is False
         and producer.get("qualified_mvp") is False,
         "FORGED_PRODUCER_PROMOTION")

    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        files = archive.infolist()
        need(len(files) == 2
             and sorted(x.filename for x in files) == ["index.html", "manifest.json"],
             "ZIP_ALLOWLIST")
        need(all(0 < x.file_size < 2_000_000
                 and not x.is_dir() for x in files), "ZIP_BOUNDS")
        manifest = json.loads(archive.read("manifest.json"))
        html = archive.read("index.html")
    need(manifest.get("schema") == "CoCivium.CoPreCursor.SourceHandoffCapsule.R0",
         "CAPSULE_SCHEMA")
    need(manifest.get("source_path") == "examples/coprecursor/index.html",
         "CAPSULE_SOURCE_PATH")
    need(gitblob(html) == PIN == manifest.get("blob_sha1")
         == producer.get("source_blob_sha1"), "PINNED_SOURCE_GITBLOB")
    need(sha(html) == manifest.get("source_sha256")
         == producer.get("source_sha256"), "PINNED_SOURCE_SHA256")
    need(len(html) == manifest.get("source_bytes"), "SOURCE_LENGTH")
    need(manifest.get("user_data_included") is False
         and manifest.get("independent_provider") is False
         and manifest.get("human_receiver") is False
         and manifest.get("durable_custody") is False
         and manifest.get("product_promotion") is False,
         "MANIFEST_FORGED_PROMOTION")

    need(receiver_receipt.get("schema") ==
         "CoCivium.CoPreCursor.ReceiverReadbackReceiptR0", "RECEIVER_RECEIPT_SCHEMA")
    need(receiver_receipt.get("report_sha256") == sha(report_raw),
         "RECEIVER_REPORT_HASH")
    need(receiver_receipt.get("capsule_sha256") == sha(bundle)
         and receiver_receipt.get("source_sha256") == sha(html)
         and receiver_receipt.get("source_blob_sha1") == PIN,
         "RECEIVER_RECEIPT_SOURCE")
    need(receiver_receipt.get("result") == "PASS_ISOLATED_SAME_PROVIDER_JOB_ONLY",
         "RECEIVER_RECEIPT_STATE")
    need(receiver_receipt.get("durable_custody") is False
         and receiver_receipt.get("independent_provider") is False
         and receiver_receipt.get("human_acceptance") is False
         and receiver_receipt.get("mvp_qualified") is False,
         "FORGED_RECEIVER_PROMOTION")

    need(receiver.get("schema") == "CoCivium.CoPreCursor.IsolatedRunnerReadbackR0",
         "RECEIVER_REPORT_SCHEMA")
    need(receiver.get("producer_capsule_sha256") == sha(bundle)
         and receiver.get("source_blob_sha1") == PIN
         and receiver.get("source_sha256") == sha(html)
         and receiver.get("source_bytes") == len(html), "RECEIVER_SOURCE_MISMATCH")
    need(receiver.get("receiver_type") == READBACK_SCOPE
         and receiver.get("receiver_readback") == "EXACT_BUNDLE_AND_SOURCE_BYTES"
         and receiver.get("behavioral_replay") == "PASS_AUTOMATED_SYNTHETIC_TASK",
         "RECEIVER_REPLAY_SCOPE")
    tests = receiver.get("checks")
    need(isinstance(tests, list) and len(tests) >= 21
         and receiver.get("total") == len(tests)
         and receiver.get("passed") == len(tests)
         and all(isinstance(t, dict) and t.get("passed") is True for t in tests),
         "RECEIVER_TESTS_INCOMPLETE")
    required = {
        "PINNED_GIT_BLOB_READBACK",
        "PINNED_SOURCE_SHA256_READBACK",
        "CLEAN_RECEIVER_EXPLICIT_ACCEPT",
        "CLEAN_RECEIVER_EXACT_UNDO",
        "CLEAN_RECEIVER_NO_PRIVATE_LEAK_IN_RECEIPT",
        "CLEAN_RECEIVER_RELOAD_ERASES_DRAFT",
        "NO_EXTERNAL_HTTP_REQUESTS",
        "NO_PAGE_JAVASCRIPT_ERRORS",
    }
    need(required.issubset({x.get("name") for x in tests}),
         "MISSING_CRITICAL_RECEIVER_CHECK")
    need(receiver.get("cross_provider") is False
         and receiver.get("durable_destination") is False
         and receiver.get("human_acceptance") == "NOT_TESTED"
         and receiver.get("coprecursor_user_data_restored") is False
         and receiver.get("operational_receiver") is False
         and receiver.get("qualified_mvp") is False
         and receiver.get("no_external_effects") is True,
         "FORGED_RECEIVER_REPORT_PROMOTION")

    hsource, hcapsule, hreport = sha(html), sha(bundle), sha(report_raw)
    nodes = [
        {"id": "source:" + PIN, "kind": "IMMUTABLE_SOURCE",
         "source_sha256": hsource, "verified_state": "VERIFIED_LOCAL",
         "owner": None, "recipient": None,
         "independent_custody": False},
        {"id": "capsule:" + hcapsule, "kind": "EPHEMERAL_TRANSPORT_CAPSULE",
         "content_sha256": hcapsule, "verified_state": "VERIFIED_LOCAL",
         "owner": "GITHUB_ACTIONS_PRODUCER_JOB", "recipient": "GITHUB_ACTIONS_RECEIVER_JOB",
         "independent_custody": False},
        {"id": "producer_receipt:" + sha(canonical(producer)),
         "kind": "PRODUCER_STATEMENT",
         "content_sha256": sha(canonical(producer)),
         "verified_state": "VERIFIED_LOCAL", "owner": "GITHUB_ACTIONS_PRODUCER_JOB"},
        {"id": "receiver_report:" + hreport, "kind": "RECEIVER_BEHAVIOR_REPORT",
         "content_sha256": hreport, "verified_state": "VERIFIED_LOCAL",
         "owner": "GITHUB_ACTIONS_RECEIVER_JOB",
         "independent_human_witness": False},
        {"id": "synthetic_task:" + hreport, "kind": "AUTOMATED_FIRST_USE_TASK",
         "test_cases": len(tests), "verified_state": "AUTOMATED_CI_ONLY",
         "receiver_acceptance": False},
    ]
    src, cap, producer_id, recv, task = (x["id"] for x in nodes)
    relations = [
        {"from": src, "type": "PACKAGED_AS", "to": cap,
         "proof": "exact Git-blob and SHA-256 bytes in manifest"},
        {"from": producer_id, "type": "ATTESTS_HASH_OF", "to": cap,
         "proof": "producer receipt SHA-256 recomputed"},
        {"from": cap, "type": "READ_BACK_BY", "to": recv,
         "proof": "receiver recomputed capsule, source and report hashes"},
        {"from": recv, "type": "REPLAYED_AS", "to": task,
         "proof": "synthetic browser check report"},
        {"from": producer_id, "type": "SHARES_PROVIDER_WITH", "to": recv,
         "proof": "both jobs are GitHub Actions, not independent providers"},
        {"from": task, "type": "DEPENDS_ON", "to": src,
         "proof": "same pinned offline HTML; not independent source evidence"},
    ]
    missing = [
        {"relation": "LANDED_AT_DURABLE_INDEPENDENT_DESTINATION",
         "status": "UNPROVEN",
         "proof_needed": "independent destination identity, exact bytes, retained receipt"},
        {"relation": "PICKED_UP_BY_ELECTED_OPERATING_RECEIVER",
         "status": "UNPROVEN",
         "proof_needed": "qualified receiver identity and durable exact-object readproof"},
        {"relation": "ACCEPTED_BY_INDEPENDENT_HUMAN",
         "status": "UNPROVEN",
         "proof_needed": "voluntary real task, measured usefulness and recovery"},
        {"relation": "INTEGRATED_AS_OPERATIONAL_MVP",
         "status": "UNPROVEN",
         "proof_needed": "named user, release switch, cold restore and live status"},
    ]
    # Heuristic 1-5 priorities, not data-backed success probabilities.
    option_set = [
        {"option": "INDEPENDENT_HOST_COLD_READBACK",
         "information_gain": 5, "independence_gain": 5,
         "reversibility": 5, "cost": 2, "latency": 3,
         "contamination_risk": 1, "observable": 5,
         "discrimination": 5, "authority": "separately_gated"},
        {"option": "INDEPENDENT_FIRST_USER_OBSERVATION",
         "information_gain": 5, "independence_gain": 5,
         "reversibility": 5, "cost": 3, "latency": 3,
         "contamination_risk": 2, "observable": 5,
         "discrimination": 5, "authority": "voluntary_consent_required"},
        {"option": "CORRUPTED_CAPSULE_FAIL_CLOSED",
         "information_gain": 4, "independence_gain": 1,
         "reversibility": 5, "cost": 1, "latency": 1,
         "contamination_risk": 1, "observable": 5,
         "discrimination": 4, "authority": "CI_only"},
        {"option": "ALTERNATE_BROWSER_REPLAY",
         "information_gain": 3, "independence_gain": 2,
         "reversibility": 5, "cost": 2, "latency": 2,
         "contamination_risk": 1, "observable": 4,
         "discrimination": 3, "authority": "CI_only"},
        {"option": "PERSISTENCE_CONTRACT_HUMAN_TASK_REVIEW",
         "information_gain": 4, "independence_gain": 3,
         "reversibility": 5, "cost": 3, "latency": 3,
         "contamination_risk": 2, "observable": 4,
         "discrimination": 5, "authority": "consent_and_rollback_required"},
    ]
    return {
        "schema": "CoCivium.CoMVP.HandoffRelations.R0",
        "result": "VERIFIED_SAME_PROVIDER_CI_GRAPH_ONLY",
        "coverage": {"bounded_inputs": 4, "source_objects": 1,
                     "evidence_source": "SAME_GITHUB_PROVIDER",
                     "not_full_history": True},
        "objects": nodes,
        "hashes": {"source_git_blob_sha1": PIN,
                   "source_sha256": hsource,
                   "capsule_sha256": hcapsule,
                   "receiver_report_sha256": hreport},
        "duplicates": {"same_source_replays": 2,
                       "independently_sourced_discoveries": 0,
                       "deduplication_key": src},
        "relations": relations,
        "graph_validation": {"pass": True,
                             "dangling_references": 0,
                             "false_independent_origin": 0},
        "missing_relations": missing,
        "content_classes": {
            "SUBSTANTIVE_TEXT_CANDIDATE": 1,
            "SUBSTANTIVE_BINARY_CANDIDATE": 1,
            "IMAGE_EVIDENCE_CANDIDATE": 0,
            "TRANSIENT_CONTROL_FILE": 3,
            "UPLOAD_SIDECAR": 0,
        },
        "semantic_coverage": {"source_semantics": "BOUNDED_BROWSER_TASK_ONLY",
                              "historical_coverage": "NOT_SEMANTICALLY_REVIEWED"},
        "claim_evidence_audit": [
            {"claim": "EXACT_SOURCE_TRANSPORT",
             "evidence": [src, cap, recv], "state": "PASS_CI",
             "independent_provider": False},
            {"claim": "FIRST_TASK_REPLAY",
             "evidence": [src, task], "state": "PASS_SYNTHETIC",
             "independent_human": False},
            {"claim": "DURABLE_CUSTODY",
             "evidence": [], "state": "HELD"},
            {"claim": "MVP_QUALIFIED",
             "evidence": [], "state": "HELD"},
        ],
        "lifecycle_evidence": {
            "exact_bytes_read_back_by_ephemeral_job": True,
            "highest_custody_state": "VERIFIED_LOCAL",
            "LANDED": False, "PICKED_UP_BY_DURABLE_RECEIVER": False,
            "INTEGRATED": False, "COEX": False,
        },
        "eligible_next_transitions": [
            "SEPARATE_DURABLE_RECEIVER_CONTRACT",
            "CONSENTED_INDEPENDENT_FIRST_TASK",
        ],
        "blocked_transitions": [
            "MVP_QUALIFIED", "PRODUCTION_SWITCH", "COEX",
            "INDEPENDENT_PROVIDER_CERTIFICATION",
        ],
        "ux_summary": {
            "front_door": "CoPreCursor Preview / Accept / Undo",
            "state": "UX_ACCEPTANCE_UNPROVEN",
            "human_comprehension": "NOT_MEASURED",
        },
        "option_set": {"scores_are_heuristics": True,
                       "execution_authority": "NONE",
                       "options": option_set},
        "nonclaims": list(REQUIRED_NONCLAIMS) + [
            "CI_JOB_NE_DURABLE_RECEIVER",
            "REPLAY_COUNT_NE_INDEPENDENCE_COUNT",
            "OPTION_GENERATION_NE_EXECUTION",
            "AUTOMATED_BROWSER_NE_HUMAN_ACCEPTANCE",
            "PROTECTED_SOURCE_NE_PRODUCT_MVP",
        ],
    }


def negative_cases(bundle, producer, report_raw, report, receiver_receipt):
    scenarios = []

    def challenge(name, mutant_bundle=None, mutant_producer=None,
                  mutant_report_raw=None, mutant_receiver=None,
                  mutant_receipt=None):
        try:
            analyze(
                bundle if mutant_bundle is None else mutant_bundle,
                producer if mutant_producer is None else mutant_producer,
                report_raw if mutant_report_raw is None else mutant_report_raw,
                report if mutant_receiver is None else mutant_receiver,
                receiver_receipt if mutant_receipt is None else mutant_receipt,
            )
        except (ValueError, zipfile.BadZipFile, KeyError):
            scenarios.append({"scenario": name, "rejected": True})
            return
        raise AssertionError("FORGED_OR_INVALID_EVIDENCE_ACCEPTED: " + name)

    challenge("CAPSULE_CORRUPTION", mutant_bundle=bundle[:-1] + bytes([bundle[-1] ^ 1]))
    changed = copy.deepcopy(producer)
    changed["receiver_ack"] = True
    challenge("FORGED_PRODUCER_ACK", mutant_producer=changed)
    changed = copy.deepcopy(receiver_receipt)
    changed["durable_custody"] = True
    challenge("FORGED_DURABLE_CUSTODY", mutant_receipt=changed)
    changed = copy.deepcopy(receiver_receipt)
    changed["report_sha256"] = "0" * 64
    challenge("RECEIVER_REPORT_HASH_DRIFT", mutant_receipt=changed)
    changed = copy.deepcopy(report)
    changed["human_acceptance"] = "CONFIRMED"
    challenge("FORGED_HUMAN_ACCEPTANCE", mutant_receiver=changed)
    changed = copy.deepcopy(report)
    changed["checks"][0]["passed"] = False
    challenge("SINGLE_FAILED_BROWSER_CHECK", mutant_receiver=changed)
    changed = copy.deepcopy(report)
    changed["cross_provider"] = True
    challenge("FORGED_PROVIDER_INDEPENDENCE", mutant_receiver=changed)
    return scenarios


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--capsule", type=Path, required=True)
    ap.add_argument("--producer-receipt", type=Path, required=True)
    ap.add_argument("--receiver-report", type=Path, required=True)
    ap.add_argument("--receiver-receipt", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    try:
        bundle = args.capsule.read_bytes()
        producer = json.loads(args.producer_receipt.read_text())
        report_raw = args.receiver_report.read_bytes()
        report = json.loads(report_raw)
        receipt = json.loads(args.receiver_receipt.read_text())
        result = analyze(bundle, producer, report_raw, report, receipt)
        negatives = negative_cases(bundle, producer, report_raw, report, receipt)
        result["negative_controls"] = negatives
        result["all_negative_controls_rejected"] = all(x["rejected"] for x in negatives)
        need(len(negatives) == 7 and result["all_negative_controls_rejected"],
             "NEGATIVE_CONTROLS")
        # One output folder is owned by this invocation. Never clobber a receipt.
        args.out.mkdir(parents=True, exist_ok=False)
        raw = canonical(result)
        with (args.out / "relations.json").open("xb") as f:
            f.write(raw)
        out_receipt = {
            "schema": "CoCivium.CoMVP.RelationAuditReceipt.R0",
            "result": "PASS_SAME_PROVIDER_RELATIONS_ONLY",
            "report_sha256": sha(raw),
            "report_bytes": len(raw),
            "source_blob_sha1": PIN,
            "mvp_qualified": False, "durable_custody": False,
            "independent_source_validation": False,
        }
        with (args.out / "receipt.json").open("xb") as f:
            f.write(canonical(out_receipt))
    except (OSError, ValueError, AssertionError, zipfile.BadZipFile, KeyError) as exc:
        print("HOLD_OR_FAIL_CLOSED:", exc)
        return 2
    print(json.dumps({"result": out_receipt["result"],
                      "relations": len(result["relations"]),
                      "negative_controls": len(negatives),
                      "mvp_qualified": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
