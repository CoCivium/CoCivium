#!/usr/bin/env python3
"""Bounded, read-only CoBeacon source/HTML gate. Python 3.12 standard library.

Run without network: python -B examples/cobeacon_useful_doors_r0/check.py
Optional remote currentness: add --remote to rehash 12 GitHub Raw objects.
No deploy, publish, account action, tracking or automatic correction.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "ai/beacon/experience-catalog-r0.json"
HTML = ROOT / "examples/cobeacon_useful_doors_r0/index.html"
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,55}$")
EMBED_RE = re.compile(
    r'<script id="experience-data" type="application/json">(.+?)</script>', re.S
)
DANGEROUS_JS = re.compile(
    r"\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon|"
    r"localStorage|sessionStorage|document\.cookie)\b"
)
TRACKS = {"START", "TRY", "EXPLORE", "LEARN", "BUILD"}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def validate_catalog(c: dict) -> None:
    require(c.get("schema") == "CoCivium.CoBeaconExperienceCatalog.R0", "schema")
    items = c.get("items")
    require(isinstance(items, list) and len(items) == 12, "bounded inventory")
    ids = [x.get("id") for x in items]
    require(len(ids) == len(set(ids)), "duplicate ids")
    require(all(isinstance(x, str) and ID_RE.fullmatch(x) for x in ids), "invalid ids")
    require(c.get("default_id") in ids, "missing default")
    require(sorted(x.get("rank") for x in items) == list(range(1, len(items) + 1)), "editorial ranks")
    require("NOT_RELEASE" in c.get("state", ""), "status honesty")
    require(c.get("release_policy", {}).get("executables", "").startswith("HELD_"), "installer gate")
    require(c.get("release_policy", {}).get("receiver", "").startswith("HELD_"), "receiver gate")
    for x in items:
        require(x.get("track") in TRACKS, "track " + str(x.get("id")))
        require(bool(x.get("title")) and bool(x.get("promise")) and bool(x.get("action")), "reader value")
        require(x.get("public_installer") is False, "unqualified installer")
        require(x.get("independent_first_use") == "HELD_NO_INDEPENDENT_RECEIVER_ACK", "receiver overclaim")
        require(SHA1_RE.fullmatch(str(x.get("blob_sha1", ""))) is not None, "sha missing " + str(x.get("id")))
        repo, ref, path = x["repo"], x["ref"], x["path"]
        require(repo in {"CoCivium/CoCivium", "CoCivium/CoAcademy"}, "non-elected repo")
        require(ref in {"main", "master"}, "non-elected ref")
        require(path and not path.startswith("/") and ".." not in Path(path).parts, "unsafe path")
        expected = f"https://github.com/{repo}/blob/{ref}/{path}"
        raw = f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"
        require(x.get("source_url") == expected, "source URL mismatch " + x["id"])
        require(x.get("raw_source_url") == raw, "raw URL mismatch " + x["id"])
        require(x.get("state", "").startswith(("SOURCE_VERIFIED", "OFFLINE_SOURCE_VERIFIED")),
                "unsupported source state " + x["id"])
    channels = c.get("distribution_channels", [])
    require({x.get("id") for x in channels} >=
            {"github", "owned_web", "pages", "youtube", "wetube", "substack", "rss", "education"},
            "channel coverage")
    for entry in channels:
        if entry["id"] not in ("github", "education"):
            require(entry["state"] != "DEPLOYED", "unverified channel promotion")
    require(c.get("selection_policy", {}).get("no_tracking") is True, "tracking policy")
    require(c.get("selection_policy", {}).get("no_unconsented_outreach") is True, "outreach policy")


def validate_html(c: dict, html: str) -> None:
    match = EMBED_RE.search(html)
    require(match is not None, "embedded catalog absent")
    embedded = json.loads(match.group(1))
    require(embedded == c, "HTML and catalog source diverged")
    require(DANGEROUS_JS.search(html) is None, "network/storage/surveillance JS detected")
    require(re.search(r"<script[^>]+\bsrc\s*=", html, re.I) is None, "external script")
    for part in ('<html lang="en">', "<main", "<h1", 'id="search"', 'id="cards"',
                 'aria-live="polite"', 'aria-pressed="true"', "prefers-reduced-motion:reduce"):
        require(part in html, "missing accessible element " + part)
    require("not a verified deployment" not in html.lower() or "not" in html.lower(), "claim review")


def self_test(c: dict, html: str) -> int:
    checks = 0
    validate_catalog(c)
    validate_html(c, html)
    checks += 2

    for transform in (
        lambda x: x["items"][0].update(blob_sha1="bad"),
        lambda x: x["items"][1].update(id=x["items"][0]["id"]),
        lambda x: x["items"][2].update(public_installer=True),
        lambda x: x["items"][3].update(independent_first_use="ACKED"),
        lambda x: x["items"][4].update(source_url="https://example.invalid"),
        lambda x: x["release_policy"].update(executables="LIVE_UNREVIEWED"),
    ):
        mutant = copy.deepcopy(c)
        transform(mutant)
        try:
            validate_catalog(mutant)
        except ValueError:
            checks += 1
        else:
            raise AssertionError("mutation was not rejected")
    for mutation in (
        html.replace('id="search"', 'id="gone"', 1),
        html.replace("document.createElement", "fetch('https://example.invalid');document.createElement", 1),
        html.replace(c["items"][0]["title"], "BROKEN_TITLE", 1),
    ):
        try:
            validate_html(c, mutation)
        except (ValueError, json.JSONDecodeError):
            checks += 1
        else:
            raise AssertionError("HTML mutation was not rejected")
    return checks


def remote_check(c: dict) -> list[dict]:
    results = []
    for x in c["items"]:
        url = x["raw_source_url"]
        parsed = urlsplit(url)
        require(parsed.scheme == "https" and parsed.hostname == "raw.githubusercontent.com", "unsafe source host")
        request = urllib.request.Request(url, headers={"User-Agent": "CoCivium-CoBeacon-R0-readonly"})
        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read(2_000_001)
        require(len(data) <= 2_000_000, "source size cap")
        sha = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        results.append({"id": x["id"], "match": sha == x["blob_sha1"], "observed_git_blob": sha})
        require(sha == x["blob_sha1"], "source drift " + x["id"])
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", action="store_true", help="Read-only external GitHub source currentness")
    args = ap.parse_args()
    c = json.loads(CATALOG.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")
    checks = self_test(c, html)
    print(json.dumps({"schema": "CoBeacon.TestReceipt.R0",
                      "local": "PASS", "checks": checks,
                      "items": len(c["items"]),
                      "remote": "NOT_RUN" if not args.remote else "RUNNING",
                      "effects": {"publish": 0, "send": 0, "installer": 0},
                      "nonclaims": ["VALIDATION_IS_NOT_ACCEPTANCE",
                                    "SOURCE_VERIFIED_NE_DEPLOYED",
                                    "NO_RECEIVER_ACK"]}, sort_keys=True))
    if args.remote:
        result = remote_check(c)
        print(json.dumps({"remote": "PASS", "observed": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, AssertionError, urllib.error.URLError, json.JSONDecodeError) as e:
        print("CoBeacon FAIL_SCOPED:", str(e), file=sys.stderr)
        sys.exit(1)
