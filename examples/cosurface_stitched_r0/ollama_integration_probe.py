"""End-to-end PS7 observer -> Python rickBar projection against a fake loopback Ollama.

CI-only fake endpoint. Never accesses the user's X2 or any real model.
"""
import json
import shutil
import subprocess
import threading
import unittest
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from model_status_projection import project

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "ollama_status.ps1"

class FakeOllama(BaseHTTPRequestHandler):
    requests = []
    def do_GET(self):
        self.requests.append(self.path)
        if self.path != "/api/tags":
            self.send_error(404)
            return
        body = json.dumps({"models": [
            {"name": "qwen3:4b", "size": 2500000000},
            {"name": "another-local:small", "size": 100000}
        ]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass

class EndToEnd(unittest.TestCase):
    def test_observer_to_projection(self):
        if shutil.which("pwsh") is None:
            self.fail("PowerShell 7 is required; do not silently skip")
        FakeOllama.requests = []
        try:
            server = ThreadingHTTPServer(("127.0.0.1", 11434), FakeOllama)
        except OSError as exc:
            self.fail(f"test loopback port unavailable: {exc}")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(SCRIPT)],
                capture_output=True, text=True, timeout=15, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            actual = json.loads(result.stdout)
            self.assertEqual(actual["status"], "LOCAL_MODEL_INVENTORY_OBSERVED")
            self.assertEqual(actual["model_count"], 2)
            self.assertEqual(actual["model_names"], ["another-local:small", "qwen3:4b"])
            self.assertEqual(actual["verified_work_effects"], 0)
            self.assertEqual(FakeOllama.requests, ["/api/tags"])
            projected = project(actual, now_utc=datetime.now(timezone.utc))
            self.assertEqual(projected["state"], "LOCAL_MODEL_INVENTORY_OBSERVED")
            self.assertEqual(projected["model_count"], 2)
            self.assertFalse(projected["show_in_rail"])
            self.assertEqual(projected["x2_power_state"], "NOT_INFERRED")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

if __name__ == "__main__":
    unittest.main()
