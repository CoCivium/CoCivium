#!/usr/bin/env python3
"""Synthetic local-only camera/device presence projection. Never actuates hardware."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "CoDeviceVisiblePresence.SyntheticObserver.R0"
EXPECTED = ("Demo Camera A", "Demo Camera B", "Demo Camera C", "Demo Camera D", "Demo Camera E", "Demo Camera F", "Demo Camera G", "Demo Camera H")
PERMITTED_EVENT = {"NONE", "PERSON", "MOTION", "DOORBELL"}
PERMITTED_LINK = {"OBSERVED_REACHABLE", "OBSERVED_UNREACHABLE", "UNKNOWN"}
PERMITTED_CONSENT = {"LOCAL_ONLY", "NO_PROJECTION"}
PERMITTED_SOURCE = {"SYNTHETIC_HA_EVENT", "SYNTHETIC_HEALTH_POLL", "NONE"}


def stamp(text):
    if text is None:
        return None
    if not isinstance(text, str):
        raise ValueError("BAD_TIMESTAMP")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("NAIVE_TIMESTAMP")
    return parsed.astimezone(timezone.utc)


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def validate(payload):
    if not isinstance(payload, dict) or set(payload) != {"schema", "as_of", "inventory_scope", "cameras", "policy"}:
        raise ValueError("HOLD_ENVELOPE")
    if payload["schema"] != SCHEMA or payload["inventory_scope"] != "EIGHT_SYNTHETIC_CAMERAS_UNBOUND_TO_DEVICES":
        raise ValueError("HOLD_SCOPE")
    now = stamp(payload["as_of"])
    cfg = payload["policy"]
    if not isinstance(cfg, dict) or set(cfg) != {"fresh_seconds", "acknowledgement_seconds", "cooldown_seconds", "no_network", "hardware_effects"}:
        raise ValueError("HOLD_POLICY")
    if (cfg["fresh_seconds"], cfg["acknowledgement_seconds"], cfg["cooldown_seconds"]) != (60, 4, 45):
        raise ValueError("HOLD_POLICY_BUDGET")
    if cfg["no_network"] is not True or cfg["hardware_effects"] is not False:
        raise ValueError("HOLD_HARDWARE_AND_NETWORK")
    entries = payload["cameras"]
    if not isinstance(entries, list) or len(entries) != len(EXPECTED):
        raise ValueError("HOLD_CAMERA_COUNT")
    names = [e.get("name") for e in entries if isinstance(e, dict)]
    if len(names) != len(EXPECTED) or set(names) != set(EXPECTED) or len(names) != len(set(names)):
        raise ValueError("HOLD_IDENTITY_COLLISION")
    for e in entries:
        if set(e) != {"name", "source", "observed_at", "link", "event", "event_at", "night", "privacy", "capabilities", "last_ack_at"}:
            raise ValueError("HOLD_CAMERA_FIELDS")
        if e["source"] not in PERMITTED_SOURCE or e["link"] not in PERMITTED_LINK or e["event"] not in PERMITTED_EVENT or e["privacy"] not in PERMITTED_CONSENT:
            raise ValueError("HOLD_ENUM")
        if not isinstance(e["night"], bool):
            raise ValueError("HOLD_DAYNIGHT")
        if not isinstance(e["capabilities"], dict) or set(e["capabilities"]) != {"verified", "low_glare_light", "ptz"}:
            raise ValueError("HOLD_CAPABILITIES")
        cap = e["capabilities"]
        if any(not isinstance(v, bool) for v in cap.values()) or (not cap["verified"] and (cap["low_glare_light"] or cap["ptz"])):
            raise ValueError("HOLD_INFERRED_CAPABILITY")
        o, ev, last = [stamp(e[k]) for k in ("observed_at", "event_at", "last_ack_at")]
        if e["source"] == "NONE" and (o is not None or e["link"] != "UNKNOWN"):
            raise ValueError("HOLD_UNSOURCED_HEALTH")
        if e["link"] != "UNKNOWN" and o is None:
            raise ValueError("HOLD_UNTIMED_HEALTH")
        if e["event"] != "NONE" and (ev is None or o is None or e["source"] != "SYNTHETIC_HA_EVENT"):
            raise ValueError("HOLD_EVENT_WITHOUT_SOURCE")
        if e["event"] == "NONE" and ev is not None:
            raise ValueError("HOLD_GHOST_EVENT")
        if any(t is not None and t > now for t in (o, ev, last)):
            raise ValueError("HOLD_FUTURE_AS_OBSERVED")
    return now


def project(payload):
    now = validate(payload)
    seconds = payload["policy"]["fresh_seconds"]
    cards = []
    for e in payload["cameras"]:
        obs = stamp(e["observed_at"])
        ev = stamp(e["event_at"])
        age = int((now - obs).total_seconds()) if obs else None
        recent = age is not None and age <= seconds
        private = e["privacy"] == "NO_PROJECTION"
        if private:
            state, hint = "PRIVATE", "Privacy boundary; no event rendered"
        elif not recent:
            state, hint = ("STALE", "Observation expired") if obs else ("UNKNOWN", "No observed health source")
        elif e["link"] == "OBSERVED_UNREACHABLE":
            state, hint = "UNREACHABLE", "Observed endpoint unreachable"
        elif e["link"] == "UNKNOWN":
            state, hint = "UNKNOWN", "Health unproven"
        elif ev and (now - ev).total_seconds() <= seconds and e["event"] != "NONE":
            state, hint = "OBSERVED_EVENT", "Local observation, no identity inferred"
        else:
            state, hint = "QUIET_REACHABLE", "Fresh source observed; quiet is not dead"

        active = state == "OBSERVED_EVENT"
        live_ack = active and ev is not None and (now - ev).total_seconds() <= payload["policy"]["acknowledgement_seconds"]
        # Never declare eligibility as an effect. No direct writes or OS calls exist.
        candidate = "NONE"
        if live_ack and e["night"] and e["capabilities"]["verified"] and e["capabilities"]["low_glare_light"]:
            last_ack = stamp(e["last_ack_at"])
            cooldown_ok = last_ack is None or (now - last_ack).total_seconds() >= payload["policy"]["cooldown_seconds"]
            if cooldown_ok:
                candidate = "REVIEW_STEADY_LOW_GLARE_LIGHT_ONLY"
        cards.append({
            "name": e["name"], "status": state, "detail": hint, "age_seconds": age,
            "local_ui_ack": "SINGLE_SOFT_NONFLASHING_OUTLINE" if live_ack else "NO_ANIMATION",
            "physical_effect": "NONE", "physical_proposal": candidate,
            "ptz": "NEVER_MOVED", "siren": "NEVER_SOUNDED", "image_or_audio_collected": False,
            "authority": "READ_ONLY", "receiver_ack": "NOT_OBSERVED", "observer": e["source"],
        })
    return {
        "schema": "CoDeviceVisiblePresence.ShadowReport.R0", "source_sha256": digest(payload),
        "state": "SYNTHETIC_SOURCE_ONLY_NO_REAL_CAMERAS", "as_of": payload["as_of"],
        "cards": cards, "camera_count": len(cards), "external_effects": 0,
        "hardware_writes": 0, "network_calls": 0, "readout": "SYNTHETIC_ONLY",
        "review_panel": "NOT_STAFFED", "real_receiver_ack": "UNPROVEN",
        "cooperation": "EIGHT_INDEPENDENT_READONLY_EVALUATIONS_ONE_PER_CAMERA_NO_ACTUATION",
        "rails": ["QUIET_NE_DEAD", "RENDERED_NE_REACHABLE", "STATUS_FROM_OBSERVATION_ONLY",
                  "PROPOSAL_NE_HARDWARE_COMMAND", "PTZ_NE_DECORATION", "NO_SIRENS", "NO_FACE_IDENTITY_INFERENCE",
                  "NO_AUDIO_OR_VIDEO_CAPTURE", "UNKNOWN_NE_OFF", "NO_PUBLIC_CAMERA_EXPOSURE",
                  "NO_SYNTHETIC_ACK_AS_REAL", "OBSERVER_OFFLINE_NE_CAMERA_OFF"],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", type=Path, default=Path(__file__).with_name("fixture.json"))
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    report = project(json.loads(a.fixture.read_text(encoding="utf-8")))
    raw = canonical(report)
    if a.output:
        with a.output.open("xb") as f:
            f.write(raw)
        if a.output.read_bytes() != raw:
            raise RuntimeError("HOLD_BAD_RECEIPT_READBACK")
    else:
        print(raw.decode("ascii"), end="")


if __name__ == "__main__":
    main()
