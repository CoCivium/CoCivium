"""Fail-closed R0.1.2 unit-anchor tests against the real pinned registry.

All mutants are memory-only or in isolated temporary directories. These tests
are not SI certification, calibration, or real receiver uptake. Their purpose
is to reject plausible-looking *wrong* scale factors in unexercised units.
"""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT = ROOT / "ai" / "measurement"
sys.path.insert(0, str(MEASUREMENT))
from verify_registry_r0_1 import validate_registry  # noqa: E402

SOURCE = MEASUREMENT / "registry_r0_1.json"
VERIFIER = MEASUREMENT / "verify_registry_r0_1.py"
EXPECTED_SHA256 = "14544bf12c8498c3fa664c7a11d01b8706d5d1f4704a7cc99f7040f159a033e7"


class UnitAnchorR0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.sha = hashlib.sha256(cls.raw).hexdigest()
        if cls.sha != EXPECTED_SHA256:
            raise AssertionError("HOLD_REGISTRY_SOURCE_REVIEW_REQUIRED")
        cls.reg = json.loads(cls.raw.decode("utf-8-sig"))
        if cls.reg.get("version") != "0.1.2" or len(cls.reg.get("units", [])) != 21:
            raise AssertionError("HOLD_PROFILE_SHAPE_CHANGED")

    def mutate_unit(self, uid, key, value):
        r = copy.deepcopy(self.reg)
        next(u for u in r["units"] if u["id"] == uid)[key] = value
        return r

    def test_exact_pinned_unmodified_registry_passes(self):
        validate_registry(copy.deepcopy(self.reg))

    def test_equivalent_rationals_preserve_semantics(self):
        for uid, key, value in (
            ("cm", "scale_to_anchor", "2/200"),
            ("Hz", "scale_to_anchor", "2/2"),
            ("km_per_h", "scale_to_anchor", "10/36"),
            ("Cel", "offset_to_anchor", "5463/20"),
        ):
            with self.subTest(uid=uid):
                validate_registry(self.mutate_unit(uid, key, value))

    def test_all_21_wrong_scales_are_held(self):
        for original in self.reg["units"]:
            bad = str(Fraction(original["scale_to_anchor"]) * 2)
            with self.subTest(uid=original["id"]):
                reg = self.mutate_unit(original["id"], "scale_to_anchor", bad)
                with self.assertRaisesRegex(ValueError, "UNIT_ANCHOR_SCALE_MISMATCH"):
                    validate_registry(reg)

    def test_dimensionally_equal_semantic_swap_is_held(self):
        for uid, new_kind in (("Hz", "event_rate"),
                              ("count", "failure_domain_count")):
            with self.subTest(uid=uid):
                with self.assertRaisesRegex(ValueError, "UNIT_ANCHOR_KIND_MISMATCH"):
                    validate_registry(self.mutate_unit(uid, "quantity_kind", new_kind))

    def test_missing_and_unknown_unit_id_are_held(self):
        missing = copy.deepcopy(self.reg)
        missing["units"] = [u for u in missing["units"] if u["id"] != "Hz"]
        with self.assertRaisesRegex(ValueError, "UNIT_ANCHOR_ID_SET_MISMATCH"):
            validate_registry(missing)
        unknown = copy.deepcopy(self.reg)
        next(u for u in unknown["units"] if u["id"] == "Hz")["id"] = "new_hz"
        with self.assertRaisesRegex(ValueError, "UNIT_ANCHOR_ID_SET_MISMATCH"):
            validate_registry(unknown)

    def test_future_registry_version_is_held(self):
        changed = copy.deepcopy(self.reg)
        changed["version"] = "0.1.3"
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_REGISTRY_PROFILE"):
            validate_registry(changed)

    def test_full_script_refuses_false_green_in_both_modes(self):
        verifier_bytes = VERIFIER.read_bytes()
        for uid in ("Hz", "J", "domain_count"):
            with self.subTest(uid=uid):
                reg = self.mutate_unit(uid, "scale_to_anchor", "2")
                payload = json.dumps(reg, sort_keys=True).encode("utf-8")
                for optimized in (False, True):
                    with self.subTest(optimized=optimized):
                        with tempfile.TemporaryDirectory() as tmp:
                            d = Path(tmp)
                            (d / "registry_r0_1.json").write_bytes(payload)
                            target = d / "verify_registry_r0_1.py"
                            target.write_bytes(verifier_bytes)
                            cmd = [sys.executable] + (["-O"] if optimized else []) + [str(target)]
                            result = subprocess.run(cmd, cwd=d, text=True,
                                                    capture_output=True, timeout=15, check=False)
                            self.assertNotEqual(result.returncode, 0)
                            self.assertIn("UNIT_ANCHOR_SCALE_MISMATCH", result.stderr)
                            self.assertNotIn("PASS_FOR_SCOPE", result.stdout)
                            self.assertFalse((d / "registry_test_receipt_r0.json").exists())


if __name__ == "__main__":
    unittest.main()
