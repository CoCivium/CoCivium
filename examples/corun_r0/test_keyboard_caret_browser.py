#!/usr/bin/env python3
"""Chromium keyboard canary: pinned CoPreCursor R0 fails; isolated R1 passes.

The R0 regression is an expected negative control. Never promote R1 based
only on synthetic browser success. No source change, persistence or external
network effects are permitted by this test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BASE = "773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101"
CANDIDATE = "9daba0043b74eee129e78b1eaaad0c44e4005640"
INITIAL = "Test one CoMap relation, then "


def canonical(data):
    return (json.dumps(data, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def replay(browser, raw):
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors, outgoing, checks = [], [], []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.on("request", lambda req: outgoing.append(req.url)
            if req.url.startswith(("http://", "https://")) else None)
    page.set_content(raw.decode("utf-8"), wait_until="load")

    def check(label, valid):
        checks.append({"name": label, "passed": bool(valid)})
        if label not in {"mid_caret_exact", "not_appended"} and not valid:
            raise AssertionError("SHARED_BASELINE_REGRESSION: " + label)

    draft = page.locator("#draft")
    check("initial_text", draft.input_value() == INITIAL)
    page.keyboard.press("Tab")
    check("tab_to_draft", page.evaluate("document.activeElement.id") == "draft")
    page.keyboard.press("Tab")
    check("tab_to_preview", page.evaluate("document.activeElement.id") == "preview")
    page.keyboard.press("Enter")
    suffix = page.locator("#prediction").inner_text()
    check("preview_shadow", draft.input_value() == INITIAL and "typed relation" in suffix)
    page.keyboard.press("Tab")
    check("tab_to_accept", page.evaluate("document.activeElement.id") == "accept")
    page.keyboard.press("Enter")
    check("default_accept", draft.input_value() == INITIAL + suffix)

    page.locator("#reset").click()
    value = "abc CoMap DEF"
    caret = len("abc CoMap")
    draft.fill(value)
    draft.focus()
    page.keyboard.press("Control+Home")
    for _ in range(caret):
        page.keyboard.press("ArrowRight")
    check("keyboard_caret_position", draft.evaluate("(e)=>e.selectionStart") == caret)
    page.keyboard.press("Tab")
    check("preview_focus_mid", page.evaluate("document.activeElement.id") == "preview")
    page.keyboard.press("Enter")
    suffix = page.locator("#prediction").inner_text()
    check("preview_unmodified_mid", draft.input_value() == value
          and "typed relation" in suffix)
    page.keyboard.press("Tab")
    check("accept_focus_mid", page.evaluate("document.activeElement.id") == "accept")
    page.keyboard.press("Enter")
    answer = draft.input_value()
    check("mid_caret_exact", answer == value[:caret] + suffix + value[caret:])
    check("not_appended", answer != value + suffix)
    # After Accept, focus returns to the draft. Tab through Preview,
    # Accept and Reject before reaching Undo.
    for _ in range(4):
        page.keyboard.press("Tab")
    check("keyboard_undo_focus", page.evaluate("document.activeElement.id") == "undo")
    page.keyboard.press("Enter")
    check("keyboard_undo_exact", draft.input_value() == value)
    check("no_remote_http", len(outgoing) == 0)
    check("no_page_error", len(errors) == 0)
    check("no_mobile_overflow", page.evaluate(
        "document.documentElement.scrollWidth <= innerWidth + 1"))
    page.close()
    return {"checks": checks, "passed": sum(v["passed"] for v in checks),
            "total": len(checks)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    root = args.repo_root
    paths = {"baseline": root / "examples/coprecursor/index.html",
             "candidate": root / "examples/coprecursor/index-r1-candidate.html"}
    raw = {name: path.read_bytes() for name, path in paths.items()}
    if blob(raw["baseline"]) != BASE or blob(raw["candidate"]) != CANDIDATE:
        raise SystemExit("FAIL_CLOSED: SOURCE_PIN_DRIFT")

    # Lazy optional import so source-only unittest discovery stays dependency-free.
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        version = browser.version
        reports = {name: replay(browser, data) for name, data in raw.items()}
        browser.close()

    expected_negative = {"mid_caret_exact", "not_appended"}
    failed = {x["name"] for x in reports["baseline"]["checks"] if not x["passed"]}
    if failed != expected_negative or reports["candidate"]["passed"] != reports["candidate"]["total"]:
        raise SystemExit("FAIL_CLOSED: WRONG_BASELINE_OR_CANDIDATE_OUTCOME")
    if any(path.read_bytes() != raw[name] for name, path in paths.items()):
        raise SystemExit("FAIL_CLOSED: SOURCE_CHANGED")

    report = {
        "schema": "CoCivium.CoPreCursor.KeyboardRegressionR0",
        "browser": {"engine": "chromium", "version": version, "viewport": [390, 844]},
        "source": {
            "baseline": {"path": "examples/coprecursor/index.html",
                         "git_blob_sha1": BASE, "sha256": hashlib.sha256(raw["baseline"]).hexdigest()},
            "candidate": {"path": "examples/coprecursor/index-r1-candidate.html",
                          "git_blob_sha1": CANDIDATE,
                          "sha256": hashlib.sha256(raw["candidate"]).hexdigest()},
        },
        "baseline": reports["baseline"],
        "candidate": reports["candidate"],
        "expected_baseline_failures": sorted(expected_negative),
        "candidate_isolated": True,
        "baseline_unmodified": True,
        "qualification": "PASS_REGRESSION_CHALLENGE_ONLY",
        "independent_human_acceptance": False,
        "normal_file_navigation": "NOT_TESTED",
        "production_switch": False,
        "mvp_qualified": False,
        "nonclaims": [
            "SYNTHETIC_KEYBOARD_TEST_NE_ACCESSIBILITY_CERTIFICATION",
            "CANDIDATE_NE_DEFAULT_PUBLIC_PRODUCT",
            "BROWSER_CHECK_NE_HUMAN_ACCEPTANCE",
            "NO_MVP_RELEASE_OR_COSTEAD_PICKUP",
        ],
    }
    args.out.mkdir(parents=True, exist_ok=False)
    data = canonical(report)
    with (args.out / "keyboard-caret.json").open("xb") as f:
        f.write(data)
    receipt = {"schema": "CoCivium.CoPreCursor.KeyboardRegressionReceiptR0",
               "report_sha256": hashlib.sha256(data).hexdigest(),
               "baseline_blob": BASE, "candidate_blob": CANDIDATE,
               "state": "PASS_REGRESSION_CHALLENGE_ONLY", "mvp_qualified": False}
    with (args.out / "receipt.json").open("xb") as f:
        f.write(canonical(receipt))
    print(json.dumps({"state": receipt["state"],
                      "baseline": reports["baseline"]["passed"],
                      "candidate": reports["candidate"]["passed"],
                      "total": reports["candidate"]["total"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
