import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from CoSessionReceiptIngressShadowR0 import Hold, shadow_ingress_one, shadow_ingress_batch


def pack(receipt_id="synthetic:receipt:1", effect_id="synthetic:effect:1"):
    delta = {
        "delta_id": "synthetic:delta:1", "source_session": "synthetic:worker:1",
        "created_at": "2026-11-18T10:00:00Z", "target_domains": ["synthetic"],
        "operations": [{"op": "ADD", "subject": "synthetic:object",
                        "relation": "tests", "object": "shadow",
                        "evidence_refs": ["fixture://test"]}],
        "authority_ceiling": "CANDIDATE_ONLY",
        "public_safety": "PRIVATE_ONLY", "nonclaims": ["NO_REAL_EFFECT"],
        "next_gate": "INDEPENDENT_RECEIVER",
    }
    source_bytes = json.dumps({"deltas": [delta]}, sort_keys=True).encode()
    hash_source = hashlib.sha256(source_bytes).hexdigest()
    receipt = {
        "schema": "CoSession.TypedReceiptCandidate.R0",
        "source_role": "SESSION_EFFECT_RECEIPT",
        "work_id": "CO-SESSION-RECOVERY",
        "effect_id": effect_id,
        "receipt_id": receipt_id, "issuer_id": "synthetic:issuer:1",
        "failure_domain": "synthetic:local",
        "epoch": 1, "source_revision": "synthetic:revision:1",
        "authority_ref": "synthetic:unverified:grant:1",
        "source_delta_id": delta["delta_id"], "source_record_index": 0,
        "source_sha256": hash_source, "observed_at": "2026-11-18T10:01:00Z",
        "receiver_origin_ack": "NOT_ESTABLISHED", "master_elected": False,
        "publish_authorized": False,
    }
    receipt_bytes = json.dumps(receipt, sort_keys=True).encode()
    manifest = {
        "source_role": "SESSION_EFFECT_RECEIPT",
        "source_sha256": hash_source,
        "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "work_id": receipt["work_id"], "effect_id": receipt["effect_id"],
        "issuer_id": receipt["issuer_id"], "failure_domain": receipt["failure_domain"],
        "authority_ref": receipt["authority_ref"], "epoch": receipt["epoch"],
    }
    return {"source_bytes": source_bytes, "receipt_bytes": receipt_bytes, "manifest": manifest}


def edit_receipt(item, **patch):
    v = copy.deepcopy(item)
    body = json.loads(v["receipt_bytes"].decode())
    body.update(patch)
    v["receipt_bytes"] = json.dumps(body, sort_keys=True).encode()
    v["manifest"]["receipt_sha256"] = hashlib.sha256(v["receipt_bytes"]).hexdigest()
    for key in ("work_id", "effect_id", "issuer_id", "failure_domain", "authority_ref", "epoch"):
        if key in patch:
            v["manifest"][key] = patch[key]
    return v


