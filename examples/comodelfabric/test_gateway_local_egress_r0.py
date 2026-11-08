"""Exact-loopback gateway URL and prompt-egress regression tests.

Ephemeral localhost HTTP only. No real Ollama, external provider or X2.
"""
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ollama_gateway_r0 import OllamaGateway, verified_loopback_base_url


class FakeOllama(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.server.seen.append(("GET", self.path))
        if self.path == "/api/tags":
            data = b'{"models":[{"name":"qualified-fixture"}]}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self):
        self.server.seen.append(("POST", self.path))
        if self.path == "/api/generate":
            self.send_response(307)
            self.send_header("Location", "https://example.invalid/forbidden-prompt-egress")
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_error(404)


class ExactLoopbackContract(unittest.TestCase):
    def test_local_origins_normalized(self):
        self.assertEqual(verified_loopback_base_url("http://127.0.0.1:11434/"),
                         "http://127.0.0.1:11434")
        self.assertEqual(verified_loopback_base_url("http://LOCALHOST:11434"),
                         "http://localhost:11434")

    def test_prefix_tricks_and_nonlocal_origins_denied(self):
        invalid = (
            "http://127.0.0.1:11434@evil.example",
            "http://localhost:11434@evil.example",
            "http://127.0.0.1:11434.attacker.invalid",
            "http://localhost:11434.evil.invalid",
            "http://127.0.0.2:11434",
            "https://127.0.0.1:11434",
            "http://127.0.0.1",
            "http://localhost:bogus",
            "http://localhost:99999",
            "http://localhost:11434?target=remote",
            "http://localhost:11434#remote",
            "http://localhost:11434/unexpected/path",
            "http://user:pass@localhost:11434",
            "http://[::1]:11434",
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    OllamaGateway(value)

    def test_invalid_timeouts_denied(self):
        for timeout in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    OllamaGateway(timeout=timeout)


class RealLoopbackHttpNoEgress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOllama)
        cls.server.seen = []
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def test_proxy_environment_cannot_capture_local_metadata(self):
        with patch.dict(os.environ, {"HTTP_PROXY": "http://127.0.0.1:1",
                                     "HTTPS_PROXY": "http://127.0.0.1:1",
                                     "NO_PROXY": ""}):
            gateway = OllamaGateway(self.base)
            self.assertEqual(gateway.models(), ["qualified-fixture"])
        self.assertIn(("GET", "/api/tags"), self.server.seen)

    def test_redirect_never_forwards_local_prompt_to_provider(self):
        seen_before = len(self.server.seen)
        gateway = OllamaGateway(self.base)
        result = gateway.generate("synthetic secret-shaped placeholder", "fixture-model", "w-fixture")
        self.assertEqual(result["status"], "MODEL_UNAVAILABLE")
        self.assertEqual(result["error"], "HTTPError")
        self.assertEqual(self.server.seen[seen_before:], [("POST", "/api/generate")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
