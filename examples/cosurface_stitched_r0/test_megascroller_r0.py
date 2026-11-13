"""Static CoAll megascroller must not simulate mirrored deployment."""
from pathlib import Path
import unittest

PAGE = (Path(__file__).resolve().parent / "megascroller_r0.html").read_text(encoding="utf-8")


class MegascrollerTests(unittest.TestCase):
    def test_is_responsive_and_accessible(self):
        self.assertIn('name="viewport"', PAGE)
        self.assertIn('aria-label="Sections"', PAGE)
        self.assertIn("@media(max-width:640px)", PAGE)
    def test_one_root_and_seven_navigable_sections(self):
        for anchor in ("here", "seed", "orb", "map", "outreach", "resilience", "proof"):
            self.assertIn('href="#'+anchor+'"', PAGE)
            self.assertIn('id="'+anchor+'"', PAGE)
    def test_public_surface_does_not_advertise_unproved_release(self):
        for text in ("NOT LIVE X2", "open draft", "not an X2 release",
                     "not a production website", "not independently verified backup copies"):
            self.assertIn(text, PAGE)
    def test_no_private_mailbox_or_secret_content(self):
        for secret in ("rballard@inseed.com", "richardmballard@gmail.com",
                       "ndizeyeelix@gmail.com", "api_key", "PRIVATE_MANIFEST"):
            self.assertNotIn(secret, PAGE)
    def test_all_external_refs_are_public_source_pointers(self):
        self.assertIn("https://github.com/CoCivium/CoCivium/pull/375", PAGE)
        self.assertIn("https://github.com/CoCivium/CoCivium/issues/317", PAGE)
    def test_no_network_scripts_or_remote_loads(self):
        self.assertNotIn("<script", PAGE)
        self.assertNotIn("<iframe", PAGE)
        self.assertNotIn("<img", PAGE)
        self.assertNotIn("@import", PAGE)
    def test_mirror_is_candidate_not_claimed(self):
        self.assertIn("Mirror candidate", PAGE)
        self.assertIn("until a fetch from each actually succeeds", PAGE)


if __name__ == "__main__":
    unittest.main()
