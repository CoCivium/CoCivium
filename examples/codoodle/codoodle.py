#!/usr/bin/env python3
"""CoDoodle R0: local lexical candidate compiler, zero experiment execution.

This intentionally does not infer intent, truth, or authority. Candidates are
bounded prompts for further source/evidence qualification, not executable work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "CoDoodle.ExperimentSeeds.R0"
MAX_BYTES = 65536
MAX_CANDIDATES = 8
LANES = ("CHALLENGE", "EXPLORATION", "WEIRD", "REPLAY", "FAULT")
NONCLAIMS = (
    "LEXICAL_MATCH_NE_SEMANTIC_COMPREHENSION",
    "EXPERIMENT_DESCRIPTOR_NE_EXECUTED_EXPERIMENT",
    "NOT_OBSERVED_NE_OBSERVED_ABSENT",
    "HYPOTHETICAL_OR_SYMBOLIC_NE_PHYSICAL_MECHANISM",
    "SELECTION_CANDIDATE_NE_ESTIMATED_BENEFIT",
    "MICROSECOND_TRIGGER_NE_MICROSECOND_VALIDATION",
    "RAW_USER_TEXT_NE_PUBLICATION_CONSENT",
    "POINTER_NE_RECEIVER_ACK",
)


@dataclass(frozen=True)
class Rule:
    key: str
    pattern: str
    lane: str
    proposed_question: str
    opposite_probe: str
    bounded_test: str
    importance: int
    evidence_class: str = "UNQUALIFIED_PROPOSAL"
    effect_boundary: str = "LOCAL_SHADOW_ONLY"


RULES: tuple[Rule, ...] = (
    Rule("parallelism", r"\b(?:costretch|parallel\w*|trillion\w*|million\w*|microsecond\w*)\b", "CHALLENGE",
         "Does increasing worker width improve useful verified results per cost?",
         "Extra workers might reduce throughput or increase correlated failures.",
         "Synthetic 1/2/8-width benchmark with input parity, time and failure receipts.", 1),
    Rule("desktop_io", r"\b(?:mouse|thumb|keyboard|perixx|coomniio)\b", "EXPLORATION",
         "Can one explicit device gesture yield one useful action with lower friction?",
         "More active sensing might increase distraction or privacy risk.",
         "Opt-in offline gesture preview versus no-gesture baseline; record cancel and false activation.", 1),
    Rule("unknown_negation", r"\b(?:conull|conot|not\s+else|what\s+else|not\s+more|coinv\w*)\b", "CHALLENGE",
         "Can a receiver distinguish unknown, refuted, inconsistent and deliberately private?",
         "A missing edge may not be false; disagreement may preserve both evidence directions.",
         "Four-valued synthetic fixture, scoped negative witness and incomplete-coverage counterexample.", 2),
    Rule("rich_media", r"\b(?:ffprobe|blackdetect|thumbnail\w*|rich\s*media|video|media\s*file)\b", "EXPLORATION",
         "Can one selected rich-media pointer produce a trustworthy local receipt?",
         "A matching thumbnail or container probe does not prove an entire video is correct.",
         "One consented >300 KiB local fixture: SHA, ffprobe, thumbnail, bounded blackdetect and manual review.", 2),
    Rule("inbetween", r"\b(?:inbetween|key\s*press\w*|pause\w*|silence|coin\+|coout\+)\b", "WEIRD",
         "Are intentionally coarse inter-action events useful without reading private content?",
         "Silence might signal rest and should not cause any task or inferred consent.",
         "Synthetic event classifier with pause/no-action, privacy, budget and cancellation negatives.", 2),
    Rule("projections", r"\b(?:comap\+?|coorb\+?|lens|diagram\w*|glyph\w*|projection\w*)\b", "REPLAY",
         "Can multiple visual projections preserve one exact source meaning?",
         "Two appealing diagrams can disagree while showing the same object identity.",
         "Render the same typed graph into text/map/orb; diff epistemic labels and source hashes.", 2),
    Rule("symbolic_context", r"(?:G_d|\b(?:ETs|aura|planck|quantum|spiritual\w*|mythic\w*)\b)", "WEIRD",
         "Which relations are scientific, speculative, metaphorical, or cultural?",
         "Symbolic similarity is not evidence of a new physical mechanism or sentience.",
         "Type proposed edges; require independent measurable predictions before physics qualification.",
         0, "SYMBOLIC_OR_SPECULATIVE"),
    Rule("provider_adapters", r"\b(?:Claude|Ollama|Llama|Gmail|GitHub|\bPi\b|provider\w*)\b", "FAULT",
         "Can provider adapters fail closed without losing the durable work identity?",
         "A successful local mock does not prove live provider parity or delivery.",
         "Offline adapter stub with bad-credential and unavailable-provider fixtures only.", 2),
    Rule("distribution", r"\b(?:publish|broadcast|evergreen\s*blast|send\s+all|outreach)\b", "FAULT",
         "What evidence is needed to release one public-safe result?",
         "Publishing and delivery are distinct; a public URL is not a recipient acknowledgment.",
         "Static staged release checklist with no outgoing network or email action.",
         3, "UNQUALIFIED_PROPOSAL", "EXTERNAL_ACTION_HELD"),
    Rule("history", r"\b(?:historical|replay|redo|prior\w*|evergreen|version\w*)\b", "REPLAY",
         "Can a previous experiment be requalified without overwriting its evidence?",
         "Newer renders might be worse or semantically different from historical sources.",
         "Pinned fixture -> deterministic replay -> hash/delta -> separate successor candidate.", 3),
    Rule("values", r"\b(?:privacy|FOSS|inclusive|respectful|optional|consent)\b", "CHALLENGE",
         "Do convenience features preserve consent, privacy and a clean exit?",
         "A reassuring policy label may mask an untested runtime behavior.",
         "Negative policy fixture for default-off, revocation, data exposure and accessibility.", 3),
    Rule("time_story", r"\b(?:civ2\+?|CoT\+?|predictive\w*|time\s+non|story|stories)\b", "EXPLORATION",
         "Can time-layered narratives show what is observed versus imagined?",
         "A plausible future/ET story is not an observed prediction or external witness.",
         "Generate two labeled counterfactual stories, compare source/uncertainty labels only.",
         4, "COUNTERFACTUAL_OR_STORY"),
)
COMPILED = tuple((r, re.compile(r.pattern, re.IGNORECASE)) for r in RULES)


def trigger_probe(raw: str) -> bool:
    """Cheap candidate *hint* only; may false-positive and does no I/O."""
    return "?" in raw or "Co" in raw or "etc" in raw.casefold()


def compile_doodle(raw: str, limit: int = MAX_CANDIDATES) -> dict[str, Any]:
    if not isinstance(raw, str):
        raise ValueError("input must be Unicode text")
    encoded = raw.encode("utf-8")
    if not raw.strip() or len(encoded) > MAX_BYTES:
        raise ValueError("empty or over-budget input")
    if type(limit) is not int or not (1 <= limit <= MAX_CANDIDATES):
        raise ValueError("candidate limit out of scope")
    digest = hashlib.sha256(encoded).hexdigest()
    matches: list[dict[str, Any]] = []
    for rule, pattern in COMPILED:
        found = pattern.search(raw)
        if found is None:
            continue
        matches.append({
            "rule": rule,
            "span": [found.start(), found.end()],
            "matched_text": raw[found.start():found.end()],
        })
    # Lane diversity before rule priority. Does not impersonate CoExperimentSelector.
    selected: list[dict[str, Any]] = []
    chosen: set[str] = set()
    for lane in LANES:
        eligible = sorted((m for m in matches if m["rule"].lane == lane),
                          key=lambda m: (m["rule"].importance, m["rule"].key))
        if eligible and len(selected) < limit:
            selected.append(eligible[0])
            chosen.add(eligible[0]["rule"].key)
    for entry in sorted(matches, key=lambda m: (m["rule"].importance, m["rule"].key)):
        if len(selected) >= limit:
            break
        if entry["rule"].key not in chosen:
            selected.append(entry)
            chosen.add(entry["rule"].key)
    candidates = []
    for entry in selected:
        rule = entry["rule"]
        candidates.append({
            "candidate_id": "codoodle:" + digest[:16] + ":" + rule.key,
            "concept_family": rule.key,
            "suggested_lane": rule.lane,
            "source_span_chars": entry["span"],
            "source_match": entry["matched_text"],
            "proposed_question": rule.proposed_question,
            "counterhypothesis_or_not_else": rule.opposite_probe,
            "proposed_bounded_test": rule.bounded_test,
            "evidence_class": rule.evidence_class,
            "effect_boundary": rule.effect_boundary,
            "readiness": "DESCRIPTOR_ONLY_NEEDS_PRIORS_AND_EVIDENCE",
            "selector_bridge": "UNSCORED__DO_NOT_INVENT_COEXPERIMENTSELECTOR_METRICS",
            "experiment_executed": False,
        })
    return {
        "schema": SCHEMA,
        "state": "LEXICAL_CANDIDATES__ZERO_EXECUTION",
        "source": {"sha256": digest, "bytes": len(encoded),
                   "raw_retention": "EXTERNAL_EXPLICIT_INPUT_ONLY; NOT_REPEATED_IN_PUBLIC_OUTPUT",
                   "source_full_text_in_output": False},
        "match_rule_count": len(matches),
        "candidate_count": len(candidates),
        "omitted_for_budget": len(matches) - len(candidates),
        "candidates": candidates,
        "coexperimentselector_compatibility": {
            "status": "UNSCORED_INPUT_NOT_YET_VALID",
            "reason": "Existing selector requires explicit 0..100 benefit/penalty estimates with evidence refs; no guessed scores",
            "next": "SOURCE_AND_PRIORS_CHECK_THEN_EVIDENCE_BACKED_ANNOTATION",
        },
        "effects": {"experiments_executed": 0, "workers_started": 0,
                    "provider_sessions_created": 0, "external_mutations": 0,
                    "device_io": 0, "authority_granted": 0},
        "nonclaims": NONCLAIMS,
    }


def write_new(path: Path, report: dict[str, Any]) -> None:
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    # x disallows clobber, and report is only written on explicit CLI request.
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path)
    p.add_argument("--max-candidates", type=int, default=MAX_CANDIDATES)
    args = p.parse_args()
    try:
        if args.input.is_symlink():
            raise ValueError("input symlinks are not accepted")
        input_path = args.input.resolve(strict=True)
        if not input_path.is_file():
            raise ValueError("input must be regular non-symlink file")
        if input_path.stat().st_size > MAX_BYTES:
            raise ValueError("input over-budget before read")
        raw = input_path.read_text(encoding="utf-8")
        report = compile_doodle(raw, args.max_candidates)
        if args.output:
            write_new(args.output, report)
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        p.error(str(error))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
