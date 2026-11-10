#!/usr/bin/env python3
"""Bounded first-task browser evidence for the public CoPreCursor source.

Checks visible browser interaction, consent and privacy on an immutable source
blob.  It deliberately does NOT claim independent human acceptance, a hosted
release, cross-device retention, first-use usefulness, or CoStead custody.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

SOURCE_PATH = "examples/coprecursor/index.html"
GIT_BLOB_SHA1 = "773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101"
INITIAL = "Test one CoMap relation, then "
SENTINEL = "PRIVATE_DO_NOT_RECORD_20261109_MOCK"


def canonical(payload):
    return (json.dumps(payload, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def blob_sha1(raw):
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw
    ).hexdigest()


def test_browser(repo_root):
    source = (repo_root / SOURCE_PATH).resolve(strict=True)
    original = source.read_bytes()
    if blob_sha1(original) != GIT_BLOB_SHA1:
        raise AssertionError("source drift, hold current-head qualification")
    checks, outbound, errors = [], [], []

    def check(name, condition, reason):
        checks.append({"name": name, "pass": bool(condition), "meaning": reason})
        if not condition:
            raise AssertionError(name + ": " + reason)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        version = browser.version
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.on("request", lambda r: outbound.append(r.url)
                if r.url.startswith(("https://", "http://")) else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(source.as_uri())
        draft = page.locator("#draft")
        initial = draft.input_value()
        check("FIRST_LOAD", initial == INITIAL
              and page.locator("#accept").is_disabled()
              and page.locator("#undo").is_disabled(),
              "public fictional task starts from a no-effect state")
        check("NARROW_SCREEN",
              page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"),
              "390px viewport does not horizontally overflow")

        page.locator("#preview").click()
        continuation = page.locator("#prediction").inner_text()
        check("PREVIEW_SHADOW_ONLY",
              "typed relation" in continuation
              and draft.input_value() == initial
              and page.locator("#accept").is_enabled()
              and page.locator("#prediction-state").inner_text().startswith("SHADOW"),
              "prediction visible before modification, not auto-accepted")

        page.locator("#accept").click()
        after_accept = draft.input_value()
        check("EXPLICIT_ACCEPT_LOCAL_ONLY",
              after_accept == initial + continuation
              and page.locator("#map-state").inner_text().endswith("Receiver still HELD.")
              and page.locator("#undo").is_enabled(),
              "click changes only this editor and receiver remains held")
        page.locator("#undo").click()
        check("EXACT_UNDO",
              draft.input_value() == initial
              and page.locator("#undo").is_disabled(),
              "undo returns exact pre-acceptance contents")

        page.locator("#preview").click()
        before_reject = draft.input_value()
        page.locator("#reject").click()
        check("REJECT_NO_EFFECT",
              draft.input_value() == before_reject
              and page.locator("#accept").is_disabled(),
              "reject preserves original text")

        draft.fill(SENTINEL)
        check("SYNTHETIC_PRIVATE_INPUT",
              draft.input_value() == SENTINEL,
              "test private marker exists only in local demo editor")
        page.locator("#receipt").click()
        receipt_text = page.locator("#receipt-output").inner_text()
        receipt = json.loads(receipt_text)
        check("RECEIPT_NO_PRIVATE_CONTENT",
              SENTINEL not in receipt_text
              and receipt.get("raw_included") is False
              and receipt.get("effects") == 0
              and receipt.get("remote_receivers") == 0,
              "receipt contains counts but excludes source text")
        check("RECEIPT_NOT_AUTHORITY",
              receipt.get("authority") == "NONE"
              and "LOCAL_RECEIPT_NE_PROVIDER_ACK" in
              receipt.get("claim_boundary", ""),
              "local receipt cannot promote receiver ACK")

        page.locator('[data-mode="ambient"]').click()
        check("AMBIENT_NO_VISIBLE_PRIVATE_EDITOR",
              not page.locator("#editor-panel").is_visible()
              and not page.locator("#receipt-panel").is_visible()
              and not page.locator("#trail").is_visible(),
              "ambient projection hides raw and receipt panels")
        page.locator('[data-mode="relations"]').click()
        check("EDITOR_REVERSIBLE",
              page.locator("#editor-panel").is_visible()
              and draft.input_value() == SENTINEL,
              "return from ambient does not lose or publish draft")

        page.locator("#reset").click()
        check("RESET_LOCAL_MEMORY",
              draft.input_value() == INITIAL
              and page.locator("#undo").is_disabled()
              and page.locator("#accept").is_disabled(),
              "reset restores source fixture and clears acceptance snapshots")
        draft.fill(SENTINEL)
        page.reload()
        check("RESTART_NO_HIDDEN_PERSISTENCE",
              draft.input_value() == INITIAL
              and page.locator("#accept").is_disabled()
              and page.locator("#undo").is_disabled(),
              "reload erases private demonstration input and prior undo stack")
        check("NO_EXTERNAL_TRAFFIC", not outbound,
              "test made no HTTP(S) request while interacting")
        check("NO_BROWSER_EXCEPTIONS", not errors,
              "browser reported no page errors")
        browser.close()

    check("SOURCE_BYTES_PRESERVED",
          source.read_bytes() == original
          and blob_sha1(source.read_bytes()) == GIT_BLOB_SHA1,
          "original offline first-use source remains unchanged")

    return {
        "schema": "CoCivium.CoMVP.CoPreCursorFirstTaskBrowserR0",
        "protected_source": {"path": SOURCE_PATH, "git_blob_sha1": GIT_BLOB_SHA1,
                             "sha256": hashlib.sha256(original).hexdigest()},
        "environment": {"browser": "chromium", "browser_version": version,
                        "viewport": {"width": 390, "height": 844}},
        "task": "Preview-next, explicit accept, exact undo, reject, privacy and reset",
        "checks": checks,
        "total": len(checks),
        "passed": len(checks),
        "qualified_scope": "SAME_PROVIDER_CI_BROWSER_ONLY",
        "independent_human_acceptance": "UNTESTED",
        "human_active_minutes": None,
        "useful_receiver_result": "UNTESTED",
        "persistent_recovery": "NOT_IMPLEMENTED_BY_THIS_DEMO",
        "cross_provider_reconstruction": "UNTESTED",
        "cold_recovery_on_CoStead": "UNTESTED",
        "authorized_product_switch": False,
        "mvp_qualified": False,
        "network_effects": 0,
        "nonclaims": [
            "AUTOMATED_FIRST_TASK_NE_REAL_USER_VALUE",
            "OFFLINE_RESET_NE_DURABLE_COLD_RESTORE",
            "PROTECTING_A_DEMO_NE_COMPLETING_A_PRODUCT",
            "SOURCE_READBACK_NE_RECEIVER_READPROOF",
            "NO_RUNTIME_COEX_CANON_OR_PUBLIC_DOMAIN_STATUS",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = test_browser(args.repo_root)
        args.out.mkdir(parents=True, exist_ok=False)
        raw = canonical(report)
        with (args.out / "first-task.json").open("xb") as file:
            file.write(raw)
        receipt = {"schema": "CoCivium.CoMVP.FirstTaskReceiptR0",
                   "report_sha256": hashlib.sha256(raw).hexdigest(),
                   "bytes": len(raw), "scope": "SAME_PROVIDER_CI_BROWSER_ONLY",
                   "result": "PASS_AUTOMATED_BROWSER_ONLY", "mvp_qualified": False}
        with (args.out / "receipt.json").open("xb") as file:
            file.write(canonical(receipt))
    except (AssertionError, ValueError, OSError) as error:
        print("FAIL_CLOSED:", error)
        return 2
    print(json.dumps({"result": receipt["result"], "checks": report["total"],
                      "mvp_qualified": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
