#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ALLOWED_EPISTEMIC_CLASSES = {
    "OBSERVED","INFERRED","HYPOTHESIS","PREDICTED","PLANNED","PREFERRED",
    "METAPHORICAL","MYTHIC","HUMOROUS","COUNTERFACTUAL","UNKNOWN"
}
ALLOWED_CONFIDENTIALITY = {"PUBLIC","PRIVATE","RESTRICTED","UNKNOWN"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def get_pulses(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        rows = value
    elif isinstance(value, dict) and isinstance(value.get("pulses"), list):
        rows = value["pulses"]
    else:
        raise ValueError("pulse input must be an array or object with pulses[]")
    if not all(isinstance(x, dict) for x in rows):
        raise ValueError("every pulse must be an object")
    return rows


def profile_map(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in value.get("profiles", []):
        pid = str(p.get("profile_id", ""))
        if pid:
            out[pid] = p
    return out


def validate_profile_domains(profile: dict[str, Any], known_domains: set[str]) -> list[str]:
    issues: list[str] = []
    for lane in ("hot", "warm", "digest"):
        for domain in profile.get(lane, []):
            if str(domain) not in known_domains:
                issues.append(f"UNKNOWN_DOMAIN:{lane}:{domain}")
    return issues


def classify(pulse: dict[str, Any], profile: dict[str, Any]) -> str:
    domains = {str(x) for x in pulse.get("domains", [])}
    if domains & {str(x) for x in profile.get("hot", [])}:
        return "HOT"
    if domains & {str(x) for x in profile.get("warm", [])}:
        return "WARM"
    if domains & {str(x) for x in profile.get("digest", [])}:
        return "DIGEST"
    return "SLEEP"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulses", required=True)
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--evolution-lanes", required=True)
    ap.add_argument("--profile-id", required=True)
    ap.add_argument("--last-acked-cursor", type=int, required=True)
    ap.add_argument("--receiver-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if args.last_acked_cursor < 0:
        raise SystemExit("FAIL_CLOSED__NEGATIVE_CURSOR")

    pulse_path = Path(args.pulses).resolve()
    profiles_path = Path(args.profiles).resolve()
    lanes_path = Path(args.evolution_lanes).resolve()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    pulse_raw = pulse_path.read_bytes()
    profiles_raw = profiles_path.read_bytes()
    lanes_raw = lanes_path.read_bytes()

    pulses = get_pulses(json.loads(pulse_raw.decode("utf-8")))
    profiles_obj = json.loads(profiles_raw.decode("utf-8"))
    lanes_obj = json.loads(lanes_raw.decode("utf-8"))

    profiles = profile_map(profiles_obj)
    if args.profile_id not in profiles:
        raise SystemExit(f"FAIL_CLOSED__UNKNOWN_PROFILE={args.profile_id}")
    profile = profiles[args.profile_id]

    known_domains = {str(row[0]) for row in lanes_obj.get("domains", []) if isinstance(row, list) and len(row) == 3}
    profile_issues = validate_profile_domains(profile, known_domains)
    if profile_issues:
        raise SystemExit("FAIL_CLOSED__PROFILE_DOMAIN_DRIFT__" + "__".join(profile_issues))

    seen_cursors: set[int] = set()
    previous_cursor = -1
    selected: list[dict[str, Any]] = []
    counts = {"HOT":0, "WARM":0, "DIGEST":0, "SLEEP":0, "OLDER_OR_ACKED":0}
    max_seen_cursor = args.last_acked_cursor
    max_selected_cursor = args.last_acked_cursor

    ordered = sorted(pulses, key=lambda p: int(p.get("cursor", -1)))
    for pulse in ordered:
        required = ("pulse_id","cursor","subject","relation_type","epistemic_class",
                    "source_identity","recorded_at","valid_from","authority_ceiling",
                    "confidentiality","topics")
        missing = [x for x in required if x not in pulse]
        if missing:
            raise SystemExit("FAIL_CLOSED__PULSE_MISSING_FIELDS=" + ",".join(missing))

        epistemic_class = str(pulse.get("epistemic_class"))
        if epistemic_class not in ALLOWED_EPISTEMIC_CLASSES:
            raise SystemExit(
                "FAIL_CLOSED__UNKNOWN_EPISTEMIC_CLASS="
                + epistemic_class
                + "__PULSE="
                + str(pulse.get("pulse_id"))
            )

        confidentiality = str(pulse.get("confidentiality"))
        if confidentiality not in ALLOWED_CONFIDENTIALITY:
            raise SystemExit(
                "FAIL_CLOSED__UNKNOWN_CONFIDENTIALITY="
                + confidentiality
                + "__PULSE="
                + str(pulse.get("pulse_id"))
            )

        domains = list(pulse.get("domains") or [])
        if not domains:
            raise SystemExit(
                "FAIL_CLOSED__ROUTABLE_PULSE_HAS_NO_DOMAINS="
                + str(pulse.get("pulse_id"))
            )

        cursor = pulse["cursor"]
        if not isinstance(cursor, int) or cursor < 0:
            raise SystemExit(f"FAIL_CLOSED__INVALID_CURSOR={cursor}")
        if cursor in seen_cursors:
            raise SystemExit(f"FAIL_CLOSED__DUPLICATE_CURSOR={cursor}")
        if previous_cursor > cursor:
            raise SystemExit("FAIL_CLOSED__NON_MONOTONIC_CURSOR_ORDER")
        seen_cursors.add(cursor)
        previous_cursor = cursor
        max_seen_cursor = max(max_seen_cursor, cursor)

        if str(pulse.get("confidentiality")) != "PUBLIC":
            raise SystemExit(
                "FAIL_CLOSED__NONPUBLIC_PULSE_ON_PUBLIC_ROUTER="
                + str(pulse.get("pulse_id"))
            )

        if cursor <= args.last_acked_cursor:
            counts["OLDER_OR_ACKED"] += 1
            continue

        lane = classify(pulse, profile)
        counts[lane] += 1
        if lane == "SLEEP":
            continue

        max_selected_cursor = max(max_selected_cursor, cursor)
        selected.append({
            "pulse_id": pulse["pulse_id"],
            "cursor": cursor,
            "delivery_class": lane,
            "digest_state": "DIGEST_CLASS__NOT_YET_COMPACTED" if lane == "DIGEST" else None,
            "subject": pulse["subject"],
            "relation_type": pulse["relation_type"],
            "epistemic_class": pulse["epistemic_class"],
            "domains": list(pulse.get("domains") or []),
            "topics": list(pulse.get("topics") or []),
            "evidence_refs": list(pulse.get("evidence_refs") or []),
            "source_identity": pulse["source_identity"],
            "authority_ceiling": pulse["authority_ceiling"],
            "confidentiality": pulse["confidentiality"],
            "wake_conditions": list(pulse.get("wake_conditions") or []),
        })

    packet_basis = {
        "receiver_id": args.receiver_id,
        "profile_id": args.profile_id,
        "last_acked_cursor": args.last_acked_cursor,
        "selected": [(x["pulse_id"], x["cursor"], x["delivery_class"]) for x in selected],
    }
    packet_id = "copulsepacket:" + sha256_bytes(
        json.dumps(packet_basis, sort_keys=True, separators=(",",":")).encode("utf-8")
    )[:24]

    packet = {
        "schema":"CoPulseSubscriptionPacket.R0A.v0.1-candidate",
        "state":"PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP",
        "packet_id":packet_id,
        "receiver_id":args.receiver_id,
        "profile_id":args.profile_id,
        "source_bindings":{
            "pulses_sha256":sha256_bytes(pulse_raw),
            "profiles_sha256":sha256_bytes(profiles_raw),
            "evolution_lanes_sha256":sha256_bytes(lanes_raw),
        },
        "cursor":{
            "last_acked_cursor":args.last_acked_cursor,
            "max_seen_cursor":max_seen_cursor,
            "candidate_delivered_cursor":max_selected_cursor,
            "ack_cursor_unchanged":args.last_acked_cursor,
        },
        "counts":counts,
        "selected_pulses":selected,
        "effects":{
            "receiver_context_mutation":0,
            "provider_session_mutation":0,
            "authority_change":0,
            "public_outreach":0,
        },
        "next":"RECEIVER_EXACT_PACKET_READPROOF_BEFORE_ACK_CURSOR_ADVANCE",
        "nonclaims":[
            "DELIVERY_NE_PICKUP",
            "PACKET_COMPILED_NE_RECEIVER_CONTEXT_MUTATED",
            "CANDIDATE_DELIVERED_CURSOR_NE_ACK_CURSOR",
            "PUBLIC_ROUTER_NE_PRIVATE_BUS",
            "SUBSCRIPTION_NE_AUTHORITY",
            "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
        ],
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    encoded=(json.dumps(packet, indent=2, ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":packet["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "PROFILE_ID":args.profile_id,
        "SELECTED":len(selected),
        "HOT":counts["HOT"],
        "WARM":counts["WARM"],
        "DIGEST":counts["DIGEST"],
        "SLEEP":counts["SLEEP"],
        "LAST_ACKED_CURSOR":args.last_acked_cursor,
        "CANDIDATE_DELIVERED_CURSOR":max_selected_cursor,
        "ACK_CURSOR_ADVANCED":False,
        "NEXT":packet["next"],
    }, separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
