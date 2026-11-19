"""CoSites R0 bounded live-root readiness and privacy classifier.

This script observes SIX fixed public HTTPS domain roots ONLY, without login,
cookies, redirect follow, metadata shard traversal, DNS edits, publication,
tracking or raw HTML export. It does not prove visitor acceptance, privacy
clearance, domain ownership, or authorization to release.

Use once in ephemeral GitHub CI, not as a resident X2 watcher.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import (
    HTTPRedirectHandler, Request, build_opener,
)

SCHEMA = "CoSites.ThreeFlagship.LiveRootPrivacyProbe.R0"
MAX_BODY_BYTES = 131072
FETCH_TIMEOUT_SECONDS = 12
ROOTS = (
    ("CoCivium", "apex", "cocivium.org"),
    ("CoCivium", "www", "www.cocivium.org"),
    ("InSeed", "apex", "inseed.com"),
    ("InSeed", "www", "www.inseed.com"),
    ("CoPolitic", "apex", "copolitic.org"),
    ("CoPolitic", "www", "www.copolitic.org"),
)

ROOT_HOSTS = frozenset(h for _, _, h in ROOTS)
WINDOWS_PATH_PATTERN = re.compile(
    r"\b[A-Za-z]:\\(?:Users|CoCivium|Windows|ProgramData)\\", re.IGNORECASE
)
HIGH_CONFIDENCE_SECRET = re.compile(
    r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|"
    r"(?<![A-Za-z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Za-z0-9])"
)
WORD_PATTERN = re.compile(r"\b[A-Za-z]{3,}\b")


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # The caller records the redirection class only, not the raw Location.
        return None


class PageEvidence(HTMLParser):
    """Minimal structural count. Never stores user-visible data."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.nav_count = 0
        self.anchor_count = 0
        self.form_count = 0
        self.script_count = 0
        self._ignored = 0
        self._visible_chars = []

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1_count += 1
        elif tag == "nav":
            self.nav_count += 1
        elif tag == "a":
            self.anchor_count += 1
        elif tag == "form":
            self.form_count += 1
        elif tag == "script":
            self.script_count += 1
        if tag in ("style", "script"):
            self._ignored += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self._ignored:
            self._ignored -= 1

    def handle_data(self, data):
        if not self._ignored:
            self._visible_chars.append(data)

    def word_count(self):
        return len(WORD_PATTERN.findall(" ".join(self._visible_chars)))


def classify_html(body: bytes) -> dict:
    """Pure, bounded, privacy-redacted page classification."""
    parsed = PageEvidence()
    document = body.decode("utf-8", errors="replace")
    parsed.feed(document)
    lower = document.casefold()
    marks = []
    if WINDOWS_PATH_PATTERN.search(document):
        marks.append("LOCAL_WINDOWS_PATH_ON_PUBLIC_ROOT")
    if HIGH_CONFIDENCE_SECRET.search(document):
        marks.append("SECRET_LIKE_TOKEN_PATTERN_ON_ROOT_REQUIRES_PRIVATE_REVIEW")
    if ("files indexed:" in lower and "shards/shard_" in lower) or (
        "coinfra260610 bulk static direct-view site candidate" in lower
    ):
        marks.append("PUBLISHED_TECHNICAL_INDEX")
    if "not_public_hosted" in lower:
        marks.append("PUBLIC_PAGE_CLAIMS_NOT_PUBLIC_HOSTED")
    if parsed.word_count() < 80:
        marks.append("TOO_LITTLE_VISIBLE_EXPLANATION_FOR_FIRST_USE")
    if parsed.h1_count != 1:
        marks.append("H1_COUNT_NOT_ONE")
    if parsed.form_count or parsed.script_count:
        marks.append("FORMS_OR_SCRIPTS_REQUIRE_SEPARATE_SCOPE_REVIEW")
    return {
        "html_h1_count": parsed.h1_count,
        "html_nav_count": parsed.nav_count,
        "html_anchor_count": parsed.anchor_count,
        "visible_word_count": parsed.word_count(),
        "forms": parsed.form_count,
        "scripts": parsed.script_count,
        "privacy_review_flags": sorted(marks),
        "source_first_use_sufficient": False,
        "human_first_use_accepted": False,
    }


def result_shell(site: str, label: str, host: str) -> dict:
    return {
        "site": site,
        "variant": label,
        "hostname": host,
        "http_status": None,
        "classification": "HOLD_UNOBSERVED",
        "content_type": "NOT_OBSERVED",
        "html_bytes": None,
        "html_sha256": None,
        "redirect_target_class": None,
        "privacy_review_flags": [],
        "source_first_use_sufficient": False,
        "human_first_use_accepted": False,
    }


def safe_redirect_class(raw: str | None) -> str:
    if not raw:
        return "REDIRECT_TARGET_MISSING"
    parsed = urlparse(raw)
    # Never report arbitrary Location text, query strings, or paths.
    if parsed.scheme == "https" and parsed.hostname in ROOT_HOSTS and parsed.path in ("", "/"):
        return "APPROVED_HOST_ROOT_REDIRECT_NOT_FOLLOWED"
    return "OUTSIDE_APPROVED_ROOT_SCOPE_NOT_FOLLOWED"


