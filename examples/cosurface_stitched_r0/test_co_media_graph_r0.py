"""Static fail-closed CoMediaGraph R0 source and representation boundaries."""
from pathlib import Path
import unittest
import json
G=json.loads(Path(__file__).with_name("co_media_graph_r0.json").read_text(encoding="utf-8"))
class CoMediaTests(unittest.TestCase):
 def test_unique_units(self):
  ids=[x["id"] for x in G["units"]]
  self.assertEqual(len(ids),len(set(ids)))
 def test_edges_resolve(self):
  ids={x["id"] for x in G["units"]}
  for e in G["relations"]:
   self.assertIn(e["from"],ids)
   self.assertIn(e["to"],ids)
 def test_no_inferred_symmetry(self):
  self.assertTrue(G["constraints"]["incoming_reference_not_reverse_fact"])
  self.assertTrue(all(e["direction"]=="DIRECTED" for e in G["relations"]))
 def test_hypotheses_not_source_proof(self):
  for e in G["relations"]:
   if e["confidence"]=="SPECULATIVE":self.assertIsNone(e["evidence"])
 def test_audio_is_opt_in(self):
  audio=next(x for x in G["units"] if x["id"]=="audio")
  self.assertEqual(audio["consent"],"EXPLICIT_OPT_IN")
  self.assertTrue(G["constraints"]["no_autoplay_audio"])
 def test_uncreated_film_not_claimed(self):
  video=next(x for x in G["units"] if x["id"]=="film")
  self.assertEqual(video["status"],"NOT_CREATED")
  self.assertIsNone(video["asset_digest_sha256"])
 def test_cultural_provenance_held(self):
  culture=next(x for x in G["units"] if x["id"]=="culture")
  self.assertEqual(culture["status"],"HYPOTHESIS")
  self.assertIsNone(culture["community_ref"])
  self.assertEqual(culture["consent_or_license"],"NOT_ESTABLISHED")
 def test_accessibility_and_rights_fences(self):
  for k in ("public_media_only_when_rights_proven","rich_media_survival_and_accessibility_required","no_private_chats"):
   self.assertTrue(G["constraints"][k])
 def test_receiver_not_inferred(self):
  self.assertIn("NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",G["nonclaims"])
 def test_draft_is_not_live(self):
  self.assertEqual(G["status"],"PUBLIC_SAFE_SYNTHETIC_EXAMPLE")
if __name__=="__main__": unittest.main()
