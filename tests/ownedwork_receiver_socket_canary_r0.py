#!/usr/bin/env python3
"""CI-only local Unix-socket façade for an existing synthetic WorkID receiver.

A separate unprivileged OS client can read a minimal state and request revoke,
but cannot issue a grant or write the SQLite database. This is an ephemeral
test fixture, NOT a deployable server, production authentication, or CoEx ACK.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import socketserver
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from CoNarrativeWorkIDR0 import Held, readback, validate
from CoOwnedWorkSqliteBridgeR0 import require, revoke_with_receiver_grant


class ClientHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            raw = self.rfile.readline(4097)
            require(raw.endswith(b"\n") and len(raw) <= 4096,
                    "HELD_REQUEST_SIZE")
            request = json.loads(raw)
            require(type(request) is dict, "HELD_REQUEST_SCHEMA")
            if request.get("action") == "READ":
                require(set(request) == {"action"}, "HELD_REQUEST_SCHEMA")
                current = readback(self.server.db_path,
                                   expected_packet=self.server.packet)
                result = {
                    "state": current["state"],
                    "work_id": self.server.packet["work_id"],
                    "receiver_ack": False,
                }
            elif request.get("action") == "REVOKE":
                require(set(request) ==
                        {"action", "actor_id", "grant_token"},
                        "HELD_REQUEST_SCHEMA")
                revoke_with_receiver_grant(
                    self.server.db_path, self.server.packet,
                    actor_id=request["actor_id"],
                    grant_token=request["grant_token"])
                result = {"state": "SYNTHETIC_REVOKED",
                          "receiver_ack": False}
            else:
                raise Held("HELD_UNKNOWN_ACTION")
        except Held as exc:
            result = {"state": "HELD", "reason": str(exc),
                      "receiver_ack": False}
        except (UnicodeError, ValueError) as exc:
            result = {"state": "HELD", "reason": "HELD_MALFORMED_JSON",
                      "receiver_ack": False}
        self.wfile.write((json.dumps(result, sort_keys=True) + "\n")
                         .encode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--socket", required=True)
    args = parser.parse_args()
    if os.environ.get("COOWNEDWORK_OS_BOUNDARY_CI") != "1":
        raise SystemExit("HELD_NOT_EXPLICIT_CI_CANARY")
    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    validate(packet)
    current = readback(args.db, expected_packet=packet)
    require(current["state"] == "COLD_SOURCE_RECONSTRUCTED" or
            current["state"] == "HELD_REVOKED",
            "HELD_RECEIVER_NOT_PREPARED")
    socket_path = Path(args.socket)
    require(not socket_path.exists() and not socket_path.is_symlink(),
            "HELD_SOCKET_EXISTS_NO_CLOBBER")
    with socketserver.UnixStreamServer(str(socket_path), ClientHandler) as server:
        server.db_path = args.db
        server.packet = packet
        # World-accessible synthetic socket only; private SQLite + bearer
        # permission guard. Never reuse this socket policy in production.
        os.chmod(socket_path, 0o666)
        signal.signal(signal.SIGTERM,
                      lambda *_: (_ for _ in ()).throw(SystemExit(0)))
        print("SYNTHETIC_SOCKET_READY_NO_EXTERNAL_ACK", flush=True)
        try:
            server.serve_forever(poll_interval=0.05)
        finally:
            if socket_path.is_socket():
                socket_path.unlink()


if __name__ == "__main__":
    main()
