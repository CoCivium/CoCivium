"""CoLockStep R1: browser-level baseline survival under experimental failure.

This checks the existing public CoDemoWow Truth Gate R1 offline HTML, pinned
to the exact Git blob on CoCivium/CoCivium main. It does NOT edit the baseline
or launch X2/CoOrb. An experimental clone deliberately fails during JavaScript
initialization. Browser automation chooses the untouched pinned baseline.

Scope: one CI runner/browser family; neither independent human acceptance nor
production automatic failover, multi-host recovery, or a stable MVP.
"""
import hashlib
import shutil
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "codemow" / "truth-gate-r1.html"
PINNED_BLOB = "2d3a1248e63b409436b6def098755f93065ebebb"
BOOTSCRIPT = "writePacket(baseline);validate();$('run').addEventListener"


def git_blob_sha1(blob):
    return hashlib.sha1(("blob " + str(len(blob)) + "\0").encode("ascii") + blob).hexdigest()


def launch_browser(playwright):
    # CI Ubuntu includes system Chrome; local Linux may supply Chromium.
    executable = next((shutil.which(name) for name in
                       ("google-chrome", "google-chrome-stable",
                        "chromium", "chromium-browser") if shutil.which(name)),
                      None)
    options = {"executable_path": executable} if executable else {}
    return playwright.chromium.launch(
        headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"],
        **options)


def snapshot(page):
    return {
        "verdict": page.locator("#verdict").inner_text().strip(),
        "passes": page.locator("#passed").inner_text().strip(),
        "x2": page.locator("#x2").inner_text().strip(),
        "effects": page.locator("#effects").inner_text().strip(),
    }


class BrowserSurvivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        cls.source_sha256 = hashlib.sha256(cls.source_bytes).hexdigest()
        if git_blob_sha1(cls.source_bytes) != PINNED_BLOB:
            raise AssertionError("HOLD_PUBLIC_BROWSER_BASELINE_SOURCE_DRIFT")
        cls.source_html = cls.source_bytes.decode("utf-8")
        if cls.source_html.count(BOOTSCRIPT) != 1:
            raise AssertionError("HOLD_BOOTSTRAP_ANCHOR_CHANGED")

    def test_baseline_pinned_and_public_source_unchanged(self):
        self.assertEqual(git_blob_sha1(self.source_bytes), PINNED_BLOB)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         self.source_sha256)

    def test_user_visible_task_survives_failing_successor(self):
        # Separate browser processes: closing the failed successor must not
        # terminate the known-green page or alter its source or receipt.
        with sync_playwright() as pw:
            baseline_browser = launch_browser(pw)
            try:
                baseline = baseline_browser.new_page(viewport={"width": 390, "height": 844})
                baseline_errors, baseline_requests = [], []
                baseline.on("pageerror", lambda error: baseline_errors.append(str(error)))
                baseline.on("request", lambda request: baseline_requests.append(request.url))
                baseline.set_content(self.source_html, wait_until="load")
                self.assertEqual(snapshot(baseline),
                                 {"verdict": "QUALIFIED", "passes": "5 / 5",
                                  "x2": "HELD", "effects": "0"})
                baseline.get_by_role("button", name="Run truth gate").click()
                self.assertEqual(snapshot(baseline)["passes"], "5 / 5")
                self.assertLessEqual(
                    baseline.evaluate("document.documentElement.scrollWidth"),
                    baseline.evaluate("window.innerWidth"))

                experimental_browser = launch_browser(pw)
                try:
                    successor = experimental_browser.new_page()
                    successor_errors = []
                    successor.on("pageerror", lambda error:
                                 successor_errors.append(str(error)))
                    sabotaged = self.source_html.replace(
                        BOOTSCRIPT, "throw new Error('EXPERIMENTAL_BOOT_FAILURE');", 1)
                    self.assertNotEqual(sabotaged, self.source_html)
                    successor.set_content(sabotaged, wait_until="load")
                    # The candidate's initial HTML can look qualified while
                    # its JavaScript never ran. Only exercised controls count.
                    self.assertIn("EXPERIMENTAL_BOOT_FAILURE",
                                  " ".join(successor_errors))
                    self.assertNotEqual(snapshot(successor)["passes"], "5 / 5")
                    earlier = snapshot(successor)
                    successor.get_by_role(
                        "button", name="Test unsupported X2 claim").click()
                    self.assertEqual(snapshot(successor), earlier)
                finally:
                    # Controlled browser-process interruption; do not call it
                    # a production crash or automatic host recovery.
                    experimental_browser.close()

                # The genuine user-facing baseline remains interactive.
                baseline.get_by_role(
                    "button", name="Test unsupported X2 claim").click()
                self.assertEqual(snapshot(baseline)["verdict"], "FAIL CLOSED")
                self.assertEqual(snapshot(baseline)["passes"], "4 / 5")
                baseline.get_by_role(
                    "button", name="Restore proven scope").click()
                self.assertEqual(snapshot(baseline),
                                 {"verdict": "QUALIFIED", "passes": "5 / 5",
                                  "x2": "HELD", "effects": "0"})
                self.assertEqual(baseline_errors, [])
                self.assertEqual(baseline_requests, [])
            finally:
                baseline_browser.close()

        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         self.source_sha256)


if __name__ == "__main__":
    unittest.main()
