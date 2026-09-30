#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    fixture = None

    def log_message(self, fmt, *args):
        return

    def _send(self, obj):
        encoded = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path != "/api/tags":
            self.send_error(404)
            return
        self._send({"models": self.fixture["models"]})

    def do_POST(self):
        if self.path != "/api/generate":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            req = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self.send_error(400)
            return
        selected = self.fixture["selected_model"]
        prompt = req.get("prompt", "")
        checks = [
            req.get("model") == selected["name"],
            req.get("stream") is False,
            req.get("format") == "json",
            isinstance(prompt, str),
            '"materialization_state": "LOGICAL_ONLY"' in prompt,
            '"spawn_id": "spawn:bound-local-ollama-r0"' in prompt,
            "do not execute tools" in prompt.lower(),
        ]
        if not all(checks):
            self.send_error(422)
            return
        self._send({
            "model": selected["name"],
            "created_at": "2026-09-30T00:00:00Z",
            "response": json.dumps(
                self.fixture["expected_worker_result"],
                sort_keys=True,
                separators=(",", ":")
            ),
            "done": True,
            "done_reason": "stop"
        })

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--ready-file", required=True)
    ap.add_argument("--port", type=int, default=0)
    args = ap.parse_args()

    Handler.fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    Path(args.ready_file).write_text(str(server.server_port), encoding="ascii")
    server.serve_forever()

if __name__ == "__main__":
    main()
