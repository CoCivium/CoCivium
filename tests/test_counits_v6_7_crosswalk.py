"""Shadow-only CoUnits proposal/receipt discipline; does not certify units or ACK."""
import json
import unittest
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REG = HERE / "ai" / "measurement" / "registry_r0_1.json"
CROSS = HERE / "ai" / "measurement" / "counits_v6_7_alias_crosswalk.json"


def load():
    return json.loads(CROSS.read_text(encoding="utf-8"))


def check_candidate(c):
    """Return fail-closed consistency result, not external proof of consensus."""
    if c.get("schema") != "CoAll.CoUnitsAliasProposalCrosswalk.R0":
        raise ValueError("SCHEMA_INVALID")
    entries = c.get("proposals")
    if not isinstance(entries, list) or len(entries) != 9:
        raise ValueError("EXACT_NINE_SOURCE_PROPOSALS_REQUIRED")
    names = [x.get("id") for x in entries]
    if len(set(names)) != 9:
        raise ValueError("DUPLICATE_ALIAS")
    if set(names) != {"CoNull", "CoTick", "CoSeed", "CoPixel", "CoBreath",
                      "CoGauge", "CoThumb", "CoOrb", "CoReceipt"}:
        raise ValueError("MISMATCHED_ALIASES")
    if any(x.get("proof_state", "").startswith("CANON") or
           "VERIFIED" == x.get("proof_state") or
           not x.get("primary_use") or not x.get("arrived_at")
           for x in entries):
        raise ValueError("UNPROVEN_CANON_OR_UNSOURCED_PROPOSAL")
    if c.get("admission_policy", {}).get("min_independent_receipts", 0) < 2:
        raise ValueError("TWO_INDEPENDENT_RECEIPTS_REQUIRED")
    if c.get("receipt", {}).get("independently_latched_count") != 0:
        raise ValueError("UNPROVEN_LATCH")
    if c.get("receipt", {}).get("proposed_count") != len(entries):
        raise ValueError("FALSE_PROPOSAL_COUNT")
    conflicts = c.get("conflicts", [])
    if len(conflicts) != 4 or len({x.get("id") for x in conflicts}) != 4:
        raise ValueError("MISSING_OR_DUPLICATE_CONFLICT")
    if c.get("receipt", {}).get("conflict_count") != len(conflicts):
        raise ValueError("FALSE_CONFLICT_COUNT")
    if any(x.get("converts_to_CoNull") != "N" for x in entries):
        raise ValueError("CONULL_NOT_A_CONVERSION_TARGET")
    if any(x.get("converts_to_CoTick") != ("Y" if x["id"] == "CoTick" else "N")
           for x in entries):
        raise ValueError("FALSE_COTICK_CONVERSION")
    clock = next(x for x in entries if x["id"] == "CoTick")
    if "Identity only" not in clock.get("conversion_note", ""):
        raise ValueError("UNBOUNDED_COTICK")
    zero = next(x for x in entries if x["id"] == "CoNull")
    if "numeric zero" not in zero.get("conversion_note", ""):
        raise ValueError("ZERO_NULL_COLLAPSE")
    if c.get("runtime_truth", {}).get("receiver_ack") != "NOT_ESTABLISHED":
        raise ValueError("INVENTED_RECEIVER_ACK")
    if c.get("runtime_truth", {}).get("wallpaper") != "STATIC_DECORATION_NOT_LIVE_GAUGE":
        raise ValueError("WALLPAPER_LIVENESS_OVERCLAIM")
    if c.get("fan_in", {}).get("additional_scheduler_created") is not False:
        raise ValueError("DUPLICATE_SCHEDULER")
    fan = c.get("fan_in", {}).get("next_utc")
    datetime.fromisoformat(fan.replace("Z", "+00:00"))
    if c["receipt"]["next_fan_in_utc"] != fan:
        raise ValueError("FAN_IN_CLOCK_MISMATCH")
    return True


