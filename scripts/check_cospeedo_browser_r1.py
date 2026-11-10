#!/usr/bin/env python3
"""CoSpeedo NeedleTrails R1: real headless-browser acceptance, static candidate only.

Tests local HTML with an actual Chromium/Chrome rendering engine, not a public URL,
deployed X2 runtime, human reader, accessibility audit, or live receiver.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "examples" / "cospeedo" / "needle-trails-r1.html"
REPORT_DIR = ROOT / "artifacts" / "cospeedo-browser-r1"
SIZES = [(360, 780), (390, 844), (768, 1024), (1440, 900)]


def run():
    assert HTML.is_file(), f"Missing candidate: {HTML}"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        opts = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        browser_path = os.environ.get("COSPEEDO_CHROME_PATH")
        if browser_path:
            opts["executable_path"] = browser_path
        browser = p.chromium.launch(**opts)
        try:
            for width, height in SIZES:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    reduced_motion="reduce",
                    color_scheme="dark",
                    java_script_enabled=True,
                )
                page = context.new_page()
                network = []
                errors = []
                popups = []
                page.on("request", lambda req: network.append(req.url))
                page.on("pageerror", lambda err: errors.append(str(err)))
                page.on("popup", lambda popup: popups.append(popup.url))
                response = page.goto(HTML.as_uri(), wait_until="load", timeout=15000)
                assert response is not None and response.ok, f"{width}: failed load"
                assert "Proof of Better R1" in page.title(), f"{width}: missing revision title"
                for heading in (
                    "What actually got better?",
                    "The one-minute answer",
                    "Needle trails through time",
                    "The human test",
                ):
                    assert page.get_by_role("heading", name=heading).count() == 1, (
                        width, "missing heading", heading
                    )
                assert page.locator("svg.needle[role='img']").count() == 1
                assert page.locator("svg.needle title").count() == 1
                assert page.locator("svg.needle desc").count() == 1
                assert page.locator("tbody tr[data-date]").count() == 4
                assert page.locator("table caption").count() == 1
                assert "not live telemetry" in page.locator("body").inner_text()
                assert "unknown coverage" in page.locator("body").inner_text()
                assert "Human improvement unknown" in page.locator("body").inner_text()
                assert "24-hour" in page.locator("body").inner_text()
                dims = page.evaluate("""() => ({
                    viewport: innerWidth,
                    htmlWidth: document.documentElement.scrollWidth,
                    bodyWidth: document.body.scrollWidth,
                    mainRight: document.querySelector('main').getBoundingClientRect().right,
                    chartRight: document.querySelector('svg.needle').getBoundingClientRect().right
                })""")
                assert dims["htmlWidth"] <= width + 2, (width, "document overflows", dims)
                assert dims["bodyWidth"] <= width + 2, (width, "body overflows", dims)
                assert dims["mainRight"] <= width + 2, (width, "main overflows", dims)
                assert dims["chartRight"] <= width + 2, (width, "chart overflows", dims)

                # Keyboard navigation and the source's single optional disclosure.
                page.keyboard.press("Tab")
                tag = page.evaluate("document.activeElement.tagName")
                assert tag in {"A", "BUTTON"}, (width, "unreachable keyboard focus", tag)
                toggle = page.locator("#explain")
                toggle.focus()
                page.keyboard.press("Enter")
                assert toggle.get_attribute("aria-expanded") == "true", (
                    width, "keyboard reveal failed"
                )
                assert page.locator("#explain-details").is_visible()
                page.keyboard.press("Enter")
                assert toggle.get_attribute("aria-expanded") == "false", (
                    width, "keyboard hide failed"
                )
                assert not page.locator("#explain-details").is_visible()
                assert not errors, (width, "JavaScript errors", errors)
                assert not popups, (width, "unexpected popups", popups)
                assert all(u.startswith("file://") for u in network), (
                    width, "network dependency detected", network
                )
                screenshot = REPORT_DIR / f"needle-trails-{width}x{height}.png"
                page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
                results.append({
                    "viewport": {"width": width, "height": height},
                    "layout": "NO_PAGE_OVERFLOW",
                    "keyboard_disclosure": "PASS",
                    "network_requests": network,
                    "runtime_errors": errors,
                    "screenshot": screenshot.name,
                    "screenshot_sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                })
                context.close()
        finally:
            browser.close()
    report = {
        "schema": "CoSpeedo.NeedleTrails.R1.BrowserQA",
        "scope": "LOCAL_FILE_CHROMIUM_TEST__NOT_PUBLIC_DEPLOYMENT",
        "source": "examples/cospeedo/needle-trails-r1.html",
        "source_sha256": hashlib.sha256(HTML.read_bytes()).hexdigest(),
        "viewport_results": results,
        "nonclaims": [
            "NOT_HUMAN_COMPREHENSION_PROOF",
            "NOT_SCREEN_READER_AUDIT",
            "NOT_SIGNED_OUT_PUBLIC_HTTPS_TEST",
            "NOT_LIVE_STATUS_TELEMETRY",
            "NO_INDEPENDENT_RECEIVER_ACK",
            "NO_X2_RUNTIME_RECOVERY_PROOF",
            "NO_24H_SURVIVAL_PROOF",
        ],
    }
    (REPORT_DIR / "browser-qa-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("PASS_COSPEEDO_R1_BROWSER_QA")
    print(json.dumps({"source_sha256": report["source_sha256"], "viewports": results}, indent=2))


if __name__ == "__main__":
    run()
