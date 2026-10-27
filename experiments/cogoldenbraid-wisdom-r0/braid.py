#!/usr/bin/env python3
"""Bounded, deterministic CoGoldenBraid *candidate* router, never an authority engine."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGES = ("INTENT", "SOURCE", "MEANING", "DECISION", "BOUNDED_DEED", "RECEIPT", "RECEIVER", "EFFECT", "LEARNING", "SUCCESSOR")
STAGE_ALIASES = {"CHALLENGE": "LEARNING"}
STATUSES = {"PASS", "FAIL", "HOLD", "NOT_RUN"}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load(path=None):
    return json.loads(Path(path or ROOT / "seed.json").read_text(encoding="utf-8"))


def validate(seed):
    if seed.get("schema") != "CoGoldenBraidWisdomSeed/0.1" or seed.get("state") != "PUBLIC_OFFLINE_CANDIDATE_NOT_CANON":
        raise ValueError("BAD_SEED_SCHEMA")
    sources = seed.get("design_sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("NO_SOURCES")
    for src in sources.values():
        if not re.fullmatch(r"[0-9a-f]{40}", src.get("git_blob", "")) or not src.get("path", "").endswith(".md"):
            raise ValueError("BAD_PROVENANCE_POINTER")
    records = seed.get("principles")
    if not isinstance(records, list) or not 1 <= len(records) <= 128:
        raise ValueError("UNBOUNDED_OR_EMPTY_SEED")
    seen, statements = set(), set()
    for p in records:
        if not re.fullmatch(r"W[0-9]{2,4}", p.get("id", "")) or p["id"] in seen:
            raise ValueError("DUPLICATE_OR_BAD_ID")
        seen.add(p["id"])
        statement = p.get("statement", "").strip()
        if len(statement) < 20 or statement.casefold() in statements:
            raise ValueError("EMPTY_OR_DUPLICATE_CLAIM")
        statements.add(statement.casefold())
        for k in ("applies_when", "limitation", "next_test", "domain", "braid_stage"):
            if not isinstance(p.get(k), str) or len(p[k].strip()) < 5:
                raise ValueError("MISSING_CHALLENGE_OR_TEST:" + p["id"])
        if p["design_reference"] not in sources:
            raise ValueError("UNKNOWN_SOURCE")
        if p.get("kind") != "NORMATIVE_HEURISTIC" or p.get("status") != "CANDIDATE_UNVALIDATED":
            raise ValueError("CLAIM_PROMOTED_WITHOUT_RECEIVER")
        if p.get("authority") != "NONE" or p.get("privacy") != "PUBLIC":
            raise ValueError("AUTHORITY_OR_PRIVACY_ESCAPE")
        if STAGE_ALIASES.get(p["braid_stage"], p["braid_stage"]) not in STAGES:
            raise ValueError("INVALID_BRAID_STAGE")
        terms = p.get("match_phrases")
        if not isinstance(terms, list) or not 2 <= len(terms) <= 8 or any(not isinstance(x, str) or len(x) < 3 for x in terms):
            raise ValueError("INVALID_MATCH_PHRASES")
    for edge in seed.get("typed_relations", []):
        if edge.get("from") not in seen or edge.get("to") not in seen or edge.get("from") == edge.get("to"):
            raise ValueError("UNKNOWN_OR_SELF_RELATION")
        if edge.get("kind") not in ("TENSION", "SUPPORT", "GUARD", "DEPENDENCY") or not edge.get("reason"):
            raise ValueError("UNTYPED_RELATION")
    return {"source_count": len(sources), "candidate_count": len(records), "relation_count": len(seed.get("typed_relations", [])), "seed_sha256": digest(seed)}


def phrase_match(phrase, query):
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(phrase.casefold()) + r"(?![a-z0-9])", query.casefold()))


def propose(query, seed=None, limit=2):
    """Return advisory *possibilities*, with abstention for unknown or ambiguous intent."""
    seed = seed or load()
    validate(seed)
    if not isinstance(query, str) or len(query) > 600 or len(query.strip()) < 4:
        raise ValueError("INVALID_LOCAL_QUERY")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 3:
        raise ValueError("RESOURCE_BUDGET")
    ranked = []
    for p in seed["principles"]:
        matches = [phrase for phrase in p["match_phrases"] if phrase_match(phrase, query)]
        if matches:
            ranked.append((len(matches), p["id"], matches))
    ranked.sort(key=lambda z: (-z[0], z[1]))
    if not ranked:
        return {"status": "ABSTAIN_NO_EVIDENCE", "candidates": [], "effect": "NONE", "claim": "NO_SEMANTIC_INFERENCE"}
    high = ranked[0][0]
    status = "AMBIGUOUS_REQUIRES_CHOICE" if sum(item[0] == high for item in ranked) > 1 else "CANDIDATE_FOR_INSPECTION"
    return {"status": status, "candidates": [{"id": p[1], "match_phrases": p[2]} for p in ranked[:limit]], "effect": "NONE", "claim": "LEXICAL_MATCH_ONLY"}


def braid_packet(principle, seed=None):
    seed = seed or load()
    validate(seed)
    p = next((x for x in seed["principles"] if x["id"] == principle), None)
    if p is None:
        raise ValueError("UNKNOWN_WISDOM_ID")
    source = seed["design_sources"][p["design_reference"]]
    result = {"schema": "CoGoldenBraidWisdomPacket/0.1", "id": p["id"],
        "seed_sha256": digest(seed),
        "stages": {
            "INTENT": p["applies_when"],
            "SOURCE": {"repo": source["repo"], "path": source["path"], "git_blob": source["git_blob"], "role": "DESIGN_REFERENCE_NOT_PROOF"},
            "MEANING": p["statement"],
            "DECISION": {"status": "REVIEW_REQUIRED", "exception": p["limitation"]},
            "BOUNDED_DEED": p["next_test"],
            "RECEIPT": "NOT_RUN",
            "RECEIVER": "NONE_VERIFIED",
            "EFFECT": "NOT_OBSERVED",
            "LEARNING": "PENDING_INDEPENDENT_CHALLENGE",
            "SUCCESSOR": "UNQUALIFIED_CANDIDATE"},
        "authority": "NONE", "privacy": "PUBLIC", "execution": "NONE"}
    if tuple(result["stages"]) != STAGES:
        raise AssertionError("BROKEN_BRAID_ORDER")
    return result


if __name__ == "__main__":
    print(json.dumps(validate(load()), indent=2))
