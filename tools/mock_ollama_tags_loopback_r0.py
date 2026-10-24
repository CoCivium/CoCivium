#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    fixture = None

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        if self.path != "/api/tags":
            self.send_error(404)
            return
        encoded = json.dumps(
            {"models": self.fixture["models"]},
            sort_keys=True,
            separators=(",", ":")
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--ready-file", required=True)
    ap.add_argument("--port", type=int, default=0)
    args = ap.parse_args()

    Handler.fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    Path(args.ready_file).write_text(str(server.server_port), encoding="ascii")
    server.handle_request()
    server.server_close()

if __name__ == "__main__":
    main()
