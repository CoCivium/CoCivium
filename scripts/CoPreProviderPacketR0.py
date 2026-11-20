#!/usr/bin/env python3
"""Create/validate bounded provider packets from an existing CoPre source.

Public synthetic/source-safe only. Does not start Claude, remap buttons,
access accounts, schedule jobs, make network calls, or grant authority.
"""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "CoCivium.CoPreGeneric.ProviderPacket.R0"
ROOT_SOURCE = {
    "repository": "CoCivium/CoCivium",
    "path": "CoPre.md",
    "commit_sha": "090c532627cd014e6c41355ddd70b90a56cc03ff",
    "git_blob_sha1": "7a1d9c2eada9432115a423bcb621793f474a4d28",
    "uri": "https://github.com/CoCivium/CoCivium/blob/090c532627cd014e6c41355ddd70b90a56cc03ff/CoPre.md",
}
# These are worker ROLE labels, not external account identities.
PROFILES = {
    "CLAUDE_CHAT": "CLAUDE_ADVISORY_RESEARCHER",
    "CLAUDE_COWORK_CLOUD": "CLAUDE_ADVISORY_RESEARCHER",
    "CLAUDE_COWORK_LOCAL": "CLAUDE_ADVISORY_RESEARCHER",
    "CLAUDE_CODE": "CLAUDE_ADVISORY_RESEARCHER",
    "ANTHROPIC_API": "CLAUDE_ADVISORY_RESEARCHER",
    "CHATGPT_WORK": "CHATGPT_ADVISORY_RESEARCHER",
    "CHATGPT_CHAT": "CHATGPT_ADVISORY_RESEARCHER",
    "OLLAMA_LOCAL": "LOCAL_ADVISORY_RESEARCHER",
}
ALLOWED = ["READ_PUBLIC_SOURCE", "RESEARCH_PUBLIC_FACTS", "PROPOSE_REVIEW_DIFF", "RUN_LOCAL_SYNTHETIC_TEST"]
HELD = [
    "SEND_TO_PERSON", "PUBLISH", "MERGE", "DEPLOY", "CHANGE_DNS", "SPEND", "DELETE",
    "READ_PRIVATE_DATA", "ACCESS_CREDENTIALS", "MUTATE_DEVICE", "SPAWN_UNBOUNDED_WORKERS",
    "CONFIGURE_MOUSE", "INSTALL_SCHEDULER",
]
NONCLAIMS = [
    "PACKET_NE_RUNTIME", "PUBLIC_SOURCE_NE_AUTHORITY", "WORKER_ROLE_NE_ACCOUNT_IDENTITY",
    "NO_PROVIDER_SESSION_CREATED", "NO_RECEIVER_ACK", "NO_INDEPENDENT_REVIEW",
    "NO_GLOBAL_BROADCAST", "NO_MOUSE_BINDING_CHANGED", "NO_AUTONOMOUS_WAKE",
]


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def prepare(work_id, profile, task):
    if not isinstance(work_id, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:-]{4,119}", work_id):
        raise ValueError("work_id must be a bounded stable identifier")
    if profile not in PROFILES:
        raise ValueError("unknown provider profile")
    if not isinstance(task, str) or not (10 <= len(task) <= 300) or any(ch in task for ch in "\r\n\x00"):
        raise ValueError("task must be one 10..300-character line without control breaks")
    packet = {
        "schema": SCHEMA,
        "user_invocation_alias": {
            "value": "CoPre9.3+",
            "classification": "USER_SUPPLIED_CURRENT_INVOCATION_NOT_REPOSITORY_CANON",
            "authority_grant": False,
        },
        "work_id": work_id,
        "source": copy.deepcopy(ROOT_SOURCE),
        "provider": {"profile": profile, "worker_role": PROFILES[profile], "external_account_id": None,
                     "auth_verified": False},
        "task": {"text": task, "classification": "PUBLIC_SAFE_CANDIDATE_REQUIRES_SOURCE_REVIEW",
                 "allowed_effects": list(ALLOWED), "held_effects": list(HELD)},
        "execution": {"state": "PREPARED_NOT_LAUNCHED", "elected_actuator": None,
                      "effect_lease": None, "scheduler": None, "idempotency_key": work_id},
        "source_gate": {"result": "FETCH_AND_COMPARE_BEFORE_EXECUTION", "confirmed_by_receiver": False},
        "receiver": {"identity": None, "readproof_sha256": None, "accepted": False},
        "thumb_pointer": {"source": "CoPre.md", "binding_state": "NOT_INSPECTED_OR_CONFIGURED",
                          "native_middle_click": "PASS_THROUGH_NATIVE", "long_prompt_in_button": False},
        "next_deed": "AUTHORIZED_WORKER_READS_EXACT_SOURCE_THEN_RESEARCHES_OR_RETURNS_HOLD",
        "nonclaims": list(NONCLAIMS),
    }
    packet["packet_sha256"] = digest(packet)
    return packet


def verify(packet):
    if not isinstance(packet, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(packet.get("packet_sha256", ""))):
        return False
    unsigned = {k: v for k, v in packet.items() if k != "packet_sha256"}
    if digest(unsigned) != packet["packet_sha256"]:
        return False
    try:
        expected = prepare(packet["work_id"], packet["provider"]["profile"], packet["task"]["text"])
    except (KeyError, ValueError, TypeError):
        return False
    return packet == expected


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sp = ap.add_subparsers(dest="action", required=True)
    p = sp.add_parser("prepare", help="Emit packet only; never launch provider or mutate device")
    p.add_argument("--work-id", required=True)
    p.add_argument("--profile", choices=sorted(PROFILES), required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--output", type=Path)
    v = sp.add_parser("verify", help="Verify sealed profile schema, not agent status/authority")
    v.add_argument("path", type=Path)
    args = ap.parse_args()
    if args.action == "prepare":
        result = json.dumps(prepare(args.work_id, args.profile, args.task), indent=2, ensure_ascii=True) + "\n"
        if args.output:
            # An explicit output path is caller-owned; no automatic folder discovery.
            if args.output.exists():
                ap.error("refusing to overwrite an existing packet")
            args.output.write_text(result, encoding="utf-8", newline="\n")
        else:
            print(result, end="")
    else:
        try:
            packet = json.loads(args.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as ex:
            ap.error(str(ex))
        if not verify(packet):
            ap.exit(1, "HOLD_PACKET_MISMATCH\n")
        print("PACKET_SCHEMA_VALID__NOT_LAUNCHED__NOT_AUTHORIZED")


if __name__ == "__main__":
    main()
