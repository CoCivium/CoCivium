#!/usr/bin/env python3
"""Offline deterministic tests for the read-only CoInverse receiver."""
import datetime as dt
import json
import pathlib
import tempfile
import unittest
from unittest import mock
import coinverse_receiver as receiver

NOW = dt.datetime(2026, 11, 10, 2, 0, tzinfo=dt.timezone.utc)

class ReceiverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.payloads = {}
        for path in receiver.SEEDS:
            dest = self.root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            raw = json.dumps({"test": path}, sort_keys=True).encode("utf-8")
            dest.write_bytes(raw)
            self.payloads[path] = raw
        self.pins = {p: receiver.blob_sha(raw) for p, raw in self.payloads.items()}
        self.patch = mock.patch.dict(receiver.SEEDS, self.pins, clear=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_valid_source_receipt(self):
        r = receiver.receive(root=self.root, now=NOW)
        self.assertTrue(r["source_verified"])
        self.assertEqual(r["status"], "SOURCE_VERIFIED")
        self.assertFalse(r["independent_handoff_verified"])
        self.assertFalse(r["survived_24h_verified"])

    def test_tampered_source_fails_closed(self):
        path = next(iter(receiver.SEEDS))
        (self.root / path).write_bytes(b'{"test":"tampered"}')
        r = receiver.receive(root=self.root, now=NOW)
        self.assertFalse(r["source_verified"])
        self.assertEqual(r["status"], "HOLD")

    def test_missing_source_fails_closed(self):
        (self.root / next(iter(receiver.SEEDS))).unlink()
        self.assertFalse(receiver.receive(root=self.root, now=NOW)["source_verified"])

    def test_invalid_json_fails_closed(self):
        path = next(iter(receiver.SEEDS))
        (self.root / path).write_bytes(b"not json")
        receiver.SEEDS[path] = receiver.blob_sha(b"not json")
        self.assertFalse(receiver.receive(root=self.root, now=NOW)["source_verified"])

    def test_simulated_24h_comparison(self):
        old_time = NOW - dt.timedelta(hours=25)
        prior = receiver.receive(root=self.root, now=old_time)
        path = self.root / "prior.json"
        path.write_text(json.dumps(prior), encoding="utf-8")
        new = receiver.receive(root=self.root, prior=path, now=NOW)
        self.assertTrue(new["survived_24h_verified"])
        self.assertTrue(new["prior_comparison"]["same_source_digests"])

    def test_under_24h_does_not_qualify(self):
        prior = receiver.receive(root=self.root, now=NOW - dt.timedelta(hours=23))
        path = self.root / "prior.json"
        path.write_text(json.dumps(prior), encoding="utf-8")
        self.assertFalse(receiver.receive(root=self.root, prior=path, now=NOW)["survived_24h_verified"])

    def test_prior_digest_mismatch_does_not_qualify(self):
        prior = receiver.receive(root=self.root, now=NOW - dt.timedelta(hours=25))
        prior["checks"][0]["sha256"] = "0" * 64
        path = self.root / "prior.json"
        path.write_text(json.dumps(prior), encoding="utf-8")
        self.assertFalse(receiver.receive(root=self.root, prior=path, now=NOW)["survived_24h_verified"])

    def test_corrupt_prior_does_not_qualify(self):
        path = self.root / "prior.json"
        path.write_text("{", encoding="utf-8")
        r = receiver.receive(root=self.root, prior=path, now=NOW)
        self.assertFalse(r["survived_24h_verified"])
        self.assertIn("error", r["prior_comparison"])

if __name__ == "__main__":
    unittest.main()
