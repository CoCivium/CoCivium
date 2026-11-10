#!/usr/bin/env python3
"""CoContextRail R1 browser-profile restart acceptance, synthetic fixture only.

Playwright Chromium navigates a stable intercepted HTTPS origin and restarts its
actual browser profile. Every network request is intercepted: only the exact
checked-in HTML is served from memory. No remote endpoint, OS mouse binding,
real conversation, user identity, external receiver, or 24h proof is involved.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
ORIGIN = "https://workid-test.invalid/"
STORAGE_KEY = "CoCivium.CoContextRail.SyntheticWorkID.R0"


def require(ok, label):
    if not ok:
        raise AssertionError(label)


def browse(playwright, profile, html, requests, *, viewport):
    executable = shutil.which("google-chrome") or shutil.which("chromium")
    require(bool(executable), "HELD_NO_CHROMIUM_EXECUTABLE")
    ctx = playwright.chromium.launch_persistent_context(
        user_data_dir=profile, headless=True, executable_path=executable,
        viewport=viewport, ignore_https_errors=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-background-networking"],
    )

    def intercepted(route):
        if route.request.url == ORIGIN and route.request.is_navigation_request():
            route.fulfill(status=200, body=html, content_type="text/html",
                          headers={"Cache-Control": "no-store"})
        else:
            requests.append(route.request.url)
            route.abort()

    ctx.route("**/*", intercepted)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(ORIGIN, wait_until="domcontentloaded", timeout=25000)
    page.wait_for_function("typeof window.CoOwnedWorkR0 !== 'undefined'")
    return ctx, page


def main():
    html = PAGE.read_text(encoding="utf-8")
    require('id="workPreserve"' in html and "CoOwnedWorkR0" in html,
            "HTML_WORK_CONTROLS_ABSENT")
    events = []
    requests = []
    viewport = {"width": 390, "height": 844}
    with tempfile.TemporaryDirectory(prefix="cocontext-browser-proof-") as d:
        profile = str(pathlib.Path(d) / "chromium-profile")
        with sync_playwright() as playwright:
            ctx, page = browse(playwright, profile, html, requests, viewport=viewport)
            try:
                require(page.locator("#workPreserve").is_disabled(), "UNAUTHORIZED_DEFAULT")
                page.locator("#workRecover").click()
                require(page.locator("#workState").inner_text() == "EMPTY",
                        "MISSING_PREVIEW_NOT_EMPTY")
                events.append("EMPTY_BASELINE")
                page.select_option("#context", "RESEARCH")
                page.select_option("#question", "WHAT_ELSE")
                page.select_option("#privacy", "PUBLIC")
                page.select_option("#gesture", "EXPLICIT_RING")
                page.locator("#fixture").uncheck()
                page.locator("#preview").click()
                require(page.locator("#state").inner_text() == "PROPOSED_ONLY",
                        "NO_EXPLICIT_PROPOSAL")
                require(page.locator("#workPreserve").is_enabled(), "NO_ELIGIBLE_WORK_PREVIEW")
                page.locator("#workPreserve").click()
                require(page.locator("#workState").inner_text() == "COMMITTED_BROWSER_LOCAL",
                        "FIRST_WRITE_NOT_COMMITTED")
                before = page.evaluate("(key) => localStorage.getItem(key)", STORAGE_KEY)
                require(before is not None, "WORKID_NOT_IN_BROWSER_STORE")
                for _ in range(9):
                    page.locator("#workPreserve").click()
                    require(page.locator("#workState").inner_text() == "DUPLICATE_SUPPRESSED",
                            "DUPLICATE_WRITE_NOT_SUPPRESSED")
                require(page.evaluate("(key) => localStorage.getItem(key)", STORAGE_KEY) == before,
                        "DUPLICATE_CHANGED_EXACT_RECORD")
                events.extend(["EXPLICIT_STORE", "NINE_DUPLICATES_SUPPRESSED"])
            finally:
                ctx.close()

            # Actually terminate Chromium and start a second Chromium process
            # using the same persistent browser profile, without reinjecting storage.
            ctx, page = browse(playwright, profile, html, requests, viewport=viewport)
            try:
                page.locator("#workRecover").click()
                require(page.locator("#workState").inner_text() == "RECOVERED_BROWSER_LOCAL",
                        "COLD_PROFILE_RECOVERY_FAILED")
                content = page.locator("#workNarrative").inner_text()
                for term in ("Ready Cycle", "Prior decisions:", "Blockers:", "Next:", "browser"):
                    require(term in content, "MISSING_RECOVERED_FIELD:" + term)
                require(page.evaluate("(key) => localStorage.getItem(key)", STORAGE_KEY) == before,
                        "RESTART_CHANGED_RECORD")
                events.append("CHROMIUM_PROCESS_RESTART_RECOVERED")

                # No native input interception or sensitive-content capture.
                page.select_option("#privacy", "SENSITIVE")
                page.locator("#preview").click()
                require(page.locator("#state").inner_text() == "HELD_PRIVACY",
                        "SENSITIVE_PREVIEW_NOT_HELD")
                require(page.locator("#workPreserve").is_disabled(),
                        "SENSITIVE_STORAGE_WRITE_OFFERED")
                page.select_option("#privacy", "PUBLIC")
                page.select_option("#gesture", "NATIVE_MIDDLE")
                page.locator("#preview").click()
                require(page.locator("#state").inner_text() == "PASS_THROUGH_NATIVE",
                        "MIDDLE_CLICK_NOT_NATIVE")
                require(page.locator("#workPreserve").is_disabled(),
                        "NATIVE_INPUT_GRANTED_STORAGE")
                require(page.evaluate("(key) => localStorage.getItem(key)", STORAGE_KEY) == before,
                        "DENIED_INPUT_CHANGED_RECORD")
                events.append("PRIVACY_AND_NATIVE_PASS_THROUGH")

                page.locator("#workRevoke").click()
                require(page.locator("#workState").inner_text() == "REVOKED_BROWSER_LOCAL",
                        "REVOKE_NOT_COMMITTED")
                page.locator("#workRecover").click()
                require(page.locator("#workState").inner_text() == "HELD_REVOKED",
                        "REVOKED_RECORD_REACTIVATED")
                events.append("REVOKE_HELD")
            finally:
                ctx.close()

            ctx, page = browse(playwright, profile, html, requests, viewport=viewport)
            try:
                page.locator("#workRecover").click()
                require(page.locator("#workState").inner_text() == "HELD_REVOKED",
                        "REVOKE_NOT_PERSISTENT_AFTER_RESTART")
                page.locator("#preview").click()
                page.locator("#workPreserve").click()
                require(page.locator("#workState").inner_text() == "HELD_REVOKED",
                        "REVOKED_RECORD_REWRITTEN")
                events.append("REVOKE_SURVIVES_SECOND_RESTART")
            finally:
                ctx.close()

    # Browsing from injected local source is the only legitimate navigation.
    # Other browser-request attempts are intercepted and never transmitted.
    result = {
        "schema": "CoAll.CoContextRail.BrowserProfileReplay.R0",
        "state": "PASS_SYNTHETIC_BROWSER_PROFILE_RESTART",
        "checks": events,
        "html_sha256": hashlib.sha256(PAGE.read_bytes()).hexdigest(),
        "viewport": viewport,
        "allowed_network_transmissions": 0,
        "blocked_request_attempts": len(requests),
        "nonclaims": [
            "BROWSER_RESTART_NE_INDEPENDENT_EXTERNAL_RECEIVER",
            "SYNTHETIC_CONSENT_NE_USER_CONSENT",
            "CHROME_PROFILE_NE_24H_DURABILITY",
            "SOURCE_REF_NE_BROWSER_SOURCE_VERIFICATION",
            "NO_LIVE_X2_OR_NATIVE_MOUSE",
            "NO_PRIVATE_CHAT_CAPTURE",
        ],
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
