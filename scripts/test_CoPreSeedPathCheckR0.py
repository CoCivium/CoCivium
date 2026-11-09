"""Synthetic negative tests for CoPre public graph validation."""
from pathlib import Path
import importlib.util
import json
import shutil
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("coprecheck",Path(__file__).with_name("CoPreSeedPathCheckR0.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ROOT=Path(__file__).resolve().parents[1]
class CoPreGraphTests(unittest.TestCase):
    def test_live_checkout(self):
        report=mod.validate(ROOT)
        self.assertEqual(report["missing_paths"],0)
        self.assertEqual(report["external_receiver_readproof"],"NOT_OBSERVED")
    def clone(self, folder):
        targets=[mod.FEDERATION,mod.FABRIC,mod.INDEX]
        fed=json.loads((ROOT/mod.FEDERATION).read_text())
        fabric=json.loads((ROOT/mod.FABRIC).read_text())
        refs=[fed["root"]["temporary_entry"],fed["root"]["public_bootstrap"],fed["root"]["machine_index"],fed["coseed"]["landing"],fed["copath"]["entry"]]
        refs += [x["path"] for x in fed["coseed"]["candidates"]]
        refs += [x["path"] for x in fed["copath"]["paths"] if x["path"]]
        refs += [x["path"] for x in fabric["nodes"]]
        for path in set(targets+refs):
            dest=folder/path;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,dest)
        return fed,fabric
    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);self.clone(p);(p/"CoPre.md").unlink()
            with self.assertRaisesRegex(ValueError,"HOLD_MISSING_PUBLIC_PATH"):mod.validate(p)
    def test_dangling_relation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);fed,fabric=self.clone(p)
            fabric["nodes"][0]["relations"].append("missing-node")
            (p/mod.FABRIC).write_text(json.dumps(fabric))
            with self.assertRaisesRegex(ValueError,"HOLD_DANGLING_RELATION"):mod.validate(p)
    def test_false_mirror_promotion_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);fed,_=self.clone(p)
            fed["elected_destinations"][0]["status"]="VERIFIED"
            (p/mod.FEDERATION).write_text(json.dumps(fed))
            with self.assertRaisesRegex(ValueError,"HOLD_UNVERIFIED_MIRROR_PROMOTION"):mod.validate(p)
    def test_fake_head_promotion_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);fed,_=self.clone(p)
            fed["coseed"]["qualified_semantic_head"]="latest"
            (p/mod.FEDERATION).write_text(json.dumps(fed))
            with self.assertRaisesRegex(ValueError,"HOLD_UNQUALIFIED_CANON_HEAD"):mod.validate(p)
    def test_missing_nonclaim_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);fed,_=self.clone(p)
            fed["nonclaims"].remove("NO_THREE_WAY_MIRROR")
            (p/mod.FEDERATION).write_text(json.dumps(fed))
            with self.assertRaisesRegex(ValueError,"HOLD_NONCLAIMS"):mod.validate(p)
if __name__=="__main__":
    unittest.main(verbosity=2)
