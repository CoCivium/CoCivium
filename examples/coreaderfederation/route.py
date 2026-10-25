#!/usr/bin/env python3
"""CoReaderFederation R0: deterministic, explicit-interest, nontracking source router.

No web calls, analytics, inferred profiles, publishing, AI calls, automatic
notifications, temporary link destruction, or effect authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "CoReaderFederation.Catalog.R0"
DEFAULT_CATALOG = Path(__file__).with_name("catalog.json")


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":")).encode("utf-8")).hexdigest()


def utc_datetime(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamps must be ISO-8601 strings with timezone")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("invalid ISO-8601 timestamp") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return result.astimezone(timezone.utc)


def safe_public_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    u = urlparse(value)
    return (u.scheme == "https" and u.netloc == "github.com"
        and u.username is None and u.password is None
        and not u.fragment and not u.query and u.path.startswith("/CoCivium/"))


def validate_catalog(catalog: dict) -> None:
    if not isinstance(catalog, dict) or catalog.get("schema") != SCHEMA:
        raise ValueError("unrecognized catalog")
    entries = catalog.get("entries")
    if not isinstance(entries, list) or not 0 < len(entries) <= 100:
        raise ValueError("catalog must contain 1-100 entries")
    for field in ("topics", "audiences", "formats"):
        values = catalog.get(field)
        if (not isinstance(values, list) or not values
            or not all(isinstance(x, str) and x.strip() for x in values)
            or len(set(values)) != len(values)):
            raise ValueError("invalid catalog taxonomy: " + field)
    if catalog.get("illustrative_scale", {}).get("raw_product") != str(10 ** 12):
        raise ValueError("illustrative scale must not silently change")
    ids = set()
    for page in entries:
        if not isinstance(page, dict):
            raise ValueError("entry must be a record")
        if not all(isinstance(page.get(f), str) and page[f].strip()
                   for f in ("id", "title", "teaser", "git_blob_sha", "publication_state")):
            raise ValueError("entry has missing identity or status")
        if page["id"] in ids:
            raise ValueError("duplicate entry id")
        ids.add(page["id"])
        if (len(page["git_blob_sha"]) != 40
            or any(c not in "0123456789abcdef" for c in page["git_blob_sha"])):
            raise ValueError("invalid source blob SHA")
        if not safe_public_url(page.get("source_url")):
            raise ValueError("public source must use allowed GitHub URL")
        for field in ("topics", "audiences", "formats"):
            values = page.get(field)
            if (not isinstance(values, list) or not values
                or not set(values).issubset(set(catalog[field]))):
                raise ValueError("entry has an unknown " + field)
        if page.get("offer") is not None:
            offer = page["offer"]
            if not isinstance(offer, dict) or set(offer) != {
                "starts_at", "ends_at", "offer_url", "evidence_url", "archive_url"
            }:
                raise ValueError("offer must have full, evidence-bound expiry data")
            start, end = utc_datetime(offer["starts_at"]), utc_datetime(offer["ends_at"])
            if start >= end:
                raise ValueError("offer end must be after start")
            if any(not safe_public_url(offer[key]) for key in
                   ("offer_url", "evidence_url", "archive_url")):
                raise ValueError("offer links must be verifiable public-source URLs")


def offer_projection(offer: dict | None, now: datetime) -> dict:
    if offer is None:
        return {"state": "NONE", "offer_url": None, "archive_url": None}
    start, end = utc_datetime(offer["starts_at"]), utc_datetime(offer["ends_at"])
    state = "UPCOMING" if now < start else "EXPIRED" if now >= end else "ACTIVE"
    return {
        "state": state,
        "offer_url": offer["offer_url"] if state == "ACTIVE" else None,
        "archive_url": offer["archive_url"],
        "evidence_url": offer["evidence_url"],
        "starts_at": offer["starts_at"],
        "ends_at": offer["ends_at"],
    }


def preview(catalog: dict, interests: list[str], audience: str,
            format_name: str, update_mode: str, as_of: str,
            limit: int = 4) -> dict:
    validate_catalog(catalog)
    if not isinstance(interests, list) or any(
        not isinstance(i, str) or i not in catalog["topics"] for i in interests
    ):
        raise ValueError("unknown interest; interests must be explicitly selected")
    if len(set(interests)) != len(interests):
        raise ValueError("duplicate interest")
    if audience not in catalog["audiences"] or format_name not in catalog["formats"]:
        raise ValueError("unknown audience or format")
    if update_mode not in ("SNAPSHOT", "LATEST_POINTER", "DIFF_AVAILABLE"):
        raise ValueError("unknown update mode")
    if type(limit) is not int or not 0 <= limit <= 10:
        raise ValueError("limit must be 0..10")
    now = utc_datetime(as_of)
    ranked = []
    for page in catalog["entries"]:
        overlap = sorted(set(page["topics"]) & set(interests))
        if interests and not overlap:
            continue
        score = 10 * len(overlap) + 3 * (audience in page["audiences"]) + 2 * (
            format_name in page["formats"])
        ranked.append((score, page["id"], overlap, page))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    candidates = []
    for score, _, overlap, page in ranked[:limit]:
        candidates.append({
            "id": page["id"],
            "title": page["title"],
            "teaser": page["teaser"],
            "rank_reason": {"declared_topic_matches": overlap,
                            "audience_match": audience in page["audiences"],
                            "format_match": format_name in page["formats"],
                            "score": score},
            "public_source_url": page["source_url"],
            "source_git_blob_sha": page["git_blob_sha"],
            "source_pointer_freshness": "NOT_LIVE_VERIFIED",
            "publication_state": page["publication_state"],
            "offer": offer_projection(page.get("offer"), now),
            "historical_source_preserved": True,
            "observed_version_recovery": "REQUIRES_EXACT_GIT_BLOB_FETCH_AND_READPROOF",
        })
    selection = {"declared_interests": interests, "audience": audience,
                 "format": format_name, "update_mode": update_mode,
                 "as_of": now.isoformat(), "limit": limit}
    return {
        "schema": "CoReaderFederation.RoutePreview.R0",
        "state": "READ_ONLY_CANDIDATES__NO_PUBLISH_OR_READER_PROFILE",
        "selection": selection,
        "catalog_sha256": fingerprint(catalog),
        "illustrative_space": catalog["illustrative_scale"],
        "selected_count": len(candidates),
        "candidates": candidates,
        "privacy": {"inferred_interests": False, "cookies": False,
                    "click_tracking": False, "subscriptions_created": 0,
                    "messages_sent": 0},
        "effects": {"publications": 0, "source_mutations": 0,
                    "workers_started": 0, "reader_notifications": 0},
        "feedback_path": "REVIEW_OR_CHALLENGE_IN_EXISTING_AUTHORIZED_CHANNEL__NO_AUTOPROMOTION",
        "nonclaims": [
            "TRILLION_CONFIGURATIONS_NE_TRILLION_MEANINGFUL_PAGES",
            "SOURCE_BLOB_SHA_NE_VERIFIED_IMMUTABLE_PUBLIC_PERMALINK",
            "POTENTIAL_INTEREST_NE_CONSENT",
            "READING_NE_AUTOMATIC_SOURCE_MUTATION",
            "DIFF_AVAILABLE_NE_ACTUAL_PUSH_OR_LIVE_DIFF",
            "EXPIRED_OFFER_NE_EXPIRED_EVIDENCE",
            "ROUTE_PREVIEW_NE_SUBSTACK_PUBLICATION",
            "RANK_NE_GUARANTEED_ENGAGEMENT_OR_VIRALITY",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--interest", action="append", default=[])
    parser.add_argument("--audience", default="curious")
    parser.add_argument("--format", dest="format_name", default="text")
    parser.add_argument("--mode", default="SNAPSHOT")
    parser.add_argument("--as-of", default="2026-10-25T00:00:00Z")
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()
    result = preview(json.loads(args.catalog.read_text(encoding="utf-8")),
                     args.interest, args.audience, args.format_name, args.mode,
                     args.as_of, args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
