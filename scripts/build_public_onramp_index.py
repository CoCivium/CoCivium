#!/usr/bin/env python3
"""Build a source-pinned public GitHub page catalog. Never fabricate the 1,000th URL.

Standard library. Public GitHub metadata only. No credentials, private repos, files
outside public Git trees, prompt injection, or provider impersonation.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import quote

REPOS = ("CoCivium/CoCivium", "CoCivium/CoAcademy", "CoCivium/CoSources",
         "CoCivium/InSeed", "CoCivium/CoStacks", "CoCivium/EntMent", "CoCivium/CoBusMirror")
DOCUMENT_EXTENSIONS = (".md", ".html", ".htm", ".json", ".jsonl", ".txt")
DENY_SEGMENTS = {"private", "secrets", "secret", "credentials", "credential", "tokens",
                 "keys", "personal", "pii", "contact", "contacts", "emails",
                 "mail", "inbox", "downloads", "node_modules", "vendor", ".git"}
MAX_FILE_BYTES = 2_000_000
TOPICS = ("Onramp", "Architecture", "Operations", "UX", "Research", "Evolution",
          "Strategy", "Tests", "Examples", "AI", "Other")


def http_json(url: str):
    request = urllib.request.Request(url, headers={
        "User-Agent": "CoCivium-Public-Onramp-Indexer/1",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        if response.status != 200:
            raise RuntimeError("GITHUB_HTTP_HOLD")
        data = response.read(16_000_000 + 1)
    if len(data) > 16_000_000:
        raise RuntimeError("TREE_RESPONSE_TOO_LARGE_HOLD")
    return json.loads(data.decode("utf-8"))


def eligible(path, size):
    parts = [x.lower() for x in path.split("/")]
    if any(x in DENY_SEGMENTS or x.startswith(".") for x in parts):
        return False
    if path.startswith(("testdata/", "fixtures/", "archive/", "archives/")):
        return False
    if not path.lower().endswith(DOCUMENT_EXTENSIONS):
        return False
    return isinstance(size, int) and 0 <= size <= MAX_FILE_BYTES


def topic_for(path):
    lower = path.lower()
    for topic in TOPICS[:-1]:
        if topic.lower() in lower.split("/"):
            return topic
    if lower.startswith("ai/"):
        return "AI"
    if lower.startswith(("examples/", "docs/")):
        return "Examples" if lower.startswith("examples/") else "Research"
    return "Other"


def gather(fetch=http_json, repos=REPOS):
    result = []
    for repository in repos:
        # Public metadata readback. Pin exact default-branch HEAD SHA before trees.
        metadata = fetch(f"https://api.github.com/repos/{repository}")
        if metadata.get("private") is not False:
            raise RuntimeError("PUBLIC_REPOSITORY_NOT_VERIFIED")
        default_branch = metadata.get("default_branch")
        if not isinstance(default_branch, str) or not re.fullmatch(r"[A-Za-z0-9._/-]+", default_branch):
            raise RuntimeError("UNKNOWN_DEFAULT_BRANCH")
        branch = fetch(f"https://api.github.com/repos/{repository}/branches/{quote(default_branch, safe='')}")
        commit = branch.get("commit", {}).get("sha")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise RuntimeError("UNPINNED_SOURCE_HOLD")
        commit_data = fetch(f"https://api.github.com/repos/{repository}/git/commits/{commit}")
        tree_sha = commit_data.get("tree", {}).get("sha")
        if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
            raise RuntimeError("MISSING_GIT_TREE_SHA_HOLD")
        tree = fetch(f"https://api.github.com/repos/{repository}/git/trees/{tree_sha}?recursive=1")
        if tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
            raise RuntimeError("TRUNCATED_OR_MISSING_TREE_HOLD")
        for object_ in tree["tree"]:
            path = object_.get("path")
            if object_.get("type") != "blob" or not isinstance(path, str):
                continue
            if not eligible(path, object_.get("size")):
                continue
            blob = object_.get("sha")
            if not isinstance(blob, str) or not re.fullmatch(r"[0-9a-f]{40}", blob):
                raise RuntimeError("BLOB_SHA_MISSING_HOLD")
            encoded = "/".join(quote(seg, safe="-._~") for seg in path.split("/"))
            result.append({
                "repository": repository,
                "commit": commit,
                "path": path,
                "topic": topic_for(path),
                "blob_sha": blob,
                "size_bytes": object_["size"],
                "url": f"https://github.com/{repository}/blob/{commit}/{encoded}",
                "evidence_class": "PUBLIC_REPOSITORY_PATH_ONLY__NOT_CONTENT_QA",
            })
    # Ordered with stable sequence, no duplicated URL or invented result.
    result.sort(key=lambda x: (x["topic"], x["repository"], x["path"]))
    urls = [r["url"] for r in result]
    if len(urls) != len(set(urls)):
        raise RuntimeError("DUPLICATED_URL_HOLD")
    return result


def render(rows, min_pages):
    if len(rows) < min_pages:
        raise RuntimeError(f"INSUFFICIENT_VERIFIED_PUBLIC_PAGES_HOLD:{len(rows)}<{min_pages}")
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    page_lines = [
        "# CoGoAll 1,000+ source-pinned public page index",
        "",
        f"Generated UTC: {stamp}. Actual eligible source pages: **{len(rows)}**.",
        "Only public GitHub tree metadata was read. Pages are source paths, not independent human-reviewed insight claims.",
        "Do not load this entire index into an AI context; filter by topic, repository, and exact revision.",
        "",
    ]
    last = None
    for r in rows:
        if r["topic"] != last:
            last = r["topic"]
            page_lines.extend([f"## {last}", ""])
        page_lines.append(f"- [{r['repository']} / {r['path']}]({r['url']})")
    encoded_jsonl = "".join(json.dumps(r, sort_keys=True, separators=(",",":")) + "\n" for r in rows)
    encoded_md = "\n".join(page_lines) + "\n"
    receipt = {
        "schema": "CoGoAll.PublicSourcePageCatalog.R1",
        "status": "SOURCE_TREE_ENUMERATED_NOT_INDEPENDENT_PAGE_QA",
        "observed_at_utc": stamp,
        "count": len(rows),
        "repositories": sorted(set(r["repository"] for r in rows)),
        "jsonl_sha256": hashlib.sha256(encoded_jsonl.encode()).hexdigest(),
        "markdown_sha256": hashlib.sha256(encoded_md.encode()).hexdigest(),
        "excluded": "credential/private/PII-like paths, binaries, oversized files, truncated trees",
        "receiver_ack": "UNPROVEN",
    }
    return encoded_jsonl, encoded_md, receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--minimum-pages", type=int, default=1000)
    args = parser.parse_args()
    if args.minimum_pages < 1000:
        parser.error("minimum-pages must be at least 1000; no count inflation")
    rows = gather()
    jsonl, markdown, receipt = render(rows, args.minimum_pages)
    folder = Path(args.output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    # CI fresh workspace; fail if output exists, never clobber.
    for filename, content in (("public-pages.jsonl", jsonl),
                              ("public-pages.md", markdown),
                              ("receipt.json", json.dumps(receipt, indent=2) + "\n")):
        with (folder / filename).open("x", encoding="utf-8") as stream:
            stream.write(content)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
