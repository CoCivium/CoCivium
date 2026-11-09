#!/usr/bin/env python3
"""CoObject+ source-to-proposal bridge R0.

A file is an addressable CoObject, not an executable authority.
This reads bounded local bytes, pins provenance, then emits *nonexecuting*
CoPulse/CoSessionAutocycle-compatible proposals for qualified adapters.
Never imports, runs, renders, decodes or follows instructions from source.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat

if __package__:
    from .CoObjectVitalityR0 import disposition
else:
    from CoObjectVitalityR0 import disposition

MAX_OBJECTS = 24
MAX_EVENTS = 48
MAX_BYTES = 2 * 1024 * 1024
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
TEXT = {".csv", ".json", ".jsonl", ".md", ".rst", ".toml", ".tsv", ".txt", ".yaml", ".yml"}
IMAGES = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
CODE = {".py", ".js", ".ts", ".sh", ".ps1", ".c", ".rs", ".go"}
EVENTS = {"SOURCE_OBSERVED", "MATERIAL_REVISION", "WAKE_OBSERVED", "NO_MATERIAL_DELTA"}
LIFECYCLES = {"ACTIVE_WORKING", "QUIESCENT_CURRENT", "DORMANT_WITH_WAKE",
              "DEGRADED_REPAIRABLE", "RETIRING", "RETIRED", "UNKNOWN_CURRENTNESS"}
SCHEMA = "CoObject.AgencyBridge.R0"
NONCLAIMS = (
    "LOCAL_IS_NOT_LANDED", "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
    "SOURCE_DATA_NE_EXECUTION_AUTHORITY", "AI_PROPOSAL_NE_WORKER_EXECUTION",
)


class Held(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Held(reason)


def parse_time(value):
    require(isinstance(value, str), "EVENT_TIME_REQUIRED")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Held("INVALID_EVENT_TIME") from exc
    require(t.tzinfo is not None, "EVENT_TIMEZONE_REQUIRED")
    return t.astimezone(timezone.utc)


def class_of(path: Path, size: int):
    name = path.name.lower()
    ext = path.suffix.lower()
    if size == 0 and ext == ".pid":
        return "TRANSIENT_CONTROL_FILE"
    if name.startswith(".") and ".codex-upload-" in name:
        return "UPLOAD_SIDECAR"
    if ext in IMAGES:
        return "IMAGE_EVIDENCE_CANDIDATE"
    if ext in TEXT:
        return "SUBSTANTIVE_TEXT_CANDIDATE"
    return "SUBSTANTIVE_BINARY_CANDIDATE"


def adapter_for(path: Path, content_class: str):
    """Conservative *fixed code-owned* mapping, never supplied by the file."""
    if content_class in {"TRANSIENT_CONTROL_FILE", "UPLOAD_SIDECAR"}:
        return "HOLD_TRANSIENT_NO_WAKE"
    ext = path.suffix.lower()
    if ext in CODE:
        return "REQUEST_TRUSTED_SOURCE_TEST_REVIEW"
    if ext in {".json", ".yaml", ".yml", ".toml"}:
        return "REQUEST_SCHEMA_AND_RIGHTS_REVIEW"
    if ext in {".md", ".txt", ".rst"}:
        return "REQUEST_SEMANTIC_AND_PRIOR_REVIEW"
    if ext in {".csv", ".jsonl", ".tsv"}:
        return "REQUEST_SCHEMA_AND_PROVENANCE_REVIEW"
    if content_class == "IMAGE_EVIDENCE_CANDIDATE":
        return "REQUEST_ACCESSIBLE_IMAGE_INTERPRETATION"
    return "REQUEST_SAFE_FORMAT_QUALIFICATION"


def verified_bytes(root: Path, relative: str, expected: str):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute()
            and "\\" not in relative, "INVALID_RELATIVE_PATH")
    require(isinstance(expected, str) and DIGEST.fullmatch(expected),
            "INVALID_EXPECTED_SHA256")
    require(".." not in Path(relative).parts, "PATH_TRAVERSAL")
    path = root / relative
    # Deny symlinks at every level before opening, including linked parents.
    cursor = root
    for part in Path(relative).parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), "SYMLINK_NOT_ALLOWED")
    resolved = path.resolve()
    require(resolved.is_relative_to(root), "SOURCE_OUTSIDE_ROOT")
    try:
        with path.open("rb") as stream:
            info = os.fstat(stream.fileno())
            require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_BYTES,
                    "UNSAFE_OR_OVERSIZED_SOURCE")
            raw = stream.read(MAX_BYTES + 1)
    except OSError as exc:
        raise Held("SOURCE_UNREADABLE") from exc
    require(len(raw) <= MAX_BYTES, "OVERSIZED_SOURCE")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == expected, "SOURCE_SHA256_MISMATCH")
    return path, len(raw), digest


def plan(root: str | Path, manifest: dict, events: list[dict], *, as_of: str):
    now = parse_time(as_of)
    root = Path(root).resolve(strict=True)
    require(root.is_dir(), "INVALID_ROOT")
    require(isinstance(manifest, dict) and manifest.get("schema") == SCHEMA,
            "MANIFEST_SCHEMA_REQUIRED")
    objects = manifest.get("objects")
    require(isinstance(objects, list) and 0 < len(objects) <= MAX_OBJECTS,
            "BOUNDED_OBJECT_SET_REQUIRED")
    require(isinstance(events, list) and len(events) <= MAX_EVENTS,
            "BOUNDED_EVENTS_REQUIRED")
    keyed = {}
    for obj in objects:
        require(isinstance(obj, dict), "OBJECT_MUST_BE_MAP")
        require(set(obj) == {"object_id", "relative_path", "expected_sha256",
                             "lifecycle_state", "known_debt", "wake_predicates"},
                "OBJECT_FIELDS_NOT_ALLOWED")
        oid = obj["object_id"]
        require(isinstance(oid, str) and ID.fullmatch(oid) and oid not in keyed,
                "DUPLICATE_OR_INVALID_OBJECT")
        require(obj["lifecycle_state"] in LIFECYCLES, "UNSUPPORTED_LIFECYCLE")
        require(isinstance(obj["known_debt"], list) and len(obj["known_debt"]) <= 8
                and all(isinstance(v, str) and len(v) <= 128 for v in obj["known_debt"]),
                "INVALID_DEBT")
        require(isinstance(obj["wake_predicates"], list) and
                len(obj["wake_predicates"]) <= 8 and
                all(isinstance(v, str) and ID.fullmatch(v) for v in obj["wake_predicates"]),
                "INVALID_WAKE_PREDICATES")
        keyed[oid] = obj
    event_by_id = {}
    for e in events:
        require(isinstance(e, dict) and set(e) == {"object_id", "kind",
                 "observed_at", "observed_sha256", "wake_key"},
                "INVALID_EVENT_FIELDS")
        oid = e["object_id"]
        require(oid in keyed and oid not in event_by_id, "UNBOUND_OR_DUPLICATE_EVENT")
        require(e["kind"] in EVENTS, "INVALID_EVENT_KIND")
        t = parse_time(e["observed_at"])
        require(t <= now, "FUTURE_EVENT_OBSERVATION")
        require(e["observed_sha256"] == keyed[oid]["expected_sha256"],
                "EVENT_REVISION_MISMATCH")
        wake = e["wake_key"]
        require(wake is None or isinstance(wake, str) and ID.fullmatch(wake),
                "INVALID_WAKE_KEY")
        event_by_id[oid] = e
    results = []
    for oid, obj in sorted(keyed.items()):
        path, size, digest = verified_bytes(root, obj["relative_path"],
                                            obj["expected_sha256"])
        content_class = class_of(path, size)
        e = event_by_id.get(oid)
        wake_ok = bool(e and e["kind"] == "WAKE_OBSERVED" and e["wake_key"]
                       in obj["wake_predicates"])
        local_vitality = {"lifecycle_state": obj["lifecycle_state"],
                          "known_debt": obj["known_debt"],
                          "wake_predicates": obj["wake_predicates"],
                          "wake_observations": [e["wake_key"]] if wake_ok else []}
        vitality = disposition(local_vitality)
        adapter = adapter_for(path, content_class)
        # Do not turn claimed timer events, quiet objects, or sidecars into active workers.
        eligible = bool(e and e["kind"] in {"SOURCE_OBSERVED", "MATERIAL_REVISION",
                     "WAKE_OBSERVED"} and vitality not in {
                        "PRESERVE_RETIRED_LINEAGE", "REMAIN_DORMANT_WITH_EXACT_WAKE",
                        "SLEEP_KEEP_ADDRESSABLE", "HOLD_UNKNOWN_CURRENTNESS"
                     } and adapter != "HOLD_TRANSIENT_NO_WAKE")
        if e and e["kind"] == "WAKE_OBSERVED" and not wake_ok:
            eligible = False
        next_proposal = adapter if eligible else "QUIET_OR_HOLD"
        pulse = {"subject": oid, "relation_type": "PROPOSED_OBJECT_ACTION",
                 "epistemic_class": "PLANNED", "evidence_ref": digest,
                 "authority_ceiling": "NONE", "effect_executed": False}
        results.append({"object_id": oid, "source_sha256": digest, "size_bytes": size,
                        "content_class": content_class,
                        "lifecycle_state": "VERIFIED_LOCAL",
                        "semantic_coverage": "NOT_SEMANTICALLY_REVIEWED",
                        "vitality_disposition": vitality, "event_class":
                        e["kind"] if e else "NO_EVENT", "proposal": next_proposal,
                        "candidate_eligible": eligible, "worker_id": None,
                        "permission_granted": False, "actual_dispatch": False,
                        "receiver_ack": False, "co_pulse_candidate": pulse})
    output = {"schema": SCHEMA + ".Report", "as_of": now.isoformat(),
              "objects": results, "examined": len(results),
              "eligible_proposals": sum(int(x["candidate_eligible"]) for x in results),
              "source_effects": 0, "workers_spawned": 0,
              "proven_lifecycle_max": "VERIFIED_LOCAL",
              "durable_landing": False, "actual_receiver_pickup": False,
              "ux_acceptance": "UX_NOT_EVALUATED", "nonclaims": list(NONCLAIMS)}
    output["receipt_sha256"] = hashlib.sha256(json.dumps(
        output, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--report", help="Create-only JSON output; no source overwrite")
    a = parser.parse_args()
    try:
        if Path(a.manifest).stat().st_size > 65536 or Path(a.events).stat().st_size > 65536:
            raise Held("OVERSIZED_MANIFEST")
        manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        events = json.loads(Path(a.events).read_text(encoding="utf-8"))
        out = plan(a.root, manifest, events, as_of=a.as_of)
        if a.report:
            data = json.dumps(out, indent=2, sort_keys=True) + "\n"
            with open(a.report, "x", encoding="utf-8") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        print(json.dumps({"state": "SOURCE_BOUND_PROPOSALS_ONLY",
                          "receipt_sha256": out["receipt_sha256"],
                          "examined": out["examined"],
                          "eligible_proposals": out["eligible_proposals"],
                          "workers_spawned": out["workers_spawned"],
                          "receiver_ack": False}, sort_keys=True))
        return 0
    except (Held, OSError, ValueError, TypeError, UnicodeError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)[:160],
                          "workers_spawned": 0, "receiver_ack": False},
                         sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
