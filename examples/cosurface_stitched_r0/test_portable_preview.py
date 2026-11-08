"""Prevent the portable CoSurface preview from silently becoming an installer."""
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("preview.ps1").read_text(encoding="utf-8")

class PortableCanaryContract(unittest.TestCase):
    def test_local_html_only_and_fail_closed(self):
        self.assertIn("Join-Path $PSScriptRoot 'index.html'", SCRIPT)
        self.assertIn("Test-Path -LiteralPath $index", SCRIPT)
        self.assertIn("NO LIVE EFFECT", SCRIPT)
        self.assertIn("Get-FileHash", SCRIPT)
        self.assertIn("Algorithm SHA256", SCRIPT)

    def test_explicit_opt_in_and_no_install(self):
        self.assertIn("param([switch]$NoLaunch)", SCRIPT)
        self.assertIn("if ($NoLaunch) { return }", SCRIPT)
        self.assertIn("Start-Process -FilePath $uri", SCRIPT)
        for forbidden in ("Invoke-Expression", "iex ", "Invoke-WebRequest", "DownloadString",
                          "Register-ScheduledTask", "New-Service", "Set-ItemProperty",
                          "Stop-Process", "Remove-Item", "Set-ExecutionPolicy"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, SCRIPT)

    def test_no_live_effect_claim(self):
        self.assertIn("PREVIEW_LAUNCH_ATTEMPTED", SCRIPT)
        self.assertIn("R5_UNCHANGED=TRUE", SCRIPT)
        self.assertNotIn("DEPLOYED=TRUE", SCRIPT)

if __name__ == "__main__":
    unittest.main()
