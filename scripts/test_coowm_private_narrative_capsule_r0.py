"""No-network private narrative capsule R0 tests. No mouse and no real receiver."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

src=Path(__file__).with_name("coowm_private_narrative_capsule_r0.py")
spec=importlib.util.spec_from_file_location("coowm_private",src)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)
        self.source=self.folder/"selected.txt"
        self.root=self.folder/"private"
        self.source.write_text("CoWingsRegrow+ / deliberate narrative selection",encoding="utf8")
    def tearDown(self):
        self.temp.cleanup()
    def test_capture_readback_local_only(self):
        r=m.capture(self.source,self.root)
        self.assertEqual(r["state"],"VERIFIED_LOCAL_ONLY")
        self.assertEqual(m.verify(self.root/r["sha256"],r["sha256"]),"VERIFIED_LOCAL_ONLY")
    def test_repeated_capture_is_one_capsule(self):
        a=m.capture(self.source,self.root)
        b=m.capture(self.source,self.root)
        self.assertEqual(b["state"],"DUPLICATE_VERIFIED_LOCAL_ONLY")
        self.assertEqual(len(list(self.root.iterdir())),1)
        self.assertEqual(a["capsule_id"],b["capsule_id"])
    def test_restart_recovery(self):
        a=m.capture(self.source,self.root)
        self.assertEqual(m.verify(self.root/a["sha256"],a["sha256"]),"VERIFIED_LOCAL_ONLY")
    def test_corrupted_text_holds(self):
        a=m.capture(self.source,self.root)
        (self.root/a["sha256"]/"text.txt").write_text("tampered")
        self.assertEqual(m.capture(self.source,self.root)["state"],"HELD_DIGEST_OR_RECEIPT_MISMATCH")
    def test_corrupted_receipt_holds(self):
        a=m.capture(self.source,self.root)
        (self.root/a["sha256"]/"receipt.json").write_text("{}")
        self.assertEqual(m.capture(self.source,self.root)["state"],"HELD_DIGEST_OR_RECEIPT_MISMATCH")
    def test_incomplete_capsule_holds_not_overwrite(self):
        data=self.source.read_bytes()
        sha=m.digest(data)
        (self.root/sha).mkdir(parents=True)
        self.assertEqual(m.capture(self.source,self.root)["state"],"HELD_INCOMPLETE_CAPSULE")
    def test_no_source_path_and_no_false_receiver(self):
        a=m.capture(self.source,self.root)
        rec=json.loads((self.root/a["sha256"]/"receipt.json").read_text())
        self.assertFalse(rec["original_source_path_stored"])
        self.assertFalse(rec["receiver_ack"])
        self.assertFalse(rec["cross_session_sync"])
        self.assertFalse(rec["published"])
        self.assertNotIn(str(self.source),json.dumps(rec))
    def test_binary_rejected(self):
        self.source.write_bytes(b"hello\x00world")
        with self.assertRaises(m.Held):m.capture(self.source,self.root)
    def test_empty_rejected(self):
        self.source.write_text("   ")
        with self.assertRaises(m.Held):m.capture(self.source,self.root)
    def test_size_bound(self):
        self.source.write_bytes(b"a"*(m.MAX_BYTES+1))
        with self.assertRaises(m.Held):m.capture(self.source,self.root)
    def test_source_symlink_rejected(self):
        other=self.folder/"original.txt"
        other.write_text("sample")
        self.source.unlink()
        self.source.symlink_to(other)
        with self.assertRaises(m.Held):m.capture(self.source,self.root)
    def test_private_root_symlink_rejected(self):
        actual=self.folder/"actual-private"
        actual.mkdir()
        self.root.symlink_to(actual,target_is_directory=True)
        with self.assertRaises(m.Held) as error:
            m.capture(self.source,self.root)
        self.assertEqual(str(error.exception),"HELD_OUTPUT_SYMLINK")
        self.assertEqual(list(actual.iterdir()),[])
    def test_distinct_content_distinct_capsule(self):
        a=m.capture(self.source,self.root)
        self.source.write_text("Different passage")
        b=m.capture(self.source,self.root)
        self.assertNotEqual(a["sha256"],b["sha256"])
        self.assertEqual(len(list(self.root.iterdir())),2)
    def test_explicit_file_and_root_required(self):
        self.assertIn('--source",required=True',src.read_text())
        self.assertIn('--private-root",required=True',src.read_text())
    def test_no_imported_capture_surfaces(self):
        s=src.read_text()
        for fragment in ["import pyautogui","import keyboard","import win32clipboard","import requests","import selenium"]:
            self.assertNotIn(fragment,s)
if __name__=="__main__":
    unittest.main()
