#!/usr/bin/env python3
"""Read-only CoDoodle R1 frontier -> source-bound, accessible experiment cards.

No network, OS input, model calls, account calls, provider calls, auto-workers,
secret reads or submission. All actions remain hypothetical and zero-authority.
Requires the existing CoDoodleNexR1.py beside this file at integration time.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import statistics
import sys
import time

SCHEMA = "CoAll.CoDoodleExperimentCardBridge.R0"
FRONTIER_SCHEMA = "CoDoodle.CoNex.CandidateFrontier.R1"
MAX_CARDS = 8
ALLOWED_SCENARIOS = {
    "ENGINEERING_DEVICE": ("ENGINEERING_CANDIDATE", "test_device_baseline"),
    "INTERSTICE_UI": ("ENGINEERING_CANDIDATE", "test_accessible_interval"),
    "ET_TECHNOSIGNATURE": ("EMPIRICAL_HYPOTHESIS", "test_rfi_baseline"),
    "G_D_PHILOSOPHY": ("PHILOSOPHICAL_OR_METAPHORICAL", "test_definition"),
    "SYNTHKIND_FICTION": ("SPECULATIVE_STORY", "test_story_swap"),
}
TEMPLATES = {
    "test_device_baseline": {
        "question": "Does a voluntary mouse preview outperform leaving native controls unchanged?",
        "baseline": "Original middle-click, scrolling and Perixx typing remain untouched.",
        "alternative": "Explicitly summoned, labelled preview of one related task.",
        "falsifier": "An accidental trigger, lost input, focus theft, failure to cancel, or no measured time benefit.",
        "safe_test": "Shadow-compare the native action and one inert local preview; ask a consenting user before native mapping.",
        "receiver": "CONSENTED_X2_USER_AFTER_ROUTE_RESTORED",
    },
    "test_accessible_interval": {
        "question": "Does an opt-in editing gap preview help without distracting or profiling the typist?",
        "baseline": "No pause monitoring or suggestion.",
        "alternative": "A coarse local interval in one elected field may prepare a dismissible hint.",
        "falsifier": "Increased interruptions, IME/dictation breakage, private text exposure, or slower first-use.",
        "safe_test": "Use public synthetic typing in a local demo; compare OFF and opt-in with screen-reader and keyboard controls.",
        "receiver": "CONSENTED_LOCAL_EDITOR_USER",
    },
    "test_rfi_baseline": {
        "question": "Could a hypothetical ET-like signal be explained by terrestrial interference?",
        "baseline": "Instrumental error, RFI and conventional astrophysical models.",
        "alternative": "An anomaly class needing independent observation, not an ET announcement.",
        "falsifier": "Matching local interference or failure to repeat in an independent instrument.",
        "safe_test": "Use a named public synthetic negative-control record; real detection requires measured calibrated data and independent review.",
        "receiver": "QUALIFIED_SCIENTIFIC_REVIEWER_UNBOUND",
    },
    "test_definition": {
        "question": "Is this G_d relation a useful symbol, a formal metric, or a testable distinct hypothesis?",
        "baseline": "Existing graph, information, semantic or observer distance measures.",
        "alternative": "A clearly defined invariant with units, domain and a counterexample search.",
        "falsifier": "Circularity, undefined variables, equivalence to a simpler baseline, or lack of a discriminating prediction.",
        "safe_test": "Compare two synthetic graphs under a published metric definition; leave metaphysical interpretation separate.",
        "receiver": "OPT_IN_THEORY_CHALLENGER_UNBOUND",
    },
    "test_story_swap": {
        "question": "Would a fictional Civ2+ and imagined ET observer understand the same Synthkind design principle?",
        "baseline": "Plain source text read as a proposal, not a constitutional fact.",
        "alternative": "Two attributed fictional narrators tell contrasting, non-empirical stories.",
        "falsifier": "Loss of original premise, hidden authority claim, cultural stereotyping or inaccessible rendering.",
        "safe_test": "Present text-only fictional variants and ask a consenting reader to identify what stayed constant and changed.",
        "receiver": "CONSENTED_STORY_READER_UNBOUND",
    },
}
GLYPHS = {
    "ELSE": ("alternative", "ALT"), "NOT": ("not-a-fact", "NOT"),
    "INVERSE": ("reverse relation", "INV"), "COMPLEMENT": ("outside view", "OUT"),
    "NULL": ("no-change baseline", "NULL"), "OUTSIDE": ("outside scope", "OUT"),
    "COUNTERFACTUAL": ("what-if", "WHATIF"), "FALSIFIER": ("challenge", "CHALLENGE"),
    "ACCESSIBILITY": ("accessible representation", "A11Y"),
    "RANDOM_MUTATION": ("seeded variety", "RANDOM"),
}
RAILS = [
    "DESCRIPTOR_NE_EXPERIMENT", "STORY_NE_OBSERVATION", "INVERSE_NE_TRUE_NEGATION",
    "PROPOSAL_NE_AUTHORITY", "MOUSE_NE_EXECUTE", "ET_HYPOTHESIS_NE_DETECTION",
    "G_D_FRAME_NE_ENTITY", "LOGICAL_FIELD_NE_LIVE_WORKERS", "SOURCE_NE_RECEIVER_ACK",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
]


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def validate_frontier(frontier):
    if not isinstance(frontier, dict) or frontier.get("schema") != FRONTIER_SCHEMA:
        raise ValueError("HELD_FRONTIER_SCHEMA")
    if frontier.get("no_execution") is not True or frontier.get("active_workers") != 0:
        raise ValueError("HELD_RUNTIME_OR_WORKERS")
    selected = frontier.get("selected")
    if (not isinstance(selected, list) or len(selected) > 32 or
            frontier.get("selected_count") != len(selected)):
        raise ValueError("HELD_UNBOUNDED_FRONTIER")
    if not isinstance(frontier.get("source_sha256"), str) or len(frontier["source_sha256"]) != 64:
        raise ValueError("HELD_SOURCE_IDENTITY")
    try:
        int(frontier["source_sha256"], 16)
    except ValueError:
        raise ValueError("HELD_SOURCE_HASH")
    ids = set()
    for row in selected:
        if not isinstance(row, dict):
            raise ValueError("HELD_ROW")
        cid = row.get("candidate_id")
        if not isinstance(cid, str) or len(cid) != 20 or cid in ids:
            raise ValueError("HELD_CANDIDATE_ID_OR_DUPLICATE")
        ids.add(cid)
        if (row.get("authority") != "NONE" or row.get("micro_canary_eligible") not in (True, False)
                or row.get("review_state") not in ("PASS_SHADOW_POLICY_ONLY", "HELD_NO_QUALIFIED_EXECUTOR_OR_EMPIRICAL_EVIDENCE")):
            raise ValueError("HELD_INHERITED_AUTHORITY_OR_REVIEW")
        effects = row.get("effects")
        if not isinstance(effects, dict) or not all(k in effects and type(effects[k]) is int and effects[k] == 0 for k in ("provider_calls", "network", "devices", "emails", "workers")):
            raise ValueError("HELD_EFFECTS")
        axis = row.get("axes")
        if not isinstance(axis, dict) or axis.get("scenario") not in ALLOWED_SCENARIOS:
            raise ValueError("HELD_SCENARIO")
        expected_epistemic, _ = ALLOWED_SCENARIOS[axis["scenario"]]
        if row.get("epistemic_class") != expected_epistemic:
            raise ValueError("HELD_EPISTEMIC_PROMOTION")
        if axis["scenario"] not in ("ENGINEERING_DEVICE", "INTERSTICE_UI") and row.get("review_state") != "HELD_NO_QUALIFIED_EXECUTOR_OR_EMPIRICAL_EVIDENCE":
            raise ValueError("HELD_ET_G_D_STORY_MUST_NOT_PASS")
        if not isinstance(axis.get("operator"), str) or not isinstance(axis.get("surface"), str):
            raise ValueError("HELD_INCOMPLETE_AXIS")
    return selected


def compile_cards(frontier, max_cards=6):
    selected = validate_frontier(frontier)
    if type(max_cards) is not int or not 0 <= max_cards <= MAX_CARDS:
        raise ValueError("HELD_MAX_CARDS_8")
    cards = []
    for row in selected[:max_cards]:
        axis = row["axes"]
        _, template_id = ALLOWED_SCENARIOS[axis["scenario"]]
        template = TEMPLATES[template_id]
        glyph_meaning, ascii_fallback = GLYPHS.get(axis["operator"], ("proposed relation", "PROPOSE"))
        cards.append({
            "card_id": "C" + row["candidate_id"],
            "descriptor_id": row["candidate_id"],
            "source_sha256": frontier["source_sha256"],
            "logical_index": row.get("logical_index"),
            "scenario": axis["scenario"],
            "operator": axis["operator"],
            "observer": axis.get("observer", "UNKNOWN"),
            "temporal_mode": axis.get("temporal", "UNKNOWN"),
            "surface_candidate": axis["surface"],
            "glyph_plain_label": glyph_meaning,
            "glyph_ascii": ascii_fallback,
            "question": template["question"],
            "null_baseline": template["baseline"],
            "alternative": template["alternative"],
            "could_falsify": template["falsifier"],
            "one_safe_next_test": template["safe_test"],
            "intended_receiver": template["receiver"],
            "epistemic_class": row["epistemic_class"],
            "proof_boundary": row.get("proof_boundary", "UNKNOWN"),
            "status": "PROPOSAL_ONLY_NOT_EXECUTED",
            "human_time_benefit_seconds": None,
            "independent_receiver_ack": False,
            "effects": dict(row["effects"]),
            "authority": "NONE",
            "score_not_truth": row.get("score"),
        })
    return {"schema": SCHEMA, "input_frontier_sha256": sha(canonical(frontier)),
            "source_sha256": frontier["source_sha256"], "selected_count": len(cards),
            "candidate_space_size": frontier.get("total_syntactic_descriptors"),
            "cards": cards, "actual_workers": 0, "network_calls": 0,
            "external_effects": 0, "receiver_ack": False, "auto_publish": False,
            "source_text_republished": False, "rails": list(RAILS)}


def load_core():
    path = Path(__file__).with_name("CoDoodleNexR1.py")
    if not path.is_file():
        raise RuntimeError("HELD_R1_CORE_NOT_PRESENT_FOR_INTEGRATION")
    spec = importlib.util.spec_from_file_location("CoDoodleNexR1", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_from_r1(source, seed, limit=6, rounds=101):
    if type(rounds) is not int or not 5 <= rounds <= 501:
        raise ValueError("HELD_BENCHMARK_ROUNDS")
    core = load_core()
    core.validate_fixture(source)
    if type(limit) is not int or not 0 <= limit <= MAX_CARDS:
        raise ValueError("HELD_MAX_CARDS_8")
    times=[]
    compiled=None
    for _ in range(rounds):
        start=time.perf_counter_ns()
        frontier=core.select_candidates(source,seed,limit)
        compiled=compile_cards(frontier,limit)
        times.append(time.perf_counter_ns()-start)
    result={"operation":"select_frontier_then_compile_text_cards", "rounds":rounds,
            "median_ns":int(statistics.median(times)),
            "p95_ns":sorted(times)[int((len(times)-1)*0.95)],
            "not_measuring":["actual_experiment_execution","model_response_time","human_time_saved","native_mouse_latency"],
            "microsecond_target_met_for_full_operation":statistics.median(times)<1000}
    return compiled,result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default=str(Path(__file__).with_name("synthetic_source.json")))
    ap.add_argument("--seed", default="CoNex-R1-cardbridge")
    ap.add_argument("--max-cards", type=int, default=6)
    ap.add_argument("--rounds", type=int, default=101)
    ap.add_argument("--output", required=True)
    args=ap.parse_args(argv)
    core=load_core()
    source=json.loads(Path(args.source).read_text(encoding="utf-8"))
    core.validate_fixture(source)
    cards,bench=run_from_r1(source,args.seed,args.max_cards,args.rounds)
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    for name,payload in (("cards.json",cards),("benchmark.json",bench)):
        path=output/name
        with path.open("xb") as f:
            data=canonical(payload)
            f.write(data);f.flush();os.fsync(f.fileno())
        if path.read_bytes()!=data:
            raise RuntimeError("HELD_READBACK_MISMATCH")
    receipt={"status":"PASS_SHADOW_PROPOSALS_ONLY", "source_sha256":cards["source_sha256"],
             "cards_sha256":sha(canonical(cards)), "bench_sha256":sha(canonical(bench)),
             "cards":cards["selected_count"],"external_effects":0,"workers":0,
             "microsecond_full_operation":bench["microsecond_target_met_for_full_operation"],
             "no_independent_acceptance":True,"nonclaims":RAILS}
    path=output/"receipt.json"
    with path.open("xb") as f:
        data=canonical(receipt);f.write(data);f.flush();os.fsync(f.fileno())
    if path.read_bytes()!=data:
        raise RuntimeError("HELD_RECEIPT_READBACK")
    print(json.dumps({"status":receipt["status"],"cards":receipt["cards"],
                      "median_full_operation_ns":bench["median_ns"],"sha256":receipt["cards_sha256"],
                      "output":str(output),"workers":0,"external_effects":0},sort_keys=True))

if __name__=="__main__":
    main()
