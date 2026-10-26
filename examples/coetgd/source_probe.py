#!/usr/bin/env python3
"""CoETSignalFinder / CoG_d SourceRegistry R0.

Validation is offline by default. Optional --probe is an explicit, single-pass
HTTPS read of four fixed public locations, bounded to 4096 bytes each.
Neither mode performs signal classification, detection, login, or model calls.
"""
import argparse
import hashlib
import http.client
import json
import ssl
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

MANIFEST = Path(__file__).with_name("sources.json")
PROBES = {
    "breakthrough_listen_archive": "https://seti.berkeley.edu/opendata",
    "nasa_exoplanet_tap": "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+top+1+pl_name+from+ps&format=json",
    "seti_detection_protocol_2026": "https://www.seti.org/research/seti-101/protocols-for-an-eti-signal-detection/",
    "sep_teleological_arguments": "https://plato.stanford.edu/entries/teleological-arguments/",
}
FAMILIES = {
    "ET_EMPIRICAL": "ASTRONOMICAL_DATA_CATALOG",
    "ET_VERIFICATION_GOVERNANCE": "DETECTION_PROTOCOL",
    "GD_PHILOSOPHICAL": "PHILOSOPHY_REFERENCE",
}
LIMIT_BYTES = 4096
LIMIT_SECONDS = 5


def load_registry():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate(registry):
    if not isinstance(registry, dict) or registry.get("schema") != "CoCivium.CoETGd.QualifiedSourceRegistry.R0":
        raise ValueError("INVALID_SCHEMA")
    rows = registry.get("sources")
    if not isinstance(rows, list) or len(rows) != 4:
        raise ValueError("REQUIRE_FOUR_FIXED_SOURCES")
    if registry.get("external_actions_default") is not False:
        raise ValueError("DEFAULT_EXTERNAL_ACTION_MUST_BE_FALSE")
    if registry.get("max_sources_per_probe") != 4:
        raise ValueError("PROBE_LIMIT_CHANGED")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("INVALID_SOURCE_RECORD")
        sid = row.get("id")
        if sid in seen or sid not in PROBES:
            raise ValueError("UNQUALIFIED_SOURCE")
        seen.add(sid)
        endpoint = row.get("probe_url")
        if endpoint != PROBES[sid]:
            raise ValueError("UNAPPROVED_ENDPOINT")
        u = urlsplit(endpoint)
        if u.scheme != "https" or not u.hostname or u.username or u.password or u.port:
            raise ValueError("UNSAFE_ENDPOINT")
        if row.get("family") not in FAMILIES or row.get("class") != FAMILIES[row["family"]]:
            raise ValueError("EPISTEMIC_FAMILY_MISMATCH")
        if row.get("detection_state") not in {"NO_DETECTION_ASSERTED", "NOT_APPLICABLE"}:
            raise ValueError("UNSUPPORTED_DETECTION_CLAIM")
        if row["family"] == "GD_PHILOSOPHICAL" and row.get("epistemic") != "PHILOSOPHICAL_ARGUMENTS_AND_OBJECTIONS":
            raise ValueError("PHILOSOPHY_CANNOT_BE_EMPIRICAL_DETECTION")
        if row.get("access") != "PUBLIC_READ_ONLY":
            raise ValueError("NOT_PUBLIC_READ_ONLY")
        if not str(row.get("license_status", "")).startswith("REVIEW_BEFORE_"):
            raise ValueError("RIGHTS_NOT_REVIEWED")
    if seen != set(PROBES):
        raise ValueError("MISSING_QUALIFIED_SOURCES")
    prohibited = ("password", "access_token", "api_key", "secret", "bearer_token", "cookie")
    for row in rows:
        if any(k.lower() in prohibited for k in row):
            raise ValueError("NO_SECRET_FIELDS")
    return {"source_count": len(rows), "family_counts": {
        k: sum(row["family"] == k for row in rows) for k in FAMILIES
    }}


def structural_fingerprint(registry):
    return hashlib.sha256(
        json.dumps(registry, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def probe_one(row, connection_factory=None):
    """One GET, zero redirects, maximum 4096 response bytes, no body retention."""
    validate({"schema": "CoCivium.CoETGd.QualifiedSourceRegistry.R0",
              "external_actions_default": False, "max_sources_per_probe": 4,
              "sources": [row] + [
                  r for r in load_registry()["sources"] if r["id"] != row["id"]
              ]})
    u = urlsplit(row["probe_url"])
    maker = connection_factory or http.client.HTTPSConnection
    conn = None
    state, status, byte_count, reason = "HELD_UNTESTED", None, 0, None
    try:
        conn = maker(u.hostname, timeout=LIMIT_SECONDS, context=ssl.create_default_context())
        route = u.path + ("?" + u.query if u.query else "")
        conn.request("GET", route, headers={
            "User-Agent": "CoCivium-CoETGd-R0/0.1 public-metadata-check",
            "Accept": "application/json,text/html;q=0.8,*/*;q=0.1",
            "Connection": "close"
        })
        response = conn.getresponse()
        status = int(response.status)
        if status == 200:
            byte_count = len(response.read(LIMIT_BYTES))
            state = "PASS_BOUNDED_HTTP_READ" if byte_count else "HELD_EMPTY_RESPONSE"
        elif 300 <= status < 400:
            state, reason = "HELD_REDIRECT_NOT_FOLLOWED", "No redirect permitted"
        else:
            state, reason = "HELD_HTTP_RESPONSE", "Source status is not a detection claim"
    except (OSError, ssl.SSLError, http.client.HTTPException, TimeoutError) as exc:
        state, reason = "HELD_NETWORK", type(exc).__name__
    finally:
        if conn:
            conn.close()
    return {
        "source_id": row["id"], "status": state, "http_status": status,
        "bytes_read": byte_count, "max_bytes": LIMIT_BYTES,
        "url_host": u.hostname, "reason": reason,
        "external_effect": "ONE_EXPLICIT_PUBLIC_READ_ONLY_GET",
        "signal_detection": "NOT_ASSESSED", "receiver_ack": None
    }


def main():
    parser = argparse.ArgumentParser(description="Offline source validation unless --probe supplied")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--validate", action="store_true")
    mode.add_argument("--probe", action="store_true", help="Explicit four-source GET, 5s socket timeout per operation; no total deadline")
    args = parser.parse_args()
    registry = load_registry()
    checked = validate(registry)
    output = {
        "schema": "CoCivium.CoETGd.ReadOnlyReceipt.R0",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "EXPLICIT_BOUNDED_GET" if args.probe else "OFFLINE_VALIDATE",
        "structural_fingerprint": structural_fingerprint(registry),
        "qualification": checked,
        "authorities_granted": [],
        "external_messages": 0,
        "provider_sessions_created": 0,
        "et_detections_asserted": 0,
        "gd_measurements_asserted": 0
    }
    if args.probe:
        output["sources"] = [probe_one(row) for row in registry["sources"]]
    else:
        output["sources"] = [
            {"source_id": r["id"], "status": "NOT_RUN_NETWORK", "direct_probe": False}
            for r in registry["sources"]
        ]
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
