#!/usr/bin/env python3
"""Real native-WebCrypto Chromium regression: canceled async work must not resurrect state.

This is a synthetic browser QA probe, not receiver acceptance or production telemetry.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

HERE = Path(__file__).resolve().parent
HTML = (HERE / "index.html").resolve().as_uri()

INTERCEPT = r"""
(() => {
  const real = SubtleCrypto.prototype.digest;
  Object.defineProperty(SubtleCrypto.prototype, 'digest', {
    configurable: true, writable: true,
    value: function(...args) {
      if (window.__holdNextDigest) {
        window.__holdNextDigest = false;
        return new Promise((resolve, reject) => {
          window.__releaseDigest = () => real.apply(this, args).then(resolve, reject);
        });
      }
      return real.apply(this, args);
    }
  });
})();
"""

def assert_state(page, text):
    expect(page.locator("#state")).to_have_text(text, timeout=12000)

def wait_digest_intercept(page):
    # Playwright wait_for_function eval is blocked by the app's intentionally strict CSP.
    # A direct inspector evaluate reads the test-only hook without relaxing page policy.
    for _ in range(80):
        if page.evaluate("typeof window.__releaseDigest === 'function'"):
            return
        page.wait_for_timeout(75)
    raise AssertionError("Timed out waiting for test-only digest intercept")

def release(page):
    page.evaluate("window.__releaseDigest()")
    page.wait_for_timeout(180)  # Allow pending WebCrypto continuation to settle.

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome", args=["--no-sandbox"])
        try:
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors, downloads, requests = [], [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("download", lambda d: downloads.append(d.suggested_filename))
            page.on("request", lambda r: requests.append(r.url) if not r.url.startswith("file://") else None)
            page.add_init_script(INTERCEPT)
            page.goto(HTML)
            assert page.evaluate("window.isSecureContext && !!crypto.subtle")
            assert_state(page, "EMPTY")

            # A reset while source SHA-256 is pending must take precedence.
            page.locator("#source").set_input_files({
                "name":"old.txt", "mimeType":"text/plain", "buffer":b"Old source may never return."
            })
            page.evaluate("window.__holdNextDigest=true")
            page.locator("#pack").click()
            wait_digest_intercept(page)
            page.locator("#reset").click()
            assert_state(page, "EMPTY")
            release(page)
            assert_state(page, "EMPTY")
            assert page.locator("#exportCapsule").is_disabled()
            assert page.locator("#restore").is_disabled()
            assert "old.txt" not in page.locator("#trace").inner_text()
            print("PASS reset during delayed package hash cannot resurrect capsule")

            # Changing the file mid-hash must fence the old selection.
            page.evaluate("window.__releaseDigest=undefined")
            page.locator("#source").set_input_files({
                "name":"first.txt", "mimeType":"text/plain", "buffer":b"Old first."
            })
            page.evaluate("window.__holdNextDigest=true")
            page.locator("#pack").click()
            wait_digest_intercept(page)
            page.locator("#source").set_input_files({
                "name":"second.txt", "mimeType":"text/plain", "buffer":b"New second."
            })
            assert_state(page, "FILE_SELECTED")
            release(page)
            assert_state(page, "FILE_SELECTED")
            assert page.locator("#exportCapsule").is_disabled()
            page.locator("#pack").click()
            assert_state(page, "READY_LOCAL_TWO_COPIES")
            trace=page.locator("#trace").inner_text()
            assert "first.txt" not in trace
            print("PASS newer source selection invalidates old async package")

            # A reset during restore re-hash must prevent the pending download.
            page.evaluate("window.__releaseDigest=undefined")
            page.evaluate("window.__holdNextDigest=true")
            page.locator("#restore").click()
            wait_digest_intercept(page)
            page.locator("#reset").click()
            release(page)
            assert_state(page, "EMPTY")
            assert not downloads, f"Stale work initiated a download: {downloads}"
            print("PASS reset during delayed restore blocks old download")

            assert not errors, f"Browser JS errors: {errors}"
            assert not requests, f"Network traffic: {requests}"
            print("PASS native browser fence tests: 3 / 3; zero effects/requests/page errors")
            context.close()
        finally:
            browser.close()

if __name__ == "__main__":
    run()