class CoUnitsV67CrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load()

    def test_machine_manifest_valid(self):
        self.assertTrue(check_candidate(self.data))

    def test_primary_registry_unchanged(self):
        reg = json.loads(REG.read_text(encoding="utf-8"))
        self.assertEqual(reg["version"], "0.1.2")
        self.assertEqual(len(reg["units"]), 21)
        self.assertEqual(self.data["primary_registry"]["pr"], 365)

    def test_nine_names_not_nine_canonical_units(self):
        self.assertEqual(self.data["receipt"]["independently_latched_count"], 0)
        self.assertEqual(len(self.data["proposals"]), 9)

    def test_only_tick_self_identity(self):
        p = {x["id"]: x for x in self.data["proposals"]}
        self.assertEqual(p["CoTick"]["converts_to_CoTick"], "Y")
        self.assertIn("Identity only", p["CoTick"]["conversion_note"])
        self.assertEqual(p["CoPixel"]["converts_to_CoTick"], "N")
        self.assertEqual(p["CoBreath"]["converts_to_CoTick"], "N")

    def test_missing_is_not_zero(self):
        reg = json.loads(REG.read_text(encoding="utf-8"))
        self.assertIn("MISSING", reg["null_states"])
        self.assertIn("OBSERVED_ZERO", reg["null_states"])
        self.assertNotEqual("MISSING", "OBSERVED_ZERO")

    def test_seed_24h_not_claimed(self):
        seed = next(x for x in self.data["proposals"] if x["id"] == "CoSeed")
        self.assertTrue(seed["proof_state"].startswith("HELD_"))

    def test_bio_and_gauge_require_real_observer(self):
        p = {x["id"]: x for x in self.data["proposals"]}
        self.assertIn("CONSENT", p["CoBreath"]["proof_state"])
        self.assertIn("RECEIVER", p["CoGauge"]["proof_state"])

    def test_aliases_dont_assert_independent_ack(self):
        self.assertEqual(self.data["provenance"],
                         "ONE_USER_SUBMISSION__NO_INDEPENDENT_SESSION_ACK")
        self.assertEqual(self.data["runtime_truth"]["receiver_ack"],
                         "NOT_ESTABLISHED")

    def test_no_user_chat_screenshot_uploaded(self):
        self.assertIn("NOT copied", self.data["source"])

    def test_false_canonical_status_is_rejected(self):
        x = json.loads(json.dumps(self.data))
        x["receipt"]["independently_latched_count"] = 9
        with self.assertRaisesRegex(ValueError, "UNPROVEN_LATCH"):
            check_candidate(x)

    def test_false_convert_to_tick_rejected(self):
        x = json.loads(json.dumps(self.data))
        x["proposals"][3]["converts_to_CoTick"] = "Y"
        with self.assertRaisesRegex(ValueError, "FALSE_COTICK_CONVERSION"):
            check_candidate(x)

    def test_zero_null_conversion_rejected(self):
        x = json.loads(json.dumps(self.data))
        x["proposals"][0]["converts_to_CoNull"] = "Y"
        with self.assertRaisesRegex(ValueError, "CONULL_NOT_A_CONVERSION_TARGET"):
            check_candidate(x)

    def test_missing_second_receipt_gate_rejected(self):
        x = json.loads(json.dumps(self.data))
        x["admission_policy"]["min_independent_receipts"] = 1
        with self.assertRaisesRegex(ValueError, "TWO_INDEPENDENT_RECEIPTS_REQUIRED"):
            check_candidate(x)

    def test_unverified_ack_rejected(self):
        x = json.loads(json.dumps(self.data))
        x["runtime_truth"]["receiver_ack"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "INVENTED_RECEIVER_ACK"):
            check_candidate(x)

    def test_no_new_scheduler(self):
        self.assertIs(self.data["fan_in"]["additional_scheduler_created"], False)
        self.assertEqual(self.data["fan_in"]["next_utc"], "2026-11-10T20:12:13Z")


if __name__ == "__main__":
    unittest.main()
