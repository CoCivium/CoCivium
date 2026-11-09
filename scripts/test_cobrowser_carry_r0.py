"""Synthetic CoCarry tests: high-volume index != high-volume live tabs."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from CoBrowserCarryProjectionR0 import evaluate, write_private, SCHEMA


def fixture(n=1001):
    rows = [{"session_id": f"synthetic-{i:04d}",
             "projection": "WORKING" if i < 12 else "DORMANT",
             "close_safety": "PROVEN_TRUE" if i % 10 == 0 else "UNPROVEN"}
            for i in range(n)]
    return {"schema": SCHEMA, "sessions": rows,
            "coverage": {"global_active_session_census": "UNPROVEN"}}


class CarryTests(unittest.TestCase):
    def test_1001_rows_one_proposed_focus_preserves_all(self):
        r = evaluate(fixture(), "synthetic-0003")
        self.assertEqual(r["coverage"]["observed_session_rows"], 1001)
        self.assertEqual(r["coverage"]["offscreen_session_rows_still_indexed"], 1000)
        self.assertEqual(r["focus"]["status"], "PROPOSED_NOT_REOPENED_OR_PICKED_UP")
        self.assertTrue(all(v == 0 for v in r["effects"].values()))

    def test_source_labels_do_not_authorize_tab_closing(self):
        r = evaluate(fixture(10), "synthetic-0000")
        self.assertEqual(r["effects"]["tabs_closed"], 0)
        self.assertEqual(r["focus"]["checkpoint_readproof"], "NOT_OBSERVED")

    def test_ledger_census_not_magically_complete(self):
        r = evaluate(fixture(1), "synthetic-0000")
        self.assertEqual(r["coverage"]["global_session_census"], "UNPROVEN")

    def test_duplicate_session_denied(self):
        data = fixture(2)
        data["sessions"][1]["session_id"] = "synthetic-0000"
        with self.assertRaisesRegex(ValueError, "HOLD_DUPLICATE"):
            evaluate(data, "synthetic-0000")

    def test_missing_focus_denied(self):
        with self.assertRaisesRegex(ValueError, "HOLD_FOCUS_NOT_IN_SOURCE"):
            evaluate(fixture(2), "outside")

    def test_schema_mismatch_denied(self):
        data = fixture(2)
        data["schema"] = "unknown"
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_LEDGER_SCHEMA"):
            evaluate(data, "synthetic-0000")

    def test_zero_and_excessive_inventory_denied(self):
        with self.assertRaisesRegex(ValueError, "HOLD_BOUNDED_INVENTORY_REQUIRED"):
            evaluate(fixture(0), "x")
        with self.assertRaisesRegex(ValueError, "HOLD_BOUNDED_INVENTORY_REQUIRED"):
            evaluate(fixture(10001), "x")

    def test_no_input_mutation(self):
        original = fixture(20)
        before = copy.deepcopy(original)
        evaluate(original, "synthetic-0000")
        self.assertEqual(original, before)

    def test_source_delta_changes_snapshot_digest(self):
        original = fixture(2)
        one = evaluate(original, "synthetic-0000")
        original["sessions"][1]["projection"] = "COTWILIGHT"
        two = evaluate(original, "synthetic-0000")
        self.assertNotEqual(one["source_sha256"], two["source_sha256"])

    def test_deterministic_replay(self):
        data = fixture(11)
        self.assertEqual(evaluate(data, "synthetic-0001"), evaluate(data, "synthetic-0001"))

    def test_write_private_no_clobber(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "private" / "carry.json"
            write_private(target, evaluate(fixture(2), "synthetic-0000"))
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                write_private(target, evaluate(fixture(2), "synthetic-0000"))
            self.assertEqual(target.read_bytes(), before)

    def test_cli_stdout_does_not_emit_identifiers(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "private.json"
            dst = Path(td) / "private-output.json"
            src.write_text(json.dumps(fixture(2)))
            run = subprocess.run([sys.executable, str(ROOT / "CoBrowserCarryProjectionR0.py"),
                                  "--ledger", str(src), "--focus-id", "synthetic-0001",
                                  "--private-output", str(dst)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertNotIn("synthetic-0001", run.stdout)
            self.assertEqual(json.loads(dst.read_text())["focus"]["session_id"], "synthetic-0001")


if __name__ == "__main__":
    unittest.main(verbosity=2)
