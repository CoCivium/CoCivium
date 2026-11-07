"""CoEntour R0: optional local cosmetics, no child-id/credential/profile and source twin."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"examples"/"coathene_copet_r0"
DATA=HOME/"learning_map.json"
HTML=HOME/"index.html"
GUIDE=ROOT/"docs"/"Architecture"/"COATHENE_COENTOUR_COSMETIC_ROUTE_R0_20261107.md"

class CoEntourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(DATA.read_text(encoding="utf-8"))
        cls.html=HTML.read_text(encoding="utf-8")
        cls.guide=GUIDE.read_text(encoding="utf-8")
        cls.e=cls.d["entourage"]
        cls.types=cls.e["item_types"]
        cls.items=[v for t in cls.types for v in t["items"]]

    def test_named_coentour_and_four_item_types(self):
        self.assertEqual(self.e["displayName"],"CoEntour+")
        self.assertEqual({x["id"] for x in self.types},{"familiar","hat","badge","trail"})
        self.assertEqual(len(self.items),16)
        self.assertEqual(len({x["id"] for x in self.items}),16)

    def test_every_look_points_to_valid_existing_question(self):
        ids={x["id"] for x in self.d["petLessons"]}
        for item in self.items:
            self.assertIn(item["routeLessonId"],ids)
            self.assertGreater(len(item["label"]),5)
            self.assertEqual(item["claimClass"],"COSMETIC_SELF_SELECTED_UNVERIFIED")
            self.assertEqual(item["levelClaim"],"NONE")
            self.assertEqual(item["accessRights"],"NONE")
            self.assertEqual(item["immutableIdentity"],"NONE")

    def test_all_outfits_available_without_login_or_earning(self):
        self.assertEqual(self.e["choice_mode"],"ALL_ITEMS_AVAILABLE_FROM_START_NO_EARNING_GATE_NO_MONEY")
        self.assertEqual(self.e["current_level"],"NONE_NO_SCALAR_LEARNER_RANK")
        self.assertEqual(self.e["default"],"NO_CLAIM_NO_AUTOMATIC_STEREOTYPE")
        self.assertIn("ATTEMPT_NE_CREDIT_OR_MASTERY",self.e["visit_marker"]["state"])

    def test_no_automatic_classification_from_child_appearance(self):
        self.assertEqual(self.e["role_of_item"],"EXPLICIT_SELF_SELECTION_LOCAL_ROUTE_HINT_ONLY")
        self.assertEqual(self.e["confirmed_route"],"REQUIRES_SEPARATE_EXPLICIT_TRY_QUESTION_ACTION")
        self.assertIn("not a diagnosis",self.e["presentation_rule"])
        self.assertIn("COENTOUR_CHOICE_NE_TRUSTED_CHILD_PROFILE",self.e["nonclaims"])

    def test_source_twin_includes_complete_entourage(self):
        m=re.search(r'<script id="copet-data" type="application/json">(.*?)</script>',self.html,re.S)
        self.assertIsNotNone(m)
        data=json.loads(m.group(1))
        self.assertEqual(data["entourage"],self.e)
        self.assertEqual(data["petLessons"],self.d["petLessons"])

    def test_one_front_with_optional_wardrobe_selector_and_explicit_route(self):
        self.assertEqual(len(re.findall(r'<main(?:\s|>)',self.html)),1)
        self.assertEqual(len(re.findall(r'<h1(?:\s|>)',self.html)),1)
        for id in ("wardrobe","gear-type","gear-item","gear-claim",
                   "gear-follow","gear-clear","gear-cue","gear-look","visit-markers"):
            self.assertIn('id="'+id+'"',self.html)
        self.assertIn('id="gear-follow" type="button" class="alt" disabled',self.html)
        self.assertIn('by("gear-follow").addEventListener("click",followGear)',self.html)

    def test_visit_marker_not_learner_grading_or_verified_badge(self):
        self.assertTrue(self.e["visit_marker"]["noChildRank"])
        self.assertTrue(self.e["visit_marker"]["noStorage"])
        self.assertIn("VISIT_ONLY_ATTEMPT_NE_CREDIT_OR_MASTERY",self.e["visit_marker"]["state"])
        self.assertIn("not a grade",self.html)
        self.assertIn("not mastery",self.html.lower())
        self.assertIn("BADGE_ICON_NE_VERIFIED_CREDENTIAL",self.e["nonclaims"])

    def test_future_credential_is_separate_and_unimplemented(self):
        future=self.e["future_credential_candidate"]
        self.assertEqual(future["state"],"NOT_IMPLEMENTED")
        self.assertIn("1EdTech Open Badges 3.0",future["relevantStandard"])
        self.assertIn("criteria",future["scope"])
        self.assertIn("issuer",future["scope"])
        self.assertIn("PUBLIC_SOURCE",self.d["status"])
        self.assertIn("Open Badges",self.guide)

    def test_privacy_no_hidden_account_tracking_or_server(self):
        self.assertEqual(self.e["visibility_default"],"LOCAL_ONLY_NO_BROADCAST_NO_ONLINE_PROFILE")
        h=self.html.lower()
        for bad in ("localstorage","sessionstorage","indexeddb","fetch(","websocket(",
                    "xmlhttprequest","document.cookie","navigator.geolocation",
                    "navigator.mediadevices","navigator.sendbeacon","<iframe","<img"):
            self.assertNotIn(bad,h)
        self.assertIn("connect-src 'none'",h)
        self.assertIn("form-action 'none'",h)

    def test_no_learning_credential_deduced_from_outfit(self):
        text=self.guide.lower()
        for phrase in ("cosmetic","not mastery","never","credential","issuer",
                       "consent","learner"):
            self.assertIn(phrase,text)
        self.assertIn("badge icon",self.e["future_credential_candidate"]["importantLimit"])

    def test_existing_guest_teach_moss_and_passport_protections_preserved(self):
        self.assertIn("function newVisit(){return {explored:[],last:null};}",self.html)
        self.assertIn("actualMasteryVerified:false",self.html)
        self.assertIn('CoPassport+',self.html)
        self.assertIn("learnerIdentity:false",self.html)
        self.assertIn("outfit=newOutfit();renderProgress();renderOutfit()",self.html)

    def test_no_school_entitlement_or_claimed_clan_membership(self):
        self.assertIn("NO_SCHOOL_IDENTITY",self.e["nonclaims"])
        self.assertEqual(self.d["proxy_and_identity"]["active_proxy"],
                        "GENERIC_FICTIONAL_PET_NOT_CHILD_PROXY_IDENTITY")
        self.assertIn("Real child pilots",self.guide)
        self.assertIn("No minors have been enrolled",self.guide)

    def test_independent_review_required_before_real_children(self):
        self.assertIn("teacher",self.guide.lower())
        self.assertIn("learner-rights/guardian reviewer",self.guide)
        self.assertIn("consent",self.guide)
        self.assertIn("code tests",self.guide.lower())

if __name__=="__main__":
    unittest.main()
