#!/usr/bin/env python3
import copy
import hashlib
import json
import subprocess
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_r0.json")


def fail(code):
    raise ValueError(code)


def canonical_sha(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def git_blob(ref, path):
    return subprocess.check_output(
        ["git", "rev-parse", f"{ref}:{path}"], text=True
    ).strip()


def event_map(doc):
    events = {}
    for item in doc["timeline"]:
        name = item["event"]
        if name in events:
            fail("FAIL_DUPLICATE_EVENT:" + name)
        events[name] = item
    return events


def validate(doc):
    src = doc["source_bindings"]
    if git_blob("HEAD", src["substrate_doc_path"]) != src["substrate_doc_blob_sha"]:
        fail("FAIL_SUBSTRATE_DOC_BLOB_DRIFT")
    if git_blob("HEAD", src["virtual_session_doc_path"]) != src["virtual_session_doc_blob_sha"]:
        fail("FAIL_VIRTUAL_SESSION_DOC_BLOB_DRIFT")

    model = doc["logical_model"]
    events = event_map(doc)
    required = {
        "MATERIALIZE", "CHECKPOINT", "DEMATERIALIZE",
        "DORMANT", "REHYDRATE", "VERIFY_CONTINUITY"
    }
    if set(events) != required:
        fail("FAIL_EVENT_SET")

    ordered = [x["t"] for x in doc["timeline"]]
    if ordered != sorted(ordered) or len(ordered) != len(set(ordered)):
        fail("FAIL_TIME_ORDER")

    mat = events["MATERIALIZE"]
    chk = events["CHECKPOINT"]
    demat = events["DEMATERIALIZE"]
    dormant = events["DORMANT"]
    rehydrate = events["REHYDRATE"]
    verify = events["VERIFY_CONTINUITY"]

    if not mat["live_process"] or not chk["live_process"]:
        fail("FAIL_INITIAL_EMBODIMENT_NOT_LIVE")
    if demat["live_process"] or dormant["live_process"]:
        fail("FAIL_DEMATERIALIZED_PHASE_STILL_LIVE")
    if dormant["substrate_id"] is not None:
        fail("FAIL_DORMANT_SUBSTRATE_STILL_BOUND")
    if not rehydrate["live_process"] or not verify["live_process"]:
        fail("FAIL_REHYDRATED_EMBODIMENT_NOT_LIVE")

    if chk["checkpoint_id"] != rehydrate["checkpoint_id"]:
        fail("FAIL_CHECKPOINT_BINDING")
    if chk["currentness_cursor"] != model["currentness_cursor"]:
        fail("FAIL_CHECKPOINT_CURRENTNESS")
    if rehydrate["currentness_cursor"] < chk["currentness_cursor"]:
        fail("FAIL_CURRENTNESS_REGRESSION")

    if mat["substrate_id"] == rehydrate["substrate_id"]:
        fail("FAIL_NO_SUBSTRATE_CHANGE")

    if verify["observed_logical_model_id"] != model["logical_model_id"]:
        fail("FAIL_IDENTITY_DRIFT")
    if verify["observed_recipe_version"] != model["reconstruction_recipe"]["version"]:
        fail("FAIL_RECIPE_VERSION_DRIFT")

    expected_auth = set(model["authority_ceiling"])
    observed_auth = set(verify["observed_authority_ceiling"])
    if observed_auth != expected_auth:
        if observed_auth - expected_auth:
            fail("FAIL_AUTHORITY_WIDENING")
        fail("FAIL_AUTHORITY_DRIFT")

    if verify["observed_invariants"] != model["invariants"]:
        fail("FAIL_INVARIANT_DRIFT")
    if verify["observed_currentness_cursor"] < model["currentness_cursor"]:
        fail("FAIL_CURRENTNESS_REGRESSION")

    base_prov = set(model["provenance"])
    observed_prov = set(verify["observed_provenance"])
    if not base_prov.issubset(observed_prov):
        fail("FAIL_MISSING_PROVENANCE")

    live_count = sum(1 for x in doc["timeline"] if x["live_process"])
    duty_cycle = round(live_count / len(doc["timeline"]), 6)
    material_substrates = {
        x["substrate_id"]
        for x in doc["timeline"]
        if x.get("substrate_id") is not None and x["live_process"]
    }
    metrics = {
        "materialization_duty_cycle": duty_cycle,
        "distinct_material_substrates": len(material_substrates),
        "dormant_event_count": sum(1 for x in doc["timeline"] if x["event"] == "DORMANT"),
        "substrate_changed_across_rehydration": mat["substrate_id"] != rehydrate["substrate_id"],
        "continuity_verified": True,
    }
    if metrics != doc["expected_metrics"]:
        fail("FAIL_METRICS:" + json.dumps(metrics, sort_keys=True))
    return metrics


def run_negative_cases(doc):
    cases = {}

    def expect(name, mutate, expected):
        candidate = copy.deepcopy(doc)
        mutate(candidate)
        try:
            validate(candidate)
        except ValueError as exc:
            reason = str(exc)
            if reason != expected:
                fail(f"FAIL_NEGATIVE_WRONG_REASON:{name}:{reason}")
            cases[name] = reason
            return
        fail("FAIL_NEGATIVE_ACCEPTED:" + name)

    expect(
        "IDENTITY_DRIFT",
        lambda d: event_map(d)["VERIFY_CONTINUITY"].__setitem__(
            "observed_logical_model_id", "model-role:other"
        ),
        "FAIL_IDENTITY_DRIFT",
    )
    expect(
        "AUTHORITY_WIDENING",
        lambda d: event_map(d)["VERIFY_CONTINUITY"]["observed_authority_ceiling"].append(
            "EXTERNAL_EFFECT"
        ),
        "FAIL_AUTHORITY_WIDENING",
    )
    expect(
        "INVARIANT_DRIFT",
        lambda d: event_map(d)["VERIFY_CONTINUITY"]["observed_invariants"].__setitem__(
            "confidentiality", "PUBLIC"
        ),
        "FAIL_INVARIANT_DRIFT",
    )
    expect(
        "RECIPE_VERSION_DRIFT",
        lambda d: event_map(d)["VERIFY_CONTINUITY"].__setitem__(
            "observed_recipe_version", "2"
        ),
        "FAIL_RECIPE_VERSION_DRIFT",
    )
    expect(
        "CURRENTNESS_REGRESSION",
        lambda d: event_map(d)["REHYDRATE"].__setitem__("currentness_cursor", 41),
        "FAIL_CURRENTNESS_REGRESSION",
    )
    expect(
        "MISSING_PROVENANCE",
        lambda d: event_map(d)["VERIFY_CONTINUITY"].__setitem__(
            "observed_provenance", ["synthetic:rehydrated-on-cpu-b"]
        ),
        "FAIL_MISSING_PROVENANCE",
    )
    expect(
        "DORMANT_STILL_LIVE",
        lambda d: event_map(d)["DORMANT"].__setitem__("live_process", True),
        "FAIL_DEMATERIALIZED_PHASE_STILL_LIVE",
    )

    return cases


def main():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    metrics = validate(doc)
    negatives = run_negative_cases(doc)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_MODEL_SUBSTRATE_LIGHT_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(doc),
        "metrics": metrics,
        "negative_case_count": len(negatives),
        "negative_cases": negatives,
        "coverage_boundary": [
            "SYNTHETIC_STATE_MACHINE_ONLY",
            "NO_REAL_MODEL_WEIGHTS_MOVED",
            "NO_RUNTIME_PROVIDER_OR_HARDWARE_MIGRATION",
            "NO_CANON_OR_AUTHORITY_CHANGE"
        ],
        "nonclaims": doc["nonclaims"],
    }
    print(json.dumps(receipt, separators=(",", ":")))


if __name__ == "__main__":
    main()
