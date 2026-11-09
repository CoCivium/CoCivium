"""CoPreGeneric public share bundle: source integrity and truth boundaries."""
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILES=("CoPreGeneric-v1.0-DRAFT.md", "CoAckRewise-v8.74.md",
       "CoFeedLoop-Devs.md", "CoMindspace-Map.md")
BUNDLE=(HERE/"CoPreGeneric-ShareableBundle-R0.md").read_text(encoding="utf-8")

class ShareableBundleTests(unittest.TestCase):
    def test_four_real_component_files_exactly_embedded(self):
        for filename in FILES:
            content=(HERE/filename).read_text(encoding="utf-8")
            self.assertIn(content, BUNDLE)
    def test_source_blobs_are_referenced(self):
        for sha in ("249da31c601e425ad32adbbe24a268f324d2b1fd",
                    "8c14dd38c7249ab0c4a5e8103d8291e5478a3f2a",
                    "a3bc21c821009c683d92d274e4ef62b0339721d5",
                    "ba367288d8ecadbd312128028c842b51109f6f43"):
            self.assertIn(sha, BUNDLE)
    def test_no_mirror_or_receiver_false_claim(self):
        self.assertIn("not independent receiver pickup", BUNDLE)
        self.assertIn("No claim of mirroring", BUNDLE)
        self.assertIn("NOT FINAL", BUNDLE.upper())
    def test_retains_human_gate_and_stop(self):
        self.assertIn("independent receiver readback", BUNDLE)
        self.assertIn("Stop", BUNDLE)
    def test_private_addresses_not_published(self):
        for token in ("rballard@inseed.com","richardmballard@gmail.com",
                      "christine@CoCivium.org","C:\\Users\\Owner",
                      "D:\\CoCivium\\"):
            self.assertNotIn(token,BUNDLE)
    def test_machine_mindspace_not_consciousness_claim(self):
        self.assertIn("not access to its hidden reasoning", BUNDLE)
        self.assertIn("No private conversation publication without consent", BUNDLE)

if __name__=="__main__":
    unittest.main()
