"""CoLatch+ R0 fail-closed admission checker. Source/fixture evaluation only.

This module never authenticates an external receiver, runs a worker, or changes
an X2 desktop. Even a structurally perfect input stays native-release HELD.
"""
from datetime import datetime, timedelta, timezone
import re

ROLES = ("seed", "orb", "gauge", "thumb", "time")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _utc(value):
    if not isinstance(value, str):
        raise ValueError("not a timestamp")
    time = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if time.tzinfo is None:
        raise ValueError("timestamp missing timezone")
    return time.astimezone(timezone.utc)


def evaluate(packet):
    """Inspect caller-supplied evidence, never grant physical/runtime authority."""
    if packet.get("material_delta") is False:
        return {
            "shadow": "NO_MATERIAL_DELTA",
            "native_x2": "HOLD_UNATTESTED_RECEIVER",
            "reasons": ["NO_CHANGE_QUIESCE"],
            "independent_sync": "UNPROVEN",
        }
    failures = []
    work = packet.get("work_id")
    sha = packet.get("source_sha256")
    if not isinstance(work, str) or not work.strip():
        failures.append("MISSING_WORK_ID")
    if not isinstance(sha, str) or not HEX64.fullmatch(sha):
        failures.append("INVALID_SOURCE_SHA256")

    components = packet.get("components", {})
    ids = []
    if not isinstance(components, dict):
        components = {}
    for role in ROLES:
        members = components.get(role)
        if not isinstance(members, list) or len(members) != 1:
            failures.append("NOT_EXACTLY_ONE_" + role.upper())
            continue
        member = members[0]
        if not isinstance(member, dict) or not member.get("id") or not member.get("source_ref"):
            failures.append("UNBOUND_" + role.upper())
            continue
        ids.append(str(member["id"]))
        if member.get("work_id") != work:
            failures.append("WORK_ID_MISMATCH_" + role.upper())
        if member.get("source_sha256") != sha:
            failures.append("SOURCE_MISMATCH_" + role.upper())
    if len(ids) != len(set(ids)):
        failures.append("COMPONENT_ID_COLLISION")

    if packet.get("placeholder_count") != 0:
        failures.append("PLACEHOLDERS_NOT_ZERO")
    if packet.get("human_relays") != 0:
        failures.append("HUMAN_RELAY_REQUIRED")
    if packet.get("system_effect_count") != 1:
        failures.append("SYSTEM_EFFECT_COUNT_NOT_ONE")
    if packet.get("stop_supported") is not True:
        failures.append("MISSING_STOP")
    if packet.get("native_escape") is not True or not packet.get("rollback_ref"):
        failures.append("MISSING_RECOVERY_OR_ESCAPE")

    observations = packet.get("seed_observations")
    if not isinstance(observations, list) or len(observations) != 2:
        failures.append("MISSING_COLD_SURVIVAL_PAIR")
    else:
        try:
            old, new = observations
            start, end = _utc(old["observed_at"]), _utc(new["observed_at"])
            same = all(
                x.get("work_id") == work and x.get("source_sha256") == sha
                and x.get("event") == "READBACK" and x.get("evidence_ref")
                for x in observations
            )
            distinct = old.get("renderer_epoch") and new.get("renderer_epoch") and old["renderer_epoch"] != new["renderer_epoch"]
            if not (same and distinct and end - start > timedelta(hours=24)):
                failures.append("COLD_SURVIVAL_GT24H_NOT_EVEN_STRUCTURALLY_SHOWN")
        except (ValueError, KeyError, TypeError):
            failures.append("INVALID_COLD_SURVIVAL_TIMES")

    handoffs = packet.get("handoffs")
    if not isinstance(handoffs, list) or len(handoffs) != 1:
        failures.append("HANDOFF_COUNT_NOT_ONE")
    else:
        h = handoffs[0]
        r = packet.get("receipt")
        if not isinstance(h, dict) or not h.get("id") or not h.get("to") or not h.get("from"):
            failures.append("UNBOUND_HANDOFF")
        elif h.get("from") == h.get("to") or h.get("work_id") != work or h.get("source_sha256") != sha:
            failures.append("HANDOFF_IDENTITY_CONFLICT")
        elif not isinstance(r, dict) or not (
            r.get("handoff_id") == h["id"] and r.get("issued_by") == h["to"]
            and r.get("work_id") == work and r.get("source_sha256") == sha
            and r.get("evidence_ref")
        ):
            failures.append("RECEIVER_ORIGIN_READBACK_NOT_STRUCTURALLY_SHOWN")
    # Caller declarations are never independently authenticated by this code.
    return {
        "shadow": "STRUCTURE_PASS_NOT_ATTESTATION" if not failures else "HOLD_INVALID_EVIDENCE",
        "native_x2": "HOLD_UNATTESTED_RECEIVER",
        "reasons": failures or ["REQUIRES_EXTERNAL_TRUSTED_X2_RECEIVER", "REQUIRES_REAL_24H_OBSERVATION", "REQUIRES_USER_OUTCOME_TEST"],
        "independent_sync": "UNPROVEN",
    }


def synthetic_example():
    """A test fixture with invented times and roles. NEVER a live-X2 receipt."""
    sha = "a" * 64
    work = "cosurface-fixture-only"
    return {
        "material_delta": True,
        "work_id": work, "source_sha256": sha,
        "components": {
            name: [{"id": name + "-fixture", "source_ref": "public-source-fixture", "work_id": work, "source_sha256": sha}]
            for name in ROLES
        },
        "placeholder_count": 0, "human_relays": 0, "system_effect_count": 1,
        "stop_supported": True, "native_escape": True, "rollback_ref": "synthetic-native-fallback",
        "seed_observations": [
            {"work_id": work, "source_sha256": sha, "event": "READBACK", "renderer_epoch": "fixture-1",
             "observed_at": "2026-11-07T16:00:00Z", "evidence_ref": "synthetic-a"},
            {"work_id": work, "source_sha256": sha, "event": "READBACK", "renderer_epoch": "fixture-2",
             "observed_at": "2026-11-08T17:00:01Z", "evidence_ref": "synthetic-b"},
        ],
        "handoffs": [{"id": "fixture-handoff", "from": "fixture-producer",
                      "to": "fixture-recipient", "work_id": work, "source_sha256": sha}],
        "receipt": {"handoff_id": "fixture-handoff", "issued_by": "fixture-recipient",
                    "work_id": work, "source_sha256": sha, "evidence_ref": "synthetic-receiver-claim"},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(synthetic_example()), indent=2, sort_keys=True))
