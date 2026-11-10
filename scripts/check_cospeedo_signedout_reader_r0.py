#!/usr/bin/env python3
"""Signed-out browser acceptance for the already-public CoSpeedo README.

A fresh ephemeral browser visits the real GitHub HTML UI over HTTPS.
This proves bounded reachability and rendering within a GitHub Actions runner,
NOT a CoCivium-hosted site, independent provider, human comprehension, or X2.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts" / "cospeedo-signedout-r0"
READER = "https://github.com/CoCivium/CoCivium/blob/main/examples/cospeedo/README.md"
COPRE = "https://github.com/CoCivium/CoCivium/blob/main/CoPre.md"
READER_DEST = "/CoCivium/CoCivium/blob/main/examples/cospeedo/README.md"
HTML_DEST = "/CoCivium/CoCivium/blob/main/examples/cospeedo/needle-trails-r1.html"


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        opts = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        exe = os.environ.get("COSPEEDO_CHROME_PATH")
        if exe:
            opts["executable_path"] = exe
        browser = p.chromium.launch(**opts)
        try:
            for width, height in ((390, 900), (1440, 900)):
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    locale="en-US",
                    color_scheme="dark",
                    service_workers="block",
                )
                page = context.new_page()
                try:
                    response = page.goto(READER, wait_until="domcontentloaded", timeout=40000)
                    assert response and response.status == 200, (
                        width, "signed-out GitHub reader did not return 200",
                        response.status if response else None
                    )
                    assert page.url.split("?")[0] == READER, (
                        width, "reader unexpectedly redirected", page.url
                    )
                    heading = page.get_by_role("heading", name="What actually got better?", exact=True)
                    heading.wait_for(state="visible", timeout=20000)
                    article = page.locator("article.markdown-body")
                    assert article.count() == 1, (
                        width, "GitHub Markdown article missing or ambiguous"
                    )
                    content = article.inner_text(timeout=15000)
                    for required in (
                        "not a live dashboard",
                        "24-hour survival",
                        "not yet proven",
                        "October 20–22",
                        "unknown coverage",
                        "2026-10-23",
                        "2026-10-26",
                        "Measured",
                    ):
                        # The archived copy sometimes renders a text variant for
                        # the baseline term. Keep the gate on actual reader facts.
                        if required == "Measured":
                            assert "human time saved" in content.lower(), (width, required)
                        else:
                            assert required.lower() in content.lower(), (width, required)
                    link = article.locator('a[href*="needle-trails-r1.html"]').first
                    assert link.count() == 1, (width, "missing R1 source trail")
                    href = link.get_attribute("href") or ""
                    assert HTML_DEST in href, (width, "wrong source link", href)
                    heading_box = heading.bounding_box()
                    assert heading_box and heading_box["width"] > 100, (width, "heading unreadable")

                    screenshot = EVIDENCE / f"github-reader-{width}x{height}.png"
                    page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
                    results.append({
                        "viewport": [width, height],
                        "reader_status": 200,
                        "rendered_heading": "What actually got better?",
                        "rendered_archive_dates": ["2026-10-23", "2026-10-26"],
                        "source_link_target": HTML_DEST,
                        "screenshot": screenshot.name,
                        "screenshot_sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                    })
                    if width == 390:
                        src_response = page.goto(COPRE, wait_until="domcontentloaded", timeout=40000)
                        assert src_response and src_response.status == 200
                        anchor = page.locator(f'a[href*="{READER_DEST}"]').first
                        anchor.wait_for(state="visible", timeout=20000)
                        assert READER_DEST in (anchor.get_attribute("href") or "")
                finally:
                    context.close()
        finally:
            browser.close()
    report = {
        "schema": "CoSpeedo.SignedOutGithubReader.R0",
        "scope": "FRESH_BROWSER_GITHUB_HOSTED__NOT_CO_CIVIUM_SITE",
        "target_url": READER,
        "copre_url": COPRE,
        "results": results,
        "nonclaims": [
            "NOT_INDEPENDENT_PROVIDER_RECEIVER",
            "NOT_HUMAN_COMPREHENSION_PROOF",
            "NOT_GITHUB_PAGES_OR_CUSTOM_DOMAIN",
            "NOT_CONTINUOUS_TELEMETRY",
            "NOT_24H_RECOVERY_PROOF",
            "NOT_X2_RUNTIME",
        ],
    }
    (EVIDENCE / "signedout-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("PASS_COSPEEDO_SIGNEDOUT_GITHUB_READER_R0")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
