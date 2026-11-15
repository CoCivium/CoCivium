"""Adversarial synthetic tests of session fan-in, custody and close-safe boundaries."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from CoSessionSuccessionGateR0 import evaluate, SCHEMA


def make_fixture():
    sources = []
    for idx in range(3):
        sources.append({
            "session_id": "fixture-session-" + str(idx),
            "source_ref": "public-synthetic-source-" + str(idx),
            "source_sha256": str(idx + 1) * 64,
            "work_id": "synthetic:evo-front",
            "privacy_class": "PUBLIC_SYNTHETIC",
            "authority_ceiling": "NO_EFFECTS",
            "contribution_ids": ["unique-" + str(idx), "shared"],
            "dissent_ids": ["contrary-" + str(idx)],
            "unresolved_obligations": ["obligation-" + str(idx)],
        })
    return {
        "schema": SCHEMA,
        "work_id": "synthetic:evo-front",
        "sources": sources,
        "successor": {
            "work_id": "synthetic:evo-front",
            "privacy_class": "PUBLIC_SYNTHETIC",
            "authority_ceiling": "NO_EFFECTS",
            "producer_id": "fixture-producer",
            "verifier_id": "fixture-verifier",
            "source_digests": {s["session_id"]: s["source_sha256"] for s in sources},
            "contribution_ids": ["shared", *["unique-" + str(i) for i in range(3)]],
            "dissent_ids": ["contrary-" + str(i) for i in range(3)],
            "accepted_obligations": ["obligation-" + str(i) for i in range(3)],
            "receiver_readproof": True,
        }
    }


class SessionSuccessionTests(unittest.TestCase):
    def setUp(self):
        self.f = make_fixture()

    def check_hold(self, reason):
        result = evaluate(self.f)
        self.assertEqual(result["state"], "HELD__SOURCE_OR_SUCCESSOR_GAP")
        self.assertIn(reason, result["reasons"])
        self.assertFalse(result["close_safe"])
        self.assertFalse(result["delete_safe"])
        self.assertTrue(all(v == 0 for v in result["effects"].values()))

    def test_three_source_candidate_preserves_distinct_provenance(self):
        r = evaluate(self.f)
        self.assertEqual(r["state"], "SHADOW_CANDIDATE__INDEPENDENT_RECEIVER_UNVERIFIED")
        self.assertEqual(r["coverage"]["observed_source_count"], 3)
        self.assertEqual(len(r["source_lineage"]), 3)
        self.assertEqual(r["distinct_contribution_count"], 4)
        self.assertEqual(len(r["preserved_dissent_ids"]), 3)
        self.assertEqual(len(r["preserved_unresolved_obligations"]), 3)
        self.assertTrue(r["one_visible_front_candidate"])
        self.assertFalse(r["close_safe"])
        self.assertEqual(r["receiver_proof"], "SYNTHETIC_SHAPE_ONLY_NOT_INDEPENDENT")

    def test_digest_mismatch_holds(self):
        self.f["successor"]["source_digests"]["fixture-session-1"] = "f" * 64
        self.check_hold("MISSING_OR_CHANGED_SOURCE_DIGEST")

    def test_missing_source_holds(self):
        del self.f["successor"]["source_digests"]["fixture-session-2"]
        self.check_hold("MISSING_OR_CHANGED_SOURCE_DIGEST")

    def test_lost_unique_contribution_holds(self):
        self.f["successor"]["contribution_ids"].remove("unique-2")
        self.check_hold("SUCCESSOR_CONTRIBUTION_IDS_LOSS")

    def test_lost_minority_dissent_holds(self):
        self.f["successor"]["dissent_ids"].remove("contrary-1")
        self.check_hold("SUCCESSOR_DISSENT_IDS_LOSS")

    def test_untransferred_obligation_holds(self):
        self.f["successor"]["accepted_obligations"].remove("obligation-0")
        self.check_hold("SUCCESSOR_ACCEPTED_OBLIGATIONS_LOSS")

    def test_independence_claim_by_same_actor_holds(self):
        self.f["successor"]["verifier_id"] = "fixture-producer"
        self.check_hold("VERIFIER_NOT_DISTINCT")

    def test_no_receiver_readproof_holds(self):
        self.f["successor"]["receiver_readproof"] = False
        self.check_hold("RECEIVER_READPROOF_NOT_DECLARED")

    def test_privacy_mismatch_holds(self):
        self.f["sources"][0]["privacy_class"] = "PRIVATE"
        self.check_hold("PRIVACY_NOT_QUALIFIED")

    def test_authority_expansion_holds(self):
        self.f["successor"]["authority_ceiling"] = "SEND_EMAIL"
        self.check_hold("SUCCESSOR_SCOPE_MISMATCH")

    def test_duplicate_session_identity_rejected(self):
        self.f["sources"][2]["session_id"] = "fixture-session-0"
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_IDENTITY"):
            evaluate(self.f)

    def test_duplicate_source_ref_rejected(self):
        self.f["sources"][2]["source_ref"] = "public-synthetic-source-0"
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_REF"):
            evaluate(self.f)

    def test_malformed_sha_rejected(self):
        self.f["sources"][0]["source_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_HASH"):
            evaluate(self.f)

    def test_mismatched_work_id_holds(self):
        self.f["sources"][2]["work_id"] = "another-work"
        self.check_hold("WORK_ID_COLLISION")

    def test_missing_producer_identity_holds(self):
        del self.f["successor"]["producer_id"]
        self.check_hold("PRODUCER_IDENTITY_INVALID")

    def test_empty_producer_identity_holds(self):
        self.f["successor"]["producer_id"] = " "
        self.check_hold("PRODUCER_IDENTITY_INVALID")

    def test_nonstring_producer_identity_holds(self):
        self.f["successor"]["producer_id"] = {"claimed": "fixture-producer"}
        self.check_hold("PRODUCER_IDENTITY_INVALID")

    def test_nonstring_verifier_identity_holds(self):
        self.f["successor"]["verifier_id"] = ["fixture-verifier"]
        self.check_hold("VERIFIER_IDENTITY_INVALID")

    def test_control_character_verifier_identity_holds(self):
        self.f["successor"]["verifier_id"] = "fixture-verifier\ninjected"
        self.check_hold("VERIFIER_IDENTITY_INVALID")

    def test_overlong_verifier_identity_holds(self):
        self.f["successor"]["verifier_id"] = "v" * 129
        self.check_hold("VERIFIER_IDENTITY_INVALID")

    def test_replay_is_deterministic(self):
        self.assertEqual(evaluate(self.f), evaluate(copy.deepcopy(self.f)))


    def test_whitespace_only_workid_is_not_a_valid_shadow(self):
        self.f["work_id"] = "  "
        for record in self.f["sources"]:
            record["work_id"] = "  "
        self.f["successor"]["work_id"] = "  "
        with self.assertRaisesRegex(ValueError, "HOLD_SCOPE"):
            evaluate(self.f)

    def test_whitespace_only_source_session_id_is_rejected(self):
        original = self.f["sources"][0]["session_id"]
        self.f["sources"][0]["session_id"] = "  "
        digests = self.f["successor"]["source_digests"]
        digests["  "] = digests.pop(original)
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_IDENTITY"):
            evaluate(self.f)

    def test_control_character_source_session_id_is_rejected(self):
        original = self.f["sources"][0]["session_id"]
        changed = "fixture-session-0" + chr(10) + "forged"
        self.f["sources"][0]["session_id"] = changed
        digests = self.f["successor"]["source_digests"]
        digests[changed] = digests.pop(original)
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_IDENTITY"):
            evaluate(self.f)

    def test_overlong_source_session_id_is_rejected(self):
        original = self.f["sources"][0]["session_id"]
        changed = "x" * 129
        self.f["sources"][0]["session_id"] = changed
        digests = self.f["successor"]["source_digests"]
        digests[changed] = digests.pop(original)
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_IDENTITY"):
            evaluate(self.f)

    def test_whitespace_only_source_ref_is_rejected(self):
        self.f["sources"][0]["source_ref"] = "  "
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_REF"):
            evaluate(self.f)

    def test_control_character_source_ref_is_rejected(self):
        self.f["sources"][0]["source_ref"] = "public-synthetic-source" + chr(10) + "forged"
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_REF"):
            evaluate(self.f)

    def test_overlong_source_ref_is_rejected(self):
        self.f["sources"][0]["source_ref"] = "x" * 1025
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_REF"):
            evaluate(self.f)

    def test_executable_url_scheme_is_not_an_evidence_source(self):
        self.f["sources"][0]["source_ref"] = "javascript:alert(1)"
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_REF"):
            evaluate(self.f)

    def test_dissent_placeholder_whitespace_is_not_preserved_dissent(self):
        self.f["sources"][0]["dissent_ids"][0] = "  "
        self.f["successor"]["dissent_ids"][0] = "  "
        with self.assertRaisesRegex(ValueError, "HOLD_DISSENT_IDS"):
            evaluate(self.f)

    def test_successor_unhashable_obligation_fails_closed(self):
        self.f["successor"]["accepted_obligations"] = [{"unqualified":"obligation"}]
        self.check_hold("SUCCESSOR_ACCEPTED_OBLIGATIONS_LOSS")

    def test_successor_nondict_unhashable_contribution_fails_closed(self):
        self.f["successor"]["contribution_ids"] = [["unique-0"]]
        self.check_hold("SUCCESSOR_CONTRIBUTION_IDS_LOSS")


if __name__ == "__main__":
    unittest.main()
