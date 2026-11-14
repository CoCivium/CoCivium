#!/usr/bin/env python3
"""PUBLIC_SYNTHETIC, standalone crash-at-any-boundary test, no real chat or device.

Tests the generic SQLite pre-ingest/commit/ACK boundary by actually killing a
child process with os._exit. This is NOT a drop-in CoCivium receiver, nor proof
of independent CoStead, provider, authorization or live recovery. Importantly,
unsent input before first durable commit is fundamentally unavailable.
"""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WORK_ID = 'CoPre.ReadyCycle.Synthetic.R0'
PAYLOAD = b'PUBLIC_SYNTHETIC_ONLY: approved minimal WorkID envelope, no chat transcript'
DIGEST = hashlib.sha256(PAYLOAD).hexdigest()


def open_db(path):
    con = sqlite3.connect(path, timeout=3)
    con.execute('PRAGMA synchronous=FULL')
    con.execute('CREATE TABLE IF NOT EXISTS intent (work_id TEXT PRIMARY KEY, sha TEXT NOT NULL, body BLOB NOT NULL)')
    con.commit()
    return con


def admit(path, body):
    con = open_db(path)
    try:
        con.execute('BEGIN IMMEDIATE')
        sha = hashlib.sha256(body).hexdigest()
        row = con.execute('SELECT sha FROM intent WHERE work_id=?', (WORK_ID,)).fetchone()
        if row:
            con.commit()
            return 'REPLAY_SAME' if row[0] == sha else 'HOLD_CONFLICT'
        con.execute('INSERT INTO intent VALUES (?,?,?)', (WORK_ID, sha, body))
        con.commit()
        return 'COMMITTED'
    finally:
        con.close()


def cold_read(path):
    if not path.exists():
        return 'NO_DURABLE_RECORD'
    con = sqlite3.connect(path)
    try:
        rows = con.execute('SELECT work_id,sha,body FROM intent').fetchall()
    finally:
        con.close()
    if not rows:
        return 'NO_DURABLE_RECORD'
    if len(rows) != 1:
        return 'HOLD_MULTIPLE_ROWS'
    work_id, sha, body = rows[0]
    return 'RECONSTRUCTABLE_LOCAL_ONLY' if (work_id == WORK_ID and sha == DIGEST and body == PAYLOAD) else 'HOLD_INTEGRITY'


def reconcile_external_effect(db, effect, receiver_origin_ack=None):
    # Even if a file exists and matches, no authenticated effect ACK was issued.
    if cold_read(db) != 'RECONSTRUCTABLE_LOCAL_ONLY':
        return 'HOLD_INTENT_NOT_VERIFIED'
    if receiver_origin_ack is None:
        return 'HOLD_EXTERNAL_EFFECT_RECEIPT_UNKNOWN'
    return 'HOLD_UNTRUSTED_RECEIVER_ACK'  # No external trust verifier in this fixture.


def child(mode, db, effect):
    if mode == 'before_any_ingest':
        transient_only = PAYLOAD  # An actual untransmitted message is unknowable to receiver.
        assert transient_only
        os._exit(71)
    if mode == 'during_uncommitted_transaction':
        con = open_db(db)
        con.execute('BEGIN IMMEDIATE')
        con.execute('INSERT INTO intent VALUES (?,?,?)', (WORK_ID, DIGEST, PAYLOAD))
        os._exit(72)
    if mode == 'after_commit_before_ack':
        assert admit(db, PAYLOAD) == 'COMMITTED'
        os._exit(73)
    if mode == 'external_effect_before_receipt':
        # A separate, harmless synthetic file effect. No WorkID side-effect ACK exists.
        with effect.open('xb') as f:
            f.write(PAYLOAD)
            f.flush()
            os.fsync(f.fileno())
        os._exit(74)
    raise ValueError(mode)


class SuddenDeathTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='co-abrupt-death-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'intents.sqlite3'
        self.effect = self.root / 'synthetic-effect.txt'

    def crash(self, mode, expected):
        p = subprocess.run([sys.executable, __file__, 'child', mode, str(self.db), str(self.effect)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=15)
        self.assertEqual(p.returncode, expected, p.stderr.decode('utf-8','replace'))
        self.assertEqual(p.stdout, b'')

    def test_01_death_before_any_ingest_cannot_recover_unknown_text(self):
        self.crash('before_any_ingest', 71)
        self.assertEqual(cold_read(self.db), 'NO_DURABLE_RECORD')
        self.assertEqual(admit(self.db, PAYLOAD), 'COMMITTED')
        # The new later admission is not a recovery of the killed child's unknown input.

    def test_02_death_mid_uncommitted_insert_rolls_back(self):
        self.crash('during_uncommitted_transaction', 72)
        self.assertEqual(cold_read(self.db), 'NO_DURABLE_RECORD')
        self.assertEqual(admit(self.db, PAYLOAD), 'COMMITTED')
        self.assertEqual(cold_read(self.db), 'RECONSTRUCTABLE_LOCAL_ONLY')

    def test_03_death_after_commit_before_ack_is_cold_reconstructable(self):
        self.crash('after_commit_before_ack', 73)
        self.assertEqual(cold_read(self.db), 'RECONSTRUCTABLE_LOCAL_ONLY')

    def test_04_retry_after_lost_ack_does_not_create_second_work_id(self):
        self.crash('after_commit_before_ack', 73)
        self.assertEqual(admit(self.db, PAYLOAD), 'REPLAY_SAME')
        con = sqlite3.connect(self.db)
        self.assertEqual(con.execute('SELECT COUNT(*) FROM intent').fetchone()[0], 1)
        con.close()

    def test_05_conflicting_retry_is_held(self):
        self.crash('after_commit_before_ack', 73)
        self.assertEqual(admit(self.db, b'PUBLIC_SYNTHETIC_DIFFERENT_REVISION'), 'HOLD_CONFLICT')
        self.assertEqual(cold_read(self.db), 'RECONSTRUCTABLE_LOCAL_ONLY')

    def test_06_effect_before_receipt_is_hold_not_blind_replay(self):
        self.assertEqual(admit(self.db, PAYLOAD), 'COMMITTED')
        self.crash('external_effect_before_receipt', 74)
        self.assertEqual(cold_read(self.db), 'RECONSTRUCTABLE_LOCAL_ONLY')
        self.assertTrue(self.effect.exists())
        self.assertEqual(hashlib.sha256(self.effect.read_bytes()).hexdigest(), DIGEST)
        self.assertEqual(reconcile_external_effect(self.db, self.effect), 'HOLD_EXTERNAL_EFFECT_RECEIPT_UNKNOWN')
        self.assertEqual(reconcile_external_effect(self.db, self.effect, {'verified': True}), 'HOLD_UNTRUSTED_RECEIVER_ACK')
        # The harness deliberately does NOT rerun the effect or claim receiver ACK.


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == 'child':
        child(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        unittest.main(verbosity=2)
