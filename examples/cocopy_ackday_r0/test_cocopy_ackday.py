"""CoCopy/CoAckRewise R0 negative and deterministic replay tests. No network."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cocopy_ackday as app

DAY="2026-10-26"
SRC="test:synthetic-public"


class TrailTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"private"

    def make_root(self):
        self.root.mkdir(exist_ok=True)
        return self.root

    def write(self,kind="RAW",data=b"example",retain=False,parent=None):
        return app.append(self.root,DAY,kind,SRC,data,retain,parent)

    def run_cli(self,*args):
        script=Path(app.__file__)
        return subprocess.run(
            [sys.executable,str(script),"--root",str(self.root),*args],
            capture_output=True,text=True,timeout=10)

    def test_01_schema(self):
        self.assertEqual(app.SCHEMA,"CoCivium.CoCopyAckDay.R0")

    def test_02_no_auto_capture_without_explicit_event(self):
        self.assertEqual(app.summary(self.make_root(),DAY)["events"],0)

    def test_03_first_event(self):
        r=self.write()
        self.assertEqual(r["seq"],1)
        self.assertIsNone(r["prev_sha256"])

    def test_04_sha_length(self):
        self.assertEqual(len(self.write()["record_sha256"]),64)

    def test_05_hash_chain(self):
        first=self.write()
        second=self.write("REWISE",b"changed",parent=first["record_sha256"])
        self.assertEqual(second["prev_sha256"],first["record_sha256"])
        self.assertEqual(len(app.read_day(self.root,DAY)),2)

    def test_06_raw_content_default_not_retained(self):
        r=self.write(data=b"private synthetic note")
        self.assertIsNone(r["retained_text"])
        text=(self.root/(DAY+".jsonl")).read_text()
        self.assertNotIn("private synthetic note",text)

    def test_07_raw_content_explicit_retain(self):
        r=self.write(data=b"synthetic note",retain=True)
        self.assertEqual(r["retained_text"],"synthetic note")
        self.assertIn("synthetic note",app.render(self.root,DAY))

    def test_08_utf8_retain_rejects_invalid(self):
        with self.assertRaisesRegex(ValueError,"NOT_UTF8"):
            self.write(data=b"\xff",retain=True)

    def test_09_utf8_hash_only_accepts_bytes(self):
        self.assertEqual(self.write(data=b"\xff")["content_bytes"],1)

    def test_10_16kiB_boundary_allowed(self):
        self.assertEqual(self.write(data=b"a"*app.MAX_NOTE)["content_bytes"],app.MAX_NOTE)

    def test_11_16kiB_plus_one_rejected(self):
        with self.assertRaisesRegex(ValueError,"CONTENT_OVER_LIMIT"):
            self.write(data=b"a"*(app.MAX_NOTE+1))

    def test_12_kind_unknown_held(self):
        with self.assertRaisesRegex(ValueError,"BAD_KIND_OR_SOURCE"):
            self.write("RUN_EVERYTHING")

    def test_13_source_id_path_injection_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_KIND_OR_SOURCE"):
            app.append(self.root,DAY,"RAW","../../unsafe with spaces",b"x")

    def test_14_day_invalid(self):
        with self.assertRaises(ValueError):
            app.summary(self.make_root(),"2026-02-30")

    def test_15_missing_time_offset(self):
        with self.assertRaisesRegex(ValueError,"MISSING_TIME_OFFSET"):
            app.append(self.root,DAY,"RAW",SRC,b"hi",source_time="2026-10-26T08:00:00")

    def test_16_offset_preserved(self):
        r=app.append(self.root,DAY,"RAW",SRC,b"ok",source_time="2026-10-26T02:00:00-04:00")
        self.assertEqual(r["source_time"],"2026-10-26T02:00:00-04:00")

    def test_17_parent_missing_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_PARENT"):
            self.write(parent="0"*64)

    def test_18_parent_ref_is_local(self):
        a=self.write()
        b=self.write("ACK",b"",parent=a["record_sha256"])
        self.assertEqual(b["parent_id"],a["record_sha256"])
        self.assertIsNone(app.summary(self.root,DAY)["receiver_ack"])

    def test_19_tamper_kind_rejected(self):
        self.write()
        f=self.root/(DAY+".jsonl")
        f.write_text(f.read_text().replace('"kind":"RAW"','"kind":"ACK"'))
        with self.assertRaisesRegex(ValueError,"TAMPER_OR_INVALID_HASH"):
            app.read_day(self.root,DAY)

    def test_20_truncated_record_held(self):
        self.write()
        f=self.root/(DAY+".jsonl")
        f.write_bytes(f.read_bytes()[:-1])
        with self.assertRaisesRegex(ValueError,"TRUNCATED_JSONL"):
            app.read_day(self.root,DAY)

    def test_21_broken_jsonl_held(self):
        self.make_root()
        (self.root/(DAY+".jsonl")).write_bytes(b"invalid json\n")
        with self.assertRaisesRegex(ValueError,"BROKEN_JSONL"):
            app.read_day(self.root,DAY)

    def test_22_unknown_field_held(self):
        self.write()
        f=self.root/(DAY+".jsonl")
        x=json.loads(f.read_text())
        x["api_key"]="synthetic"
        f.write_text(json.dumps(x)+"\n")
        with self.assertRaisesRegex(ValueError,"UNKNOWN_FIELDS"):
            app.read_day(self.root,DAY)

    def test_23_forged_ack_held(self):
        self.write()
        f=self.root/(DAY+".jsonl")
        x=json.loads(f.read_text())
        x["receiver_ack"]="fake"
        f.write_text(json.dumps(x)+"\n")
        with self.assertRaisesRegex(ValueError,"FORGED_AUTHORITY"):
            app.read_day(self.root,DAY)

    def test_24_no_overwrite_of_html(self):
        self.write()
        out=self.root/"view.html"
        out.write_text("existing")
        r=self.run_cli("render","--day",DAY,"--output",str(out))
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(out.read_text(),"existing")

    def test_25_html_escapes_raw_content(self):
        self.write(data=b"<script>alert('x')</script>",retain=True)
        page=app.render(self.root,DAY)
        self.assertNotIn("<script>",page)
        self.assertIn("&lt;script&gt;",page)

    def test_26_html_has_no_remote_resources(self):
        self.write()
        page=app.render(self.root,DAY)
        self.assertIn("default-src &#39;none&#39;",page)
        self.assertNotIn("<script ",page)
        self.assertNotIn("<iframe",page)

    def test_27_html_keyboard_details(self):
        self.write(retain=True)
        page=app.render(self.root,DAY)
        self.assertIn("<details>",page)
        self.assertIn("summary:focus",page)

    def test_28_missing_log_not_absence_of_work(self):
        page=app.render(self.make_root(),DAY)
        self.assertIn("not evidence that no work happened",page)

    def test_29_no_authority_or_receiver_ack_in_all_records(self):
        self.write()
        self.write("CHALLENGE",b"synthetic")
        for row in app.read_day(self.root,DAY):
            self.assertEqual(row["authority"],"NONE")
            self.assertIsNone(row["receiver_ack"])

    def test_30_lock_collision_no_append(self):
        self.make_root()
        (self.root/(DAY+".lock")).write_text("in-progress")
        with self.assertRaises(FileExistsError):
            self.write()
        self.assertEqual(app.summary(self.root,DAY)["events"],0)

    @unittest.skipUnless(hasattr(os,"symlink"),"symlink absent")
    def test_31_symlink_journal_rejected(self):
        self.make_root()
        target=Path(self.tmp.name)/"target.txt"
        target.write_text("sentinel")
        (self.root/(DAY+".jsonl")).symlink_to(target)
        with self.assertRaisesRegex(ValueError,"JOURNAL_NOT_REGULAR"):
            app.read_day(self.root,DAY)
        self.assertEqual(target.read_text(),"sentinel")

    def test_32_cli_append_zero_content_receipt(self):
        r=self.run_cli("append","--day",DAY,"--kind","ACK","--source-id",SRC)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)["state"],"APPENDED_LOCAL_ONLY")

    def test_33_cli_verify_counts(self):
        self.write()
        r=self.run_cli("verify","--day",DAY)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)["kind_counts"],{"RAW":1})

    def test_34_cli_render(self):
        self.write()
        out=self.root/"view.html"
        r=self.run_cli("render","--day",DAY,"--output",str(out))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("CoAckRewise",out.read_text())

    def test_35_cli_explicit_file_hash_only(self):
        self.make_root()
        text=Path(self.tmp.name)/"note.txt"
        text.write_text("synthetic scoped input")
        r=self.run_cli("append","--day",DAY,"--kind","RAW","--source-id",SRC,"--input-file",str(text))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertNotIn("synthetic scoped input",(self.root/(DAY+".jsonl")).read_text())

    def test_36_cli_retained_requires_explicit_flag(self):
        self.make_root()
        text=Path(self.tmp.name)/"note.txt"
        text.write_text("opt in local test text")
        r=self.run_cli("append","--day",DAY,"--kind","RAW","--source-id",SRC,
                       "--input-file",str(text),"--retain-raw")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("opt in local test text",(self.root/(DAY+".jsonl")).read_text())

    def test_37_cli_file_too_large_rejects(self):
        self.make_root()
        text=Path(self.tmp.name)/"large.txt"
        text.write_bytes(b"X"*(app.MAX_NOTE+1))
        r=self.run_cli("append","--day",DAY,"--kind","RAW","--source-id",SRC,"--input-file",str(text))
        self.assertNotEqual(r.returncode,0)
        self.assertIn("HELD",r.stderr)

    def test_38_default_does_not_import_network_or_clipboard(self):
        import inspect
        s=inspect.getsource(app)
        for token in ("import socket","import requests","import pyperclip","win32clipboard","pynput","import selenium"):
            self.assertNotIn(token,s)

    def test_39_replay_identical(self):
        self.write()
        self.write("REWISE",b"another")
        a=app.summary(self.root,DAY)
        b=app.summary(self.root,DAY)
        self.assertEqual(a,b)

    def test_40_multi_day_isolation(self):
        self.write()
        self.assertEqual(app.summary(self.root,"2026-10-25")["events"],0)

    @unittest.skipUnless(hasattr(os,"symlink"),"symlink absent")
    def test_41_broken_symlink_is_not_empty_log(self):
        self.make_root()
        file=self.root/(DAY+".jsonl")
        file.symlink_to(Path(self.tmp.name)/"absent.txt")
        with self.assertRaisesRegex(ValueError,"JOURNAL_NOT_REGULAR"):
            app.read_day(self.root,DAY)

    def test_42_private_html_outside_root_held(self):
        self.write(retain=True)
        external=Path(self.tmp.name)/"unsafe-outside.html"
        r=self.run_cli("render","--day",DAY,"--output",str(external))
        self.assertNotEqual(r.returncode,0)
        self.assertIn("OUTPUT_MUST_STAY_IN_PRIVATE_ROOT",r.stderr)
        self.assertFalse(external.exists())

if __name__=="__main__":
    unittest.main()
