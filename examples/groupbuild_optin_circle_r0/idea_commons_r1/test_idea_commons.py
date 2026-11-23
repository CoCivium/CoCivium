"""R1 source-only feedback and walk-away safety tests; no public inbox or effect."""
import json
from pathlib import Path
import re
import unittest

R=Path(__file__).resolve().parent
D=json.loads((R/"contract.json").read_text(encoding="utf-8"))
H=(R/"index.html").read_text(encoding="utf-8")
class IdeaCommonsTests(unittest.TestCase):
 def test_no_external_service(self):
  self.assertEqual(D["public_submission"],"NOT_CONNECTED")
  self.assertEqual(D["federation_delivery"],"NOT_CONNECTED")
 def test_no_real_people(self):
  self.assertEqual(D["real_submissions"],0)
  self.assertEqual(D["real_members"],0)
  self.assertEqual(D["real_assignments"],0)
 def test_no_effect(self): self.assertEqual(D["effect_authority"],"NONE")
 def test_no_ip_transfer(self): self.assertFalse(D["automatic_rights_transfer"])
 def test_three_views(self): self.assertEqual([v["id"] for v in D["views"]],["float","sketch","circle"])
 def test_all_views_honest(self): self.assertTrue(all(v["status"]!="LIVE" for v in D["views"]))
 def test_local_only_channel(self): self.assertEqual(D["channels"][0]["status"],"LOCAL_SAVE_BY_EXPLICIT_CLICK_ONLY")
 def test_export_not_delivery(self): self.assertIn("NOT_RECEIVER",D["channels"][1]["status"])
 def test_no_federation_claim(self): self.assertIn("NO_RECEIVER_CONNECTED",D["channels"][2]["status"])
 def test_bound_model(self):
  m=re.search(r'<script type="application/json" id="source-model">([\s\S]*?)</script>',H)
  self.assertIsNotNone(m)
  self.assertEqual(json.loads(m.group(1)),D)
 def test_input_bounded(self): self.assertIn('maxlength="500"',H)
 def test_no_automatic_upload(self):
  for item in ["fetch(", "XMLHttpRequest", "WebSocket(", "sendBeacon", "<form", "<script src=", "navigator.serviceWorker", "indexedDB"]:
   self.assertNotIn(item,H)
 def test_network_disabled(self): self.assertIn("connect-src 'none'",H)
 def test_explicit_local_save(self): self.assertIn('"save").addEventListener("click"',H)
 def test_explicit_export(self): self.assertIn('"export").addEventListener("click"',H)
 def test_explicit_clear(self): self.assertIn('"clear").addEventListener("click"',H)
 def test_no_click_to_join(self): self.assertNotIn("join(",H)
 def test_no_auto_save_on_input(self):
  self.assertNotIn("localStorage.setItem(key",H.split('$("idea").addEventListener("input"')[1])
 def test_no_preemptive_user_state(self): self.assertIn("let selected=\"float\", saved=false;",H)
 def test_export_unsent(self): self.assertIn('record("EXPORT_REQUESTED_UNSENT")',H)
 def test_project_sense(self): self.assertIn("One thought is enough",H)
 def test_no_assigned_work(self): self.assertIn("Not a job.",H)
 def test_optional_walkaway(self): self.assertIn("CoWalkAway+",H)
 def test_rickbar_not_runtime(self):
  item=next(x for x in D["candidate_terms"] if x["label"]=="rickbar.org")
  self.assertIn("UNVERIFIED",item["state"])
 def test_explicit_retention_disclosure(self): self.assertIn("stores only the current idea draft",H)
 def test_accessible_focus(self): self.assertIn("focus-visible",H)
 def test_reduced_motion(self): self.assertIn("prefers-reduced-motion",H)
 def test_no_hidden_persona(self): self.assertIn("Fictional UX",H)
 def test_lifecycle_separates_receipt(self): self.assertEqual(D["lifecycle"][-1]["id"],"RECEIVER_ACK")
 def test_source_bound(self): self.assertGreaterEqual(len(D["sources"]),7)
if __name__=="__main__": unittest.main()
