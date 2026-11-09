import unittest
from select import select as standard_select
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("cowave",Path(__file__).with_name("select.py"))
wave=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)

def c(i,front="A",method="test",substrate="browser",domain="one",v=.7,cost=.1,eligible=True):
    return {"id":i,"front":front,"method":method,"substrate":substrate,
            "failure_domain":domain,"evidence_target":"receiver-readproof",
            "expected_value":v,"cost":cost,"eligible":eligible}

class Tests(unittest.TestCase):
    def test_deterministic(self):
        pool=[c("a"),c("b","B","field","local","two")]
        self.assertEqual(wave.choose(pool,[],budget=2),wave.choose(pool,[],budget=2))
    def test_repeat_is_allowed_when_only_useful_option(self):
        x=c("recovery",v=.95)
        res=wave.choose([x],[("A","test","browser","one")],budget=1)
        self.assertEqual(res["selected_ids"],["recovery"])
        self.assertEqual(res["repeat_signatures"],1)
    def test_diversity_without_overriding_eligibility(self):
        pool=[c("x",eligible=False),c("y","B","field","local","two")]
        self.assertEqual(wave.choose(pool,[],budget=2)["selected_ids"],["y"])
    def test_protected_front_prioritized_and_uncovered_reported(self):
        pool=[c("a"),c("b","B"),c("c","C")]
        res=wave.choose(pool,[],budget=2,protected_fronts=("B","C","D"))
        self.assertEqual(set(res["protected_fronts_covered"]),{"B","C"})
        self.assertEqual(res["uncovered_protected_fronts"],["D"])
        self.assertEqual(res["effect_count"],0)
    def test_no_workers_no_hallucinated_success(self):
        res=wave.choose([],[],budget=3,protected_fronts=("A",))
        self.assertEqual(res["selected_ids"],[])
        self.assertEqual(res["uncovered_protected_fronts"],["A"])
    def test_duplicate_and_bad_budget_fail(self):
        with self.assertRaises(ValueError):
            wave.choose([c("x"),c("x")],[])
        with self.assertRaises(ValueError):
            wave.choose([],[],budget=-1)
    def test_budget_zero(self):
        self.assertEqual(wave.choose([c("x")],[],budget=0)["selected_ids"],[])
if __name__=="__main__":
    unittest.main()
