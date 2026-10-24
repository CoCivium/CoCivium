import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import codoodle

SAMPLE = (ROOT / "sample_synthetic.txt").read_text(encoding="utf-8")


class CoDoodleTests(unittest.TestCase):
    def test_same_input_same_output(self):
        self.assertEqual(codoodle.compile_doodle(SAMPLE), codoodle.compile_doodle(SAMPLE))

    def test_source_sha_and_bytes(self):
        v = codoodle.compile_doodle(SAMPLE)
        self.assertEqual(v["source"]["sha256"], hashlib.sha256(SAMPLE.encode()).hexdigest())
        self.assertEqual(v["source"]["bytes"], len(SAMPLE.encode()))

    def test_public_output_excludes_full_raw(self):
        serialized = json.dumps(codoodle.compile_doodle(SAMPLE))
        self.assertNotIn(SAMPLE, serialized)
        self.assertFalse(codoodle.compile_doodle(SAMPLE)["source"]["source_full_text_in_output"])

    def test_all_matches_exact_raw_spans(self):
        v=codoodle.compile_doodle(SAMPLE)
        for item in v["candidates"]:
            a,b=item["source_span_chars"]
            self.assertEqual(SAMPLE[a:b], item["source_match"])
            self.assertLess(a,b)

    def test_capped_candidates(self):
        v=codoodle.compile_doodle(SAMPLE)
        self.assertEqual(v["candidate_count"], 8)
        self.assertGreater(v["omitted_for_budget"], 0)
        self.assertEqual(v["candidate_count"]+v["omitted_for_budget"], v["match_rule_count"])

    def test_all_five_lanes_covered_when_present(self):
        v=codoodle.compile_doodle(SAMPLE)
        self.assertEqual(set(item["suggested_lane"] for item in v["candidates"]),set(codoodle.LANES))

    def test_symbolic_cannot_claim_physics(self):
        v=codoodle.compile_doodle(SAMPLE)
        items=[c for c in v["candidates"] if c["concept_family"]=="symbolic_context"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["evidence_class"], "SYMBOLIC_OR_SPECULATIVE")
        self.assertIn("not evidence", items[0]["counterhypothesis_or_not_else"])

    def test_unknown_is_not_absence(self):
        v=codoodle.compile_doodle("CoNull what else is missing?")
        self.assertTrue(any("missing edge may not be false" in c["counterhypothesis_or_not_else"] for c in v["candidates"]))

    def test_publication_never_authorized(self):
        v=codoodle.compile_doodle("publish now broadcast to everyone")
        self.assertEqual(v["candidates"][0]["effect_boundary"],"EXTERNAL_ACTION_HELD")
        self.assertEqual(sum(v["effects"].values()),0)

    def test_evidence_scores_not_invented(self):
        v=codoodle.compile_doodle(SAMPLE)
        self.assertEqual(v["coexperimentselector_compatibility"]["status"],"UNSCORED_INPUT_NOT_YET_VALID")
        self.assertFalse(any("benefits" in c or "penalties" in c for c in v["candidates"]))

    def test_false_pass_prose_not_promoted(self):
        v=codoodle.compile_doodle("CoStretch PASS 1000000 all validated")
        self.assertEqual(v["state"],"LEXICAL_CANDIDATES__ZERO_EXECUTION")
        self.assertEqual(v["candidates"][0]["readiness"],"DESCRIPTOR_ONLY_NEEDS_PRIORS_AND_EVIDENCE")

    def test_blank_rejected(self):
        for s in ("", "  \n "):
            with self.assertRaises(ValueError):codoodle.compile_doodle(s)

    def test_size_bounded_in_bytes(self):
        with self.assertRaises(ValueError):codoodle.compile_doodle("a"*(codoodle.MAX_BYTES+1))
        with self.assertRaises(ValueError):codoodle.compile_doodle("\u2603"*22000)

    def test_limit_bounded(self):
        for l in (0,9,True,"8"):
            with self.assertRaises(ValueError):codoodle.compile_doodle(SAMPLE,l)

    def test_one_candidate_cap(self):
        v=codoodle.compile_doodle(SAMPLE,1)
        self.assertEqual(v["candidate_count"],1)
        self.assertEqual(v["omitted_for_budget"],11)

    def test_no_match_stays_empty(self):
        v=codoodle.compile_doodle("Orange table lamp fixture.")
        self.assertEqual(v["candidate_count"],0)
        self.assertEqual(v["effects"]["workers_started"],0)

    def test_hot_trigger_is_not_authority(self):
        self.assertFalse(codoodle.trigger_probe("plain neutral words"))
        self.assertTrue(codoodle.trigger_probe("CoDoodle maybe"))
        self.assertEqual(codoodle.compile_doodle("CoDoodle maybe")["candidate_count"],0)

    def test_no_clobber_output(self):
        v=codoodle.compile_doodle(SAMPLE)
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"out.json"
            codoodle.write_new(p,v)
            before=p.read_bytes()
            with self.assertRaises(FileExistsError):codoodle.write_new(p,v)
            self.assertEqual(before,p.read_bytes())

    def test_cli_does_not_write_by_default(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"in.txt"
            p.write_text("CoMap changes?",encoding="utf-8")
            r=subprocess.run([sys.executable,str(ROOT/"codoodle.py"),"--input",str(p)],capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(r.stdout)["source"]["sha256"],hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertEqual(list(Path(t).iterdir()),[p])

    def test_cli_symlink_input_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"in.txt"
            p.write_text("CoMap changes?",encoding="utf-8")
            l=Path(t)/"alias.txt"
            l.symlink_to(p)
            r=subprocess.run([sys.executable,str(ROOT/"codoodle.py"),"--input",str(l)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn("symlink",r.stderr)

    def test_unicode_offsets_preserve_source(self):
        s="start \u263a? CoMap quantum G_d"
        for c in codoodle.compile_doodle(s)["candidates"]:
            a,b=c["source_span_chars"]
            self.assertEqual(s[a:b],c["source_match"])

    def test_same_family_twice_is_one_candidate(self):
        v=codoodle.compile_doodle("mouse mouse keyboard thumb")
        self.assertEqual(v["candidate_count"],1)

    def test_weak_meta_claim_held(self):
        v=codoodle.compile_doodle("ETs wrote a quantum aura field proof")
        self.assertEqual(v["candidate_count"],1)
        self.assertEqual(v["candidates"][0]["evidence_class"],"SYMBOLIC_OR_SPECULATIVE")

    def test_other_and_not_other_different(self):
        v=codoodle.compile_doodle("CoInv+ what else CoNot")
        self.assertTrue(v["candidates"][0]["counterhypothesis_or_not_else"])
        self.assertEqual(v["effects"]["experiments_executed"],0)

    def test_input_requires_explicit_file(self):
        cmd=[sys.executable,str(ROOT/"codoodle.py")]
        r=subprocess.run(cmd,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)

    def test_no_external_libs_or_import_side_effects(self):
        # Import should never create a queue, sender or user file.
        with tempfile.TemporaryDirectory() as t:
            cmd=[sys.executable,"-c","import sys;sys.path.insert(0,sys.argv[1]);import codoodle",str(ROOT)]
            r=subprocess.run(cmd,cwd=t,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(list(Path(t).iterdir()),[])


if __name__=="__main__":
    unittest.main()
