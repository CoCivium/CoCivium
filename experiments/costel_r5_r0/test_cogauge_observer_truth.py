"""CoSpeedo observer honesty controls for unattended WorkID continuity.

Pure synthetic contract. A fresh local sample or animated Orb never grants
independent receiver ACK, useful work, or service survivorship.
"""
import unittest
from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    sample_age_seconds: float | None = None
    source_status: str = "UNKNOWN"
    work_id: str = ""
    source_hash: str = ""
    producer_receipt_hash: str = ""
    receiver_identity: str = ""
    receiver_readback_hash: str = ""
    receiver_fresh: bool = False
    work_effect_verified: bool = False
    tested_runtime_seconds: float = 0.0


def projection(e: Evidence, freshness_ttl=30.0):
    if e.sample_age_seconds is None or e.sample_age_seconds < 0:
        observer = "UNKNOWN"
    elif e.sample_age_seconds > freshness_ttl:
        observer = "STALE"
    else:
        observer = "FRESH_LOCAL_SAMPLE"
    if e.source_status in ("STANDBY", "RELEASE_PASS", "STOPPED"):
        source = "NOT_ACTIVE"
    elif e.source_status == "RUNNING":
        source = "REPORTED_RUNNING_NOT_VERIFIED"
    else:
        source = "UNKNOWN"

    valid_readback = bool(
        e.work_id and e.source_hash and e.producer_receipt_hash
        and e.receiver_identity and e.receiver_readback_hash
        and e.receiver_readback_hash == e.producer_receipt_hash
        and e.receiver_fresh and e.work_effect_verified
    )
    return {
        "observer": observer,
        "source": source,
        "effect": "INDEPENDENTLY_RECEIPTED" if valid_readback else "UNVERIFIED",
        "runtime_24h": "OBSERVED_24H" if e.tested_runtime_seconds >= 86400 and valid_readback
                       else "NOT_PROVEN",
        "display_green_effect": valid_readback,
    }


class HonestProjectionTests(unittest.TestCase):
    def test_fresh_local_sample_is_not_effect(self):
        o = projection(Evidence(sample_age_seconds=0))
        self.assertEqual(o["observer"], "FRESH_LOCAL_SAMPLE")
        self.assertEqual(o["effect"], "UNVERIFIED")
        self.assertFalse(o["display_green_effect"])

    def test_old_sample_not_fresh(self):
        self.assertEqual(projection(Evidence(sample_age_seconds=301))["observer"], "STALE")

    def test_unknown_sample_not_running(self):
        self.assertEqual(projection(Evidence())["observer"], "UNKNOWN")

    def test_standby_false_green_regression(self):
        for status in ("STANDBY", "RELEASE_PASS", "STOPPED"):
            o = projection(Evidence(sample_age_seconds=1, source_status=status))
            self.assertEqual(o["source"], "NOT_ACTIVE")
            self.assertFalse(o["display_green_effect"])

    def test_running_process_does_not_prove_effect(self):
        o = projection(Evidence(sample_age_seconds=1, source_status="RUNNING"))
        self.assertEqual(o["source"], "REPORTED_RUNNING_NOT_VERIFIED")
        self.assertEqual(o["effect"], "UNVERIFIED")

    def test_receiver_hash_mismatch_rejected(self):
        e = Evidence(work_id="w1", source_hash="source1", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="other",
                     receiver_fresh=True, work_effect_verified=True)
        self.assertEqual(projection(e)["effect"], "UNVERIFIED")

    def test_producer_self_claim_not_ack(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     work_effect_verified=True)
        self.assertEqual(projection(e)["effect"], "UNVERIFIED")

    def test_valid_synthetic_readback_requires_identity(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True)
        self.assertEqual(projection(e)["effect"], "INDEPENDENTLY_RECEIPTED")

    def test_24h_not_inferred_from_receiver(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True,
                     tested_runtime_seconds=60)
        self.assertEqual(projection(e)["runtime_24h"], "NOT_PROVEN")

    def test_24h_requires_observed_duration_and_readback(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True,
                     tested_runtime_seconds=86400)
        self.assertEqual(projection(e)["runtime_24h"], "OBSERVED_24H")

    def test_time_without_readback_never_proves_seed(self):
        e = Evidence(sample_age_seconds=1, tested_runtime_seconds=999999)
        self.assertEqual(projection(e)["runtime_24h"], "NOT_PROVEN")


if __name__ == "__main__":
    unittest.main()
