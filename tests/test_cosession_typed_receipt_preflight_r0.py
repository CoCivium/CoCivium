import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from CoSessionRelationalFanIn import validate_delta
from CoSessionTypedReceiptPreflightR0 import Hold, batch_preflight, digest, preflight


def fixture():
    delta = {
        "delta_id": "fixture:typed:1", "source_session": "synthetic:session:1",
        "created_at": "2026-11-18T10:00:00Z", "target_domains": ["synthetic"],
        "operations": [{"op": "ADD", "subject": "synthetic:question",
                        "relation": "tests", "object": "review",
                        "evidence_refs": ["fixture://a"]}],
        "authority_ceiling": "CANDIDATE_ONLY", "public_safety": "PUBLIC_SAFE",
        "nonclaims": ["NOT_PRODUCTION"], "next_gate": "INDEPENDENT_RECEIVER",
    }
    source = json.dumps({"deltas": [delta]}, sort_keys=True).encode()
    receipt = {
        "schema": "CoSession.TypedReceiptCandidate.R0",
        "work_id": "CO-SESSION-RECOVERY", "effect_id": "synthetic:effect:1",
        "receipt_id": "synthetic:receipt:1", "issuer_id": "synthetic:issuer:1",
        "failure_domain": "synthetic:local", "epoch": 1,
        "source_revision": "fixture:revision:1", "authority_ref": "fixture:authority:unknown",
        "source_delta_id": "fixture:typed:1", "source_record_index": 0,
        "source_sha256": digest(source), "observed_at": "2026-11-18T10:01:00Z",
        "receiver_origin_ack": "NOT_ESTABLISHED", "master_elected": False,
        "publish_authorized": False,
    }
    return delta, source, receipt


def call(source, receipt):
    raw = json.dumps(receipt, sort_keys=True).encode()
    return preflight(source, raw, digest(raw))


