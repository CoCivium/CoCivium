#!/usr/bin/env python3
"""Offline, source-bound Chromium interaction canary. Not an X2 native runtime test."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
raw = HTML.read_bytes()
checks = []
def check(ok, label):
    checks.append({"check": label, "pass": bool(ok)})
    if not ok:
        raise AssertionError(label)

def case(browser, name, width, height):
    ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
    page = ctx.new_page()
    errors = []
    outbound = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    def block_remote(route):
        if route.request.url.startswith("file:"):
            route.continue_()
        else:
            outbound.append(route.request.url)
            route.abort()
    page.route("**/*", block_remote)
    page.goto(HTML.as_uri(), wait_until="load")
    check(page.locator(".demo-banner").is_visible(), name + "_demo_notice_visible")
    notice = page.locator(".demo-banner").inner_text()
    check("NOT LIVE" in notice and "X2 native runtime remain unverified" in notice, name + "_not_live_notice_truthful")
    check(page.locator(".node").count() == 6, name + "_six_nodes")
    check(page.locator(".stat").count() == 4, name + "_four_glance_fields")
    check("synthetic fixture" in page.locator(".kv").inner_text(), name + "_synthetic_currentness")
    check("not live-tested" in page.locator(".kv").inner_text(), name + "_recovery_not_claimed")
    check("not measured" in page.locator(".kv").inner_text(), name + "_crown_not_claimed")
    check("not verified independent failover paths" not in page.locator(".paths").inner_text(), name + "_paths_are_separate_from_notice")
    check("unverified candidate" in page.locator(".paths").inner_text(), name + "_peer_explicitly_unverified")
    check(page.locator(".node.unknown").get_attribute("data-state") == "held", name + "_unknown_is_held")
    check(page.get_by_role("button", name="Orb + Map").get_attribute("aria-pressed") == "true", name + "_default_map_mode")

    page.get_by_role("button", name="Text", exact=True).click()
    check(page.locator(".textview").is_visible(), name + "_text_fallback_visible")
    check(page.locator(".stage").is_hidden(), name + "_text_hides_spatial_only")
    check("has not been demonstrated" in page.locator(".textview").inner_text(), name + "_text_recovery_no_overclaim")
    page.get_by_role("button", name="Orb + Map").click()
    check(page.locator(".stage").is_visible(), name + "_map_restored")

    page.get_by_role("button", name="3D+").click()
    check("threed" in (page.locator("#field").get_attribute("class") or ""), name + "_optional_3d_on")
    page.get_by_role("button", name="3D+").click()
    check("threed" not in (page.locator("#field").get_attribute("class") or ""), name + "_optional_3d_off")
    page.get_by_role("button", name="Ambient").click()
    check(page.locator(".rail").is_hidden(), name + "_ambient_hides_detail")
    page.get_by_role("button", name="Orb + Map").click()
    check(page.locator(".rail").is_visible(), name + "_ambient_exit")

    old = page.locator("#draft").input_value()
    page.get_by_role("button", name="Accept locally").click()
    check(page.locator("#draft").input_value().startswith(old) and page.locator("#draft").input_value() != old, name + "_local_shadow_accept")
    check("SEND 0" in page.locator("#receipt").inner_text() and "EXECUTE 0" in page.locator("#receipt").inner_text(), name + "_accept_no_external_effect")
    page.get_by_role("button", name="Reject", exact=True).click()
    check("LOCAL REJECTED" in page.locator("#receipt").inner_text(), name + "_shadow_reject")
    check("AUTHORITY 0" in page.locator("#receipt").inner_text(), name + "_reject_not_authority")

    colors = page.evaluate("""() => ({
      demo: getComputedStyle(document.querySelector('.demo-banner')).backgroundColor,
      panel: getComputedStyle(document.querySelector('.card')).backgroundColor,
      text: getComputedStyle(document.querySelector('.demo-banner')).color
    })""")
    check(colors["demo"] == "rgb(23, 55, 44)" and colors["panel"] != colors["demo"], name + "_selective_green_not_all_success")
    check(page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), name + "_no_horizontal_overflow")
    check(len(outbound) == 0, name + "_zero_outbound_requests")
    check(len(errors) == 0, name + "_zero_browser_errors")
    target=ROOT / ("preview_" + name + ".png")
    page.screenshot(path=str(target), full_page=True)
    check(target.is_file() and target.stat().st_size > 12000, name + "_screenshot_saved")
    ctx.close()

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        case(browser, "desktop", 1280, 840)
        case(browser, "mobile", 390, 844)
    finally:
        browser.close()
receipt = {
    "schema": "CoGbx.UX.BrowserQA.R0.1",
    "status": "PASS" if all(x["pass"] for x in checks) else "FAIL",
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "observed_utc": datetime.now(timezone.utc).isoformat(),
    "pass": sum(x["pass"] for x in checks),
    "fail": sum(not x["pass"] for x in checks),
    "checks": checks,
    "nonclaims": [
        "BROWSER_QA_NE_X2_NATIVE_RUNTIME",
        "SYNTHETIC_PATH_NE_INDEPENDENT_FAILOVER",
        "TEXT_PROJECTION_NE_DEVICE_RECOVERY",
        "CHROMIUM_PASS_NE_FIREFOX_OR_HUMAN_ACCEPTANCE",
        "GITHUB_PR_NE_COGBX_ORG_DEPLOYMENT"
    ]
}
(ROOT / "browser_qa_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({k:receipt[k] for k in ("schema","status","pass","fail","source_sha256")},indent=2))
