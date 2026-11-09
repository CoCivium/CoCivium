#!/usr/bin/env python3
"""CoMVP+ / CoLockStep+ R0: local source-qualified release slots.

Operational boundary: atomic local SQLite pointer transitions over pinned
source artifacts. This does NOT establish a usable native X2 service,
off-host receiver acceptance, public product release, or independent QA.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

_ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
MAX_SOURCE_BYTES = 1024 * 1024
MAX_TEST_BYTES = 256 * 1024
MAX_TEST_SEC = 10


class Held(ValueError):
    pass


def _require(ok, reason):
    if not ok:
        raise Held(reason)


def _sha(data: bytes):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _name(value):
    _require(isinstance(value, str) and _ID.fullmatch(value), "INVALID_SLOT_NAME")
    return value


def _revision(value):
    _require(isinstance(value, str) and _SHA.fullmatch(value), "INVALID_REVISION")
    return value


class CoMVPSlots:
    """Multiple locally qualified prodlet heads, with atomic cohort updates.

    SQLite transactions and exact artifact hashes are mechanical guarantees.
    Validator programs are locally executed code, not independent reviewers.
    """

    def __init__(self, db_path, source_root):
        self.root = Path(source_root).resolve(strict=True)
        _require(self.root.is_dir(), "SOURCE_ROOT_NOT_DIRECTORY")
        self.db = sqlite3.connect(str(db_path), timeout=5, isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS versions (
            slot TEXT NOT NULL, revision TEXT NOT NULL,
            artifact_rel TEXT NOT NULL, test_rel TEXT NOT NULL,
            test_sha TEXT NOT NULL, deps_json TEXT NOT NULL,
            state TEXT NOT NULL, test_log_sha TEXT,
            PRIMARY KEY(slot,revision))""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS heads (
            slot TEXT PRIMARY KEY, revision TEXT NOT NULL, generation INTEGER NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS contracts (
            slot TEXT PRIMARY KEY, acceptance_rel TEXT NOT NULL,
            acceptance_sha TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL, action TEXT NOT NULL,
            changed_json TEXT NOT NULL, previous_hash TEXT NOT NULL,
            digest TEXT NOT NULL)""")

    def close(self):
        self.db.close()

    def _source(self, relative, limit):
        _require(isinstance(relative, str) and relative and
                 not Path(relative).is_absolute() and "\\" not in relative,
                 "INVALID_SOURCE_PATH")
        # Resolve without requiring existence first, so traversal is held even
        # when the target outside root happens not to exist.
        path = (self.root / relative).resolve()
        _require(path.is_relative_to(self.root), "SOURCE_OUTSIDE_ROOT")
        _require(path.is_file(), "SOURCE_MISSING_OR_NOT_FILE")
        _require(path.stat().st_size <= limit, "SOURCE_TOO_LARGE")
        raw = path.read_bytes()
        _require(len(raw) <= limit, "SOURCE_TOO_LARGE")
        return path, _sha(raw)

    def _event(self, action, changed):
        prev = self.db.execute("SELECT digest FROM events ORDER BY id DESC LIMIT 1").fetchone()
        parent = prev[0] if prev else "0" * 64
        stamp = _utc()
        data = {"timestamp": stamp, "action": action,
                "changed": changed, "previous_hash": parent}
        digest = _sha(_canonical(data).encode())
        self.db.execute("INSERT INTO events(timestamp,action,changed_json,previous_hash,digest) VALUES (?,?,?,?,?)",
                        (stamp, action, _canonical(changed), parent, digest))
        return digest

    def stage(self, slot, artifact_rel, test_rel, dependencies=(), acceptance_rel=None):
        slot = _name(slot)
        _, revision = self._source(artifact_rel, MAX_SOURCE_BYTES)
        _, test_sha = self._source(test_rel, MAX_TEST_BYTES)
        acceptance_sha = None
        if acceptance_rel is not None:
            _, acceptance_sha = self._source(acceptance_rel, MAX_TEST_BYTES)
        _require(isinstance(dependencies, (list, tuple)) and len(dependencies) <= 24,
                 "UNBOUNDED_DEPENDENCIES")
        deps = {}
        for item in dependencies:
            _require(isinstance(item, tuple) and len(item) == 2, "INVALID_DEPENDENCY")
            other, required_rev = item
            _name(other)
            _revision(required_rev)
            _require(other != slot and other not in deps, "INVALID_DEPENDENCY_IDENTITY")
            deps[other] = required_rev
        self.db.execute("BEGIN IMMEDIATE")
        try:
            contract = self.db.execute(
                "SELECT acceptance_rel,acceptance_sha FROM contracts WHERE slot=?",
                (slot,)).fetchone()
            if contract is not None:
                _require(acceptance_rel is None or
                         (acceptance_rel, acceptance_sha) == contract,
                         "PINNED_ACCEPTANCE_CONTRACT_CHANGE")
            elif acceptance_rel is not None:
                any_previous = self.db.execute(
                    "SELECT 1 FROM versions WHERE slot=? LIMIT 1", (slot,)).fetchone()
                _require(not any_previous, "CONTRACT_RETROFIT_REQUIRES_REVIEW")
                self.db.execute(
                    "INSERT INTO contracts(slot,acceptance_rel,acceptance_sha) VALUES (?,?,?)",
                    (slot, acceptance_rel, acceptance_sha))
                self._event("PIN_ACCEPTANCE_CONTRACT",
                            {"slot": slot, "acceptance_sha256": acceptance_sha})
            row = self.db.execute("SELECT artifact_rel,test_rel,test_sha,deps_json FROM versions WHERE slot=? AND revision=?",
                                  (slot, revision)).fetchone()
            fields = (artifact_rel, test_rel, test_sha, _canonical(deps))
            _require(row is None or row == fields, "REVISION_REGISTRATION_CONFLICT")
            if row is None:
                self.db.execute("""INSERT INTO versions(slot,revision,artifact_rel,test_rel,test_sha,deps_json,state)
                                   VALUES (?,?,?,?,?,?,'STAGED')""", (slot, revision, *fields))
                self._event("STAGE", {"slot": slot, "revision": revision})
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return {"state": "STAGED_OR_EXISTING", "slot": slot, "revision": revision,
                "acceptance_contract_pinned": bool(contract is not None or acceptance_sha),
                "source_only": True}

    def qualify(self, slot, revision):
        slot, revision = _name(slot), _revision(revision)
        row = self.db.execute("""SELECT artifact_rel,test_rel,test_sha,state FROM versions
                                 WHERE slot=? AND revision=?""", (slot,revision)).fetchone()
        _require(row is not None, "VERSION_NOT_STAGED")
        artifact_rel, test_rel, expected_test_sha, state = row
        _, current_sha = self._source(artifact_rel, MAX_SOURCE_BYTES)
        test_path, current_test_sha = self._source(test_rel, MAX_TEST_BYTES)
        _require(current_sha == revision and current_test_sha == expected_test_sha,
                 "SOURCE_OR_TEST_MUTATED")
        # Deliberately run registered Python programs without a shell.
        # They are NOT sandboxed: on a real host only authorize trusted tests.
        env = dict(os.environ, COMVP_ARTIFACT_PATH=str((self.root / artifact_rel).resolve()),
                   COMVP_SLOT=slot, COMVP_REVISION=revision)
        try:
            out = subprocess.run([sys.executable, "-B", str(test_path)],
                                 cwd=str(self.root), timeout=MAX_TEST_SEC,
                                 capture_output=True, check=False, env=env)
        except subprocess.TimeoutExpired:
            return {"state": "HELD_TEST_TIMEOUT", "slot": slot, "revision": revision}
        contract = self.db.execute(
            "SELECT acceptance_rel,acceptance_sha FROM contracts WHERE slot=?",
            (slot,)).fetchone()
        acceptance_out = None
        if out.returncode == 0 and contract is not None:
            acceptance_path, actual_acceptance_sha = self._source(
                contract[0], MAX_TEST_BYTES)
            _require(actual_acceptance_sha == contract[1],
                     "PINNED_ACCEPTANCE_CONTRACT_MUTATED")
            try:
                acceptance_out = subprocess.run(
                    [sys.executable, "-B", str(acceptance_path)], cwd=str(self.root),
                    timeout=MAX_TEST_SEC, capture_output=True,
                    check=False, env=env)
            except subprocess.TimeoutExpired:
                return {"state": "HELD_ACCEPTANCE_TIMEOUT", "slot": slot,
                        "revision": revision}
        _, after_sha = self._source(artifact_rel, MAX_SOURCE_BYTES)
        _, after_test_sha = self._source(test_rel, MAX_TEST_BYTES)
        _require(after_sha == revision and after_test_sha == expected_test_sha,
                 "SOURCE_MUTATED_DURING_TEST")
        if contract is not None:
            _, after_acceptance_sha = self._source(contract[0], MAX_TEST_BYTES)
            _require(after_acceptance_sha == contract[1],
                     "PINNED_ACCEPTANCE_CONTRACT_MUTATED")
        log_bytes = out.stdout + out.stderr
        if acceptance_out is not None:
            log_bytes += acceptance_out.stdout + acceptance_out.stderr
        digest = _sha(log_bytes[:MAX_SOURCE_BYTES])
        if out.returncode != 0:
            return {"state": "HELD_TEST_FAILED", "slot": slot, "revision": revision,
                    "test_log_sha256": digest, "exit_code": out.returncode}
        if acceptance_out is not None and acceptance_out.returncode != 0:
            return {"state": "HELD_ACCEPTANCE_REGRESSION",
                    "slot": slot, "revision": revision,
                    "acceptance_contract_sha256": contract[1],
                    "test_log_sha256": digest, "exit_code": acceptance_out.returncode}
        qualified_state = "CONTRACT_TESTED" if contract is not None else "SOURCE_TESTED"
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row2 = self.db.execute("SELECT state,test_log_sha FROM versions WHERE slot=? AND revision=?",
                                   (slot, revision)).fetchone()
            _require(row2 is not None, "VERSION_DISAPPEARED")
            if row2[0] != qualified_state:
                self.db.execute("UPDATE versions SET state=?,test_log_sha=? WHERE slot=? AND revision=?",
                                (qualified_state, digest, slot, revision))
                self._event("SOURCE_TEST_PASS", {"slot": slot, "revision": revision,
                                                "test_log_sha256": digest,
                                                "contract_pinned": bool(contract)})
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return {"state": "CONTRACT_TESTED_LOCAL_ONLY" if contract is not None else
                         "SOURCE_TESTED_LOCAL_ONLY",
                "slot": slot, "revision": revision,
                "test_log_sha256": digest,
                "acceptance_contract_sha256": contract[1] if contract else None,
                "receiver_qualified": False}

    def active(self):
        rows = self.db.execute("SELECT slot,revision FROM heads ORDER BY slot").fetchall()
        return {slot: rev for slot, rev in rows}

    def promote_cohort(self, changes, expected_heads):
        """One transaction for compatible changes; never self-approve a real MVP."""
        _require(isinstance(changes, dict) and 0 < len(changes) <= 24, "INVALID_COHORT")
        _require(isinstance(expected_heads, dict) and set(expected_heads) == set(changes),
                 "MISSING_CAS_EXPECTATIONS")
        for slot, rev in changes.items():
            _name(slot)
            _revision(rev)
            expected = expected_heads[slot]
            if expected is not None:
                _revision(expected)
        # Acquire the writer lock before checking heads and every active edge.
        self.db.execute("BEGIN IMMEDIATE")
        try:
            current = self.active()
            for slot in changes:
                _require(current.get(slot) == expected_heads[slot], "STALE_RELEASE_HEAD")
            proposed = {**current, **changes}
            details = {}
            for slot, rev in proposed.items():
                row = self.db.execute("""SELECT artifact_rel,test_rel,test_sha,deps_json,state
                                         FROM versions WHERE slot=? AND revision=?""",
                                      (slot, rev)).fetchone()
                contract = self.db.execute(
                    "SELECT acceptance_rel,acceptance_sha FROM contracts WHERE slot=?",
                    (slot,)).fetchone()
                required_state = "CONTRACT_TESTED" if contract else "SOURCE_TESTED"
                _require(row is not None and row[4] == required_state,
                         "UNQUALIFIED_RELEASE_VERSION")
                artifact_rel, test_rel, test_sha, deps_json, _ = row
                _, actual_artifact = self._source(artifact_rel, MAX_SOURCE_BYTES)
                _, actual_test = self._source(test_rel, MAX_TEST_BYTES)
                _require(actual_artifact == rev and actual_test == test_sha,
                         "ACTIVE_SOURCE_CHANGED")
                if contract is not None:
                    _, check_acceptance = self._source(contract[0], MAX_TEST_BYTES)
                    _require(check_acceptance == contract[1],
                             "PINNED_ACCEPTANCE_CONTRACT_MUTATED")
                deps = json.loads(deps_json)
                for dependency, expected_rev in deps.items():
                    _require(proposed.get(dependency) == expected_rev,
                             "COHORT_DEPENDENCY_INCOMPATIBLE")
                details[slot] = {"revision": rev, "depends": deps}
            changed = {}
            for slot, rev in changes.items():
                prior = current.get(slot)
                if prior == rev:
                    continue
                row = self.db.execute("SELECT generation FROM heads WHERE slot=?", (slot,)).fetchone()
                generation = row[0] + 1 if row else 1
                self.db.execute("""INSERT INTO heads(slot,revision,generation) VALUES (?,?,?)
                                   ON CONFLICT(slot) DO UPDATE SET revision=excluded.revision,
                                   generation=excluded.generation""",
                                (slot, rev, generation))
                changed[slot] = {"from": prior, "to": rev, "generation": generation}
            if changed:
                audit_hash = self._event("COHORT_POINTER_COMMIT", changed)
            else:
                audit_hash = None
            self.db.execute("COMMIT")
            return {"state": "SOURCE_HEADS_COMMITTED_LOCAL_ONLY",
                    "changed": changed, "active": proposed, "audit_hash": audit_hash,
                    "receiver_qualified": False, "native_runtime_updated": False}
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def audit_chain(self):
        previous = "0" * 64
        count = 0
        for timestamp, action, raw, parent, digest in self.db.execute(
                "SELECT timestamp,action,changed_json,previous_hash,digest FROM events ORDER BY id"):
            _require(parent == previous, "EVENT_PARENT_MISMATCH")
            rebuilt = _sha(_canonical({"timestamp":timestamp,"action":action,
                                       "changed":json.loads(raw),"previous_hash":parent}).encode())
            _require(rebuilt == digest, "EVENT_DIGEST_MISMATCH")
            previous = digest
            count += 1
        return {"events_checked": count, "latest_digest": previous,
                "tamper_evident_local_only": True, "independent_custody": False}