class TypedReceiptGateTests(unittest.TestCase):
    def test_pinned_compiler_unchanged(self):
        data = (Path(__file__).resolve().parents[1] / "scripts/CoSessionRelationalFanIn.py").read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        self.assertEqual(blob, "690cba4811eb8f4cf8cb6f4b1d4b52d8b6776002")

    def test_valid_candidate_stays_held(self):
        _, source, receipt = fixture()
        result = call(source, receipt)
        self.assertEqual(result["typed_preflight"], "PASS_SOURCE_BOUND_CANDIDATE_ONLY")
        self.assertEqual(result["admission"], "HOLD_INDEPENDENT_AUTHORITY_AND_RECEIVER")
        self.assertFalse(result["master_elected"])
        self.assertFalse(result["receiver_origin_ack"])
        self.assertEqual(result["external_effects"], 0)

    def test_two_original_malformed_compiler_acceptances_now_hold(self):
        delta, _, receipt = fixture()
        for patch, reason in [
            ({"source_session": None, "created_at": None, "authority_ceiling": None,
              "nonclaims": None, "next_gate": None}, "HOLD_SOURCE_SESSION"),
            ({"delta_id": 0, "source_session": {"invented": 1}, "created_at": -100,
              "target_domains": [True], "authority_ceiling": {"delete": True},
              "nonclaims": 7, "next_gate": 0}, "HOLD_DELTA_ID")
        ]:
            with self.subTest(reason=reason):
                d = copy.deepcopy(delta); d.update(patch)
                self.assertIsNone(validate_delta(d), "must reproduce R0 weakness")
                s = json.dumps({"deltas": [d]}, sort_keys=True).encode()
                r = dict(receipt, source_sha256=digest(s))
                with self.assertRaisesRegex(Hold, reason):
                    call(s, r)

    def test_exact_receipt_pin_required(self):
        _, source, receipt = fixture()
        b = json.dumps(receipt, sort_keys=True).encode()
        with self.assertRaisesRegex(Hold, "HOLD_RECEIPT_BYTES_CHANGED"):
            preflight(source, b, "0" * 64)

    def test_source_tamper_rejected(self):
        _, source, receipt = fixture()
        tampered = source.replace(b"review", b"other")
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_BYTES_CHANGED"):
            call(tampered, receipt)

    def test_source_delta_binding_rejected(self):
        _, source, receipt = fixture()
        receipt["source_delta_id"] = "synthetic:different"
        with self.assertRaisesRegex(Hold, "HOLD_DELTA_SOURCE_BINDING"):
            call(source, receipt)

    def test_forged_ack_master_and_publish_rejected(self):
        _, source, receipt = fixture()
        for change in ({"receiver_origin_ack": "PICKED_UP"}, {"master_elected": True},
                       {"publish_authorized": True}):
            with self.subTest(change=change):
                with self.assertRaisesRegex(Hold, "HOLD_FORGED_EFFECT_OR_ACK"):
                    call(source, dict(receipt, **change))

    def test_wrong_type_epoch_index_and_domain_rejected(self):
        delta, source, receipt = fixture()
        for key, value, error in [("epoch", True, "HOLD_EPOCH"),
                                  ("source_record_index", True, "HOLD_SOURCE_RECORD_INDEX")]:
            with self.subTest(key=key):
                with self.assertRaisesRegex(Hold, error):
                    call(source, dict(receipt, **{key: value}))
        delta["target_domains"] = [True]
        s = json.dumps({"deltas": [delta]}).encode()
        with self.assertRaisesRegex(Hold, "HOLD_DOMAIN_TYPES"):
            call(s, dict(receipt, source_sha256=digest(s)))

    def test_invalid_time_rejected(self):
        delta, _, receipt = fixture()
        delta["created_at"] = "2026-11-18T10:00:00"
        s = json.dumps({"deltas": [delta]}).encode()
        with self.assertRaisesRegex(Hold, "HOLD_TIME_NOT_UTC"):
            call(s, dict(receipt, source_sha256=digest(s)))

    def test_exact_replay_dedupes_but_retains_observations(self):
        _, source, receipt = fixture()
        raw = json.dumps(receipt, sort_keys=True).encode()
        out = batch_preflight([(source, raw, digest(raw))] * 30)
        self.assertEqual(len(out["source_observations"]), 30)
        self.assertEqual(out["typed_candidates_unconflicted"], 1)
        self.assertEqual(out["source_observations"][1]["state"], "EXACT_REPLAY_NO_NEW_RECEIPT")
        self.assertEqual(out["qualified_receipts"], 0)
        self.assertEqual(out["elected_masters"], 0)
        self.assertEqual(out["fanout"], "HOLD")

    def test_same_identity_different_body_quarantined(self):
        _, source, receipt = fixture()
        altered = dict(receipt, observed_at="2026-11-18T10:02:00Z")
        rows = []
        for r in (receipt, altered):
            b = json.dumps(r, sort_keys=True).encode()
            rows.append((source, b, digest(b)))
        out = batch_preflight(rows)
        self.assertEqual(out["collision_groups"], 1)
        self.assertEqual(out["typed_candidates_unconflicted"], 0)
        self.assertEqual(out["source_observations"][-1]["state"], "HOLD_RECEIPT_IDENTITY_COLLISION")

    def test_distinct_receipts_same_effect_hold_without_erasing_lineage(self):
        _, source, receipt = fixture()
        receipt2 = dict(receipt, receipt_id="synthetic:receipt:2")
        rows = []
        for r in (receipt, receipt2):
            raw = json.dumps(r, sort_keys=True).encode()
            rows.append((source, raw, digest(raw)))
        out = batch_preflight(rows)
        self.assertEqual(len(out["source_observations"]), 2)
        self.assertEqual(out["effect_collision_groups"], 1)
        self.assertEqual(out["typed_candidates_unconflicted"], 0)
        self.assertTrue(all(
            r["state"] == "HOLD_UNADJUDICATED_EFFECT_MULTI_RECEIPT"
            for r in out["source_observations"]))
        self.assertEqual(out["qualified_receipts"], 0)
        self.assertEqual(out["receiver_origin_acks"], 0)
        self.assertEqual(out["elected_masters"], 0)
        self.assertEqual(out["external_effects"], 0)

    def test_different_effect_ids_remain_two_review_candidates(self):
        _, source, receipt = fixture()
        receipt2 = dict(receipt, receipt_id="synthetic:receipt:2",
                        effect_id="synthetic:effect:2")
        rows = []
        for r in (receipt, receipt2):
            raw = json.dumps(r, sort_keys=True).encode()
            rows.append((source, raw, digest(raw)))
        out = batch_preflight(rows)
        self.assertEqual(out["effect_collision_groups"], 0)
        self.assertEqual(out["typed_candidates_unconflicted"], 2)
        self.assertEqual(out["elected_masters"], 0)
        self.assertEqual(out["fanout"], "HOLD")


if __name__ == "__main__":
    unittest.main()
