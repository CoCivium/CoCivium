#!/usr/bin/env python3
"""Deterministic read-only CoAlways R0 contract canary. No external effects."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "ai" / "always-conversion-r0.json"

def validate(doc):
    failures = []
    if doc.get("status") != "DRAFT_SHADOW_ONLY":
        failures.append("must remain shadow-only")
    if doc.get("existing_bootstrap_runtime_adoption") != "UNPROVEN":
        failures.append("runtime adoption incorrectly claimed")
    lanes = doc.get("proposal_lanes", [])
    if not lanes:
        failures.append("no lanes")
    seen = set()
    for lane in lanes:
        identity = lane.get("id")
        if not identity or identity in seen:
            failures.append("missing/duplicate lane id")
        seen.add(identity)
        for field in ("domain", "mode", "wake", "output", "proof"):
            if not lane.get(field):
                failures.append(f"{identity}: missing {field}")
        if lane.get("effect_permission") not in ("NONE", "READ_ONLY"):
            failures.append(f"{identity}: forbidden effects")
    limits = doc.get("resource_control", {})
    if limits.get("default_effect_leases") != 0 or limits.get("concurrent_external_actuators") != 0:
        failures.append("external actuator or effect lease > 0")
    if "DRAFT_NE_SCHEDULER" not in doc.get("gates", []):
        failures.append("missing DRAFT_NE_SCHEDULER")
    return failures

def main():
    doc = json.loads(CONFIG.read_text(encoding="utf-8"))
    failures = validate(doc)
    bad = json.loads(json.dumps(doc))
    bad["proposal_lanes"][0]["effect_permission"] = "UNBOUNDED_SEND"
    if not validate(bad):
        failures.append("negative unauthorized-send case not rejected")
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("PASS: shadow contract, forbidden effect rejection")
    print("NOTE: does not prove scheduler, receiver or live worker")
    return 0

if __name__ == "__main__":
    sys.exit(main())
