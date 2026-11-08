"""CoMeasure R0.1.2 exact-branch verifier adversaries, in normal and -O Python.

All mutations happen only in temporary CI directories, not X2 or the registry.
Source owner: elected CoMeasure draft PR #365, private OptimizeGuard/InputGuard
R0/R1 donors, and prior X2 proof of optimization-dependent false PASS.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "ai" / "measurement" / "verify_registry_r0_1.py"
REGISTRY = ROOT / "ai" / "measurement" / "registry_r0_1.json"
EXPECTED_SOURCE_SHA256 = "14544bf12c8498c3fa664c7a11d01b8706d5d1f4704a7cc99f7040f159a033e7"


class OptimizeFailClosedR0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier_bytes = VERIFIER.read_bytes()
        cls.registry_bytes = REGISTRY.read_bytes()
        cls.registry = json.loads(cls.registry_bytes.decode("utf-8-sig"))
        cls.sha = hashlib.sha256(cls.registry_bytes).hexdigest()
        if cls.sha != EXPECTED_SOURCE_SHA256:
            raise AssertionError("HOLD_SOURCE_REGISTRY_CHANGED__REFRESH_PIN")
        if cls.registry["version"] != "0.1.2":
            raise AssertionError("HOLD_UNEXPECTED_VERSION")
        if len(cls.registry["units"]) != 21 or len(cls.registry["metric_families"]) != 7:
            raise AssertionError("HOLD_PROFILE_MISMATCH")
        if b"    assert " in cls.verifier_bytes:
            raise AssertionError("HOLD_CORRECTNESS_ASSERT_REMAINS")

    def run_once(self, folder, raw, optimized=False):
        path = Path(folder)
        (path / "verify_registry_r0_1.py").write_bytes(self.verifier_bytes)
        (path / "registry_r0_1.json").write_bytes(raw)
        cmd = [sys.executable] + (["-O"] if optimized else []) + [str(path / "verify_registry_r0_1.py")]
        result = subprocess.run(cmd, cwd=path, timeout=12, capture_output=True, text=True, check=False)
        receipt = path / "registry_test_receipt_r0.json"
        return result, (receipt.read_bytes() if receipt.exists() else None)

    def assert_held(self, raw, expected_fragment=None):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                with tempfile.TemporaryDirectory() as tmp:
                    p, receipt = self.run_once(tmp, raw, optimized=optimized)
                    self.assertNotEqual(p.returncode, 0, p.stdout)
                    self.assertNotIn("PASS_FOR_SCOPE", p.stdout)
                    self.assertIsNone(receipt)
                    if expected_fragment:
                        self.assertIn(expected_fragment, p.stderr)

    def mutate(self, updater):
        reg = copy.deepcopy(self.registry)
        updater(reg)
        return json.dumps(reg, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def test_original_exact_registry_passes_in_both_modes_idempotently(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                with tempfile.TemporaryDirectory() as tmp:
                    first, receipt_1 = self.run_once(tmp, self.registry_bytes, optimized)
                    self.assertEqual(first.returncode, 0, first.stderr)
                    self.assertIn("PASS_FOR_SCOPE", first.stdout)
                    self.assertIsNotNone(receipt_1)
                    result = json.loads(receipt_1)
                    self.assertEqual(result["registry_sha256"], EXPECTED_SOURCE_SHA256)
                    self.assertEqual(result["total_asserted_cases"], 35)
                    self.assertTrue(all(v == 0 for v in result["effects"].values()))
                    second, receipt_2 = self.run_once(tmp, self.registry_bytes, optimized)
                    self.assertEqual(second.returncode, 0, second.stderr)
                    self.assertEqual(receipt_2, receipt_1)

    def test_corrupt_centimetre_scale_refused_under_O(self):
        def broken(r):
            next(u for u in r["units"] if u["id"] == "cm")["scale_to_anchor"] = "1/10"
        self.assert_held(self.mutate(broken), "centimetre")

    def test_unused_zero_and_negative_scales_refused(self):
        for value in ("0", "-1"):
            with self.subTest(value=value):
                def broken(r):
                    next(u for u in r["units"] if u["id"] == "domain_count")["scale_to_anchor"] = value
                self.assert_held(self.mutate(broken), "NONPOSITIVE_SCALE")

    def test_duplicate_unit_id_refused_before_dict_loss(self):
        def broken(r):
            dup = copy.deepcopy(r["units"][0])
            dup["dimensions"] = [0, 0, 0, 0, 0, 0, 0]
            r["units"].append(dup)
        self.assert_held(self.mutate(broken), "DUPLICATE_UNIT_ID")

    def test_wrong_hz_dimensions_refused(self):
        def broken(r):
            next(u for u in r["units"] if u["id"] == "Hz")["dimensions"] = [1,0,0,0,0,0,0]
        self.assert_held(self.mutate(broken), "WRONG_KIND_DIMENSION")

    def test_wrong_metric_unit_or_kind_refused(self):
        for which in ("unit", "kind"):
            with self.subTest(which=which):
                def broken(r):
                    r["metric_families"][0]["unit_id" if which=="unit" else "quantity_kind"] = (
                        "unknown_unit" if which == "unit" else "event_count"
                    )
                self.assert_held(self.mutate(broken),
                                 "UNBOUND_UNIT_ID" if which == "unit" else "METRIC_KIND_MISMATCH")

    def test_wrong_dimension_width_and_types_refused(self):
        for dimensions in ([1,0,0], [1,0,0,0,0,0,True]):
            with self.subTest(dimensions=dimensions):
                def broken(r):
                    r["units"][0]["dimensions"] = dimensions
                self.assert_held(self.mutate(broken), "DIMENSION_VECTOR")

    def test_temperature_offset_boundary_preserved(self):
        for uid, value in (("Cel", "0"), ("K", "27315/100"),
                           ("delta_Cel", "27315/100")):
            with self.subTest(unit=uid):
                def broken(r):
                    next(u for u in r["units"] if u["id"] == uid)["offset_to_anchor"] = value
                self.assert_held(self.mutate(broken), "AFFINE_OFFSET_NOT_PERMITTED")

    def test_invalid_unreferenced_rational_refused(self):
        for scale in ("nan", "1/0", "very_wrong"):
            with self.subTest(scale=scale):
                def broken(r):
                    next(u for u in r["units"] if u["id"] == "domain_count")["scale_to_anchor"] = scale
                self.assert_held(self.mutate(broken))

    def test_duplicate_top_level_and_nested_json_keys_refused(self):
        raw = json.dumps(self.registry, indent=2)
        self.assertIn('"version": "0.1.2",', raw)
        self.assertIn('"id": "cm",', raw)
        inputs = [
            raw.replace('"version": "0.1.2",',
                        '"version": "FORGED", "version": "0.1.2",', 1),
            raw.replace('"id": "cm",', '"id": "FORGED", "id": "cm",', 1),
        ]
        for data in inputs:
            with self.subTest(which=data[:38]):
                self.assert_held(data.encode("utf-8"), "HOLD_DUPLICATE_JSON_KEY")

    def test_nonfinite_json_constants_refused(self):
        raw = json.dumps(self.registry, indent=2)
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                bad = raw.replace('"version": "0.1.2",',
                                  '"version": "0.1.2", "extras": '+value+',', 1)
                self.assert_held(bad.encode("utf-8"), "HOLD_NONFINITE_JSON_CONSTANT")

    def test_existing_receipt_conflict_fails_without_clobber(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                with tempfile.TemporaryDirectory() as tmp:
                    first, previous = self.run_once(tmp, self.registry_bytes, optimized)
                    self.assertEqual(first.returncode, 0, first.stderr)
                    self.assertIsNotNone(previous)
                    changed = self.mutate(lambda r: r.update({"unused_comment": "harmless but different bytes"}))
                    second, current = self.run_once(tmp, changed, optimized)
                    self.assertNotEqual(second.returncode, 0)
                    self.assertIn("HOLD_EXISTING_RECEIPT_CONFLICT", second.stderr)
                    self.assertEqual(previous, current)
                    self.assertNotIn("PASS_FOR_SCOPE", second.stdout)

    def test_version_and_kind_profile_are_explicit(self):
        for case in ("version", "kind"):
            with self.subTest(case=case):
                def broken(r):
                    if case == "version":
                        r["version"] = "0.1.3"
                    else:
                        r["units"][0]["quantity_kind"] = "UNBOUND_FUTURE_KIND"
                self.assert_held(self.mutate(broken),
                                 "UNSUPPORTED_REGISTRY_PROFILE" if case == "version"
                                 else "UNKNOWN_QUANTITY_KIND")


if __name__ == "__main__":
    unittest.main()
