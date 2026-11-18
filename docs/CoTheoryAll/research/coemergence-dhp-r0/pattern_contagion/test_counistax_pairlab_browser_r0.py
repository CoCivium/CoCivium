#!/usr/bin/env python3
"""Actual headless Chromium QA for CoUniStax PairLab, not a human receiver test."""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = Path(__file__).with_name("counistax-pairlab-r0.html").resolve().as_uri()
KEY = [True, False, False, True, False, True]
CASE_TITLES = ["Two feedback loops", "Two selection processes", "The echo chamber",
               "Two integrity checks", "Two timeouts", "Two types of review"]

def normalize(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))

def check_view(browser, width: int, arm: str):
    context = browser.new_context(
        viewport={"width": width, "height": 820},
        color_scheme="dark",
        reduced_motion="reduce",
        java_script_enabled=True,
    )
    page = context.new_page()
    outside, errors, popups, dialogs = [], [], [], []
    page.on("request", lambda req: outside.append(req.url) if
            req.url.startswith(("http://", "https://")) else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("popup", lambda pop: popups.append(pop.url))
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    page.goto(URL + "?arm=" + arm, wait_until="load")
    assert page.locator("h1").count() == 1
    assert page.locator("#result").is_hidden()
    assert page.locator("#quiz").is_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), width
    facts_texts = []
    for i, key in enumerate(KEY):
        assert page.locator("#caseTitle").inner_text() == CASE_TITLES[i]
        fact = page.locator("#facts").inner_text()
        assert "Shared feature" in fact and "Mechanisms" in fact and "Boundary" in fact
        if arm == "ordinary":
            assert page.locator("#facts p").count() == 1
            assert page.locator("#facts dt").count() == 0
        else:
            assert page.locator("#facts dt").count() == 3
            assert page.locator("#facts dd").count() == 3
        facts_texts.append(normalize(fact))
        # Exercise actual keyboard activation for the first trial.
        selector = "#yes" if key else "#no"
        if i == 0:
            page.locator(selector).focus()
            page.keyboard.press("Enter")
        else:
            page.locator(selector).click()
        assert page.locator("#yes").is_disabled()
        assert page.locator("#no").is_disabled()
        assert page.locator("#next").is_visible()
        assert "Recorded" in page.locator("#choiceStatus").inner_text()
        if i < len(KEY) - 1:
            page.locator("#next").click()
        else:
            page.get_by_role("button", name="View local results").click()
    assert page.locator("#quiz").is_hidden()
    assert page.locator("#result").is_visible()
    assert "6 of 6 keyed decisions correct" in page.locator("#summary").inner_text()
    page.get_by_role("button", name="Show optional local JSON receipt").click()
    receipt = json.loads(page.locator("#receipt").inner_text())
    assert receipt["schema"] == "CoUniStax.LocalPairLabReceipt.R0"
    assert receipt["assignment"] == arm
    assert receipt["scored_correct"] == 6 and receipt["scored_total"] == 6
    assert len(receipt["answers"]) == 6
    assert receipt["transmitted"] is False and receipt["stored"] is False
    assert receipt["independent_receiver_ack"] is False
    assert receipt["real_world_transfer_validated"] is False
    assert receipt["source_publication"] == "DRAFT_BRANCH_ONLY"
    assert not errors, errors
    assert not outside, outside
    assert not popups, popups
    assert not dialogs, dialogs
    context.close()
    return facts_texts

def main():
    with sync_playwright() as p:
        chrome = os.environ.get("COSPEEDO_CHROME_PATH")
        opts = {"headless": True, "args": ["--no-sandbox","--disable-dev-shm-usage"]}
        if chrome:
            opts["executable_path"] = chrome
        browser = p.chromium.launch(**opts)
        try:
            for width in (360, 1440):
                ordinary = check_view(browser, width, "ordinary")
                structured = check_view(browser, width, "structured")
                assert ordinary == structured, (
                    "Different semantic facts leaked across display arms", width
                )
        finally:
            browser.close()
    print("PASS_COUNISTAX_PAIRLAB_CHROMIUM_R0: 2 widths x 2 arms x 6 trials; no telemetry")

if __name__ == "__main__":
    main()
