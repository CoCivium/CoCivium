"""CoMail R0: offline, deterministic, public-safe invitation -> versioned resource.

This library has no network, email, account, clipboard, keylogging or payment APIs.
No authority is inferred from a link, source code, opening an HTML file or a click.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "CoCivium.CoMail.LivingResource.R0"
DISALLOWED_EFFECTS = ("SENT", "DELIVERED", "ACKED", "SUBSCRIBED", "LIVE", "AUTHORIZED")


def json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_sha(text: str) -> str:
    return sha(text.encode("utf-8"))


def material(version: dict) -> dict:
    """Source bytes that define immutable content. Hash excludes the self-reference."""
    return {k: v for k, v in version.items() if k != "sha256"}


def digest_version(version: dict) -> str:
    return sha(json_bytes(material(version)))


def update_pins(fixture: dict) -> dict:
    for v in fixture["resource"]["versions"]:
        v["sha256"] = digest_version(v)
    fixture["fixed_message"]["sha256"] = sha(json_bytes({k: v for k, v in fixture["fixed_message"].items() if k != "sha256"}))
    fixture["resource"]["current_sha256"] = fixture["resource"]["versions"][-1]["sha256"]
    return fixture


def required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError(f"invalid {field}")
    return value


def timestamp(s: str) -> datetime:
    required(s, "timestamp")
    if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", s):
        raise ValueError("timestamp must be exact UTC Z")
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo != timezone.utc:
        raise ValueError("UTC required")
    return d


def validate(fixture: dict) -> dict:
    if not isinstance(fixture, dict) or fixture.get("schema") != SCHEMA:
        raise ValueError("schema mismatch")
    if fixture.get("visibility") != "PUBLIC_SAFE_SYNTHETIC":
        raise ValueError("not public-safe synthetic")
    expected_top={"schema","visibility","artifact_id","distribution","fixed_message","resource","source_contracts","nonclaims"}
    if set(fixture) != expected_top:
        raise ValueError("unexpected top-level fields")
    # A public-safe demo may never smuggle a real receiver address or outbound link.
    serialized=json.dumps(fixture, ensure_ascii=False)
    if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:https?://|mailto:)",serialized,re.I):
        raise ValueError("public fixture contains possible recipient or outbound link")
    required(fixture.get("artifact_id"), "artifact_id")
    if not fixture["artifact_id"].startswith("urn:co:comail:example:"):
        raise ValueError("not demonstration artifact")
    delivery = fixture.get("distribution", {})
    required_keys = {
        "auto_send": False,
        "actual_recipient_count": 0,
        "subscription_runtime": "NOT_CONFIGURED",
        "payment_runtime": "NOT_CONFIGURED",
        "feedback_runtime": "LOCAL_UNSENT_ONLY",
        "delivery_evidence": "NOT_SENT",
    }
    if set(delivery) != set(required_keys):
        raise ValueError("unexpected distribution field")
    for k, v in required_keys.items():
        if type(delivery.get(k)) is not type(v) or delivery.get(k) != v:
            raise ValueError("effect boundary: " + k)
    m = fixture.get("fixed_message", {})
    if set(m) != {"message_id","state","title","body","resource_ref","sha256"}:
        raise ValueError("unexpected fixed-message field")
    if m.get("state") != "SYNTHETIC_NOT_SENT":
        raise ValueError("fixed message was silently promoted to sent")
    for field in ("title", "body", "message_id"):
        required(m.get(field), "message." + field)
    if len(m["body"]) > 3000:
        raise ValueError("message too large")
    expected_message = sha(json_bytes({k: v for k, v in m.items() if k != "sha256"}))
    if m.get("sha256") != expected_message:
        raise ValueError("fixed historical message tampered")
    r = fixture.get("resource", {})
    if set(r) != {"resource_id","title","current","current_sha256","rights","epistemic_status","versions"}:
        raise ValueError("unexpected resource field")
    required(r.get("resource_id"), "resource_id")
    required(r.get("title"), "resource title")
    if m.get("resource_ref") != r.get("resource_id"):
        raise ValueError("fixed message points to wrong living resource")
    if r.get("rights") != "ORIGINAL_SYNTHETIC_DEMO; NO THIRD_PARTY CONTENT":
        raise ValueError("rights mismatch")
    if r.get("epistemic_status") != "DESIGN_CANDIDATE_NOT_DEPLOYED":
        raise ValueError("unproven status promoted")
    versions = r.get("versions")
    if not isinstance(versions, list) or not 2 <= len(versions) <= 8:
        raise ValueError("bounded version history required")
    prev_id, prev_time = None, None
    for i, v in enumerate(versions):
        if not isinstance(v,dict) or set(v) != {"id","predecessor","observed_at","headline","body","why_changed","evidence","state","sha256"}:
            raise ValueError("unexpected version shape")
        if not isinstance(v, dict):
            raise ValueError("bad version object")
        if v.get("id") != f"v{i}":
            raise ValueError("version identity or sequence mismatch")
        if v.get("predecessor") != prev_id:
            raise ValueError("predecessor mismatch")
        t = timestamp(v.get("observed_at"))
        if prev_time is not None and not t > prev_time:
            raise ValueError("version time reversed")
        for field in ("headline", "body", "why_changed", "evidence"):
            required(v.get(field), "version." + field)
        if v.get("state") != "DRAFT_REVIEWED_ONLY_BY_BUILDER":
            raise ValueError("version automatically promoted")
        if v.get("sha256") != digest_version(v):
            raise ValueError("version content hash mismatch")
        prev_id, prev_time = v["id"], t
    if r.get("current") != versions[-1]["id"] or r.get("current_sha256") != versions[-1]["sha256"]:
        raise ValueError("current pointer inconsistent")
    donors = fixture.get("source_contracts")
    if not isinstance(donors, list) or len(donors) != 3:
        raise ValueError("source-contract coverage")
    for d in donors:
        if not isinstance(d,dict) or set(d) != {"repo","path","blob_sha"}:
            raise ValueError("unexpected donor shape")
        if d.get("repo") != "CoCivium/CoCivium" or not re.fullmatch(r"[0-9a-f]{40}", d.get("blob_sha", "")):
            raise ValueError("source link identity or digest invalid")
        required(d.get("path"), "source path")
    if not isinstance(fixture.get("nonclaims"), list) or "NO_EMAIL_SENT" not in fixture["nonclaims"]:
        raise ValueError("nonclaims missing")
    for item in ("to", "from", "cc", "bcc", "subscriber_email", "credentials", "payment_url", "payment_account"):
        if item in fixture or item in m or item in delivery or item in r:
            raise ValueError("forbidden recipient/credential/payment key " + item)
    return {
        "status": "PASS_BOUNDED_SYNTHETIC_R0",
        "scope": "PUBLIC_SAFE_OFFLINE_NO_RECEIVER",
        "version_count": len(versions),
        "resource_id": r["resource_id"],
        "latest_sha256": r["current_sha256"],
        "immutable_message_sha256": m["sha256"],
        "actual_sends": 0,
        "actual_subscribers": 0,
        "payment_runtime": "NOT_CONFIGURED",
    }


def read_fixture(path: str | Path) -> dict:
    obj = json.loads(Path(path).read_text("utf-8"))
    validate(obj)
    return obj
