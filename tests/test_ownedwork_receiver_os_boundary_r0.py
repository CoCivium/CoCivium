#!/usr/bin/env python3
"""CI-only, two-UID process boundary and restart test for the existing receiver.

The privileged synthetic SQLite receiver stays behind a 0700 directory.
A separate OS user ('nobody') can reach only an ephemeral Unix socket.
No live devices, production identity, independent host, or CoEx ACK.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoNarrativeWorkIDR0 import commit_once, readback
from CoOwnedWorkSqliteBridgeR0 import (
    BROWSER_SCHEMA, adapt, issue_receiver_revocation_grant, node_fixture,
)

SERVER = ROOT / "tests/ownedwork_receiver_socket_canary_r0.py"
JS = ROOT / "examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js"
GATE = ROOT / "tests/fixtures/ownedwork_synthetic_gate_r0.json"

# This code runs in a DIFFERENT OS process under UID nobody, not the test
# runner's UID. It never receives the private DB or grant-issuer file handles.
UNPRIVILEGED_CLIENT = r'''
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys

args = json.loads(sys.stdin.read())
assert os.geteuid() != args["receiver_uid"], "HELD_SAME_OS_PRINCIPAL"
db = Path(args["db"])
try:
    fd = os.open(db, os.O_RDWR)
except PermissionError:
    direct_db_denied = True
else:
    os.close(fd)
    raise AssertionError("HELD_RAW_DB_WRITE_EXPOSED")

sys.path.insert(0, args["scripts_dir"])
from CoOwnedWorkSqliteBridgeR0 import issue_receiver_revocation_grant
try:
    issue_receiver_revocation_grant(
        db, args["packet"], "CI_UNTRUSTED_ACTOR", ttl_seconds=60)
except (PermissionError, sqlite3.OperationalError):
    direct_issue_denied = True
else:
    raise AssertionError("HELD_UNPRIVILEGED_GRANT_ISSUER_EXPOSED")

pending = Path(args["pending_path"])
if not pending.exists():
    pending.write_text(
        json.dumps({"work_id": args["packet"]["work_id"],
                    "pending_edit": "synthetic unsent client branch",
                    "authoritative": False}, sort_keys=True) + "\n",
        encoding="utf-8")
pending_sha = hashlib.sha256(pending.read_bytes()).hexdigest()

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
    sock.settimeout(5)
    sock.connect(args["socket"])
    sock.sendall((json.dumps(args["request"], sort_keys=True) + "\n")
                 .encode("utf-8"))
    with sock.makefile("rb") as reader:
        response = json.loads(reader.readline())
print(json.dumps({
    "euid": os.geteuid(), "direct_db_denied": direct_db_denied,
    "direct_issue_denied": direct_issue_denied,
    "pending_sha256": pending_sha, "response": response,
}, sort_keys=True))
'''


class ReceiverOSBoundaryCanary(unittest.TestCase):
    def setUp(self):
        self.assertEqual(os.environ.get("COOWNEDWORK_OS_BOUNDARY_CI"), "1")
        check = subprocess.run(
            ["sudo", "-n", "-u", "nobody", "id", "-u"],
            capture_output=True, text=True, timeout=5, check=True)
        self.assertNotEqual(int(check.stdout.strip()), os.geteuid())

    def start_server(self, db, packet_path, socket_path):
        env = dict(os.environ, COOWNEDWORK_OS_BOUNDARY_CI="1")
        process = subprocess.Popen(
            [sys.executable, "-B", str(SERVER), "--db", str(db),
             "--packet", str(packet_path), "--socket", str(socket_path)],
            cwd=ROOT, env=env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        for _ in range(100):
            if socket_path.is_socket():
                self.assertIsNone(process.poll(), "HELD_RECEIVER_EXITED")
                return process
            if process.poll() is not None:
                out, err = process.communicate(timeout=3)
                self.fail("HELD_RECEIVER_START: " + out + err)
            time.sleep(0.05)
        process.terminate()
        out, err = process.communicate(timeout=5)
        self.fail("HELD_RECEIVER_SOCKET_TIMEOUT: " + out + err)

    def stop_server(self, process):
        if process.poll() is None:
            process.terminate()
        out, err = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0,
                         "HELD_RECEIVER_STOP: " + out + err)

    def client(self, db, socket_path, packet, pending_path, request):
        args = {
            "db": str(db), "socket": str(socket_path),
            "packet": packet, "pending_path": str(pending_path),
            "request": request, "scripts_dir": str(ROOT / "scripts"),
            "receiver_uid": os.geteuid(),
        }
        result = subprocess.run(
            ["sudo", "-n", "-u", "nobody", sys.executable,
             "-B", "-c", UNPRIVILEGED_CLIENT],
            input=json.dumps(args), capture_output=True, text=True,
            timeout=12, check=False)
        self.assertEqual(result.returncode, 0,
                         "HELD_UNPRIVILEGED_CLIENT: " + result.stderr)
        observed = json.loads(result.stdout)
        self.assertNotEqual(observed["euid"], os.geteuid())
        self.assertTrue(observed["direct_db_denied"])
        self.assertTrue(observed["direct_issue_denied"])
        self.assertFalse(observed["response"]["receiver_ack"])
        return observed

    def test_unprivileged_revoke_hold_authorized_grant_restart_and_pending(self):
        fixture = node_fixture(JS)
        record = {
            "schema": BROWSER_SCHEMA + ".Record",
            "packet": fixture, "state": "ACTIVE",
            "commit_sequence": 1, "receiver_ack": False,
            "source_verified_by_browser": False,
        }
        gate = json.loads(GATE.read_text(encoding="utf-8"))
        packet = adapt(record, gate, os.environ["COPRE_PINNED_SOURCE"], JS)
        with tempfile.TemporaryDirectory(prefix="ownedwork-os-boundary-") as d:
            root = Path(d)
            os.chmod(root, 0o755)  # nobody can traverse only this CI fixture
            private = root / "receiver-private"
            private.mkdir(mode=0o700)
            os.chmod(private, 0o700)
            public_socket = root / "socket-public"
            public_socket.mkdir(mode=0o755)
            os.chmod(public_socket, 0o755)
            pending_dir = root / "client-pending"
            pending_dir.mkdir(mode=0o733)
            os.chmod(pending_dir, 0o733)
            pending = pending_dir / "synthetic-unsent-branch.json"
            db = private / "receiver.sqlite"
            packet_path = private / "packet.json"
            packet_path.write_text(json.dumps(packet, sort_keys=True) + "\n",
                                   encoding="utf-8")
            self.assertEqual(commit_once(db, packet)["new_commits"], 1)
            actor = "CI_SYNTHETIC_AUTHORIZED_ACTOR"
            token = issue_receiver_revocation_grant(db, packet, actor, 300)
            socket_path = public_socket / "receiver.sock"
            process = self.start_server(db, packet_path, socket_path)
            try:
                first = self.client(db, socket_path, packet, pending,
                                    {"action": "READ"})
                self.assertEqual(first["response"]["state"],
                                 "COLD_SOURCE_RECONSTRUCTED")
                pending_sha = first["pending_sha256"]
                for request, reason in (
                    ({"action": "REVOKE", "actor_id": actor,
                      "grant_token": None}, "HELD_UNAUTHENTICATED_REVOCATION"),
                    ({"action": "REVOKE", "actor_id": actor,
                      "grant_token": "A" * 43},
                     "HELD_UNAUTHENTICATED_REVOCATION"),
                    ({"action": "REVOKE", "actor_id": "CI_OTHER_ACTOR",
                      "grant_token": token}, "HELD_UNAUTHORIZED_ACTOR"),
                    ({"action": "ISSUE_GRANT"}, "HELD_UNKNOWN_ACTION"),
                ):
                    observed = self.client(db, socket_path, packet,
                                           pending, request)
                    self.assertEqual(observed["response"]["state"], "HELD")
                    self.assertEqual(observed["response"]["reason"], reason)
                    self.assertEqual(observed["pending_sha256"], pending_sha)
                self.assertEqual(readback(db, expected_packet=packet)["state"],
                                 "COLD_SOURCE_RECONSTRUCTED")
                authorized = self.client(
                    db, socket_path, packet, pending,
                    {"action": "REVOKE", "actor_id": actor,
                     "grant_token": token})
                self.assertEqual(authorized["response"]["state"],
                                 "SYNTHETIC_REVOKED")
                self.assertEqual(authorized["pending_sha256"], pending_sha)
            finally:
                self.stop_server(process)

            self.assertEqual(readback(db, expected_packet=packet)["state"],
                             "HELD_REVOKED")
            self.assertFalse(socket_path.exists())
            process = self.start_server(db, packet_path, socket_path)
            try:
                cold = self.client(db, socket_path, packet, pending,
                                   {"action": "READ"})
                self.assertEqual(cold["response"]["state"], "HELD_REVOKED")
                replay = self.client(
                    db, socket_path, packet, pending,
                    {"action": "REVOKE", "actor_id": actor,
                     "grant_token": token})
                self.assertEqual(replay["response"]["state"], "HELD")
                self.assertEqual(replay["response"]["reason"],
                                 "HELD_GRANT_REPLAY")
                self.assertEqual(replay["pending_sha256"], pending_sha)
            finally:
                self.stop_server(process)

            self.assertEqual(
                hashlib.sha256(pending.read_bytes()).hexdigest(), pending_sha)
            self.assertEqual(readback(db, expected_packet=packet)["state"],
                             "HELD_REVOKED")
            print(json.dumps({
                "state": "CI_OS_PRINCIPAL_BOUNDARY_AND_RESTART_PASS",
                "distinct_os_uids": True, "unprivileged_db_write_denied": True,
                "unprivileged_grant_issue_denied": True,
                "unauthorized_revoke_held": True,
                "receiver_restart_replay_held": True,
                "client_pending_sha256": pending_sha,
                "client_pending_is_nonauthoritative": True,
                "receiver_ack": False, "independent_host": False,
                "production_identity": False, "x2_runtime": False,
            }, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
