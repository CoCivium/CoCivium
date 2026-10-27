#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

POLICY = Path("ai/strategy/coglukey-careers-improvement-clubs-r0.json")
KIT = Path("docs/Outreach/IMPROVEMENT_CLUB_KIT_R0.md")

required_policy_rails = {
    "TRANSPARENT_AGENDA_NE_COVERT_PERSUASION",
    "IMPROVEMENT_CLUB_NE_ASTROTURF",
    "OUTREACH_NE_SPAM",
    "MARKETING_NE_MANIPULATION",
    "RECEIVER_NE_TARGET",
}
required_kit_terms = [
    "Independent, unofficial community",
    "Do not disguise a CoCivium adoption funnel",
    "mass-invite uninterested users",
    "PASS / FAIL / HELD / UNKNOWN",
    "Challenge path",
    "Exit / fork path",
    "No CoCivium vocabulary is required for participation",
]

def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    kit = KIT.read_text(encoding="utf-8")

    assert policy["state"] == "CANDIDATE__NO_EXTERNAL_CLUB_CREATED__NO_MASS_OUTREACH"
    assert policy["improvement_club"]["agenda"] == "EXPLICIT_AND_PUBLIC"
    assert policy["improvement_club"]["mass_invites"] is False
    assert policy["improvement_club"]["covert_funnel"] is False
    assert policy["improvement_club"]["astroturf"] is False
    assert required_policy_rails.issubset(set(policy["rails"]))

    for term in required_kit_terms:
        assert term in kit, term

    assert "MEMBERS_NE_USEFULNESS" in kit
    assert "USED_NE_RETURNED_DELTA" in kit
    print("PASS_COGLUKEY_CAREERS_IMPROVEMENT_CLUBS_R0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
