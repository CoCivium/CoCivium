"""Negative controls for source-only public-front-door release HOLD gate.

All observations are fabricated, and there are NO network or site effects.
"""
from datetime import datetime, timedelta, timezone
import copy
import json
import unittest

from public_frontdoor_release_gate_r0 import evaluate, OUTPUT_SCHEMA, INPUT_SCHEMA, ROOTS

NOW = datetime(2026, 11, 20, 1, 15, 0, tzinfo=timezone.utc)
SHA = "a" * 64
COMMIT = "b" * 40


def fixture():
    return {
        "schema": INPUT_SCHEMA,
        "observed_utc": (NOW-timedelta(minutes=1)).isoformat(),
        "scope": {
            "https_roots_checked": 6,
            "approved_hostnames": [host for _, _, host in ROOTS],
            "no_follow_redirect": True,
            "no_shard_traversal": True,
            "no_raw_body_export": True,
            "no_auth_or_config_writes": True,
        },
        "records": [
            {"site": site, "variant": role, "hostname": host,
             "http_status": 200, "content_type": "TEXT_HTML",
             "html_bytes": 8000, "html_sha256": SHA,
             "classification": "HTTP_200_HTML_STRUCTURE_OBSERVED_NOT_ACCEPTED",
             "privacy_review_flags": [],
             "source_first_use_sufficient": False,
             "human_first_use_accepted": False}
            for site, role, host in ROOTS
        ],
        "release_authorized": False,
        "privacy_cleared": False,
        "human_first_use_accepted": False,
    }


