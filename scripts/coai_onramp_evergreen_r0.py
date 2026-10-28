#!/usr/bin/env python3
"""CoAll machine onramp R0: offline source-bound discovery, not agent elevation."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "CoCivium.CoAIEvergreenOnrampShadow.R0"
SOURCES = {
    "ai_index": ("ai/index.json", "CoCivium.AIDiscoveryIndex.v0.2-candidate", "updated_utc"),
    "session_bootstrap": ("ai/session-bootstrap.json", "CoAll.SessionBootstrap.v0.1-candidate", "updated_utc"),
    "first_use": ("ai/onramp/cocivia-first-use-r0.json", "CoCivium.CoCiviaFirstUse.v0.1-candidate", "updated_utc"),
    "specialist": ("ai/onramp/specialist-entrypoints-r0.json", "CoCivium.ProgressiveSpecialistEntry.R0", "observed_date"),
    "llms": ("llms.txt", None, None),
}
EXPECTED_REMOTE_SOURCE = "https://github.com/CoCivium/CoAcademy/blob/master/docs/coorb/index.html"
EXPECTED_REMOTE_DISCOVERY = "https://raw.githubusercontent.com/CoCivium/CoAcademy/master/docs/coorb/discovery.json"
MAX_SOURCE_BYTES = 131072
MAX_OUTPUT_BYTES = 8192

class OnrampHold(ValueError):
    """A failed local source contract; never inferred as missing globally."""


def fail(code: str) -> None:
    raise OnrampHold(code)


def source_bytes(root: Path, path: str) -> bytes:
    if root.is_symlink():
        fail("ROOT_SYMLINK_REFUSED")
    curr = root
    for component in Path(path).parts:
        if component in ("..", ".", ""):
            fail("UNSAFE_PATH")
        curr = curr / component
        if curr.is_symlink():
            fail("SOURCE_SYMLINK_REFUSED")
    if not curr.is_file():
        fail("LOCAL_SOURCE_NOT_FOUND")
    if curr.stat().st_size > MAX_SOURCE_BYTES:
        fail("LOCAL_SOURCE_TOO_LARGE")
    b = curr.read_bytes()
    if len(b) > MAX_SOURCE_BYTES:
        fail("LOCAL_SOURCE_TOO_LARGE")
    return b


def parse_date(s: str | None, today: dt.date) -> tuple[str, int | None]:
    if not s:
        return ("OBSERVATION_DATE_UNDECLARED", None)
    try:
        observed = dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        fail("INVALID_SOURCE_OBSERVATION_DATE")
    age = (today - observed).days
    if age < 0:
        fail("SOURCE_OBSERVATION_IN_FUTURE")
    return (observed.isoformat(), age)


def trusted_url(url: str, host: str, prefix: str) -> bool:
    if not isinstance(url, str):
        return False
    o = urlparse(url)
    return o.scheme == "https" and o.hostname == host and o.netloc == host and o.path.startswith(prefix) and not o.username and not o.password and not o.query and not o.fragment


def compile_shadow(root: Path, today: dt.date, max_age_days: int = 14) -> dict:
    if not isinstance(max_age_days, int) or max_age_days < 1 or max_age_days > 365:
        fail("INVALID_RECHECK_WINDOW")
    root = Path(root)
    loaded = {}
    receipts = []
    warnings = []
    for key, (path, schema, datekey) in SOURCES.items():
        b = source_bytes(root, path)
        sha = hashlib.sha256(b).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
        data = None
        if schema:
            try:
                data = json.loads(b.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                fail("INVALID_LOCAL_JSON")
            if not isinstance(data, dict) or data.get("schema") != schema:
                fail("SOURCE_SCHEMA_CHANGED_REVALIDATE")
        else:
            try:
                txt = b.decode("utf-8")
            except UnicodeDecodeError:
                fail("INVALID_LOCAL_NAVIGATION_TEXT")
            if not txt.startswith("# CoCivium") or "ai/index.json" not in txt or "ai/session-bootstrap.json" not in txt:
                fail("MACHINE_NAVIGATION_POINTER_MISSING")
        observed, age = parse_date(data.get(datekey) if datekey else None, today)
        if age is not None and age > max_age_days:
            warnings.append({"source": path, "reason": "DECLARED_OBSERVATION_OLDER_THAN_WINDOW", "age_days": age})
        receipts.append({"path": path, "bytes": len(b), "sha256": sha, "git_blob_sha1": blob, "declared_observation": observed, "age_days": age, "readproof": "EXACT_LOCAL_CHECKOUT_BYTES_ONLY"})
        loaded[key] = data
    ai = loaded["ai_index"]
    sb = loaded["session_bootstrap"]
    first = loaded["first_use"]
    specialist = loaded["specialist"]
    if ai.get("machine_bootstrap") != "ai/session-bootstrap.json" or sb.get("onramp", {}).get("machine_twin") != "ai/onramp/cocivia-first-use-r0.json":
        fail("ONRAMP_BOOTSTRAP_POINTER_DRIFT")
    if specialist.get("parent") != "CoCivium/CoCivium:docs/Onramp/COCIVIA_FIRST_USE_R0.md":
        fail("FIRST_USE_PARENT_POINTER_DRIFT")
    if first.get("core") != "START_WITH_ONE_REAL_THING__RETURN_ONE_CONCRETE_USEFUL_RESULT_BEFORE_DEEP_ARCHITECTURE":
        fail("FIRST_USE_SEMANTIC_DRIFT")
    routes = specialist.get("routes")
    if not isinstance(routes, list):
        fail("INVALID_SPECIALIST_ROUTE_REGISTRY")
    by_id = {r.get("id"): r for r in routes if isinstance(r, dict)}
    if len(by_id) != len(routes) or "one-task" not in by_id or "relationships" not in by_id:
        fail("ONRAMP_ROUTE_MISSING_OR_DUPLICATED")
    rel = by_id["relationships"]
    if rel.get("source_url") != EXPECTED_REMOTE_SOURCE or not str(rel.get("independent_receiver", "")).startswith("HELD"):
        fail("COORB_ROUTE_UNVERIFIED_OR_POINTER_DRIFT")
    exp = ai.get("external_public_experiments")
    if not isinstance(exp, list):
        fail("PUBLIC_EXPERIMENTS_NOT_LISTED")
    orb = [x for x in exp if isinstance(x, dict) and x.get("id") == "CoOrbWare.FirstLook.R0"]
    if len(orb) != 1 or orb[0].get("source") != EXPECTED_REMOTE_SOURCE or orb[0].get("discovery") != EXPECTED_REMOTE_DISCOVERY:
        fail("COORB_DISCOVERY_POINTER_DRIFT")
    if not trusted_url(EXPECTED_REMOTE_SOURCE, "github.com", "/CoCivium/CoAcademy/blob/master/docs/coorb/"):
        fail("REMOTE_SOURCE_BOUNDARY_CHANGED")
    packet = {
        "schema": SCHEMA,
        "as_of_date": today.isoformat(),
        "state": "SHADOW_DISCOVERY_SOURCE_BOUND__IA_AND_RECEIVER_HELD",
        "sources": receipts,
        "recheck_warnings": warnings,
        "freshness_policy": "RECHECK_ON_RELEVANT_SOURCE_CHANGE_OR_MATERIAL_WAKE__NOT_ALWAYS_RUNNING",
        "ai_discovery": {"state": "PUBLIC_LOCAL_SOURCE_REFERENCES_VERIFIED", "roles": ["READ", "COMPARE", "CHALLENGE", "PROPOSE"], "effect_authority": "NONE"},
        "ia_candidate": {"state": "HELD_NO_NAMED_WORKER_ADAPTER_PERMISSION_OR_RUNTIME_EVIDENCE", "effect_authority": "NONE"},
        "coorbware": {"source": EXPECTED_REMOTE_SOURCE, "discovery": EXPECTED_REMOTE_DISCOVERY, "state": "REMOTE_SOURCE_POINTER_ONLY__NO_RECEIVER_READBACK_THIS_GATE", "effect_authority": "NONE"},
        "receiver_ack": False,
        "active_worker_count": 0,
        "effects": {"network": 0, "model": 0, "device": 0, "send": 0, "files_mutated": 0},
        "nonclaims": ["SOURCE_READ_NE_AI_OR_IA_ADOPTION", "POINTER_NE_REMOTE_SOURCE_READPROOF", "MACHINE_READABLE_NE_EFFECT_AUTHORITY", "EVERGREEN_INTENT_NE_ALWAYS_RUNNING", "LISTED_ROLE_NE_ACTIVE_WORKER", "COORB_VIEW_NE_INSTALLED_OS", "GITHUB_PROVIDER_NE_INDEPENDENT_CUSTODY", "STALENESS_WARNING_NE_SOURCE_INVALIDITY"],
        "next_proof": "Independent AI reader binds the remote discovery source and returns a source-linked comprehension result; actual IA worker additionally needs a named adapter, scoped grant, receiver ACK and real task acceptance."
    }
    if len(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()) > MAX_OUTPUT_BYTES:
        fail("OUTPUT_PACKET_TOO_LARGE")
    return packet


def main() -> int:
    p = argparse.ArgumentParser(description="Offline CoAll AI/IA CoOrbWare onramp source/freshness guard")
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--as-of", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    p.add_argument("--max-age-days", type=int, default=14)
    a = p.parse_args()
    try:
        day = dt.date.fromisoformat(a.as_of)
        result = compile_shadow(a.repo_root, day, a.max_age_days)
    except (OnrampHold, ValueError) as e:
        print(json.dumps({"state": "HELD", "reason": str(e) if isinstance(e, OnrampHold) else "INVALID_ARGUMENT", "effects": {"network": 0, "model": 0, "device": 0, "send": 0}}))
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
