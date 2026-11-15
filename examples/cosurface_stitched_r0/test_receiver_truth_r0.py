"""Bounded CoGoAll receipt/claim negative tests; no live provider calls."""
import hashlib
import unittest

from receiver_truth_r0 import classify_text_claims, verify_public_file


class CoGoAllReceiverTruthTests(unittest.TestCase):
    def setUp(self):
        self.payload = b"public candidate: source only\n"
        self.sha = hashlib.sha256(self.payload).hexdigest()
        self.repo = "CoCivium/CoCivium"
        self.commit = "a" * 40
        self.path = "examples/cosurface_stitched_r0/index.html"

    def check(self, fetch=None, expected=None, **kw):
        return verify_public_file(self.repo, self.commit, self.path,
                                  expected or self.sha, fetch=fetch, **kw)

    def test_empty_claim_header_has_no_authority(self):
        out = classify_text_claims({})
        self.assertEqual(out["claimed_consent"], "SCOPED_AUTHORITY_NOT_ESTABLISHED")
        self.assertEqual(out["claimed_landing"], "TEXT_ONLY_NO_SOURCE_PROOF")

    def test_appealing_formatted_header_is_not_authentication(self):
        out = classify_text_claims({
            "FROM": "SyntheticExternalChat",
            "Auth": "SyntheticConsentFlag ON",
            "Custody": "ClaimsSeedWithoutReadback",
            "Halo": "N", "Rep": "1.0",
        })
        self.assertEqual(out["claimed_origin"], "SELF_ASSERTION_NOT_AUTHENTICATED")
        self.assertEqual(out["claimed_custody"], "NO_EXACT_CUSTODY_READBACK")
        self.assertEqual(out["claimed_aliveness"], "NO_MEASURED_CAUSAL_EFFECT")

    def test_pasted_prompts_are_not_independent_receiver_ack(self):
        out = classify_text_claims({"coprompt_landed": True, "sent_to_five_sessions": True})
        self.assertEqual(out["claimed_session_fanout"], "NO_INDEPENDENT_RECEIVER_PICKUP")
        self.assertEqual(out["human_relay"], "REQUIRES_HUMAN_IF_PASTE_TO_OTHER_CHAT")

    def test_claims_must_be_structured(self):
        with self.assertRaisesRegex(ValueError, "CLAIMS_MUST_BE_OBJECT"):
            classify_text_claims("everything approved")

    def test_synthetic_hash_match_is_not_external_landing(self):
        out = self.check(fetch=lambda _: self.payload)
        self.assertEqual(out["source_readback"], "SYNTHETIC_BYTES_MATCH_NOT_EXTERNAL_READBACK")
        for k in ("receiver_pickup", "sender_identity", "consent_authority",
                  "seed_custody", "x2_runtime", "real_24h_survival"):
            self.assertEqual(out[k], "UNPROVEN")

    def test_source_digest_mismatch_holds(self):
        out = self.check(fetch=lambda _: b"changed", expected="0" * 64)
        self.assertEqual(out["source_readback"], "HOLD_SOURCE_SHA_MISMATCH")

    def test_network_failure_holds(self):
        def failing(url):
            raise OSError("transport fail")
        out = self.check(fetch=failing)
        self.assertEqual(out["source_readback"], "HOLD_READ_FAILURE")

    def test_redirect_or_invalid_bytes_holds(self):
        out = self.check(fetch=lambda _: "text, not bytes")
        self.assertEqual(out["source_readback"], "HOLD_READ_FAILURE")

    def test_oversized_source_holds(self):
        out = self.check(fetch=lambda _: b"x" * (1_048_576 + 1))
        self.assertEqual(out["source_readback"], "HOLD_READ_FAILURE")

    def test_repo_allowlist_blocks_arbitrary_host(self):
        with self.assertRaisesRegex(ValueError, "INVALID_REPOSITORY"):
            verify_public_file("EvilOrg/CoCivium", self.commit, self.path, self.sha, fetch=lambda _: self.payload)

    def test_revision_must_be_exact_hash(self):
        with self.assertRaisesRegex(ValueError, "INVALID_PINNED_COMMIT"):
            verify_public_file(self.repo, "main", self.path, self.sha, fetch=lambda _: self.payload)

    def test_path_traversal_blocked(self):
        for path in ("../private", "/etc/passwd", "a//b", "a/./b", "a/../b", "a\\b"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "INVALID_PATH"):
                    verify_public_file(self.repo, self.commit, path, self.sha, fetch=lambda _: self.payload)

    def test_expected_digest_must_be_exact(self):
        with self.assertRaisesRegex(ValueError, "INVALID_EXPECTED_SHA256"):
            self.check(fetch=lambda _: self.payload, expected="not-the-sha")

    def test_exact_url_is_pinned_and_not_redirected(self):
        seen = []
        def mock_fetch(url):
            seen.append(url)
            return self.payload
        self.check(fetch=mock_fetch)
        self.assertEqual(seen, ["https://raw.githubusercontent.com/CoCivium/CoCivium/"
                                + self.commit + "/" + self.path])

    def test_even_verified_source_does_not_claim_live_receipt(self):
        out = self.check(fetch=lambda _: self.payload)
        self.assertEqual(out["receiver_pickup"], "UNPROVEN")
        self.assertEqual(out["x2_runtime"], "UNPROVEN")


if __name__ == "__main__":
    unittest.main()
