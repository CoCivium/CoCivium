"""Adversarial synthetic session-source fan-in, no provider access."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from CoAllSessionFanInR0 import reconcile_sources


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


if __name__=="__main__":
    unittest.main()