def main(argv=None):
    """Usable local CLI over the same atomic release slots; no remote effects."""
    import argparse
    p = argparse.ArgumentParser(description="Source-qualified CoMVP release heads (local only)")
    p.add_argument("--root", required=True, help="Trusted existing source root")
    p.add_argument("--db", required=True, help="Local SQLite release-head store")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("audit")
    stage = sub.add_parser("stage")
    stage.add_argument("--slot", required=True)
    stage.add_argument("--artifact", required=True)
    stage.add_argument("--test", required=True)
    stage.add_argument("--deps-json", default="{}",
                       help="JSON object mapping dependent slot to exact source revision")
    stage.add_argument("--acceptance", help="Trusted pinned minimum-use test, on first version only")
    qualify = sub.add_parser("qualify")
    qualify.add_argument("--slot", required=True)
    qualify.add_argument("--revision", required=True)
    promote = sub.add_parser("promote")
    promote.add_argument("--changes-json", required=True,
                         help="JSON map slot -> source revision")
    promote.add_argument("--expected-json", required=True,
                         help="JSON map of exactly the changed slots to previous revision/null")
    a = p.parse_args(argv)
    try:
        store = CoMVPSlots(a.db, a.root)
        try:
            if a.command == "status":
                value = {"state": "SOURCE_HEADS_LOCAL_ONLY", "active": store.active(),
                         "audit": store.audit_chain(), "receiver_qualified": False}
            elif a.command == "audit":
                value = store.audit_chain()
            elif a.command == "stage":
                deps = json.loads(a.deps_json)
                _require(isinstance(deps, dict), "INVALID_DEPS_JSON")
                value = store.stage(a.slot, a.artifact, a.test,
                                    tuple(deps.items()), acceptance_rel=a.acceptance)
            elif a.command == "qualify":
                value = store.qualify(a.slot, a.revision)
            else:
                value = store.promote_cohort(json.loads(a.changes_json),
                                             json.loads(a.expected_json))
        finally:
            store.close()
        print(_canonical(value))
        return 0 if not str(value.get("state", "")).startswith("HELD_") else 3
    except (Held, ValueError, TypeError, OSError, sqlite3.Error) as exc:
        print(_canonical({"state": "HELD", "reason": str(exc)[:120],
                          "native_runtime_updated": False, "receiver_qualified": False}))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
