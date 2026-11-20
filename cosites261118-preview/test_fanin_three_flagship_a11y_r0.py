import unittest
from fanin_three_flagship_a11y_r0 import fanin, EXPECTED

COMMIT = "f" * 40

def mk(name):
 return {"site":name, "schema":"CoSites.ThreeFlagship.PinnedSourceAccessibility.R0", "expected_blob":EXPECTED[name],
 "source_blob_sha1":EXPECTED[name], "source_sha256":"a"*64, "run_commit":COMMIT,
 "state":"PASS_AUTOMATED_A11Y_NO_DETECTED_VIOLATIONS_NOT_HUMAN_ACCEPTED",
 "viewports":[{"viewport":vp, "violations":[], "incomplete_rule_count":0} for vp in ("mobile390", "desktop1365")]}

class TestFanIn(unittest.TestCase):
 def test_all_three(self):
  r=fanin([mk(x) for x in EXPECTED],COMMIT)
  self.assertEqual(r["state"],"PASS_AUTOMATED_WCAG_AA_SOURCE_SCAN_ONLY")
  self.assertFalse(r["human_first_use_accepted"])
  self.assertFalse(r["public_release_authorized"])
 def test_missing(self):self.assertEqual(fanin([mk("cocivium")],COMMIT)["state"],"HOLD_ACCESSIBILITY_REVIEW")
 def test_duplicate(self):self.assertIn("DUPLICATE_SITE:cocivium",fanin([mk(x) for x in EXPECTED]+[mk("cocivium")],COMMIT)["problems"])
 def test_wrong_sha(self):
  a=[mk(x) for x in EXPECTED]; a[1]["source_blob_sha1"]="0"*40
  self.assertIn("SOURCE_OR_COMMIT_BINDING_FAILED:inseed",fanin(a,COMMIT)["problems"])
 def test_wrong_commit(self):
  a=[mk(x) for x in EXPECTED]; a[1]["run_commit"]="0"*40
  self.assertIn("SOURCE_OR_COMMIT_BINDING_FAILED:inseed",fanin(a,COMMIT)["problems"])
 def test_violation(self):
  a=[mk(x) for x in EXPECTED];a[0]["viewports"][0]["violations"]=[{"id":"color-contrast"}]
  self.assertIn("ACCESSIBILITY_REVIEW_REQUIRED:cocivium",fanin(a,COMMIT)["problems"])
 def test_wrong_state(self):
  a=[mk(x) for x in EXPECTED];a[0]["state"]="PASS_FULL_PUBLIC_ACCEPTANCE"
  self.assertIn("INVALID_STATE:cocivium",fanin(a,COMMIT)["problems"])
 def test_unknown_site(self):
  a=[mk(x) for x in EXPECTED];a.append({"site":"unknown"})
  self.assertIn("UNEXPECTED_SITE",fanin(a,COMMIT)["problems"])

if __name__=="__main__":unittest.main()