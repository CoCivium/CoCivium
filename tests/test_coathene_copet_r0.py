"""CoAthene CoPet R0: source-only privacy, no-login and child learning contract."""
import json
import re
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
HOME=BASE/"examples"/"coathene_copet_r0"
DATA=HOME/"learning_map.json"
INDEX=HOME/"index.html"
GUIDE=HOME/"README.md"
PASSPORT=BASE/"docs"/"Architecture"/"COATHENE_COPASSPORT_LOGINLESS_CONTINUITY_R0_20261107.md"

class CoPetR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(DATA.read_text(encoding="utf-8"))
        cls.html=INDEX.read_text(encoding="utf-8")
        cls.guide=GUIDE.read_text(encoding="utf-8")
        cls.passport=PASSPORT.read_text(encoding="utf-8")

    def test_four_interests_and_five_coverage_windows(self):
        d=self.data
        self.assertEqual(len(d["petLessons"]),4)
        self.assertEqual(len(d["coPathViews"]),5)
        self.assertEqual({x["id"] for x in d["petLessons"]},
                         {"river","space","animals","games"})
        self.assertEqual({x["id"] for x in d["coPathViews"]},
                         {"communication","quantitative","science","systems","ethics"})

    def test_no_official_curriculum_mastery_or_profile(self):
        d=self.data
        self.assertEqual(d["experience"]["curriculum_policy"],
                         "BROAD_CAPABILITY_WINDOWS_NOT_OFFICIAL_ON_CURRICULUM_ALIGNMENT")
        self.assertIn("LOCAL_CORRECT_CHOICE_NE_MASTERY",d["nonclaims"])
        self.assertIn("COVERAGE_MAP_NE_OFFICIAL_CURRICULUM",d["nonclaims"])

    def test_exercises_have_valid_claim_evidence_and_nontransfer(self):
        for x in self.data["petLessons"]:
            self.assertEqual(len(x["claims"]),3)
            self.assertEqual(len(x["evidence"]),3)
            self.assertIn(x["claimCorrect"],range(3))
            self.assertIn(x["evidenceCorrect"],range(3))
            self.assertGreater(len(x["why"]),65)
            self.assertGreater(len(x["boundary"]),55)
            self.assertTrue(x["source"].startswith("https://"))
            self.assertGreater(len(x["curricularViews"]),1)

    def test_person_child_id_or_data_collection_not_present(self):
        x=self.data["proxy_and_identity"]
        for k in ("child_names","accounts","cookies","tracking","localStorage",
                  "indexedDB","network_calls","camera_microphone"):
            self.assertEqual(x[k],"NONE" if k not in ("child_names",) else "NEVER_REQUESTED",k)
        self.assertEqual(x["active_proxy"],"GENERIC_FICTIONAL_PET_NOT_CHILD_PROXY_IDENTITY")
        self.assertIn("PET_NE_CHILD_CLONE",self.data["nonclaims"])

    def test_loginless_does_not_require_fake_continuity(self):
        d=self.data
        self.assertEqual(d["experience"]["session_scope"],
                         "VOLATILE_BROWSER_MEMORY_ONLY_NEVER_SAVED")
        self.assertEqual(d["proxy_and_identity"]["sync_across_devices"],"NOT_PRESENT")
        self.assertIn("No traditional login",self.passport)

    def test_future_passport_not_claimed_implemented_or_certified(self):
        text=self.passport
        self.assertIn("no login screen",text.lower())
        self.assertIn("not a child account service",text.lower())
        self.assertIn("No traditional login",text)
        self.assertIn("CoLearnerHandle+",text)
        self.assertIn("CoPassport+",text)
        self.assertIn("CoDelegation+",text)
        self.assertIn("passkey",text.lower())
        self.assertIn("not",text.lower())

    def test_ai_checker_is_not_guardian_or_child_arbitrator(self):
        d=self.data
        self.assertEqual(d["experience"]["actual_AI"],"NONE")
        self.assertEqual(d["synth_review_future"]["status"],"NOT_IMPLEMENTED")
        self.assertIn("SYNTH_REVIEW_NE_CHILD_GUARDIAN",d["nonclaims"])
        self.assertIn("SYNTH_CHECK_NE_TRUSTED_HUMAN_ARBITRATOR",d["nonclaims"])

    def test_no_persistent_remote_or_background_storage_in_html(self):
        h=self.html.lower()
        for bad in ("fetch(","xmlhttprequest","websocket(","localstorage",
                    "sessionstorage","indexeddb","document.cookie","<iframe",
                    "<img","navigator.geolocation","navigator.mediadevices",
                    "navigator.sendbeacon"):
            self.assertNotIn(bad,h)
        self.assertIn("connect-src 'none'",h)
        self.assertIn("form-action 'none'",h)

    def test_one_primary_self_contained_offline_page(self):
        h=self.html
        self.assertEqual(len(re.findall(r"<main(?:\s|>)",h)),1)
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)",h)),1)
        self.assertIn('id="results" hidden',h)
        self.assertIn('id="progress" aria-live="polite"',h)
        self.assertIn("renderLesson();renderProgress()",h)

    def test_html_json_source_twin_equals_real_current_data(self):
        m=re.search(r'<script id="copet-data" type="application/json">(.*?)</script>',
                    self.html,re.S)
        self.assertIsNotNone(m)
        data=json.loads(m.group(1))
        d=self.data
        for k in ("schema","experience","coPathViews","petLessons"):
            self.assertEqual(data[k],d[k],k)

    def test_fictional_pet_cannot_trick_child_into_relationship(self):
        self.assertIn("not a real person, teacher or guardian",self.html)
        self.assertIn("No child identity collected",self.html)
        self.assertIn("No stored answers",self.html)
        self.assertIn("FICTIONAL_CHARACTER",self.data["experience"]["teachable_agent_mode"])
        self.assertEqual(self.data["experience"]["character_emotion_policy"],
                         "NO_ATTACHMENT_PRESSURE_NO_GUILT_NO_STREAKS_NO_ROMANTIC_OR_DEPENDENCY_LANGUAGE")

    def test_opc_unicef_and_actual_teachable_agents_research_cited(self):
        urls=" ".join(x["url"] for x in self.data["sources"])
        self.assertIn("priv.gc.ca",urls)
        self.assertIn("unicef.org",urls)
        self.assertIn("vanderbilt.edu",urls)
        self.assertIn("OPC",self.passport)
        self.assertIn("Vanderbilt",self.guide)

    def test_no_false_child_deployment_or_school_identity(self):
        self.assertIn("NOT_CERTIFIED_CHILD_SERVICE",self.data["status"])
        self.assertIn("NO_MINOR_PILOT_AUTHORIZED",self.data["nonclaims"])
        self.assertIn("not a child",self.guide.lower())
        self.assertIn("not a deployed",self.guide.lower())
        self.assertNotIn("CoCivium/CoSteward",self.html+self.guide)

if __name__=="__main__":unittest.main()
