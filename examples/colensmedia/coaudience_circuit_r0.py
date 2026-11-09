#!/usr/bin/env python3
"""Public-safe CoNav audience/circuit lens over an existing pinned retro manifest.

Symbolic flow, NOT a physical or executable circuit, ontology, provider effect,
receiver adoption, media reproduction, or authenticated G_dSide instruction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from conav_retro_r0 import read_manifest, git_blob

POLICY_SCHEMA = "CoAll.CoRepresentationAudience.R0"
MEDIA_SCHEMA = "CoAll.CoNavRetroMedia.R0"
AUDIENCE = re.compile(r"[a-z][a-z0-9_]{1,40}\Z")
SAFE = re.compile(r"[A-Za-z0-9 +,./:()_-]{1,140}\Z")
ALLOWED_SUBSTRATES = {
    "CIRCUIT", "NESTED_MAP", "TEMPORAL", "ORB_STATUS", "ACCESSIBLE_TEXT",
    "RICH_MEDIA", "OUTREACH",
}
LENSES = ("SUPPLY", "DEMAND", "G_DSIDE")
NONCLAIMS = (
    "CIRCUIT_NOT_EXECUTABLE", "PROJECTION_NOT_SEMANTIC_EQUIVALENCE",
    "G_DSIDE_NOT_AUTHORITY", "PINNED_MANIFEST_NOT_MEDIA_RIGHTS",
    "SOURCE_LANDED_NOT_RECEIVER_PICKED_UP", "DRAFT_EVOLUTION_NOT_SEND",
    "RETRO_CANDIDATE_NOT_ADOPTED_SEED", "NO_X2_OR_CROSS_SESSION_SYNC",
)


def _token(value, *, name):
    if not isinstance(value, str) or not SAFE.fullmatch(value):
        raise ValueError("INVALID_" + name)
    return value


def _audience_id(value):
    if not isinstance(value, str) or not AUDIENCE.fullmatch(value):
        raise ValueError("INVALID_AUDIENCE_ID")
    return value


def validate(policy, manifest):
    expected_keys = {"schema", "work_id", "source_manifest_path", "source_git_blob",
                     "effect_authority", "g_dside_authority", "lenses",
                     "audiences", "substrates"}
    if not isinstance(policy, dict) or policy.get("schema") != POLICY_SCHEMA or set(policy) != expected_keys:
        raise ValueError("INVALID_AUDIENCE_POLICY")
    if not isinstance(manifest, dict) or manifest.get("schema") != MEDIA_SCHEMA:
        raise ValueError("INVALID_RETRO_MANIFEST")
    if policy.get("source_manifest_path") != "examples/colensmedia/conav_retro_manifest_r0.json":
        raise ValueError("WRONG_SOURCE_GRAPH")
    if not isinstance(policy.get("source_git_blob"), str) or not re.fullmatch(r"[0-9a-f]{40}", policy["source_git_blob"]):
        raise ValueError("MISSING_SOURCE_PIN")
    if policy.get("g_dside_authority") != "NONE_SYMBOLIC_HYPOTHESIS":
        raise ValueError("G_DSIDE_CANNOT_GRANT_AUTHORITY")
    if policy.get("lenses") != list(LENSES):
        raise ValueError("LOSS_OF_SUPPLY_DEMAND_FUTURES_BRAID")
    if policy.get("effect_authority") != "NONE":
        raise ValueError("UNAUTHORIZED_SUBSTRATE_EFFECTS")
    items = manifest.get("candidates")
    if not isinstance(items, list) or not 1 <= len(items) <= 40:
        raise ValueError("UNBOUNDED_RETRO_INVENTORY")
    ids = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or item["id"] in ids:
            raise ValueError("INVALID_OR_DUPLICATED_CANDIDATE")
        ids.add(item["id"])
        if (item.get("visibility") != "PUBLIC_REPO_SOURCE"
            or item.get("rights_state") != "METADATA_LINK_ONLY"
            or item.get("status") != "RETRO_INSPIRATION_CANDIDATE_UNREVIEWED"):
            raise ValueError("UNAUTHORIZED_RETRO_PROMOTION")
        _token(item.get("label"), name="CANDIDATE_LABEL")
    audiences = policy.get("audiences")
    substrates = policy.get("substrates")
    if not isinstance(audiences, list) or not 3 <= len(audiences) <= 20:
        raise ValueError("NO_BOUNDED_AUDIENCES")
    if not isinstance(substrates, list) or len(substrates) != len(ALLOWED_SUBSTRATES):
        raise ValueError("SUBSTRATE_COVERAGE_MISSING")
    seen = set()
    for a in audiences:
        if not isinstance(a, dict) or set(a) != {"id", "need", "supply", "future_hypothesis", "falsifier"}:
            raise ValueError("BAD_AUDIENCE_RECORD")
        key = _audience_id(a["id"])
        if key in seen:
            raise ValueError("DUPLICATE_AUDIENCE")
        seen.add(key)
        for attr in ("need", "supply", "future_hypothesis", "falsifier"):
            _token(a[attr], name="AUDIENCE_" + attr.upper())
    seen_substrates = set()
    for s in substrates:
        if not isinstance(s, dict) or set(s) != {"id", "audience_ids", "preserves", "losses", "effect_ceiling"}:
            raise ValueError("BAD_SUBSTRATE_RECORD")
        key = s["id"]
        if key not in ALLOWED_SUBSTRATES or key in seen_substrates:
            raise ValueError("UNKNOWN_OR_DUPLICATE_SUBSTRATE")
        seen_substrates.add(key)
        for name in ("preserves", "losses"):
            if not isinstance(s[name], list) or not s[name] or len(s[name]) > 8:
                raise ValueError("MISSING_PROJECTION_LOSS_CONTRACT")
            for value in s[name]:
                _token(value, name="PROJECTION_" + name.upper())
        if (not isinstance(s["audience_ids"], list) or not s["audience_ids"]
            or any(x not in seen for x in s["audience_ids"])):
            raise ValueError("UNBOUND_SUBSTRATE_AUDIENCE")
        if s["effect_ceiling"] != "PROPOSE_ONLY_NO_EXTERNAL_EFFECT":
            raise ValueError("SUBSTRATE_UNAUTHORIZED_ACTION")
    if seen_substrates != ALLOWED_SUBSTRATES:
        raise ValueError("SUBSTRATE_COVERAGE_MISSING")
    return True


def render(policy, manifest, raw_source):
    validate(policy, manifest)
    actual = git_blob(raw_source)
    if actual != policy["source_git_blob"]:
        raise ValueError("HOLD_PINNED_SOURCE_CHANGED")
    source_ids = [c["id"] for c in manifest["candidates"]]
    # A circuit-inspired *notation*: each source is a symbolic input. A zero
    # rights/review/receiver input holds downstream promotion. No hardware or
    # executable authorization semantics are conferred by this drawing.
    projection = hashlib.sha256(json.dumps({"policy": policy, "source": actual},
                        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    lines = [
        "# CoNav+ Circuit Lens and Audience Braid R0", "",
        "**PUBLIC SOURCE-ONLY RESEARCH PROJECTION. No physical circuit, auto-send, or receiver ACK.**", "",
        "Source manifest Git blob: `" + actual + "`", "Projection SHA-256: `" + projection + "`", "",
        "## Symbolic signal-flow diagram", "",
        "```mermaid", "flowchart LR",
        '  S["Existing CoNav retro manifest"]',
        '  RIGHTS{"Rights / consent checked?"}',
        '  REVIEW{"Semantic review accepted?"}',
        '  AUD["Audience + demand/supply/future braid"]',
        '  VIEW["Candidate circuit / map / orb / media view"]',
        '  RECEIVER{"Independent receiver readback?"}',
        '  HOLD["HOLD: links only; no effect or adoption"]',
        '  S --> RIGHTS',
        '  RIGHTS -->|UNVERIFIED| HOLD',
        '  RIGHTS -.->|future reviewed candidate| REVIEW',
        '  REVIEW -->|UNREVIEWED| HOLD',
        '  REVIEW -.->|future authorized review| AUD',
        '  AUD --> VIEW',
        '  VIEW --> RECEIVER',
        '  RECEIVER -->|NOT OBSERVED| HOLD',
        "```", "",
        "The dotted edges are **possible future transitions**, not permissions, completed effects, physical signal wires, or verified causal laws.", "",
        "## Audience demand, available supply and candidate futures", "",
        "| Audience | Demand / need | Available source or capability | G_dSide candidate benefit | Falsifier |",
        "| --- | --- | --- | --- | --- |",
    ]
    for a in policy["audiences"]:
        lines.append("| " + " | ".join(a[x] for x in ("id", "need", "supply", "future_hypothesis", "falsifier")) + " |")
    lines.extend(["", "## Substrate receivers and declared representation losses", "",
        "| Projection substrate | Audience IDs | Preserves | Loses or cannot establish | Effect ceiling |",
        "| --- | --- | --- | --- | --- |"])
    for s in policy["substrates"]:
        lines.append("| " + " | ".join((s["id"], ", ".join(s["audience_ids"]),
                       "; ".join(s["preserves"]), "; ".join(s["losses"]), s["effect_ceiling"])) + " |")
    lines.extend(["", "## Retro inputs and present gate truth table", "",
        "| Candidate ID | Pinned metadata source | Rights reviewed | Meaning reviewed | Receiver readback | Promotion |",
        "| --- | --- | --- | --- | --- | --- |"])
    for c in manifest["candidates"]:
        lines.append("| `" + c["id"] + "` | `" + c["git_blob"] + "` | NO | NO | NO | HOLD |")
    lines.extend(["", "## CoBraid evaluation and falsifiers", "",
        "Supply means available declared source capabilities. Demand means receiver needs, not assumed clicks or purchasing power.",
        "G_dSide means plural, revisable hypotheses about agency, fairness, ecology, wellbeing, optionality and non-participants.",
        "These are **separate perspectives**, not summed into a magic number or a divine instruction. Keep counterexamples and cases where this lens loses to a simpler baseline.",
        "The same WorkID and source pins may yield multiple diagrams, circuit metaphors, text, CoOrb or CoMail proposals; any change to claimed effects requires separate authority and independent readproof.", "",
        "## Custody and nonclaims", "",
        "- These five inputs are public *metadata pointers* selected previously. No source images, audio, video or private draft contents are copied here.",
        "- The source manifest is Git-blob pinned. It does not prove that each separately named media file remains current or license-cleared.",
        "- Source-only render cannot certify an electrical implementation, total retro corpus ingestion, X2 deployment, CI acceptance or cross-provider synchronization.",
    ])
    lines += ["- `" + s + "`" for s in NONCLAIMS]
    lines.append("")
    return "\n".join(lines), {"source_ids": source_ids, "projection_sha256": projection,
             "promoted": 0, "sent": 0, "receiver_acks": 0,
             "meta_candidates": len(source_ids), "source_git_blob": actual,
             "nonclaims": list(NONCLAIMS)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--diagram", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = read_manifest(args.manifest)
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    output, report = render(policy, manifest, args.manifest.read_bytes())
    if args.check:
        if not args.diagram.is_file() or args.diagram.read_text(encoding="utf-8") != output:
            raise SystemExit("HOLD_STALE_CIRCUIT_VIEW")
    else:
        args.diagram.parent.mkdir(parents=True, exist_ok=True)
        with args.diagram.open("x", encoding="utf-8") as fp:
            fp.write(output)
    print(json.dumps({"result": "EXACT_SOURCE_ONLY_PROJECTION", "candidates": report["meta_candidates"],
                      "external_effects": 0, "promotions": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
