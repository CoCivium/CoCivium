#!/usr/bin/env python3
"""Fail-closed fan-in for bounded CoSites candidate-source WCAG audit receipts.

One repo artifact reader only; no URL fetching, no deployment or human acceptance.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

EXPECTED = {
    "cocivium": "ce97f53e7c28791319f7bca369c26fcac3ba7f36",
    "inseed": "0effb59c4a4e830f2ce5297998df496786d49f32",
    "copolitic": "1ae823ad0072cb310c2f30f7cb464c05b375a43f",
}
SCHEMA = "CoSites.ThreeFlagship.PinnedSourceAccessibility.R0"
VIEWPORTS = {"mobile390", "desktop1365"}


def fanin(rows: list[dict], expected_commit: str) -> dict:
    found = set()
    summary = []
    problems = []
    if not (isinstance(expected_commit, str) and len(expected_commit) == 40 and
            all(c in "0123456789abcdef" for c in expected_commit)):
        problems.append("INVALID_CI_COMMIT")
    for row in rows:
        if not isinstance(row, dict):
            problems.append("NON_OBJECT_RECEIPT")
            continue
        name = row.get("site")
        if name not in EXPECTED:
            problems.append("UNEXPECTED_SITE")
            continue
        if name in found:
            problems.append("DUPLICATE_SITE:" + name)
            continue
        found.add(name)
        if row.get("schema") != SCHEMA or row.get("expected_blob") != EXPECTED[name] or \
                row.get("source_blob_sha1") != EXPECTED[name] or row.get("run_commit") != expected_commit:
            problems.append("SOURCE_OR_COMMIT_BINDING_FAILED:" + name)
        if row.get("state") not in (
            "PASS_AUTOMATED_A11Y_NO_DETECTED_VIOLATIONS_NOT_HUMAN_ACCEPTED",
            "HOLD_AUTOMATED_A11Y_VIOLATIONS", "HOLD_AUDIT_ERROR"):
            problems.append("INVALID_STATE:" + name)
        views = row.get("viewports", [])
        if not isinstance(views, list) or {x.get("viewport") for x in views if isinstance(x, dict)} != VIEWPORTS or len(views) != 2:
            problems.append("MISSING_VIEWPORTS:" + name)
        vcount = 0
        incomplete = 0
        for x in views:
            if not isinstance(x, dict) or not isinstance(x.get("violations"), list):
                problems.append("MALFORMED_RULE_RESULT:" + name)
                continue
            vcount += len(x["violations"])
            incomplete += x.get("incomplete_rule_count", 0)
        if row.get("state") != "PASS_AUTOMATED_A11Y_NO_DETECTED_VIOLATIONS_NOT_HUMAN_ACCEPTED" or vcount:
            problems.append("ACCESSIBILITY_REVIEW_REQUIRED:" + name)
        summary.append({"site": name, "automated_violation_rules": vcount,
                        "manual_review_needed": True, "incomplete_rule_count": incomplete,
                        "source_sha256": row.get("source_sha256"),
                        "source_blob_sha1": row.get("source_blob_sha1")})
    missing = sorted(set(EXPECTED) - found)
    if missing:
        problems.append("MISSING_SITE_RECEIPTS:" + ",".join(missing))
    summary.sort(key=lambda x: x["site"])
    return {
        "schema": "CoSites.ThreeFlagship.AccessibilityFanIn.R0",
        "state": "HOLD_ACCESSIBILITY_REVIEW" if problems else "PASS_AUTOMATED_WCAG_AA_SOURCE_SCAN_ONLY",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": expected_commit,
        "candidate_sites": summary,
        "problems": sorted(set(problems)),
        "source_candidate_review_only": True,
        "human_first_use_accepted": False,
        "privacy_cleared": False,
        "public_release_authorized": False,
        "independent_roots": 1,
        "next": "Review human keyboard/screenreader/meaning and private domain privacy gates before hosted preview or release",
        "nonclaims": ["CI_NE_THREE_INDEPENDENT_ROOTS", "AUTOMATED_SCAN_NE_HUMAN_ACCEPTANCE",
                      "SOURCE_NE_PUBLIC_DEPLOYMENT", "NO_SITE_OR_DNS_MUTATION", "NO_PHANTOM_ACK"]
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--commit", required=True)
    args = p.parse_args()
    files = sorted(Path(args.input_dir).glob("*/audit_receipt.json"))
    rows = []
    for f in files:
        try:
            rows.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            rows.append({"site": "UNKNOWN", "state": "HOLD_UNREADABLE_ARTIFACT"})
    result = fanin(rows, args.commit)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"state": result["state"], "issues": result["problems"],
                      "scanned": len(result["candidate_sites"]), "output": str(out)}))
    return 0 if not result["problems"] else 3


if __name__ == "__main__":
    sys.exit(main())