"""No-network, adversarial tests of a benchmark log contract."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "scripts" / "validate_benchmark_evo_r0.py"
SPEC = importlib.util.spec_from_file_location("bench", P)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
SAMPLE = ROOT / "benchmarks" / "costretch" / "benchmark_evo.jsonl"


def sample():
    return [json.loads(x) for x in SAMPLE.read_text().splitlines()]


def pack(rows):
    return "".join(json.dumps(x) + "\n" for x in rows)


class BenchTest(unittest.TestCase):
    def test_sample_has_failure_and_hold_and_pass(self):
        v=M.validate_jsonl(SAMPLE.read_text())
        self.assertEqual((v["records"], v["pass"], v["fail"], v["hold"]), (4, 2, 1, 1))
        self.assertEqual(v["comparable_groups"], ["synthetic-andrew-R0"])
        self.assertEqual(v["state"], "SCHEMA_PASS__OUTCOME_TRUTH_UNASSESSED")

    def test_duplicate_event_rejected(self):
        s=sample(); s[1]["event_id"]=s[0]["event_id"]
        with self.assertRaisesRegex(M.EvidenceError, "duplicate event"): M.validate_jsonl(pack(s))

    def test_pass_cannot_mask_failure(self):
        s=sample(); s[0]["checks"][0]["outcome"]="FAIL"
        with self.assertRaisesRegex(M.EvidenceError, "conceals"): M.validate_jsonl(pack(s))

    def test_synthetic_cannot_claim_real_receipt(self):
        s=sample(); s[0]["lifecycle"]["stage"]="PICKED_UP"
        with self.assertRaises(M.EvidenceError): M.validate_jsonl(pack(s))

    def test_synthetic_cannot_claim_measured_energy(self):
        s=sample(); s[0]["resource"]["energy_j"]=0
        with self.assertRaisesRegex(M.EvidenceError, "measured usage"): M.validate_jsonl(pack(s))

    def test_mixed_evidence_not_comparable(self):
        s=sample(); s[1]["evidence_class"]="DETERMINISTIC_LOCAL"
        with self.assertRaisesRegex(M.EvidenceError, "mixed evidence classes"): M.validate_jsonl(pack(s))

    def test_task_drift_not_comparable(self):
        s=sample(); s[1]["task_sha256"]="b"*64
        with self.assertRaisesRegex(M.EvidenceError, "task drift"): M.validate_jsonl(pack(s))

    def test_missing_model_provenance_rejected(self):
        s=sample(); s[0]["evidence_class"]="MODEL_RUN"
        with self.assertRaisesRegex(M.EvidenceError, "model run provenance"): M.validate_jsonl(pack(s))

    def test_historical_needs_original(self):
        s=sample(); s[2]["evidence_class"]="HISTORICAL_REPLAY"
        with self.assertRaisesRegex(M.EvidenceError, "historical source record"): M.validate_jsonl(pack(s))

    def test_receiver_needs_proof_and_origin(self):
        s=sample(); s[2]["evidence_class"]="DETERMINISTIC_LOCAL"; s[2]["lifecycle"]["stage"]="PICKED_UP"; s[2]["lifecycle"]["landing_receipt_sha256"]="a"*64;s[2]["lifecycle"]["receiver_ack_sha256"]="b"*64
        with self.assertRaisesRegex(M.EvidenceError, "receiver origin"): M.validate_jsonl(pack(s))

    def test_blank_lines_rejected(self):
        with self.assertRaisesRegex(M.EvidenceError, "blank line"): M.validate_jsonl(SAMPLE.read_text()+"\n")

    def test_stable_content_hash_and_no_mutation(self):
        raw=SAMPLE.read_text(); before=SAMPLE.read_bytes(); a=M.validate_jsonl(raw); b=M.validate_jsonl(raw)
        self.assertEqual(a,b)
        self.assertEqual(before,SAMPLE.read_bytes())

    def test_unknown_keys_fail_closed(self):
        s=sample();s[0]["magic_allowed"]="yes"
        with self.assertRaisesRegex(M.EvidenceError, "unknown keys"): M.validate_jsonl(pack(s))

    def test_invalid_time_rejected(self):
        s=sample();s[0]["created_utc"]="not-a-time"
        with self.assertRaisesRegex(M.EvidenceError, "timestamp"): M.validate_jsonl(pack(s))

    def test_no_newline_still_valid(self):
        raw=SAMPLE.read_text().rstrip("\n")
        self.assertEqual(M.validate_jsonl(raw)["records"],4)


if __name__ == "__main__": unittest.main()
