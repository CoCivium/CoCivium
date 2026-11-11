"""CoSpeedo observer honesty controls for unattended WorkID continuity.

Pure synthetic contract. Matching caller-provided strings are unverified
receipt claims, not independent receiver-origin evidence or useful results.
"""
import math
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


def _valid_seconds(value, *, positive=False):
    """Accept only finite numeric durations; fail closed on corrupt feed ages."""
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value) and (value > 0 if positive else value >= 0)
    except OverflowError:
        return False


def projection(e: Evidence, freshness_ttl=30.0):
    if not _valid_seconds(e.sample_age_seconds) or not _valid_seconds(
        freshness_ttl, positive=True
    ):
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

    claimed_match = bool(
        e.work_id and e.source_hash and e.producer_receipt_hash
        and e.receiver_identity and e.receiver_readback_hash
        and e.receiver_readback_hash == e.producer_receipt_hash
        and e.receiver_fresh and e.work_effect_verified
    )
    # This pure model has no independently authenticated receiver channel.
    # A caller can forge every field above. Never promote those assertions
    # into a green indicator, independent ACK or 24h runtime proof.
    return {
        "observer": observer,
        "source": source,
        "effect": "CLAIMED_RECEIPT_MATCH__INDEPENDENCE_UNVERIFIED" if claimed_match else "UNVERIFIED",
        "claimed_hash_match": claimed_match,
        "receiver_independence": "NOT_PROVEN",
        "runtime_24h": "NOT_PROVEN",
        "display_green_effect": False,
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

    def test_nonfinite_and_malformed_sample_age_fail_closed(self):
        # NaN previously skipped both < 0 and > ttl comparisons,
        # incorrectly promoting an invalid sample age to FRESH_LOCAL_SAMPLE.
        values = (
            ("nan", float("nan")),
            ("positive_infinity", float("inf")),
            ("negative_infinity", float("-inf")),
            ("negative_age", -1.0),
            ("bool_not_seconds", True),
            ("string_not_seconds", "7"),
            ("huge_integer", 10**1000),
        )
        for label, age in values:
            with self.subTest(value=label):
                result = projection(Evidence(sample_age_seconds=age, source_status="RUNNING"))
                self.assertEqual(result["observer"], "UNKNOWN")
                self.assertFalse(result["display_green_effect"])

    def test_invalid_freshness_policy_fails_closed(self):
        values = (
            ("nan", float("nan")),
            ("positive_infinity", float("inf")),
            ("negative_infinity", float("-inf")),
            ("negative", -1.0),
            ("zero", 0),
            ("boolean", True),
            ("string", "30"),
            ("huge_integer", 10**1000),
        )
        for label, ttl in values:
            with self.subTest(policy=label):
                result = projection(Evidence(sample_age_seconds=3), freshness_ttl=ttl)
                self.assertEqual(result["observer"], "UNKNOWN")
                self.assertFalse(result["display_green_effect"])

    def test_valid_freshness_threshold_boundary(self):
        self.assertEqual(projection(Evidence(sample_age_seconds=30), freshness_ttl=30)["observer"],
                         "FRESH_LOCAL_SAMPLE")
        self.assertEqual(projection(Evidence(sample_age_seconds=30.01), freshness_ttl=30)["observer"],
                         "STALE")
        self.assertEqual(projection(Evidence(sample_age_seconds=0), freshness_ttl=30)["observer"],
                         "FRESH_LOCAL_SAMPLE")

    def test_invalid_age_cannot_become_ack_even_with_claimed_receiver(self):
        spoof = Evidence(
            sample_age_seconds=float("nan"), source_status="RUNNING",
            work_id="w1", source_hash="s", producer_receipt_hash="p",
            receiver_identity="claimed_receiver", receiver_readback_hash="p",
            receiver_fresh=True, work_effect_verified=True
        )
        result = projection(spoof)
        self.assertEqual(result["observer"], "UNKNOWN")
        self.assertEqual(result["receiver_independence"], "NOT_PROVEN")
        self.assertFalse(result["display_green_effect"])

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

    def test_matching_synthetic_strings_are_only_claims(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True)
        o = projection(e)
        self.assertEqual(o["effect"], "CLAIMED_RECEIPT_MATCH__INDEPENDENCE_UNVERIFIED")
        self.assertEqual(o["receiver_independence"], "NOT_PROVEN")
        self.assertTrue(o["claimed_hash_match"])
        self.assertFalse(o["display_green_effect"])

    def test_24h_not_inferred_from_receiver(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True,
                     tested_runtime_seconds=60)
        self.assertEqual(projection(e)["runtime_24h"], "NOT_PROVEN")

    def test_24h_claimed_duration_does_not_prove_runtime(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True,
                     tested_runtime_seconds=86400)
        self.assertEqual(projection(e)["runtime_24h"], "NOT_PROVEN")

    def test_time_without_readback_never_proves_seed(self):
        e = Evidence(sample_age_seconds=1, tested_runtime_seconds=999999)
        self.assertEqual(projection(e)["runtime_24h"], "NOT_PROVEN")

    def test_forged_receiver_identity_cannot_claim_independence(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="independent_receiver_claimed_by_writer",
                     receiver_readback_hash="p", receiver_fresh=True,
                     work_effect_verified=True)
        self.assertEqual(projection(e)["receiver_independence"], "NOT_PROVEN")
        self.assertFalse(projection(e)["display_green_effect"])

    def test_forged_hundred_day_uptime_cannot_claim_survival(self):
        e = Evidence(work_id="w1", source_hash="s", producer_receipt_hash="p",
                     receiver_identity="r2", receiver_readback_hash="p",
                     receiver_fresh=True, work_effect_verified=True,
                     tested_runtime_seconds=100 * 86400)
        self.assertEqual(projection(e)["runtime_24h"], "NOT_PROVEN")

    def test_stopped_source_with_claimed_match_never_green(self):
        e = Evidence(sample_age_seconds=1, source_status="STOPPED", work_id="w1",
                     source_hash="s", producer_receipt_hash="p", receiver_identity="r2",
                     receiver_readback_hash="p", receiver_fresh=True, work_effect_verified=True)
        o = projection(e)
        self.assertEqual(o["source"], "NOT_ACTIVE")
        self.assertFalse(o["display_green_effect"])

    def test_stale_observer_with_claimed_match_never_green(self):
        e = Evidence(sample_age_seconds=3000, source_status="RUNNING", work_id="w1",
                     source_hash="s", producer_receipt_hash="p", receiver_identity="r2",
                     receiver_readback_hash="p", receiver_fresh=True, work_effect_verified=True)
        o = projection(e)
        self.assertEqual(o["observer"], "STALE")
        self.assertFalse(o["display_green_effect"])

    def test_verified_flag_without_external_attestation_is_not_green(self):
        e = Evidence(sample_age_seconds=0, source_status="RUNNING", work_id="w1",
                     source_hash="s", producer_receipt_hash="p", receiver_identity="r2",
                     receiver_readback_hash="p", receiver_fresh=True, work_effect_verified=True)
        self.assertFalse(projection(e)["display_green_effect"])


if __name__ == "__main__":
    unittest.main()
