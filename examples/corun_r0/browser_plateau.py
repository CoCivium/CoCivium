#!/usr/bin/env python3
"""CoLockStep+ browser regression: pinned public R0/R1 vs broken candidate.

Browser-only evidence. Reproduces a deliberate regression in a temporary copy,
rejects it, and preserves both original source files. It neither deploys nor
qualifies a user-facing MVP, and it creates no remote effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from playwright.sync_api import sync_playwright

PINS = {
    "R0": "7ecaa9e563bc57694b5f4e130a17655115ac4acd",
    "R1": "2d3a1248e63b409436b6def098755f93065ebebb",
}
TIMESTAMP_GUARD = "a.observed_utc===baseline.observed_utc"


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("utf-8")


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def browser_probe(root):
    directory = root / "examples/codemow"
    files = {
        name: (directory / ("truth-gate-" + name.lower() + ".html")).resolve(strict=True)
        for name in PINS
    }
    initial = {name: p.read_bytes() for name, p in files.items()}
    for name in PINS:
        require(git_blob(initial[name]) == PINS[name],
                name + ": source drift, do not overwrite predecessor")
    observations = []
    outbound = []
    errors = []

    def check(label, value, purpose):
        observations.append({"test": label, "pass": bool(value), "purpose": purpose})
        require(value, label + ": " + purpose)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        browser_version = browser.version
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.on("request", lambda req: outbound.append(req.url)
                if req.url.startswith(("https://", "http://")) else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        page.goto(files["R0"].as_uri())
        check("R0_BASELINE", page.locator("#passed").inner_text() == "4 / 4"
              and page.locator("#verdict").inner_text() == "QUALIFIED",
              "R0 baseline structurally passes")
        page.locator("#inject").click()
        check("R0_NEGATIVE", page.locator("#verdict").inner_text() == "FAIL CLOSED",
              "R0 unsupported X2 claim is rejected")
        page.locator("#reset").click()
        check("R0_RECOVERS", page.locator("#passed").inner_text() == "4 / 4"
              and page.locator("#verdict").inner_text() == "QUALIFIED",
              "R0 remains a working offline browser demonstration")

        page.goto(files["R1"].as_uri())
        check("R1_BASELINE", page.locator("#passed").inner_text() == "5 / 5"
              and page.locator("#verdict").inner_text() == "QUALIFIED",
              "R1 baseline structurally passes")
        check("R1_FRESHNESS_SCOPE",
              page.locator("#x2").inner_text() == "HELD"
              and "X2 receiver freshness remains UNVERIFIED"
              in page.locator("#freshness").inner_text(),
              "source-age display does not assert X2 health")
        page.locator("#inject").click()
        check("R1_NEGATIVE", page.locator("#verdict").inner_text() == "FAIL CLOSED"
              and page.locator("#passed").inner_text() == "4 / 5",
              "R1 unsupported X2 claim is rejected")
        page.locator("#reset").click()
        page.locator("summary").click()
        changed = json.loads(page.locator("#packet").input_value())
        changed["observed_utc"] = "2026-11-09T00:00:00Z"
        page.locator("#packet").fill(json.dumps(changed))
        page.locator("#verifyText").click()
        check("R1_TIMESTAMP_NEGATIVE",
              page.locator("#verdict").inner_text() == "FAIL CLOSED"
              and page.locator("#passed").inner_text() == "4 / 5",
              "R1 rejects made-up source freshness")
        page.locator("#packet").fill("{invalid-json")
        page.locator("#verifyText").click()
        check("R1_MALFORMED_NEGATIVE",
              page.locator("#verdict").inner_text() == "FAIL CLOSED",
              "R1 malformed packet is rejected")
        page.locator("#reset").click()
        check("R1_RECOVERS", page.locator("#passed").inner_text() == "5 / 5"
              and page.locator("#verdict").inner_text() == "QUALIFIED",
              "R1 resets to pinned source claim")
        check("MOBILE_NO_OVERFLOW",
              page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"),
              "narrow viewport does not overflow")

        # Red-team the new guard in a nonpersistent copy. Test harness must
        # demonstrate the mutant falsely passes before it can reject it.
        original = initial["R1"].decode("utf-8")
        require(original.count(TIMESTAMP_GUARD) == 1,
                "timestamp comparison changed; requires new test")
        mutant = original.replace(TIMESTAMP_GUARD, "true", 1)
        with tempfile.TemporaryDirectory(prefix="colockstep-mutation-") as td:
            unsafe_path = Path(td) / "UNSAFE_NOT_FOR_RELEASE.html"
            unsafe_path.write_text(mutant, encoding="utf-8")
            page.goto(unsafe_path.as_uri())
            page.locator("summary").click()
            page.locator("#packet").fill(json.dumps(changed))
            page.locator("#verifyText").click()
            false_green = (page.locator("#passed").inner_text() == "5 / 5"
                           and page.locator("#verdict").inner_text() == "QUALIFIED")
            check("BROKEN_SUCCESSOR_DETECTED", false_green,
                  "the deliberately weakened version falsely qualifies a new timestamp")
            bad_candidate = {
                "isolated_in_temporary_directory": True,
                "mutation": "REMOVE_TIMESTAMP_INTEGRITY_GUARD",
                "unsafe_success_reproduced": false_green,
                "decision": "REJECT_AND_RETAIN_R1",
                "runtime_switch": False,
            }

        page.goto(files["R1"].as_uri())
        check("R1_STILL_WORKS",
              page.locator("#passed").inner_text() == "5 / 5"
              and page.locator("#x2").inner_text() == "HELD",
              "rejected experimental sibling never clobbers R1")
        browser.close()

    for name, p in files.items():
        check(name + "_HASH_PRESERVED", p.read_bytes() == initial[name]
              and git_blob(p.read_bytes()) == PINS[name],
              "exact predecessor source remains byte-identical")
    check("NO_HTTP_REQUESTS", not outbound, "offline QA emitted no HTTP(S) calls")
    check("NO_PAGE_ERRORS", not errors, "browser emitted no JS exceptions")

    return {
        "schema": "CoCivium.CoLockStep.BrowserPlateauR0",
        "browser": {"engine": "chromium", "version": browser_version,
                    "viewport": [390, 844]},
        "sources": [
            {"version": name, "path": "examples/codemow/truth-gate-"
             + name.lower() + ".html", "git_blob_sha1": PINS[name],
             "sha256": hashlib.sha256(initial[name]).hexdigest()}
            for name in ("R0", "R1")
        ],
        "tests": observations,
        "passed": len(observations),
        "total": len(observations),
        "bad_candidate": bad_candidate,
        "preserved_originals": True,
        "qualified_mvp": False,
        "independent_user_accepted": "UNKNOWN",
        "off_provider_recovery": "NOT_TESTED",
        "X2_runtime": "UNVERIFIED",
        "external_effects": "NONE",
        "nonclaims": [
            "BROWSER_TEST_NE_HUMAN_RECEIVER_ADOPTION",
            "TEMPORARY_MUTANT_NE_PRODUCTION_ROLLBACK",
            "GITHUB_SOURCE_NE_INDEPENDENT_CUSTODY",
            "NO_MVP_OR_RUNTIME_RELEASE",
        ],
    }


def write_evidence(out, report):
    out.mkdir(parents=True, exist_ok=False)
    raw = canonical(report)
    data = out / "browser-plateau.json"
    receipt = out / "receipt.json"
    with data.open("xb") as handle:
        handle.write(raw)
    proof = {"schema": "CoCivium.CoLockStep.BrowserPlateauReceipt.R0",
             "report_sha256": hashlib.sha256(raw).hexdigest(),
             "report_bytes": len(raw), "state": "PASS_BROWSER_SCOPE_ONLY",
             "qualified_mvp": False, "receiver_ack": False}
    with receipt.open("xb") as handle:
        handle.write(canonical(proof))
    return data, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = browser_probe(args.repo_root)
        data, proof = write_evidence(args.out, report)
    except (OSError, AssertionError, ValueError) as err:
        print("HOLD_OR_FAIL_CLOSED:", err)
        return 2
    print(json.dumps({"status": "PASS_BROWSER_SCOPE_ONLY", "checks": report["total"],
                      "qualified_mvp": False, "report": str(data), "receipt": str(proof)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
