#!/usr/bin/env python3
"""CoOwm R0: opt-in local form -> private narrative capsule.

Bound ONLY to 127.0.0.1. No ChatGPT API, clipboard hook, mouse driver, cookies,
scripts, cross-provider sync, independent receiver, or automatic sharing.
"""

import argparse
import html
import http.server
import secrets
import sys
from pathlib import Path
from urllib.parse import parse_qs

from coowm_private_narrative_capsule_r0 import MAX_BYTES, Held, capture_bytes, private_dir

MAX_FORM_BYTES = 3 * MAX_BYTES + 1024
FORM_CSS = """
:root {color-scheme:dark;font:16px/1.55 system-ui,sans-serif}
body {margin:0;background:#111526;color:#f6f3fa}
main {max-width:690px;margin:2rem auto;padding:1.3rem}
h1 {line-height:1.12;letter-spacing:-.04em}
p {color:#d0cadd}
label {font-weight:700;display:block;margin:1.4rem 0 .4rem}
textarea {box-sizing:border-box;width:100%;min-height:230px;border:2px solid #8d89a5;
  border-radius:12px;padding:.85rem;font:inherit;color:#f8f8ff;background:#23283b}
textarea:focus-visible,button:focus-visible,a:focus-visible {outline:3px solid #8ceade;outline-offset:3px}
button {margin-top:1rem;padding:.9rem 1.25rem;border:0;border-radius:999px;
 background:#b7fff2;color:#0b292c;font:inherit;font-weight:800;cursor:pointer}
aside {border:1px solid #8d89a5;border-radius:12px;padding:1rem;margin:1.3rem 0}
small {color:#cbc7d6}
"""
PAGE_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>CoOwm | Save one narrative privately</title><style>{css}</style></head>
<body><main><p>CoOwm+ &middot; private local candidate</p>
<h1>Keep the thought. Lose the repetition.</h1>
<p>Paste only a passage you choose to save. Nothing is read from other apps,
tabs, the clipboard, microphone, or screen. This stores locally on this computer.
It does <strong>not</strong> publish or sync between sessions.</p>
{status}
<form method="post" action="/" autocomplete="off">
<input type="hidden" name="token" value="{token}">
<label for="narrative">Narrative to keep</label>
<textarea id="narrative" name="narrative" maxlength="262144"
 required aria-describedby="privacy"></textarea>
<button type="submit">Save privately</button>
</form>
<p id="privacy"><small>One user-initiated submit, one content-addressed capsule.
Duplicate text reuses the existing capsule. No automatic sensing.
Closing this tab does not stop the local server; press Ctrl+C in its terminal.</small></p>
</main></body></html>"""

class CoOwmServer(http.server.HTTPServer):
    def __init__(self, private_root, port=0):
        if type(port) is not int or not 0 <= port <= 65535:
            raise ValueError("INVALID_PORT")
        self.root = private_dir(private_root)
        self.form_token = secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", port), CoOwmHandler)

class CoOwmHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # No request paths, text, CSRF token or browser metadata in console logs.
        return

    def _origin(self):
        return "http://127.0.0.1:" + str(self.server.server_port)

    def _host_ok(self):
        return self.headers.get("Host") == "127.0.0.1:" + str(self.server.server_port)

    def respond(self, code, *, status=""):
        display = ('<aside role="status">' + html.escape(status, quote=True) + '</aside>') if status else ""
        content = PAGE_TEMPLATE.format(css=FORM_CSS, status=display,
                                       token=html.escape(self.server.form_token, quote=True)).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; base-uri 'none'; script-src 'none'; "
                         "form-action 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path != "/" or not self._host_ok():
            self.respond(404, status="HELD_NO_SUCH_LOCAL_ROUTE")
        else:
            self.respond(200)

    def do_POST(self):
        if self.path != "/" or not self._host_ok():
            self.respond(403, status="HELD_INVALID_LOCAL_HOST")
            return
        if self.headers.get("Origin") != self._origin():
            self.respond(403, status="HELD_ORIGIN_NOT_LOCAL_FORM")
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].lower() != "application/x-www-form-urlencoded":
            self.respond(415, status="HELD_UNSUPPORTED_POST_FORMAT")
            return
        try:
            n = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.respond(411, status="HELD_MISSING_LENGTH")
            return
        if n <= 0 or n > MAX_FORM_BYTES:
            self.respond(413, status="HELD_OVERSIZED_FORM")
            return
        try:
            body = self.rfile.read(n).decode("ascii")
            fields = parse_qs(body, strict_parsing=True, keep_blank_values=True,
                              encoding="utf-8", errors="strict", max_num_fields=3)
        except (UnicodeError, ValueError):
            self.respond(400, status="HELD_MALFORMED_FORM")
            return
        if (set(fields) != {"token", "narrative"} or
            len(fields["token"]) != 1 or len(fields["narrative"]) != 1 or
            not secrets.compare_digest(fields["token"][0], self.server.form_token)):
            self.respond(403, status="HELD_INVALID_OR_MISSING_FORM_TOKEN")
            return
        try:
            raw = fields["narrative"][0].encode("utf-8")
            result = capture_bytes(raw, self.server.root)
        except (Held, OSError) as err:
            state = str(err) if isinstance(err, Held) else "HELD_IO_ERROR"
            self.respond(400, status=state)
            return
        state = result["state"]
        if state in {"VERIFIED_LOCAL_ONLY", "DUPLICATE_VERIFIED_LOCAL_ONLY"}:
            # No narrative echo; only a truncated digest and local status.
            self.respond(200, status=state + " | SHA256: " + result["sha256"][:16] +
                         " | No independent receiver readproof.")
        else:
            self.respond(409, status=state)

def main():
    ap = argparse.ArgumentParser(description="Consent-based localhost CoOwm intake, no external sync")
    ap.add_argument("--private-root", type=Path, required=True,
                    help="A trusted user-owned private capsule directory")
    ap.add_argument("--port", type=int, default=0, help="Loopback-only port, 0 selects a free port")
    args = ap.parse_args()
    server = CoOwmServer(args.private_root, args.port)
    print("CoOwm private intake: http://127.0.0.1:%d/" % server.server_port, flush=True)
    print("Explicit paste and click required. Ctrl+C ends server.", flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
