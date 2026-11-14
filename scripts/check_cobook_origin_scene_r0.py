#!/usr/bin/env python3
"""Source + actual browser QA for public-safe CoBook origin-scene candidate.

Checks only a local static draft. Does not assert permission to publish,
real child biographical accuracy, human reader comprehension or a live book.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "Books" / "CoBook_Origin_Beetle_Cartographer_Interactive_R0.html"
STORY = ROOT / "docs" / "Books" / "COBOOK_ORIGIN_MYTHOS_BEETLE_CARTOGRAPHER_R0_20261110.md"
LENSES = ROOT / "ai" / "cobook-source-to-human-lenses-r0.json"
REPORT = ROOT / "artifacts" / "cobook-origin-scene-r0"
EXPECTED = {
    "keep": ("Keep the door", "preserving something"),
    "draw": ("Draw another", "stops explaining"),
    "leave": ("Walk elsewhere", "field without walls"),
}


class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.routes = []
        self.references = []
        self.external = []
    def handle_starttag(self, tag, attrs):
        x = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if tag == "button" and "data-route" in x:
            self.routes.append(x["data-route"])
        if "src" in x:
            self.references.append(x["src"])
            if not x["src"].startswith(("data:", "file:", "./")):
                self.external.append(x["src"])
        if tag == "script" and x.get("src"):
            self.external.append(x["src"])


def main():
    assert PAGE.is_file() and STORY.is_file()
    content = PAGE.read_text(encoding="utf-8")
    story = STORY.read_text(encoding="utf-8")
    a = Audit()
    a.feed(content)
    assert a.routes == ["keep", "draw", "leave"], a.routes
    assert a.tags.get("svg") == 1
    assert a.tags.get("button") == 3
    assert a.tags.get("title") >= 2
    assert a.tags.get("desc") == 1
    assert a.tags.get("details") == 2
    assert a.tags.get("script") == 1
    assert not a.external
    assert not any(f"<{tag}" in content for tag in ["iframe", "audio", "video", "form"])
    for forbidden in ["localStorage", "sessionStorage", "navigator.mediaDevices", "fetch(",
                      "XMLHttpRequest", "sendBeacon", "window.open("]:
        assert forbidden not in content, f"Unexpected tracking or device capability: {forbidden}"
    assert "SILENT" not in content or "No analytics" in content
    assert "No real child's name" in content
    assert "not a published chapter" in content
    assert "fictional" in story.lower()
    assert "not an autobiography" in story.lower()
    assert "The Cartographer's agency" in story
    assert "cobook.origin.beetle-cartographer.r0" in story

    # The optional source-to-human lens is one reversible projection,
    # not four new ungrounded storylets or a second source of truth.
    manifest = json.loads(LENSES.read_text(encoding="utf-8"))
    assert manifest["schema"] == "CoBook.SourceToHumanLenses.R0.v0.1"
    assert manifest["story_identity"] in story
    lenses = manifest["lenses"]
    expected_ids = ["comap", "cotheoryall", "coglukey", "highlights"]
    assert [lens["id"] for lens in lenses] == expected_ids
    import re
    assert re.findall(r'data-lens-id="([a-z]+)"', content) == expected_ids
    for item in lenses:
        source = (ROOT / item["source_path"]).resolve()
        assert source.is_relative_to(ROOT) and source.is_file(), item["source_path"]
        source_bytes = source.read_bytes()
        source_blob = hashlib.sha1(
            b"blob " + str(len(source_bytes)).encode("ascii") + b"\0" + source_bytes
        ).hexdigest()
        assert source_blob == item["git_blob_sha"], (item["id"], "source changed; review translation")
        for field in ("plain_language", "technical_fact", "projection_loss", "evidence_limit"):
            assert item[field] in content, (item["id"], field)
        assert item["kind"].endswith(("CANDIDATE","SNAPSHOT","REGISTER")), item["id"]
    assert "Do not introduce them here as competing standalone plots." in LENSES.read_text(encoding="utf-8")

    REPORT.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        args = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        exe = os.environ.get("COBOOK_CHROME_PATH")
        if exe:
            args["executable_path"] = exe
        browser = p.chromium.launch(**args)
        try:
            for width, height in ((360, 780), (390, 844), (1440, 900)):
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    reduced_motion="reduce",
                    color_scheme="dark",
                    service_workers="block",
                    device_scale_factor=1,
                )
                page = context.new_page()
                errors = []
                popups = []
                requests = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("popup", lambda p: popups.append(p.url))
                page.on("request", lambda q: requests.append(q.url))
                response = page.goto(PAGE.as_uri(), wait_until="load")
                assert response and response.ok, (width, "no local rendering")
                assert page.get_by_role("heading", name="The Beetle and the Unfinished Map").count() == 1
                assert page.locator("svg[role='img'] title").count() == 1
                assert page.locator("svg[role='img'] desc").count() == 1
                assert page.locator("details summary").count() == 2
                assert page.locator('a[href$="COBOOK_ORIGIN_MYTHOS_BEETLE_CARTOGRAPHER_R0_20261110.md"]').count() == 1
                assert page.locator("button[data-route]").count() == 3
                dims = page.evaluate("() => ({page:document.documentElement.scrollWidth, width:innerWidth})")
                assert dims["page"] <= dims["width"] + 2, (width, "horizontal overflow", dims)
                for key, (title, phrase) in EXPECTED.items():
                    button = page.locator(f'button[data-route="{key}"]')
                    button.focus()
                    page.keyboard.press("Enter")
                    assert button.get_attribute("aria-pressed") == "true", (width, key, "not pressed")
                    assert page.locator("#result-title").inner_text() == title
                    assert phrase in page.locator("#result-text").inner_text()
                    for other in EXPECTED:
                        if other != key:
                            assert page.locator(f'button[data-route="{other}"]').get_attribute("aria-pressed") == "false"
                # The alternate endings remain available without JS interaction.
                disclosure = page.locator("details").first
                disclosure.locator("summary").focus()
                page.keyboard.press("Enter")
                assert disclosure.get_attribute("open") is not None, (width, "details inaccessible")
                assert "Draw another" in disclosure.inner_text()
                # Extra interpretation remains quiet until the reader requests it.
                source_lens = page.locator("details#source-lenses")
                assert source_lens.get_attribute("open") is None
                source_lens.locator("summary").focus()
                page.keyboard.press("Enter")
                assert source_lens.get_attribute("open") is not None, (width, "lens keyboard open failed")
                assert source_lens.locator("[data-lens-id]").count() == 4
                source_open_shot = REPORT / f"beetle-human-lenses-{width}x{height}.png"
                page.screenshot(path=str(source_open_shot), full_page=True, animations="disabled")
                assert source_lens.get_by_text(
                    "A map can show the paths someone recorded", exact=False
                ).count() == 1
                page.keyboard.press("Enter")
                assert source_lens.get_attribute("open") is None, (width, "lens keyboard close failed")
                screenshot = REPORT / f"beetle-cartographer-{width}x{height}.png"
                page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
                assert not errors, (width, "JavaScript errors", errors)
                assert not popups, (width, "unexpected popup", popups)
                assert all(u.startswith("file://") for u in requests), (width, "external request", requests)
                results.append({
                    "viewport": [width, height],
                    "all_outcomes_keyboard_reachable": True,
                    "responsive_overflow": "NONE",
                    "unexpected_network_requests": 0,
                    "screenshot": screenshot.name,
                    "screenshot_sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                    "optional_lenses_screenshot": source_open_shot.name,
                    "optional_lenses_screenshot_sha256": hashlib.sha256(source_open_shot.read_bytes()).hexdigest(),
                })
                context.close()
        finally:
            browser.close()
    receipt = {
        "schema": "CoBook.OriginMythos.ReaderQA.R0",
        "state": "SOURCE_BRANCH_BROWSER_QA_ONLY",
        "source": str(PAGE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(PAGE.read_bytes()).hexdigest(),
        "results": results,
        "nonclaims": [
            "NOT_PUBLISHED_BOOK_CHAPTER", "NOT_CANON_OR_DEPLOYED",
            "NO_REAL_CHILD_BIOGRAPHY_OR_CHILD_CONSENT_PROOF",
            "NO_HUMAN_READER_COMPREHENSION_PROOF", "NO_AUDIO_OR_VIDEO",
            "NO_INDEPENDENT_RECEIVER_OR_24H_SURVIVAL",
        ],
    }
    (REPORT / "browser-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PASS_COBOOK_BEETLE_ORIGIN_READER_R0")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
