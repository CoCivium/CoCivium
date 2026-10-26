#!/usr/bin/env python3
"""No-network tests. No real ET, provider, credential or G_d claim."""
import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import source_probe as app


class DummyResponse:
    def __init__(self, status=200, body=b"public data"):
        self.status, self.body = status, body
        self.read_calls = 0

    def read(self, n):
        self.read_calls += 1
        return self.body[:n]


class DummyConn:
    def __init__(self, host, timeout=None, context=None, *, status=200, body=b"public"):
        self.host, self.timeout, self.context = host, timeout, context
        self.response = DummyResponse(status, body)
        self.path, self.headers = None, None
        self.closed = False

    def request(self, method, path, headers):
        if method != "GET":
            raise AssertionError("not a read-only GET")
        self.path, self.headers = path, headers

    def getresponse(self):
        return self.response

    def close(self):
        self.closed = True


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.manifest = app.load_registry()
        self.source = self.manifest["sources"][0]

    def changed(self, edit):
        m = deepcopy(self.manifest)
        edit(m)
        return m

    def rejects(self, edit, expression=None):
        with self.assertRaisesRegex(ValueError, expression or "."):
            app.validate(self.changed(edit))

    def test_01_registry_and_family_count(self):
        c = app.validate(self.manifest)
        self.assertEqual(c["source_count"], 4)
        self.assertEqual(c["family_counts"]["ET_EMPIRICAL"], 2)
        self.assertEqual(c["family_counts"]["GD_PHILOSOPHICAL"], 1)

    def test_02_exact_four_limit(self):
        self.rejects(lambda m: m["sources"].pop(), "REQUIRE_FOUR")

    def test_03_duplication_rejected(self):
        self.rejects(lambda m: m["sources"].__setitem__(1, deepcopy(m["sources"][0])), "UNQUALIFIED")

    def test_04_no_extra_catalogue_source(self):
        self.rejects(lambda m: m["sources"].append(deepcopy(m["sources"][0])), "REQUIRE_FOUR")

    def test_05_schema_enforced(self):
        self.rejects(lambda m: m.__setitem__("schema", "Untrusted"), "INVALID_SCHEMA")

    def test_06_no_automatic_network(self):
        self.rejects(lambda m: m.__setitem__("external_actions_default", True), "DEFAULT_EXTERNAL")

    def test_07_probe_budget_fixed(self):
        self.rejects(lambda m: m.__setitem__("max_sources_per_probe", 400), "PROBE_LIMIT")

    def test_08_https_endpoint_fixed(self):
        self.rejects(lambda m: m["sources"][0].__setitem__("probe_url", "http://seti.berkeley.edu/opendata"), "UNAPPROVED")

    def test_09_no_private_network_endpoint(self):
        self.rejects(lambda m: m["sources"][0].__setitem__("probe_url", "https://127.0.0.1/admin"), "UNAPPROVED")

    def test_10_no_url_with_credentials(self):
        self.rejects(lambda m: m["sources"][0].__setitem__("probe_url", "https://x@y.example/"), "UNAPPROVED")

    def test_11_no_family_confusion(self):
        self.rejects(lambda m: m["sources"][3].__setitem__("class", "ASTRONOMICAL_DATA_CATALOG"), "EPISTEMIC_FAMILY")

    def test_12_no_et_detection_overclaim(self):
        self.rejects(lambda m: m["sources"][0].__setitem__("detection_state", "CONFIRMED_ET"), "UNSUPPORTED_DETECTION")

    def test_13_no_philosophical_data_promotion(self):
        self.rejects(lambda m: m["sources"][3].__setitem__("epistemic", "MEASURED_DIVINITY"), "PHILOSOPHY_CANNOT")

    def test_14_no_unreviewed_republication(self):
        self.rejects(lambda m: m["sources"][1].__setitem__("license_status", "CLEAR_FOR_ALL"), "RIGHTS_NOT")

    def test_15_no_secret_fields(self):
        self.rejects(lambda m: m["sources"][0].__setitem__("api_key", "inert-fixture"), "NO_SECRET_FIELDS")

    def test_16_all_sources_public_read_only(self):
        self.rejects(lambda m: m["sources"][0].__setitem__("access", "PRIVATE_LOGGED_IN"), "NOT_PUBLIC")

    def test_17_stable_structural_hash(self):
        a = app.structural_fingerprint(self.manifest)
        b = app.structural_fingerprint(json.loads(json.dumps(self.manifest, sort_keys=True)))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)

    def test_18_change_changes_fingerprint(self):
        m = self.changed(lambda m: m["sources"][0].__setitem__("update_cadence", "UNKNOWN"))
        self.assertNotEqual(app.structural_fingerprint(m), app.structural_fingerprint(self.manifest))

    def test_19_probe_bounded_data(self):
        c = DummyConn("", status=200, body=b"a"*100000)
        r = app.probe_one(self.source, connection_factory=lambda *a, **k: c)
        self.assertEqual(r["status"], "PASS_BOUNDED_HTTP_READ")
        self.assertEqual(r["bytes_read"], app.LIMIT_BYTES)
        self.assertEqual(c.timeout, None)  # injected fake; real constructor receives fixed timeout
        self.assertEqual(c.response.read_calls, 1)
        self.assertTrue(c.closed)
        self.assertEqual(r["receiver_ack"], None)
        self.assertEqual(r["signal_detection"], "NOT_ASSESSED")

    def test_20_no_redirect_follow(self):
        c = DummyConn("", status=301)
        r = app.probe_one(self.source, connection_factory=lambda *a, **k: c)
        self.assertEqual(r["status"], "HELD_REDIRECT_NOT_FOLLOWED")
        self.assertEqual(c.response.read_calls, 0)
        self.assertTrue(c.closed)

    def test_21_http_403_not_detection_failure(self):
        c = DummyConn("", status=403)
        r = app.probe_one(self.source, connection_factory=lambda *a, **k: c)
        self.assertEqual(r["status"], "HELD_HTTP_RESPONSE")
        self.assertEqual(r["signal_detection"], "NOT_ASSESSED")

    def test_22_network_error_not_fabricated_success(self):
        def broken(*args, **kwargs):
            raise OSError("synthetic DNS outage")
        r = app.probe_one(self.source, connection_factory=broken)
        self.assertEqual(r["status"], "HELD_NETWORK")
        self.assertEqual(r["bytes_read"], 0)
        self.assertIsNone(r["http_status"])

    def test_23_empty_response_held(self):
        c = DummyConn("", status=200, body=b"")
        r = app.probe_one(self.source, connection_factory=lambda *a, **k: c)
        self.assertEqual(r["status"], "HELD_EMPTY_RESPONSE")

    def test_24_default_cli_is_offline(self):
        script = Path(__file__).with_name("source_probe.py")
        # No public network is requested because --probe is not supplied.
        q = subprocess.run([sys.executable, str(script), "--validate"], capture_output=True, text=True, check=True, timeout=6)
        o = json.loads(q.stdout)
        self.assertEqual(o["mode"], "OFFLINE_VALIDATE")
        self.assertEqual(o["external_messages"], 0)
        self.assertEqual(o["provider_sessions_created"], 0)
        self.assertTrue(all(s["status"] == "NOT_RUN_NETWORK" for s in o["sources"]))

    def test_25_no_fabricated_detector(self):
        self.assertEqual(self.manifest["state"].split("__")[2], "NO_DETECTIONS")
        self.assertEqual(len(self.manifest["next_receiver_qualifications"]), 5)


if __name__ == "__main__":
    unittest.main()
