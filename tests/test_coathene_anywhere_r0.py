"""CoAthene Anywhere R0 public-safe source, policy and UI projection checks."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"examples"/"coathene_anywhere_r0"
DATA=HOME/"recipe.json"
INDEX=HOME/"index.html"
GUIDE=HOME/"README.md"


class AnywhereR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(DATA.read_text(encoding="utf-8"))
        cls.html=INDEX.read_text(encoding="utf-8")
        cls.guide=GUIDE.read_text(encoding="utf-8")

    def test_source_state_public_candidate_not_school_or_runtime(self):
        d=self.data
        self.assertEqual(d["schema"],"CoAthene.AnywhereSessionRecipe.R0-candidate")
        self.assertIn("NOT_SCHOOL",d["state"])
        self.assertEqual(d["limits"]["onlineSchool"],"NOT_OPERATED")
        self.assertEqual(d["limits"]["publicSite"],"NOT_DEPLOYED")

    def test_question_first_and_usable_three_original_scenarios(self):
        d=self.data
        self.assertEqual(len(d["scenarios"]),3)
        self.assertEqual({v["id"] for v in d["scenarios"]},
                         {"runoff","mirror","commons"})
        for v in d["scenarios"]:
            self.assertTrue(v["question"].endswith("?"))
            self.assertGreater(len(v["knowledge"]),60)
            self.assertGreater(len(v["challenge"]),60)
            self.assertGreater(len(v["transfer"]),60)

    def test_modes_do_not_mandate_institution_or_live_social_link(self):
        d=self.data
        self.assertEqual({m["id"] for m in d["modes"]},
                         {"solo","group","mentor","institution"})
        self.assertFalse(next(m for m in d["modes"] if m["id"]=="group")
                         ["requiresHumanInstitution"])
        self.assertFalse(next(m for m in d["modes"] if m["id"]=="solo")
                         ["requiresOnline"])
        self.assertEqual(d["limits"]["realTimeSync"],"NOT_PRESENT")
        self.assertEqual(d["limits"]["autoMessaging"],"NONE")

    def test_place_is_composable_not_compulsory(self):
        d=self.data
        self.assertEqual(len(d["placeOptions"]),5)
        self.assertEqual({p["id"] for p in d["placeOptions"]},
                         {"anywhere","offline","remote","local","mixed"})
        self.assertEqual(sum(not p["physicalRequired"] for p in d["placeOptions"]),4)
        self.assertTrue(all(not p["networkRequired"] for p in d["placeOptions"]))

    def test_learner_minors_and_institution_rights_do_not_disappear(self):
        d=self.data
        youth=next(a for a in d["audiences"] if a["id"]=="youth")
        self.assertTrue(youth["adultFacilitatorRequired"])
        self.assertIn("adult oversight",d["limits"]["minorSafety"])
        self.assertIn("GROUP_PLAN_NE_PARTICIPANT_CONSENT",d["nonclaims"])
        self.assertIn("ANYWHERE_NE_OPTIONAL_ATTENDANCE_LAW",d["nonclaims"])
        self.assertIn("responsible adult oversight",d["limits"]["minorSafety"])

    def test_json_source_twin_matches_real_html_embedded_app(self):
        match=re.search(r'<script id="coathene-recipe" type="application/json">(.*?)</script>',
                        self.html,re.S)
        self.assertIsNotNone(match)
        twin=json.loads(match.group(1))
        d=self.data
        for key in ("schema","modes","placeOptions","audiences","groupRoles","scenarios"):
            self.assertEqual(twin[key],d[key],key)

    def test_csp_requires_no_network_media_forms_or_remote_scripts(self):
        h=self.html.lower()
        for text in ("default-src 'none'","connect-src 'none'",
                     "frame-src 'none'","media-src 'none'",
                     "img-src 'none'","form-action 'none'"):
            self.assertIn(text,h)
        for text in ("localstorage","sessionstorage","indexeddb",
                     "navigator.geolocation","navigator.mediadevices",
                     "xmlhttprequest","websocket(","fetch(","<iframe","<img"):
            self.assertNotIn(text,h)

    def test_visible_one_front_reset_and_activity_reveal(self):
        h=self.html
        self.assertEqual(len(re.findall(r"<main(?: |>)",h)),1)
        self.assertEqual(len(re.findall(r"<h1(?: |>)",h)),1)
        self.assertIn('<section id="session"',h)
        self.assertIn("setup.hidden=true;session.hidden=false",h)
        self.assertIn("session.hidden=true;setup.hidden=false",h)
        self.assertIn('id="prediction-feedback" aria-live="polite"',h)
        self.assertIn('id="new-plan"',h)

    def test_accessibility_keyboard_print_and_no_headset(self):
        h=self.html
        self.assertIn(":focus-visible",h)
        self.assertIn("prefers-reduced-motion",h)
        self.assertIn("@media print",h)
        self.assertIn("<label for=",h)
        self.assertIn("No account",h)
        self.assertIn("No network needed",h)
        self.assertIn("headset",h)

    def test_public_source_does_not_disclose_private_repo_identifiers(self):
        joined=self.html+self.guide+DATA.read_text(encoding="utf-8")
        for secretish in ("CoCivium/CoSteward", "private-source sha",
                          "Richard Ballard", "rick@", "C:\\Users\\Owner",
                          "D:\\CoCivium\\CoFarm"):
            self.assertNotIn(secretish,joined)
        self.assertIn("PUBLIC SOURCE DRAFT",self.guide)

    def test_reuse_explicit_prior_groupbuild_and_roamlab_lineage(self):
        paths=[v["source"] for v in self.data["reuse"]]
        self.assertTrue(any("GROUPBUILD_COTEAMING" in x for x in paths))
        self.assertTrue(any("RoamLab_R0" in x for x in paths))
        self.assertTrue(any("COVIRTUAL_SESSION_MORPHOLOGY" in x for x in paths))
        self.assertIn("Existing",self.guide)

    def test_real_pilot_and_credits_remain_unproven(self):
        self.assertIn("not a deployed website",self.guide.lower())
        self.assertIn("independent first-use",self.guide.lower())
        self.assertIn("NOT_CLAIMED",self.data["limits"]["accreditation"])
        self.assertIn("school",self.html.lower())

    def test_no_automatic_source_navigation_or_read_receipt_claim(self):
        h=self.html
        self.assertNotIn("window.location",h)
        self.assertIn('rel="noopener noreferrer"',h)
        self.assertIn("Opening the link leaves the local-only prototype",h)
        self.assertNotIn("SENT_PROVIDER_RECORD_READ_BACK",h)


if __name__=="__main__":unittest.main()
