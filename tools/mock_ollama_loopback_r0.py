#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

EXPECTED_RESULT = {
    "analysis_summary": "Deterministic loopback adapter qualification response.",
    "proposed_deltas": [],
    "contradictions": [],
    "tests": [
        "loopback_ollama_protocol",
        "json_response_parse",
        "zero_effect_artifact",
    ],
    "uncertainty": ["MOCK_RECEIVER_NE_REAL_MODEL"],
    "source_refs": ["fixture:model-substrate-light-local-worker-adapter-r0"],
    "nonclaims": [
        "MOCK_RESPONSE_NE_MODEL_REASONING",
        "MOCK_OLLAMA_NE_REAL_OLLAMA_RUNTIME",
        "ADAPTER_PASS_NE_MODEL_QUALITY",
    ],
}


class Handler(BaseHTTPRequestHandler):
    expected_model = None

    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/api/generate":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            req = json.loads(raw.decode("utf-8"))
        except Exception:
            self.send_error(400)
            return

        checks = [
            req.get("model") == self.expected_model,
            req.get("stream") is False,
            req.get("format") == "json",
            isinstance(req.get("prompt"), str),
            '"materialization_state": "LOGICAL_ONLY"' in req.get("prompt", ""),
            '"spawn_id": "spawn:substrate-light-local-worker-r0"' in req.get("prompt", ""),
            "do not execute tools" in req.get("prompt", "").lower(),
        ]
        if not all(checks):
            self.send_error(422)
            return

        envelope = {
            "model": self.expected_model,
            "created_at": "2026-09-30T00:00:00Z",
            "response": json.dumps(EXPECTED_RESULT, sort_keys=True, separators=(",", ":")),
            "done": True,
            "done_reason": "stop",
        }
        encoded = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ready-file", required=True)
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--expected-model", required=True)
    args = ap.parse_args()

    Handler.expected_model = args.expected_model
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    Path(args.ready_file).write_text(str(server.server_port), encoding="ascii")
    server.handle_request()
    server.server_close()


if __name__ == "__main__":
    main()
