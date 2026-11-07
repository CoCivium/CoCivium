"""CoAthene CoLens R0 source, age-hint privacy, first-child companion and vector QA."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"examples"/"coathene_copet_r0"
DATA=HOME/"learning_map.json"
HTML=HOME/"index.html"
DOC=ROOT/"docs"/"Architecture"/"COATHENE_COLENS_PRESENTATION_DIAL_R0_20261107.md"

class CoLensSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(DATA.read_text(encoding="utf-8"))
        cls.html=HTML.read_text(encoding="utf-8")
        cls.doc=DOC.read_text(encoding="utf-8")
        cls.lens=cls.data["lens"]

    def test_version_not_credential_or_minor_service(self):
        self.assertEqual(self.lens["schema"],"CoAthene.CoLensPresentation.R0-candidate")
        self.assertIn("NOT_CHILD_AGE_VERIFICATION",self.lens["state"])
        self.assertEqual(self.lens["effectBoundary"]["realChildrenObserved"],0)
        self.assertEqual(self.lens["effectBoundary"]["schoolEnrollment"],0)
        self.assertEqual(self.lens["effectBoundary"]["teacherApproval"],"NOT_OBSERVED")

    def test_four_optional_modes_and_intents(self):
        self.assertEqual([x["id"] for x in self.lens["modes"]],
                         ["together","play","explore","research"])
        self.assertEqual([x["id"] for x in self.lens["focuses"]],
                         ["wonder","make","explain","challenge"])
        self.assertEqual(self.lens["defaultMode"],"explore")
        self.assertEqual(self.lens["defaultFocus"],"wonder")

    def test_toddler_is_grownup_offscreen_not_unattended_classroom(self):
        first=self.lens["modes"][0]
        self.assertTrue(first["adultPresenceRequired"])
        self.assertTrue(first["noSoloChild"])
        self.assertIn("NO_QUIZ_NO_PROGRESS",first["interaction"])
        self.assertIn("no sedentary screen time",first["disclosure"])
        self.assertIn("less screen time is better",first["disclosure"])
        self.assertIn("adult-only",self.doc)
        self.assertIn("do not market",self.doc.lower())

    def test_all_subjects_have_short_human_play_prompts(self):
        self.assertEqual(len(self.lens["scenes"]),4)
        for sc in self.lens["scenes"]:
            self.assertLess(len(sc["toddlerPrompt"]),115)
            self.assertLess(len(sc["playPrompt"]),105)
            self.assertGreater(len(sc["offline"]),45)
            self.assertIn("Screen away:",sc["offline"])
            self.assertEqual(len(sc["playOptions"]),2)
            self.assertIn(sc["correct"],(0,1))
            self.assertEqual({*sc["focusPrompts"]},
                             {"wonder","make","explain","challenge"})

    def test_exact_html_source_twin_and_four_original_vector_pictures(self):
        m=re.search(r'<script id="copet-data" type="application/json">(.*?)</script>',
                    self.html,re.S)
        self.assertIsNotNone(m)
        embedded=json.loads(m.group(1))
        self.assertEqual(embedded["lens"],self.lens)
        self.assertEqual(len(re.findall(r'<svg id="lens-art-',self.html)),4)
        self.assertEqual(len(re.findall(r'<svg id="lens-art-[^"]+" viewBox="0 0 320 230" role="img" aria-label=',self.html)),4)

    def test_explicit_mode_controls_not_deceptive_automatic_age_detection(self):
        h=self.html
        for mode in ("together","play","explore","research"):
            self.assertIn('data-lens-mode="'+mode+'"',h)
        self.assertIn("aria-pressed",h)
        self.assertIn("id=\"lens-focus\"",h)
        self.assertIn('role="group" aria-label="Presentation mode, not an age test"',h)
        self.assertEqual(self.lens["policy"]["selection"],"EXPLICIT_CHOICE_ONLY_NO_DETECTION")
        self.assertEqual(self.lens["policy"]["childData"],"NONE_NO_DATE_OF_BIRTH_NO_PROFILE")

    def test_child_safety_stays_prior_to_cosmetic_game(self):
        self.assertEqual(self.lens["policy"]["noArtificialRewards"],
                         "NO_STREAKS_NO_RANKS_NO_FORCED_CONTINUATION")
        self.assertIn("TOGETHER_NO_CHILD_QUIZ",self.lens["policy"]["interactivity"])
        self.assertIn("CoEntour",self.doc)
        self.assertIn("CoPassport",self.doc)
        self.assertIn("no quiz",self.doc.lower())
        self.assertIn("NO_AUTO_AUDIO",self.lens["policy"]["sharedPlay"])

    def test_original_science_unchanged(self):
        canonical_ids={x["id"] for x in self.data["petLessons"]}
        self.assertEqual({x["id"] for x in self.lens["scenes"]},canonical_ids)
        for lesson in self.data["petLessons"]:
            self.assertEqual(len(lesson["claims"]),3)
            self.assertEqual(len(lesson["evidence"]),3)
            self.assertTrue(lesson["source"].startswith("https://"))
        self.assertIn("same source remains governing",self.doc.lower())

    def test_offline_no_persistent_profile_or_media_access(self):
        h=self.html.lower()
        for bad in ("localstorage","sessionstorage","indexeddb","fetch(",
                    "websocket(","xmlhttprequest","document.cookie",
                    "navigator.geolocation","navigator.mediadevices",
                    "speechsynthesis.speak","<iframe","<img"):
            self.assertNotIn(bad,h)
        self.assertIn("connect-src 'none'",h)
        self.assertIn("script-src 'unsafe-inline'",h)
        self.assertIn("no birth date",self.doc.lower())

    def test_parent_stop_clear_and_reopen_have_real_buttons(self):
        for key in ("lens-finish","lens-reopen","lens-switch","lens-done",
                    "lens-play","lens-play-result","lens-focus-cue"):
            self.assertIn('id="'+key+'"',self.html)
        self.assertIn("visit=newVisit();outfit=newOutfit()",self.html)
        self.assertIn('lens-scene-content").classList.add("is-finished"',self.html)
        self.assertIn("screen away",self.html.lower())

    def test_mode_switch_preserves_one_current_front(self):
        h=self.html
        self.assertEqual(len(re.findall(r"<main(?:\s|>)",h)),1)
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)",h)),1)
        self.assertIn('body[data-lens="together"] .layout',h)
        self.assertIn('body[data-lens="play"] .layout',h)
        self.assertIn('body[data-lens="research"] .lens-research',h)

    def test_genuine_external_guidance_not_fake_endorsement(self):
        urls=" ".join(v["url"] for v in self.lens["externalSources"])
        self.assertIn("who.int",urls)
        self.assertIn("naeyc.org",urls)
        self.assertIn("aap.org",urls)
        self.assertIn("not a child-facing deployed service",self.doc.lower())
        self.assertIn("not a child",self.doc.lower())

    def test_no_age_hint_as_privilege_or_credential(self):
        self.assertIn("AGE_GATING",self.lens["policy"]["ageLabel"])
        self.assertIn("LICENSED_SCHOOL",self.lens["policy"]["legalSchool"])
        self.assertEqual(self.lens["effectBoundary"]["screenTimeTelemetry"],"NONE")
        self.assertEqual(self.lens["effectBoundary"]["personalizationModel"],"NOT_PRESENT")

if __name__=="__main__":
    unittest.main()
