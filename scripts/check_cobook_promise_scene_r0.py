#!/usr/bin/env python3
"""CoBook parent-child promise scene: isolated source and Chromium QA.

Claims only local branch candidate accessibility/safety behavior, not a deployed
public book, independent reader comprehension, child permission, or receiver ACK.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs/Books/CoBook_The_Promise_Across_the_River_Interactive_R0.html"
REPORT = ROOT / "artifacts/cobook-promise-scene-r0"
CHOICES = {
    "paper": ("Paper survives differently", "HELD: receiver intent unknown"),
    "digital": ("A perfect copy is not a delivery", "HELD: readback missing"),
    "hybrid": ("The question changes the mission", "REQUEST RECEIVED: action still unverified"),
}

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.choice_ids = []
        self.links = []
        self.script_sources = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if tag == "button" and "data-choice" in d:
            self.choice_ids.append(d["data-choice"])
        if tag == "a":
            self.links.append(d.get("href", ""))
        if "src" in d:
            self.script_sources.append(d["src"])


def check_source():
    content = PAGE.read_text(encoding="utf-8")
    tree = Audit()
    tree.feed(content)
    assert "**fictional thought experiment**" not in content, "Raw Markdown in HTML"
    assert "<strong>fictional thought experiment</strong>" in content
    assert tree.choice_ids == list(CHOICES)
    assert tree.tags.get("button", 0) == 3
    assert tree.tags.get("script", 0) == 1
    assert tree.tags.get("details", 0) == 2
    assert tree.tags.get("svg", 0) == 1
    assert not tree.script_sources, "Unexpected external subresource"
    assert all(not u.startswith(("http://", "https://")) for u in tree.links)
    for href in tree.links:
        assert href and not href.startswith("/"), href
        if href.startswith("#"):
            # In-page navigation is not a filesystem dependency.
            assert 'id="' + href[1:] + '"' in content, href
            continue
        path = (PAGE.parent / href.split("#", 1)[0]).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), href
    for forbidden in (
        "<iframe", "<form", "<audio", "<video", "localStorage",
        "sessionStorage", "navigator.mediaDevices", "fetch(", "WebSocket(",
        "sendBeacon", "document.cookie", "window.open(", "XMLHttpRequest",
    ):
        assert forbidden not in content, forbidden
    # Rule is stronger than sex-unspecified only: no gendered narrator tokens
    # anywhere in the story or interface (excluding case-insensitive substrings).
    gendered = re.findall(
        r"\b(?:he|she|him|his|her|hers|husband|wife|boy|girl|son|daughter|mother|father)\b",
        content, re.I,
    )
    assert not gendered, ("Unexpected gender coding", gendered)
    for phrase in (
        "The Parent", "The Child", "what was true", "Civic Bridge Era",
        "No real", "No login", "not a published edition",
        "FICTION:", "EXPLANATION:", "NOT VERIFIED:", "CONSENT:",
        "HELD: readback missing", "REQUEST RECEIVED: action still unverified",
        "not a real communication service",
    ):
        if phrase == "No real":
            assert "real child's" not in content.lower()
        else:
            assert phrase.lower() in content.lower(), phrase
    assert 'role="status"' in content and 'aria-live="polite"' in content
    assert 'button[aria-pressed=true]' in content
    return content


def run():
    content = check_source()
    REPORT.mkdir(parents=True, exist_ok=True)
    result = []
    with sync_playwright() as p:
        args = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        chrome = os.environ.get("COBOOK_CHROME_PATH")
        if chrome:
            args["executable_path"] = chrome
        browser = p.chromium.launch(**args)
        try:
            for width, height in ((360, 780), (390, 844), (768, 1024), (1440, 900)):
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    color_scheme="dark", reduced_motion="reduce",
                    service_workers="block", device_scale_factor=1,
                )
                page = context.new_page()
                errs = []
                popup = []
                requests = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.on("popup", lambda v: popup.append(v.url))
                page.on("request", lambda v: requests.append(v.url))
                response = page.goto(PAGE.as_uri(), wait_until="load", timeout=15000)
                assert response and response.ok, (width, "No local page")
                assert page.get_by_role("heading", name="The Promise Across the River").count() == 1
                assert page.locator("svg[role='img'] title").count() == 1
                assert page.locator("svg[role='img'] desc").count() == 1
                assert page.locator("#result[role='status']").count() == 1
                assert page.locator("button[data-choice]").count() == 3
                assert page.locator("details summary").count() == 2
                dims = page.evaluate(
                    "()=>({documentWidth:document.documentElement.scrollWidth,viewport:innerWidth})"
                )
                assert dims["documentWidth"] <= width + 2, (width, "Horizontal overflow", dims)
                assert page.locator('button[data-choice="paper"]').get_attribute("aria-pressed") == "true"
                for selected, (title, status) in CHOICES.items():
                    button = page.locator('button[data-choice="' + selected + '"]')
                    button.focus()
                    page.keyboard.press("Enter")
                    assert button.get_attribute("aria-pressed") == "true", (width, selected)
                    assert page.locator("#result-title").inner_text() == title
                    assert page.locator("#result-state").inner_text() == status
                    assert page.locator("#result-question").inner_text().endswith("?")
                    for other in CHOICES:
                        if other != selected:
                            assert page.locator(
                                'button[data-choice="' + other + '"]'
                            ).get_attribute("aria-pressed") == "false"
                for block_id in ("paths", "evidence"):
                    details = page.locator("details#" + block_id)
                    assert details.get_attribute("open") is None
                    details.locator("summary").focus()
                    page.keyboard.press("Enter")
                    assert details.get_attribute("open") is not None, (width,block_id,"open")
                    if block_id == "evidence":
                        assert "FICTION:" in details.inner_text()
                        assert "NOT VERIFIED:" in details.inner_text()
                    page.keyboard.press("Enter")
                    assert details.get_attribute("open") is None, (width,block_id,"close")
                assert not errs and not popup, (width,errs,popup)
                assert all(u.startswith("file://") for u in requests), (width, requests)
                screenshot = REPORT / f"promise-river-{width}x{height}.png"
                page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
                result.append({
                    "viewport": [width, height],
                    "document_overflow": False,
                    "keyboard_choice_states": list(CHOICES),
                    "evidence_disclosure_reversible": True,
                    "external_requests": 0,
                    "screenshot": screenshot.name,
                    "sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                })
                context.close()
        finally:
            browser.close()
    receipt = {
        "schema": "CoBook.ParentChild.PromiseAcrossRiver.QA.R0",
        "state": "ISOLATED_BRANCH_CHROMIUM_QA_NOT_PUBLIC_RELEASE",
        "source": str(PAGE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "results": result,
        "nonclaims": [
            "NO_UNCOACHED_HUMAN_READER",
            "NO_CHILD_CONSENT_FROM_FICTION",
            "NO_X2_RUNTIME",
            "NO_LIVE_BOOK_SITE",
            "NO_ACTUAL_RECIPIENT_ACK",
            "NO_CIV3_TRANSITION",
        ],
    }
    (REPORT / "proof.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print("PASS_COBOOK_PARENT_CHILD_PROMISE_QA_R0")
    print(json.dumps({"source_sha256": receipt["source_sha256"],
                      "viewports": [x["viewport"] for x in result]}, indent=2))


if __name__ == "__main__":
    run()
