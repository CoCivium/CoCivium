"""Cold-successor packet must be a pointer, never a simulated ACK."""
import json
import re
import unittest
from pathlib import Path
P=json.loads(Path(__file__).with_name("copre_cold_successor_packet_r0.json").read_text(encoding="utf-8"))
class ColdSuccessorPacketTests(unittest.TestCase):
 def test_source_commit_immutable_form(self):
  self.assertRegex(P["source"]["commit_sha"],r"^[0-9a-f]{40}$")
 def test_draft_not_pickup(self):
  self.assertIn("RECEIVER_NOT_ACKED",P["state"])
  self.assertIsNone(P["receiver"]["actor_id"])
  self.assertFalse(P["receiver"]["independent_fetch"])
  self.assertIsNone(P["receiver"]["durable_ack_uri"])
 def test_no_fake_mirrors(self):
  self.assertEqual(len(P["targets"]),3)
  for x in P["targets"]:
   self.assertIsNone(x["sha256"])
   self.assertIsNone(x["receiver_ack"])
   self.assertIn("NOT_QUALIFIED",x["status"])
 def test_no_fake_24h_or_schedule(self):
  self.assertIsNone(P["seed_survival"]["observed_hours"])
  self.assertFalse(P["seed_survival"]["verified_over_24h"])
  self.assertFalse(P["system_owned_sync"]["observed_run"])
  self.assertIsNone(P["system_owned_sync"]["human_relay_count"])
 def test_diverse_lanes_distinct(self):
  lanes=[x["lane"] for x in P["roles"]]
  self.assertEqual(len(lanes),len(set(lanes)))
  self.assertGreaterEqual(len(lanes),3)
 def test_cold_start_dedup(self):
  s=" ".join(P["fresh_start"]).lower()
  self.assertIn("dedupe",s)
  self.assertIn("pinned",s)
 def test_safety_boundary(self):
  s=json.dumps(P)
  self.assertIn("NO_HIDDEN_CAPTURE",s)
  self.assertIn("NO_SELF_DECLARED_ACK",s)
  self.assertIn("NO_CHILD_LABOUR_OR_INFERRED_CONSENT",s)
 def test_target_refs_are_literal_expected_destinations(self):
  self.assertEqual({x["uri"] for x in P["targets"]},{"https://github.com/CoCivium/CoPreGeneric","https://CoCivium.org/CoPre","https://InSeed.com/Stead"})
 def test_unknown_not_zero(self):
  self.assertIn("UNKNOWN_NE_ZERO",P["nonclaims"])
if __name__=="__main__":unittest.main()
