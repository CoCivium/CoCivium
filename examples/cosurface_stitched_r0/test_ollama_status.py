"""Guard local RickBar/Ollama observer against accidental agent/service scope."""
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("ollama_status.ps1").read_text(encoding="utf-8")

class OllamaStatusContract(unittest.TestCase):
    def test_loopback_inventory_only(self):
        self.assertIn("http://127.0.0.1:11434/api/tags", SCRIPT)
        self.assertIn("Invoke-RestMethod -Method Get", SCRIPT)
        self.assertIn("-NoProxy", SCRIPT)
        self.assertIn("LOCAL_MODEL_INVENTORY_OBSERVED", SCRIPT)
        self.assertIn("OLLAMA_ENDPOINT_UNREACHABLE", SCRIPT)
        self.assertIn("no_model_inference = $true", SCRIPT)
        self.assertIn("verified_work_effects = 0", SCRIPT)

    def test_fail_closed_and_no_overwrite(self):
        self.assertIn("[IO.FileMode]::CreateNew", SCRIPT)
        self.assertIn("OUTPUT_DIRECTORY_NOT_FOUND_HOLD", SCRIPT)
        for forbidden in ("Start-Process", "Stop-Process", "Remove-Item", "Register-ScheduledTask",
                          "New-Service", "Set-ExecutionPolicy", "ollama pull",
                          "ollama run", "/api/generate", "/api/chat", "Invoke-Expression"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, SCRIPT)

    def test_never_conflate_model_failure_with_x2_failure(self):
        self.assertIn("Do not report that X2 is offline", SCRIPT)
        self.assertNotIn("X2_OFFLINE", SCRIPT)

if __name__ == "__main__":
    unittest.main()
