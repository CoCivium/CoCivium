#!/usr/bin/env python3
"""Magic Workshop source-only conformance tests.

This file proves finite, local structural invariants; not browser accessibility,
independent human first-use, live GroupBuild service, consent or deployment.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "lexicon.json").read_text(encoding="utf-8"))
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
EXPECTED_STAGES = ["WISH","MAP","MAKE","TRY","GATE","GO","SEEN","GROW"]
EXPECTED_LENSES = ["kid","builder","philosopher","theologian"]

class MagicWorkshopR0Tests(unittest.TestCase):
    def stages(self):
        return {s["id"]:s for s in SPEC["stages"]}

    def test_identity_and_provenance(self):
        self.assertEqual(SPEC["work_id"],"GroupBuild.MagicWorkshop.CoTermables.20261123.R0")
        self.assertGreaterEqual(len(SPEC["provenance"]),5)
        self.assertTrue(all(x["path"] and len(x["blob"])==40 for x in SPEC["provenance"]))

    def test_embedded_model_is_exact_semantic_twin(self):
        m=re.search(r'<script type="application/json" id="workshop-data">([\s\S]*?)</script>',HTML)
        self.assertIsNotNone(m)
        self.assertEqual(json.loads(m.group(1)),SPEC)

    def test_stage_order(self):
        self.assertEqual([x["id"] for x in SPEC["stages"]],EXPECTED_STAGES)

    def test_stage_identity_unique(self):
        self.assertEqual(len(set(EXPECTED_STAGES)),len(EXPECTED_STAGES))

    def test_stage_explanations_complete(self):
        for stage in SPEC["stages"]:
            for key in ["label","truth","next","proof","type","act"]+EXPECTED_LENSES:
                self.assertIsInstance(stage[key],str)
                self.assertTrue(stage[key].strip())

    def test_three_acts_and_child_audience(self):
        self.assertEqual([a["id"] for a in SPEC["acts"]],["IMAGINE","WORKSHOP","WORLD"])
        self.assertEqual({s["act"] for s in SPEC["stages"]},set(a["id"] for a in SPEC["acts"]))
        self.assertTrue(all(s["kid"].strip() for s in SPEC["stages"]))

    def test_default_make_is_private(self):
        self.assertEqual(self.stages()["MAKE"]["type"],"PRIVATE_PREVIEW_ONLY")
        self.assertIn("not yet a public service",self.stages()["MAKE"]["truth"])

    def test_try_cannot_claim_user_acceptance(self):
        self.assertEqual(self.stages()["TRY"]["type"],"LOCAL_TEST_NOT_ACCEPTANCE")

    def test_gate_holds_effect(self):
        self.assertEqual(self.stages()["GATE"]["type"],"EFFECT_HELD_NOT_AUTHORIZED")
        self.assertIn("permission",self.stages()["GATE"]["truth"])

    def test_go_has_explicit_nonclaim(self):
        self.assertEqual(self.stages()["GO"]["type"],"EXTERNAL_EFFECT_REQUIRES_RECEIPT")
        self.assertIn("No effect occurred",self.stages()["GO"]["truth"])

    def test_receiver_not_merged_with_launch(self):
        self.assertEqual(self.stages()["SEEN"]["type"],"RECEIVER_READBACK_NOT_ADOPTION")
        self.assertIn("Independent receiver",self.stages()["SEEN"]["truth"])

    def test_real_outcomes_not_assumed(self):
        self.assertEqual(self.stages()["GROW"]["type"],"MEASURED_VALUE_NE_PERFECTION")
        self.assertIn("No success claim",self.stages()["GROW"]["truth"])

    def test_no_real_effects(self):
        for key in ["real_members","real_invites","real_publications","records_of_actual_first_use"]:
            self.assertEqual(SPEC[key],0)
        self.assertEqual(SPEC["effect_authority"],"NONE")

    def test_scenario_ids_unique_and_stages_known(self):
        ideas=SPEC["ideas"]
        self.assertEqual(len({i["id"] for i in ideas}),len(ideas))
        self.assertTrue(all(i["current"] in EXPECTED_STAGES for i in ideas))

    def test_three_audiences_in_every_scenario(self):
        for i in SPEC["ideas"]:
            self.assertTrue(i["kid"] and i["builder"] and i["philosopher"] and i["theologian"])
            self.assertTrue(i["next"])

    def test_game_and_institution_cases(self):
        classes=" ".join(i["class"] for i in SPEC["ideas"])
        self.assertIn("CoPlay",classes)
        self.assertIn("GroupBuild",classes)
        self.assertIn("Civ2+",classes)

    def test_exception_terms_no_effects(self):
        terms=SPEC["exception_terms"]
        self.assertGreaterEqual(len(terms),6)
        self.assertTrue(all(t["effect"]=="NONE" for t in terms))

    def test_all_names_not_canon(self):
        self.assertTrue(all(t["state"]!="CANON" for t in SPEC["term_candidates"]))
        self.assertEqual(len({t["name"] for t in SPEC["term_candidates"]}),len(SPEC["term_candidates"]))

    def test_collisions_held(self):
        by={t["name"]:t["state"] for t in SPEC["term_candidates"]}
        for name in ["CoGB+","CoInstaVyild+","CoGrouoByild+","CoWand+","IA"]:
            self.assertIn("HOLD",by[name])

    def test_source_vs_new_term(self):
        by={t["name"]:t["state"] for t in SPEC["term_candidates"]}
        self.assertEqual(by["GroupBuild+"],"EXISTING_SOURCE")
        self.assertEqual(by["CoInstaBuild+"],"WORKING_CANDIDATE")
        self.assertEqual(by["CoProof+"],"EXISTING_SOURCE")
        self.assertEqual(by["CoPoof+"],"WORKING_CANDIDATE")

    def test_ia_not_hijacked(self):
        label=next(t for t in SPEC["term_candidates"] if t["name"]=="IA")
        self.assertIn("MULTISENSE",label["state"])

    def test_poof_is_not_proof_rail(self):
        self.assertIn("POOF_NE_PROOF",SPEC["safety_rails"])
        self.assertIn("PREVIEW_NE_RELEASE",SPEC["safety_rails"])
        self.assertIn("PUBLIC_SITE_NE_HUMAN_ADOPTION",SPEC["safety_rails"])

    def test_html_unambiguous_public_nonclaims(self):
        self.assertIn("No accounts, real members, invitations",HTML)
        self.assertIn("Selecting a step only explains it.",HTML)
        self.assertIn("not saved, sent, verified, approved, or deployed",HTML)

    def test_browser_does_not_request_network_or_external_storage(self):
        for banned in ["fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket(", "<script src=", "localStorage", "sessionStorage", "indexedDB"]:
            self.assertNotIn(banned,HTML)

    def test_accessible_interaction_basics(self):
        for text in ['id="project"','id="toy-world"','id="toy-rule"','type="button" id="poof"','role="status"','aria-live="polite"','aria-pressed','<noscript>']:
            self.assertIn(text,HTML)

    def test_viewport_reduced_motion_and_csp(self):
        self.assertIn("viewport",HTML)
        self.assertIn("prefers-reduced-motion:reduce",HTML)
        self.assertIn("connect-src 'none'",HTML)
        self.assertIn("form-action 'none'",HTML)

    def test_buttons_do_not_advance_source_work_status(self):
        self.assertIn('explainId=s.id;render();',HTML)
        self.assertIn('const current=stageBy(story.current);',HTML)
        self.assertNotIn("story.current=",HTML)
        self.assertNotIn("stage.current=",HTML)

    def test_no_real_accounts_or_outbound_work(self):
        self.assertNotIn("<form",HTML)
        self.assertNotIn("window.location=",HTML)
        self.assertNotIn(".submit(",HTML)
        self.assertNotIn("navigator.sendBeacon",HTML)

if __name__=="__main__":
    unittest.main()
