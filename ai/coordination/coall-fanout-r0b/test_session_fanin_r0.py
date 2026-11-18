"""Adversarial synthetic session-source fan-in, no provider access."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from CoAllSessionFanInR0 import reconcile_sources, reconcile_receipt_blobs


def row(session, work, sha="a"*64, *, state="OBSERVED", delta=True):
    return dict(session_id=session, work_id=work, source_sha256=sha,
                scope="PUBLIC_SAFE_SYNTHETIC", state=state, material_delta=delta)


class SessionFanInR0(unittest.TestCase):
    def test_same_work_two_sessions_deduplicated_without_fake_ack(self):
        result = reconcile_sources([row("s:a", "w:orb"), row("s:b", "w:orb")],
                                   scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(result["observed_unique_workids"], 1)
        self.assertEqual(result["work"][0]["duplicate_session_sources_collapsed"], 1)
        self.assertEqual(result["work"][0]["disposition"], "CANDIDATE_FOR_AUTHORIZED_RECEIVER")
        self.assertEqual(result["external_receivers_contacted"], 0)
        self.assertEqual(result["receiver_ack"], "NOT_ESTABLISHED")

    def test_missing_source_fails_closed(self):
        result = reconcile_sources([row("s:a", "w:orb", None)],
                                   scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(result["work"][0]["disposition"], "HOLD_MISSING_SOURCE")
        self.assertIsNone(result["work"][0]["exact_source_hash"])

    def test_disagreeing_sessions_do_not_silently_merge(self):
        result = reconcile_sources([row("s:a", "w:orb"), row("s:b", "w:orb", "b"*64)],
                                   scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(result["work"][0]["disposition"], "HOLD_CONFLICTING_SOURCE_REVISIONS")
        self.assertIsNone(result["work"][0]["exact_source_hash"])

    def test_identical_titles_are_not_work_identity(self):
        result = reconcile_sources([row("s:a", "w:orb"), row("s:b", "w:mail")],
                                   scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(result["observed_unique_workids"], 2)

    def test_quiet_and_held_remain_addressable(self):
        result = reconcile_sources([row("s:a", "w:quiet", delta=False),
                                    row("s:b", "w:held", state="HELD")],
                                   scanned_scope="BOUNDED_SYNTHETIC")
        by={x["work_id"]: x for x in result["work"]}
        self.assertEqual(by["w:quiet"]["disposition"], "QUIET_NO_MATERIAL_DELTA")
        self.assertEqual(by["w:held"]["disposition"], "HOLD_SOURCE_HELD")

    def test_coverage_never_global_even_if_unscanned_zero(self):
        result = reconcile_sources([row("s:a", "w:orb")], scanned_scope="BOUNDED_SYNTHETIC",
                                   unscanned_sources=0)
        self.assertEqual(result["global_session_completeness"], "UNKNOWN")

    def test_unknown_unscanned_stays_null(self):
        result = reconcile_sources([], scanned_scope="BOUNDED_SYNTHETIC")
        self.assertIsNone(result["unscanned_source_count"])
        self.assertEqual(result["observed_unique_workids"], 0)

    def test_private_source_metadata_never_echoes_payload(self):
        private = row("s:a", "w:orb")
        private["scope"] = "PRIVATE_METADATA_ONLY"
        result = reconcile_sources([private], scanned_scope="BOUNDED_AUTHORIZED_METADATA")
        self.assertNotIn("session_id", str(result))
        self.assertNotIn("s:a", str(result))
        self.assertNotIn("PRIVATE_METADATA_ONLY", str(result))

    def test_duplicate_session_id_rejected_and_inputs_unchanged(self):
        inputs=[row("s:a", "w:orb"), row("s:a", "w:mail")]
        original=copy.deepcopy(inputs)
        with self.assertRaisesRegex(ValueError, "DUPLICATE_SESSION_ID"):
            reconcile_sources(inputs, scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(inputs, original)

    def test_unexpected_private_payload_rejected(self):
        inputs=[dict(row("s:a", "w:orb"), email_body="private text")]
        with self.assertRaisesRegex(ValueError, "INVALID_SOURCE_SHAPE"):
            reconcile_sources(inputs, scanned_scope="BOUNDED_SYNTHETIC")

    def test_invalid_budget_and_confused_completeness_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_sources([row("s:a", "w:orb")]*1001, scanned_scope="BOUNDED_SYNTHETIC")
        with self.assertRaises(ValueError):
            reconcile_sources([], scanned_scope="ALL")
        with self.assertRaises(ValueError):
            reconcile_sources([], scanned_scope="BOUNDED_SYNTHETIC", unscanned_sources=False)

    def test_order_independent_semantic_result(self):
        inputs=[row("s:b", "w:orb"), row("s:a", "w:orb"), row("s:c", "w:mail",delta=False)]
        a=reconcile_sources(inputs, scanned_scope="BOUNDED_SYNTHETIC")
        b=reconcile_sources(list(reversed(inputs)), scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(a,b)


def source_receipt(i, *, receipt_id=None, sender=None, work="w:seed",
                   source_hash="a"*64, state="OBSERVED_SOURCE_ONLY",
                   receiver_ack=False, master_authorized=False,
                   effect_count=0):
    obj = {
        "schema": "CoAll.FanIn.SourceOnlyReceipt.R0",
        "receipt_id": receipt_id or f"r:{i:02d}",
        "source_claim_id": sender or f"s:{i:02d}",
        "work_id": work,
        "source_sha256": source_hash,
        "privacy": "SYNTHETIC_PUBLIC_SAFE",
        "state": state,
        "effect_count": effect_count,
        "receiver_ack": receiver_ack,
        "master_authorized": master_authorized,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ReceiptFanIn30R0(unittest.TestCase):
    def test_30_receipts_form_one_candidate_but_zero_masters_or_effects(self):
        result = reconcile_receipt_blobs([source_receipt(i) for i in range(30)])
        self.assertEqual(result["state"], "ONE_REVIEW_CANDIDATE_NO_MASTER_COMMIT")
        self.assertEqual(result["unique_receipt_bytes"], 30)
        self.assertEqual(result["self_asserted_source_claims"], 30)
        self.assertEqual(result["unique_workids"], 1)
        self.assertEqual(result["source_revision_hint_variants"], 1)
        self.assertEqual(result["review_candidates"], 1)
        self.assertEqual(result["committed_masters"], 0)
        self.assertEqual(result["ledger_writes"], 0)
        self.assertEqual(result["effect_count"], 0)
        self.assertEqual(result["receiver_ack"], "NOT_ESTABLISHED")
        self.assertEqual(result["fanout"], "HOLD")
        self.assertEqual(result["three_independent_witnesses"], "HOLD_DIM")
        self.assertEqual(result["sender_authentication"], "NOT_ESTABLISHED")
        self.assertFalse(result["source_bytes_independently_read"])

    def test_thirty_session_metadata_records_are_not_receipts(self):
        metadata = [row(f"s:{i:02d}", "w:seed") for i in range(30)]
        previous = reconcile_sources(metadata, scanned_scope="BOUNDED_SYNTHETIC")
        self.assertEqual(previous["observed_session_count"], 30)
        self.assertEqual(previous["observed_unique_workids"], 1)
        self.assertEqual(previous["receiver_ack"], "NOT_ESTABLISHED")
        self.assertEqual(reconcile_receipt_blobs([])["state"], "HOLD")
        self.assertEqual(reconcile_receipt_blobs([])["committed_masters"], 0)

    def test_duplicate_receipt_bytes_never_count_as_thirty(self):
        same = source_receipt(0)
        result = reconcile_receipt_blobs([same] * 30)
        self.assertEqual(result["unique_receipt_bytes"], 1)
        self.assertEqual(result["duplicate_receipt_inputs_collapsed"], 29)
        self.assertIn("HOLD_NOT_30_UNIQUE_RECEIPT_BYTES", result["holds"])
        self.assertEqual(result["review_candidates"], 0)

    def test_duplicate_bytes_with_thirty_unique_still_do_not_add_votes(self):
        blobs = [source_receipt(i) for i in range(30)]
        a = reconcile_receipt_blobs(blobs)
        b = reconcile_receipt_blobs(list(reversed(blobs)) + blobs[:1])
        self.assertEqual(a["receipt_sha256s"], b["receipt_sha256s"])
        self.assertEqual(a["review_candidates"], b["review_candidates"])
        self.assertEqual(b["duplicate_receipt_inputs_collapsed"], 1)

    def test_missing_thirtieth_is_held(self):
        r = reconcile_receipt_blobs([source_receipt(i) for i in range(29)])
        self.assertEqual(r["state"], "HOLD")
        self.assertIn("HOLD_NOT_30_UNIQUE_RECEIPT_BYTES", r["holds"])
        self.assertEqual(r["committed_masters"], 0)

    def test_duplicate_receipt_id_with_different_bytes_holds(self):
        blobs = [source_receipt(i) for i in range(30)]
        blobs[29] = source_receipt(29, receipt_id="r:00")
        r = reconcile_receipt_blobs(blobs)
        self.assertIn("HOLD_RECEIPT_ID_REUSED_WITH_DIFFERENT_BYTES", r["holds"])
        self.assertEqual(r["review_candidates"], 0)

    def test_one_source_claim_cannot_mint_two_different_receipts(self):
        blobs = [source_receipt(i) for i in range(30)]
        blobs[29] = source_receipt(29, sender="s:00")
        r = reconcile_receipt_blobs(blobs)
        self.assertIn("HOLD_SOURCE_CLAIM_HAS_MULTIPLE_RECEIPTS", r["holds"])
        self.assertEqual(r["review_candidates"], 0)

    def test_forked_source_revision_not_coerced_into_master(self):
        blobs = [source_receipt(i) for i in range(30)]
        blobs[29] = source_receipt(29, source_hash="b"*64)
        r = reconcile_receipt_blobs(blobs)
        self.assertIn("HOLD_SOURCE_REVISION_FORK_OR_MISSING", r["holds"])
        self.assertEqual(r["committed_masters"], 0)

    def test_forked_work_id_preserved_as_hold(self):
        blobs = [source_receipt(i) for i in range(30)]
        blobs[29] = source_receipt(29, work="w:other")
        r = reconcile_receipt_blobs(blobs)
        self.assertIn("HOLD_WORKID_FORK_OR_MISSING", r["holds"])
        self.assertIsNone(r["work_id_hint"])

    def test_no_effectful_or_inflated_authority_receipts(self):
        for changes in [
            {"receiver_ack": True}, {"master_authorized": True},
            {"effect_count": 1}, {"effect_count": False},
            {"state": "COMMITTED"},
        ]:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, "HOLD_UNQUALIFIED"):
                    reconcile_receipt_blobs([source_receipt(0, **changes)])

    def test_private_extra_field_and_spoofed_privacy_are_held(self):
        good = json.loads(source_receipt(0))
        good["private_transcript"] = "must not enter public CI"
        with self.assertRaisesRegex(ValueError, "HOLD_RECEIPT_SCHEMA_FIELDS"):
            reconcile_receipt_blobs([json.dumps(good).encode()])
        del good["private_transcript"]
        good["privacy"] = "PRIVATE_METADATA_ONLY"
        with self.assertRaisesRegex(ValueError, "HOLD_UNQUALIFIED"):
            reconcile_receipt_blobs([json.dumps(good).encode()])

    def test_duplicate_json_keys_and_invalid_source_hash_fail_closed(self):
        raw = source_receipt(0)
        duplicate = raw[:-1] + b',"work_id":"w:other"}'
        with self.assertRaisesRegex(ValueError, "HOLD_DUPLICATE_JSON_KEY"):
            reconcile_receipt_blobs([duplicate])
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_HASH_HINT"):
            reconcile_receipt_blobs([source_receipt(0, source_hash="a"*63)])

    def test_input_budget_and_receipt_type_are_strict(self):
        with self.assertRaisesRegex(ValueError, "HOLD_RECEIPT_SCAN_BUDGET"):
            reconcile_receipt_blobs([source_receipt(0)] * 1001)
        with self.assertRaisesRegex(ValueError, "HOLD_RECEIPT_BYTES_OR_SIZE"):
            reconcile_receipt_blobs(["not raw bytes"])
        with self.assertRaisesRegex(ValueError, "HOLD_RECEIPT_BYTES_OR_SIZE"):
            reconcile_receipt_blobs([b"x" * 4097])


if __name__=="__main__":
    unittest.main()