class HoldGateTests(unittest.TestCase):
    def report(self, q=None, at=NOW):
        return evaluate(fixture() if q is None else q, now=at, source_commit=COMMIT)

    def test_clean_synthetic_six_root_structure_is_not_release_authority(self):
        r = self.report()
        self.assertEqual(r["schema"], OUTPUT_SCHEMA)
        self.assertEqual(r["state"], "STRUCTURAL_SIX_ROOT_CANDIDATE_NOT_RELEASED")
        self.assertEqual(len(r["root_results"]), 6)
        self.assertEqual(r["release_authorized"], False)
        self.assertEqual(r["security_owner_acceptance"], "NOT_ATTESTED")
        self.assertEqual(sum(r["effects"].values()), 0)

    def test_legacy_index_flags_trigger_separate_failed_gate(self):
        q = fixture()
        row = next(x for x in q["records"] if x["hostname"] == "www.cocivium.org")
        row["classification"] = "HOLD_PUBLIC_METADATA_OR_PRIVACY_REVIEW"
        row["privacy_review_flags"] = ["PUBLISHED_TECHNICAL_INDEX", "LOCAL_WINDOWS_PATH_ON_PUBLIC_ROOT"]
        r = self.report(q)
        self.assertEqual(r["state"], "HOLD_PUBLIC_FRONTDOOR_READINESS")
        self.assertIn("HOLD_ROOT_PRIVACY_OR_FIRST_USE_FLAGS", r["hold_reason_codes"])
        self.assertNotIn("LOCAL_WINDOWS_PATH_ON_PUBLIC_ROOT", json.dumps(r))

    def test_apex_404_does_not_get_silent_success(self):
        q = fixture()
        q["records"][0]["http_status"] = 404
        r = self.report(q)
        self.assertIn("HOLD_ROOT_NOT_HTML200", r["hold_reason_codes"])

    def test_www_redirect_not_followed_is_unqualified(self):
        q = fixture()
        q["records"][3]["http_status"] = 301
        q["records"][3]["classification"] = "HOLD_REDIRECT_NOT_FOLLOWED"
        self.assertEqual(self.report(q)["state"], "HOLD_PUBLIC_FRONTDOOR_READINESS")

    def test_missing_dns_tls_or_network_does_not_claim_site_down(self):
        q = fixture()
        q["records"][2]["http_status"] = None
        q["records"][2]["classification"] = "HOLD_NETWORK_OR_TLS_UNAVAILABLE"
        r = self.report(q)
        self.assertIn("HOLD_ROOT_NOT_HTML200", r["hold_reason_codes"])
        self.assertNotIn("HOST_OFFLINE", json.dumps(r))

    def test_duplicate_root_is_held(self):
        q = fixture()
        q["records"][1] = copy.deepcopy(q["records"][0])
        r = self.report(q)
        self.assertIn("HOLD_UNEXPECTED_OR_DUPLICATE_ROOT", r["hold_reason_codes"])
        self.assertIn("HOLD_ROOT_SET_NOT_EXACT", r["hold_reason_codes"])

    def test_missing_root_is_held(self):
        q = fixture()
        q["records"].pop()
        self.assertIn("HOLD_INCOMPLETE_ROOT_SET", self.report(q)["hold_reason_codes"])

    def test_unlisted_host_injected_is_held_without_path_echo(self):
        q = fixture()
        q["records"][0]["hostname"] = "private-secret-host.invalid"
        q["records"][0]["raw_body"] = "D:\\PRIVATE\\token.txt"
        r = self.report(q)
        self.assertIn("HOLD_UNEXPECTED_OR_DUPLICATE_ROOT", r["hold_reason_codes"])
        self.assertNotIn("private-secret", json.dumps(r))
        self.assertNotIn("token", json.dumps(r))

    def test_current_root_with_missing_hash_is_held(self):
        q = fixture()
        q["records"][0]["html_sha256"] = "NOT_A_REAL_HASH"
        self.assertIn("HOLD_ROOT_CONTENT_UNQUALIFIED", self.report(q)["hold_reason_codes"])

    def test_oversized_body_or_bad_content_type_held(self):
        q = fixture()
        q["records"][0]["html_bytes"] = 9999999
        q["records"][1]["content_type"] = "APPLICATION_JSON"
        self.assertIn("HOLD_ROOT_CONTENT_UNQUALIFIED", self.report(q)["hold_reason_codes"])

    def test_private_text_does_not_echo_or_extend_allowed_scopes(self):
        q = fixture()
        q["raw_response_body"] = "SECRET_DO_NOT_PRINT"
        q["records"][0]["raw_html"] = "PRIVATE_PASSWORD_NEVER_OUTPUT"
        r = json.dumps(self.report(q))
        self.assertNotIn("SECRET_DO_NOT_PRINT", r)
        self.assertNotIn("PRIVATE_PASSWORD", r)

    def test_expired_observation_cannot_become_fresh_after_redraw(self):
        q = fixture()
        q["observed_utc"] = (NOW-timedelta(days=1)).isoformat()
        r = self.report(q)
        self.assertIn("HOLD_OBSERVATION_STALE_OR_FUTURE", r["hold_reason_codes"])

    def test_future_observation_held(self):
        q = fixture()
        q["observed_utc"] = (NOW+timedelta(minutes=1)).isoformat()
        self.assertIn("HOLD_OBSERVATION_STALE_OR_FUTURE", self.report(q)["hold_reason_codes"])

    def test_no_shard_traversal_claim_false_held(self):
        q = fixture()
        q["scope"]["no_shard_traversal"] = False
        self.assertIn("HOLD_SOURCE_SCOPE_UNQUALIFIED", self.report(q)["hold_reason_codes"])

    def test_untrusted_source_release_permission_held(self):
        q = fixture()
        q["release_authorized"] = True
        q["privacy_cleared"] = True
        q["human_first_use_accepted"] = True
        r = self.report(q)
        self.assertIn("HOLD_SPOOFED_SOURCE_AUTHORITY", r["hold_reason_codes"])
        self.assertFalse(r["release_authorized"])

    def test_bad_root_source_schema_held(self):
        q = fixture()
        q["schema"] = "ATTACKER_OVERRIDE"
        self.assertIn("HOLD_SOURCE_SCHEMA", self.report(q)["hold_reason_codes"])

    def test_invalid_source_commit_does_not_get_pass(self):
        self.assertIn("HOLD_INVALID_SOURCE_COMMIT",
            evaluate(fixture(), now=NOW, source_commit="UNPINNED")["hold_reason_codes"])

    def test_observation_does_not_mutate_input(self):
        q = fixture()
        before = copy.deepcopy(q)
        a = self.report(q)
        b = self.report(q)
        self.assertEqual(q, before)
        self.assertEqual(a, b)
        self.assertEqual(sum(a["effects"].values()), 0)

    def test_missing_or_malformed_source_fails_closed(self):
        self.assertIn("HOLD_SOURCE_SCHEMA", self.report({})["hold_reason_codes"])
        self.assertIn("HOLD_SOURCE_SCHEMA", self.report([])["hold_reason_codes"])

    def test_reversed_or_naive_time_rejected(self):
        with self.assertRaisesRegex(ValueError, "HOLD_NOW_NOT_AWARE"):
            evaluate(fixture(), now=datetime(2026, 11, 20, 1, 15))

if __name__ == "__main__":
    unittest.main()
