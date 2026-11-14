#!/usr/bin/env python3
"""CoAll session public-derivative R0 gate. Pure, no provider access or publishing.

Accept ONLY a deliberately curated, bounded candidate. Never ingest raw chat
transcripts here. Passing structural checks is NOT a privacy, rights, consent,
receiver, restoration or release certification. Unknown fields fail closed.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit

SCHEMA = "CoAll.SessionPublicDerivative.CandidateR0"
FIELDS = {
    "schema", "public_work_id", "title", "summary", "evidence_urls",
    "candidate_scope", "history_coverage",
}
ID = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{2,80}\Z")
RISK = (
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b(?:\+?\d[\s.-]?){9,14}\d\b"),
    re.compile(r"(?i)\b(?:password|api[_ -]?key|bearer|access[_ -]?token|secret|ssn)\b"),
    re.compile(r"(?i)\b(?:sk-|ghp_|github_pat_|xox[baprs]-)[A-Za-z0-9_-]{4,}"),
    re.compile(r"(?i)(?:(?<![A-Za-z])[A-Za-z]:[\\/]|/(?:home|Users|private|mnt)/)"),
    re.compile(r"(?i)(?:chatgpt\.com/c/|chat\.openai\.com/c/|file://|localhost)"),
    re.compile(r"<[^>]*>"),
)
NONCLAIMS = [
    "CANDIDATE_NE_PUBLICATION",
    "REDACTION_NE_PRIVACY_CLEARANCE",
    "PUBLIC_DERIVATIVE_NE_COMPLETE_TRANSCRIPT",
    "STRUCTURAL_PASS_NE_RIGHTS_OR_CONSENT",
    "SOURCE_HASH_NE_PUBLIC_METADATA",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_PROVIDER_EXPORT_OR_DELETE_EFFECT",
]


def unsafe_text(value: object, limit: int) -> bool:
    if not isinstance(value, str) or not 1 <= len(value) <= limit:
        return True
    if unicodedata.normalize("NFKC", value) != value:
        return True
    if any(unicodedata.category(c)[0] == "C" for c in value):
        return True
    return any(p.search(value) for p in RISK)


def safe_public_ref(value: object) -> bool:
    if not isinstance(value, str) or not 30 <= len(value) <= 450:
        return False
    if unsafe_text(value, 450) or "%" in value:
        return False
    try:
        u = urlsplit(value)
    except ValueError:
        return False
    if (u.scheme != "https" or u.netloc != "github.com"
            or u.username or u.password or u.query or u.fragment):
        return False
    parts = u.path.split("/")
    return (len(parts) >= 5
            and parts[1:3] == ["CoCivium", "CoCivium"]
            and parts[3] in {"blob", "issues", "pull"}
            and all(part not in {"", ".", ".."} for part in parts[1:]))


def review_candidate(payload: object) -> dict:
    """Fail closed. Returns a LOCAL review preview, never publication authority.

    The caller must keep the result private until independently reviewed.
    Neither source content nor candidate text is echoed on an invalid input.
    """
    holds = set()
    if not isinstance(payload, dict) or set(payload) != FIELDS:
        holds.add("HELD_UNKNOWN_OR_MISSING_FIELDS")
    else:
        if payload["schema"] != SCHEMA:
            holds.add("HELD_SCHEMA")
        if (not isinstance(payload["public_work_id"], str)
                or not ID.fullmatch(payload["public_work_id"])):
            holds.add("HELD_PUBLIC_WORK_ID")
        if unsafe_text(payload["title"], 100):
            holds.add("HELD_TITLE_RISK")
        if unsafe_text(payload["summary"], 600):
            holds.add("HELD_SUMMARY_RISK")
        if payload["candidate_scope"] not in {
            "SYNTHETIC_CI_ONLY", "CURATED_PRIVATE_REVIEW"
        }:
            holds.add("HELD_SCOPE")
        if payload["history_coverage"] not in {"UNKNOWN", "BOUNDED_PARTIAL"}:
            holds.add("HELD_UNSUPPORTED_COMPLETENESS")
        refs = payload["evidence_urls"]
        if (not isinstance(refs, list) or not 1 <= len(refs) <= 8
                or len(set(map(str, refs))) != len(refs)
                or not all(safe_public_ref(x) for x in refs)):
            holds.add("HELD_PUBLIC_EVIDENCE_REFS")
    base = {
        "schema": "CoAll.SessionPublicDerivative.ReviewReceiptR0",
        "effect": "NONE", "publication_authorized": False,
        "provider_sessions_accessed": 0, "provider_sessions_deleted": 0,
        "receiver_ack": "NOT_ESTABLISHED", "cold_restore": "NOT_TESTED",
        "history_completeness": "UNKNOWN", "nonclaims": NONCLAIMS,
    }
    if holds:
        return {**base, "state": "HOLD_UNQUALIFIED_INPUT",
                "holds": sorted(holds), "local_preview": None}
    return {
        **base,
        "state": "HOLD_INDEPENDENT_PRIVACY_RIGHTS_CONSENT_REVIEW",
        "holds": [
            "HELD_PRIVACY_REVIEW", "HELD_RIGHTS_REVIEW",
            "HELD_CONSENT_REVIEW", "HELD_RELEASE_AUTHORITY",
        ],
        "local_preview": {
            "work_id": payload["public_work_id"],
            "title": payload["title"],
            "summary": payload["summary"],
            "evidence_urls": sorted(payload["evidence_urls"]),
            "coverage": payload["history_coverage"],
        },
    }
