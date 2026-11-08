"""Synthetic end-to-end model -> WorkID receipt tests. No X2/Ollama runtime claimed."""
import json
import pathlib
import tempfile
import unittest
from ollama_gateway_r0 import OllamaGateway
from rickbar_ollama_bridge_r0 import run

class Response:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.payload).encode("utf-8")

class IntegrationTests(unittest.TestCase):
    def test_roundtrip_replay_and_conflict(self):
        def success(req, timeout):
            self.assertEqual(req.full_url, "http://127.0.0.1:11434/api/generate")
            return Response({"response":"synthetic response","done":True})
        gateway = OllamaGateway(opener=success)
        with tempfile.TemporaryDirectory() as directory:
            a = run("hello", "qwen3:4b", directory, "wid-1", gateway)
            b = run("hello", "qwen3:4b", directory, "wid-1", gateway)
            self.assertEqual(a["status"], "RECORDED_UNVERIFIED")
            self.assertEqual(b["status"], "REPLAY")
            self.assertEqual(a["receipt_sha256"], b["receipt_sha256"])
            self.assertEqual(a["model_status"], "MODEL_OUTPUT_UNVERIFIED")
            saved = json.loads((pathlib.Path(directory)/"wid-1.json").read_text())
            self.assertEqual(saved["result"]["text"], "synthetic response")
            self.assertEqual(saved["status"], "MODEL_OUTPUT_UNVERIFIED")
            def changed(req, timeout): return Response({"response":"changed","done":True})
            c = run("hello", "qwen3:4b", directory, "wid-1", OllamaGateway(opener=changed))
            self.assertEqual(c["status"], "CONFLICT")
    def test_unavailable_creates_no_receipt(self):
        def down(req, timeout): raise OSError("synthetic down")
        with tempfile.TemporaryDirectory() as directory:
            result = run("hello", "qwen3:4b", directory, "wid-2", OllamaGateway(opener=down))
            self.assertEqual(result["status"], "MODEL_UNAVAILABLE")
            self.assertFalse((pathlib.Path(directory)/"wid-2.json").exists())
    def test_invalid_id_cannot_escape_directory(self):
        def success(req, timeout): return Response({"response":"hello","done":True})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                run("hello", "qwen3:4b", directory, "../escape", OllamaGateway(opener=success))

if __name__ == "__main__":
    unittest.main(verbosity=2)
