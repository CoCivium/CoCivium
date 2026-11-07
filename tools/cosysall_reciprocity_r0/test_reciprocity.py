import copy
import unittest
from reciprocity import Held, make_proposal, project, qualify_graph

GRAPH={"schema":"CoAll.CoMapProjection.R0", "state":"PUBLIC_SOURCE_BOUND_PROJECTION_NOT_CANON_OR_RUNTIME",
"sources":[{"id":"source:ai/evolution-lanes.json","url":"https://github.com/CoCivium/CoCivium/blob/main/ai/evolution-lanes.json"}],
"nodes":[{"id":"domain:CoStrategy+","label":"CoStrategy+","kind":"domain","source":"source:ai/evolution-lanes.json"},
{"id":"repo:CoCivium/MasterPlan","label":"MasterPlan","kind":"repository","source":"source:ai/evolution-lanes.json"},
{"id":"repo:CoCivium/CoCivium","label":"CoCivium","kind":"repository","source":"source:ai/evolution-lanes.json"}],
"edges":[{"id":"e1","from":"domain:CoStrategy+","to":"repo:CoCivium/MasterPlan","relation":"REGISTERED_REPOSITORY","source":"source:ai/evolution-lanes.json","state":"SOURCE_REGISTERED"},
{"id":"e2","from":"domain:CoStrategy+","to":"repo:CoCivium/CoCivium","relation":"REGISTERED_REPOSITORY","source":"source:ai/evolution-lanes.json","state":"SOURCE_REGISTERED"}]}
ARGS=("repo:CoCivium/MasterPlan","domain:CoStrategy+","repo:CoCivium/CoCivium","e1","e2","local:test","2026-11-07T02:53:30Z")

class Contract(unittest.TestCase):
 def test_qualified_source(self):self.assertEqual(len(qualify_graph(GRAPH)),3)
 def test_project_source_links(self):
  x=project(GRAPH,"domain:CoStrategy+","machine",1)
  self.assertEqual(x["eligible_neighbors"],2)
  self.assertEqual(x["truncated_relations"],1)
  self.assertEqual(x["actual_draw_calls"],0)
  self.assertFalse(x["grants_effect_authority"])
 def test_none_render(self):
  x=project(GRAPH,"domain:CoStrategy+","none")
  self.assertEqual(x["planned_visible_nodes"],0)
  self.assertEqual(x["relations"],[])
  self.assertEqual(x["network_fetches"],0)
 def test_source_to_proposal(self):
  x=make_proposal(GRAPH,*ARGS)
  self.assertEqual(x["mutation_class"],"PROPOSE")
  self.assertEqual(x["epistemic_class"],"HYPOTHESIS")
  self.assertEqual(x["authority_ceiling"],"NO_EXTERNAL_EFFECTS__REVIEW_ONLY")
  self.assertIn("e1",x["tests"][0])
 def test_bad_proposed_edge(self):
  with self.assertRaises(Held):make_proposal(GRAPH,*ARGS[:3],"forged","e2",*ARGS[5:])
 def test_bad_path(self):
  with self.assertRaises(Held):make_proposal(GRAPH,ARGS[0],ARGS[2],ARGS[1],*ARGS[3:])
 def test_bad_time(self):
  with self.assertRaises(Held):make_proposal(GRAPH,*ARGS[:-1],"2026-11-07")
 def test_missing_schema(self):
  g=copy.deepcopy(GRAPH);g["state"]="LIVE_ALL_RECEIVERS_ACKED"
  with self.assertRaises(Held):qualify_graph(g)
 def test_orphan_relation(self):
  g=copy.deepcopy(GRAPH);g["edges"][0]["to"]="not-real"
  with self.assertRaises(Held):qualify_graph(g)
 def test_source_spoof(self):
  g=copy.deepcopy(GRAPH);g["edges"][0]["source"]="not-real"
  with self.assertRaises(Held):qualify_graph(g)
 def test_private_payload(self):
  g=copy.deepcopy(GRAPH);g["nodes"][1]["confidentiality"]="PRIVATE"
  with self.assertRaises(Held):make_proposal(g,*ARGS)
 def test_private_neighbor_not_rendered(self):
  g=copy.deepcopy(GRAPH);g["nodes"][1]["confidentiality"]="PRIVATE"
  x=project(g,"domain:CoStrategy+")
  self.assertEqual(x["eligible_neighbors"],1)
  self.assertNotIn("repo:CoCivium/MasterPlan",[n["id"] for n in x["nodes"]])
 def test_invalid_budget(self):
  with self.assertRaises(Held):project(GRAPH,"domain:CoStrategy+",limit=-1)
 def test_budget_zero_hides_all(self):
  x=project(GRAPH,"domain:CoStrategy+",limit=0)
  self.assertEqual(x["planned_visible_nodes"],0)
  self.assertEqual(x["nodes"],[])
 def test_candidate_source_not_fact(self):
  g=copy.deepcopy(GRAPH);g["edges"][0]["state"]="CANDIDATE"
  with self.assertRaises(Held):make_proposal(g,*ARGS)
 def test_no_surface_authority(self):
  with self.assertRaises(Held):project(GRAPH,"domain:CoStrategy+",surface="EXECUTE")
 def test_duplicate_ids(self):
  g=copy.deepcopy(GRAPH);g["nodes"].append(copy.deepcopy(g["nodes"][0]))
  with self.assertRaises(Held):qualify_graph(g)

if __name__=='__main__': unittest.main()