class ShadowIngressTests(unittest.TestCase):
    def test_one_valid_candidate_stays_held(self):
        o = shadow_ingress_one(pack())
        self.assertEqual(o["state"], "TYPED_SOURCE_BOUND_UNAUTHENTICATED_CANDIDATE")
        out = shadow_ingress_batch([pack()])
        self.assertEqual((out["qualified_receipts"], out["independent_receiver_acks"],
                          out["master_elections"], out["external_effects"]), (0, 0, 0, 0))
        self.assertEqual(out["fanout"], "HOLD")
        self.assertEqual(out["authority"], "NONE_RESEARCH_ONLY")

    def test_30_exact_replays_preserve_all_observations(self):
        item = pack()
        out = shadow_ingress_batch([item] * 30)
        self.assertEqual(len(out["observations"]), 30)
        self.assertEqual(out["distinct_receipt_identifiers_seen"], 1)
        self.assertEqual(out["unconflicted_effect_candidates"], 1)
        self.assertEqual(out["observations"][1]["state"],
                         "EXACT_RECEIPT_REPLAY_NO_NEW_CANDIDATE")
        self.assertEqual(out["qualified_receipts"], 0)

    def test_source_role_guardian_audit_rejected_even_if_wrapped(self):
        item = pack()
        item["manifest"]["source_role"] = "GUARDIAN_AUDIT"
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_ROLE_NOT_EFFECT_RECEIPT"):
            shadow_ingress_one(item)
        self.assertEqual(shadow_ingress_batch([item])["unconflicted_effect_candidates"], 0)

    def test_receipt_cannot_assign_its_own_role(self):
        item = edit_receipt(pack(), source_role="COMPILER_OUTPUT")
        with self.assertRaisesRegex(Hold, "HOLD_RECEIPT_ROLE_MISMATCH"):
            shadow_ingress_one(item)

    def test_source_and_receipt_pins_reject_tampering(self):
        item = pack()
        for key in ("source_bytes", "receipt_bytes"):
            x = copy.deepcopy(item)
            x[key] += b" "
            with self.subTest(key=key):
                with self.assertRaisesRegex(Hold, "HOLD_MANIFEST_"):
                    shadow_ingress_one(x)

    def test_manifest_issuer_mismatch_rejected(self):
        item = pack()
        item["manifest"]["issuer_id"] = "synthetic:other:issuer"
        with self.assertRaisesRegex(Hold, "HOLD_MANIFEST_IDENTITY_ISSUER_ID"):
            shadow_ingress_one(item)

    def test_forged_receiver_ack_rejected(self):
        item = edit_receipt(pack(), receiver_origin_ack="PICKED_UP")
        out = shadow_ingress_batch([item])
        self.assertEqual(out["observations"][0]["state"], "HOLD_FORGED_EFFECT_OR_ACK")
        self.assertEqual(out["independent_receiver_acks"], 0)

    def test_identical_receipt_id_different_body_quarantined(self):
        original = pack()
        altered = edit_receipt(original, observed_at="2026-11-18T10:03:00Z")
        out = shadow_ingress_batch([original, altered])
        self.assertEqual(out["conflicting_effect_groups"], 1)
        self.assertEqual(out["unconflicted_effect_candidates"], 0)
        self.assertEqual(out["observations"][1]["state"], "HOLD_RECEIPT_BODY_COLLISION")

    def test_distinct_receipt_id_same_effect_quarantined(self):
        original = pack()
        other = edit_receipt(original, receipt_id="synthetic:receipt:2")
        out = shadow_ingress_batch([original, other])
        self.assertEqual(out["distinct_receipt_identifiers_seen"], 2)
        self.assertEqual(out["conflicting_effect_groups"], 1)
        self.assertEqual(out["unconflicted_effect_candidates"], 0)
        self.assertEqual(out["observations"][1]["state"],
                         "HOLD_SAME_EFFECT_DIFFERENT_RECEIPT")
        self.assertEqual(out["qualified_receipts"], 0)

    def test_distinct_effects_preserve_lineage_no_master(self):
        original = pack()
        separate = edit_receipt(original, effect_id="synthetic:effect:2",
                                receipt_id="synthetic:receipt:2")
        out = shadow_ingress_batch([original, separate])
        self.assertEqual(out["unconflicted_effect_candidates"], 2)
        self.assertEqual(out["conflicting_effect_groups"], 0)
        self.assertEqual(out["master_elections"], 0)

    def test_malformed_metadata_does_not_enter_candidate_count(self):
        original = pack()
        bad = edit_receipt(original, source_record_index=True)
        out = shadow_ingress_batch([bad, original])
        self.assertEqual(out["observations"][0]["state"], "HOLD_SOURCE_RECORD_INDEX")
        self.assertEqual(out["unconflicted_effect_candidates"], 1)

    def test_type_and_batch_bound_hold(self):
        with self.assertRaisesRegex(Hold, "HOLD_BATCH_BOUND_1_TO_30"):
            shadow_ingress_batch([])
        with self.assertRaisesRegex(Hold, "HOLD_BATCH_BOUND_1_TO_30"):
            shadow_ingress_batch([pack()] * 31)
        with self.assertRaisesRegex(Hold, "HOLD_ENVELOPE_TYPES"):
            shadow_ingress_one({"source_bytes": "not bytes", "receipt_bytes": b"", "manifest": {}})


if __name__ == "__main__":
    unittest.main()