def observe(site: str, variant: str, host: str, opener) -> dict:
    if host not in ROOT_HOSTS or variant not in ("apex", "www"):
        raise ValueError("HOLD_UNAPPROVED_HOST")
    row = result_shell(site, variant, host)
    req = Request(
        "https://" + host + "/",
        headers={
            "User-Agent": "CoSitesReadOnlyRootCheck-R0/1.0",
            "Accept": "text/html",
            "Cookie": "",
        },
        method="GET",
    )
    try:
        with opener.open(req, timeout=FETCH_TIMEOUT_SECONDS) as r:
            status = int(r.status)
            row["http_status"] = status
            ctype = r.headers.get_content_type().lower()
            row["content_type"] = "TEXT_HTML" if ctype == "text/html" else "OTHER"
            if status != 200:
                row["classification"] = "HOLD_NON200_HTTP"
            elif ctype != "text/html":
                row["classification"] = "HOLD_NON_HTML_ROOT"
            else:
                data = r.read(MAX_BODY_BYTES + 1)
                if len(data) > MAX_BODY_BYTES:
                    row["classification"] = "HOLD_TOO_LARGE_ROOT_NO_BODY_RETAINED"
                else:
                    row["html_bytes"] = len(data)
                    row["html_sha256"] = hashlib.sha256(data).hexdigest()
                    page = classify_html(data)
                    row.update(page)
                    row["classification"] = (
                        "HOLD_PUBLIC_METADATA_OR_PRIVACY_REVIEW"
                        if page["privacy_review_flags"] else
                        "HTTP_200_HTML_STRUCTURE_OBSERVED_NOT_ACCEPTED"
                    )
    except HTTPError as exc:
        row["http_status"] = int(exc.code)
        if 300 <= exc.code <= 399:
            row["classification"] = "HOLD_REDIRECT_NOT_FOLLOWED"
            row["redirect_target_class"] = safe_redirect_class(exc.headers.get("Location"))
        else:
            row["classification"] = "HOLD_HTTP_ERROR"
    except (URLError, TimeoutError, OSError):
        row["classification"] = "HOLD_NETWORK_OR_TLS_UNAVAILABLE"
    return row


def self_test() -> None:
    technical = b"""<html><body><h1>CoInfra260610 Bulk Static Direct-View Site Candidate</h1>
    Files indexed: 100000 <a href="shards/shard_00001.json">list</a>
    <p>NOT_PUBLIC_HOSTED</p><p>Source root: D:\CoCivium\CoFarm\</p></body></html>"""
    x = classify_html(technical)
    assert "PUBLISHED_TECHNICAL_INDEX" in x["privacy_review_flags"]
    assert "LOCAL_WINDOWS_PATH_ON_PUBLIC_ROOT" in x["privacy_review_flags"]
    assert "PUBLIC_PAGE_CLAIMS_NOT_PUBLIC_HOSTED" in x["privacy_review_flags"]
    assert x["source_first_use_sufficient"] is False
    assert x["human_first_use_accepted"] is False
    assert "D:\\CoCivium" not in json.dumps(x)
    assert safe_redirect_class("https://www.cocivium.org/") == (
        "APPROVED_HOST_ROOT_REDIRECT_NOT_FOLLOWED"
    )
    assert safe_redirect_class("https://evil.example/steal?q=password") == (
        "OUTSIDE_APPROVED_ROOT_SCOPE_NOT_FOLLOWED"
    )
    safe = classify_html(b"<html lang='en'><h1>Test</h1>" +
        (b"<p>Checkable public explanation and an accessible place to learn more.</p>" * 15) +
        b"</html>")
    assert safe["privacy_review_flags"] == []
    assert safe["human_first_use_accepted"] is False
    assert result_shell("InSeed", "apex", "inseed.com")["classification"] == "HOLD_UNOBSERVED"
    assert all(host and host in ROOT_HOSTS for _, _, host in ROOTS)
    print("PASS_ROOT_ONLY_FAIL_CLOSED_CLASSIFIER_SELF_TEST")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", default="out/cosites261119-live-root-r0.json")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    opener = build_opener(NoRedirects)
    rows = [observe(site, label, host, opener) for site, label, host in ROOTS]
    report = {
        "schema": SCHEMA,
        "state": "BOUNDED_PUBLIC_ROOT_OBSERVATIONS_RELEASE_HOLD",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "observer": "EPHEMERAL_GITHUB_ACTIONS_RUNNER_NOT_INDEPENDENT_SECURITY_REVIEW",
        "scope": {
            "https_roots_checked": len(rows),
            "approved_hostnames": [host for _, _, host in ROOTS],
            "maximum_body_bytes_per_root": MAX_BODY_BYTES,
            "timeout_seconds_per_root": FETCH_TIMEOUT_SECONDS,
            "no_follow_redirect": True,
            "no_shard_traversal": True,
            "no_raw_body_export": True,
            "no_auth_or_config_writes": True,
        },
        "records": rows,
        "release_authorized": False,
        "privacy_cleared": False,
        "human_first_use_accepted": False,
        "next": "PRIVATE_OWNER_SECURITY_REVIEW_OF_WWW_TECH_INDEX_THEN_INDEPENDENT_HOST_AND_FIRST_USE_CHECK",
        "nonclaims": [
            "SINGLE_CI_VANTAGE_NOT_THREE_INDEPENDENT_ROOTS",
            "HTTP_200_NE_HUMAN_USABILITY",
            "TECHNICAL_INDEX_NE_PRIVACY_CLEARED",
            "NO_PUBLIC_RELEASE", "NO_HOST_MUTATION", "NO_X2_RUNTIME",
            "LOCAL_IS_NOT_LANDED", "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF", "NO_COEX",
            "NO_PHANTOM_ACK",
        ],
    }
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": report["state"],
        "observations": len(rows),
        "summary": [
            {"site": r["site"], "variant": r["variant"],
             "status": r["http_status"], "classification": r["classification"]}
            for r in rows
        ],
        "output": str(dest),
        "release_authorized": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
