"""CoFront public CoTalkItOut exact-object receiver tests, with no remote access."""
import copy
import json
from pathlib import Path
import unittest

from cofront_public_consumer import (
    verify_autonomy_publication, AUTONOMY_RECEIPT, AUTONOMY_STEM, AUTONOMY_SUFFIXES
)


class CoTalkItOutReadback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.receipt = json.loads((cls.repo / AUTONOMY_RECEIPT).read_text("utf-8"))
        cls.baseline = {AUTONOMY_RECEIPT: (cls.repo / AUTONOMY_RECEIPT).read_bytes()}
        for suffix in AUTONOMY_SUFFIXES:
            path = "docs/CoLocal/" + AUTONOMY_STEM + suffix
            cls.baseline[path] = (cls.repo / path).read_bytes()

    def fixture(self):
        return copy.deepcopy(self.baseline)

    def check(self, data):
        return verify_autonomy_publication(lambda path: data[path])

    def mutate_receipt(self, edit):
        data = self.fixture()
        obj = copy.deepcopy(self.receipt)
        edit(obj)
        data[AUTONOMY_RECEIPT] = json.dumps(obj).encode()
        return data

    def test_four_real_public_objects_match(self):
        r = self.check(self.fixture())
        self.assertTrue(r["passed"])
        self.assertEqual(len(r["public_files"]), 4)
        self.assertTrue(all(f["matched"] for f in r["public_files"]))

    def test_work_id_exact(self):
        r = self.check(self.fixture())
        self.assertEqual(r["work_id"], "CoLocal2601109_CoTalkItOut_Headless_Screenless_R1")

    def test_xlsx_exact_bytes(self):
        r = self.check(self.fixture())
        v = next(x for x in r["public_files"] if x["path"].endswith(".xlsx"))
        self.assertEqual(v["bytes"], 88769)
        self.assertEqual(v["expected_sha256"], "4ca848b814292d0a0ff1c8bfc2d1193ad0f660f629133794fba3be046a0c10dc")

    def test_one_changed_byte_blocks_pickup(self):
        data = self.fixture()
        name = "docs/CoLocal/" + AUTONOMY_STEM + ".xlsx"
        data[name] = data[name][:-1] + bytes([data[name][-1] ^ 1])
        self.assertFalse(self.check(data)["passed"])

    def test_status_inflation_fails(self):
        data = self.mutate_receipt(lambda x: x.update(state="COEX"))
        with self.assertRaisesRegex(ValueError, "HOLD_AUTONOMY_RECEIPT"):
            self.check(data)

    def test_wrong_work_id_fails(self):
        data = self.mutate_receipt(lambda x: x.update(work_id="different"))
        with self.assertRaisesRegex(ValueError, "HOLD_AUTONOMY_RECEIPT"):
            self.check(data)

    def test_private_content_disallowed(self):
        data = self.mutate_receipt(lambda x: x["publication_preflight"].update(public_safe_only=False))
        with self.assertRaisesRegex(ValueError, "HOLD_AUTONOMY_RECEIPT"):
            self.check(data)

    def test_forged_receiver_ack_disallowed(self):
        data = self.mutate_receipt(lambda x: x["lifecycle"].update(independently_operated_receiver_pickup="PASS"))
        with self.assertRaisesRegex(ValueError, "HOLD_AUTONOMY_RECEIPT"):
            self.check(data)

    def test_private_path_substitution_fails(self):
        data = self.mutate_receipt(lambda x: x["public_files"][0].update(path="private/secret.txt"))
        with self.assertRaisesRegex(ValueError, "HOLD_AUTONOMY_SOURCE_PATH_SET"):
            self.check(data)

    def test_boolean_byte_size_fails(self):
        data = self.mutate_receipt(lambda x: x["public_files"][1].update(bytes=True))
        with self.assertRaisesRegex(ValueError, "HOLD_AUTONOMY_FILE_DESCRIPTOR"):
            self.check(data)

    def test_missing_asset_fails_closed(self):
        data = self.fixture()
        del data["docs/CoLocal/" + AUTONOMY_STEM + ".csv"]
        with self.assertRaises(KeyError):
            self.check(data)

    def test_no_full_asset_bytes_or_private_paths_in_receipt(self):
        result = json.dumps(self.check(self.fixture()))
        self.assertNotIn("D:\\CoCivium", result)
        self.assertNotIn("C:\\Users\\Owner", result)
        self.assertNotIn("PRIVATE_CHAT_EXPORT", result)
        self.assertIn("PUBLIC_SOURCE_IDENTITY_READBACK_ONLY", result)

    def test_no_runtime_or_live_session_promotion(self):
        r = self.check(self.fixture())
        for key in ("native_x2_runtime", "independent_costead_receiver_ack",
                    "interactive_sessions_notified", "coex_or_canon",
                    "semantic_workbook_reviewed", "private_data_accessed"):
            self.assertIs(r[key], False, key)

    def test_historical_preflight_is_not_current_status(self):
        r = self.check(self.fixture())
        self.assertTrue(r["passed"])
        self.assertFalse(r["independent_costead_receiver_ack"])


if __name__ == "__main__":
    unittest.main()
