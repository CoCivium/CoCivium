"""CoBudgetNeedles synthetic forecasting and anti-self-funding controls."""
import copy
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from budget_needles_r0 import NEEDLES,NONCLAIMS,check_budget,apply_needle,insertion_deficits,compare
from allocator import plan
import json

DATA=json.loads((pathlib.Path(__file__).resolve().parent/"fixture.json").read_text("utf-8"))

class NeedleTests(unittest.TestCase):
    def bad(self,needle,reason):
        with self.assertRaisesRegex(ValueError,reason):
            apply_needle(DATA["budget"],DATA["candidates"],needle)
    def test_baseline_exact(self):
        b=DATA["budget"]
        self.assertEqual(set(check_budget(b)),set(("cash_cents","cpu_units","energy_units","human_minutes","reviewer_minutes","worker_slots")))
    def test_bad_budget_negative(self):
        x=copy.deepcopy(DATA["budget"]);x["cpu_units"]=-1
        with self.assertRaises(ValueError):check_budget(x)
    def test_bad_budget_bool(self):
        x=copy.deepcopy(DATA["budget"]);x["cpu_units"]=True
        with self.assertRaises(ValueError):check_budget(x)
    def test_bad_budget_unlisted_dimension(self):
        x=copy.deepcopy(DATA["budget"]);x["imaginary_universe"]=999
        with self.assertRaises(ValueError):check_budget(x)
    def test_nonmutation(self):
        before=copy.deepcopy(DATA)
        apply_needle(DATA["budget"],DATA["candidates"],NEEDLES[0])
        self.assertEqual(DATA,before)
    def test_no_cash_generation(self):
        n={"id":"money","mode":"supply","resource":"cash_cents","delta":1,"reason":"wish"}
        self.bad(n,"CASH_OR_HUMAN_CAPACITY_HELD")
    def test_no_human_time_generation(self):
        n={"id":"time","mode":"supply","resource":"human_minutes","delta":1,"reason":"wish"}
        self.bad(n,"CASH_OR_HUMAN_CAPACITY_HELD")
    def test_no_unknown_resource(self):
        n={"id":"galaxies","mode":"supply","resource":"galaxies","delta":1,"reason":"wish"}
        self.bad(n,"CASH_OR_HUMAN_CAPACITY_HELD")
    def test_negative_forecast(self):
        self.bad({**NEEDLES[0],"delta":-1},"BAD_FORECAST_DELTA")
    def test_zero_forecast(self):
        self.bad({**NEEDLES[0],"delta":0},"BAD_FORECAST_DELTA")
    def test_boolean_forecast(self):
        self.bad({**NEEDLES[0],"delta":True},"BAD_FORECAST_DELTA")
    def test_unbounded_forecast(self):
        self.bad({**NEEDLES[0],"delta":1000000},"BAD_FORECAST_DELTA")
    def test_undeclared_spend_authority(self):
        self.bad({**NEEDLES[0],"permission":"SPEND"},"UNDECLARED_FORECAST_FIELD")
    def test_wrong_forecast_mode(self):
        self.bad({**NEEDLES[0],"mode":"activate"},"UNKNOWN_MODE")
    def test_unknown_cost_target(self):
        self.bad({**NEEDLES[-1],"target":"no-such-task"},"UNBOUND_EFFICIENCY_TARGET")
    def test_negative_unit_cost(self):
        self.bad({**NEEDLES[-1],"delta":19},"BAD_EFFICIENCY_FLOOR")
    def test_budget_growth_is_hypothetical(self):
        b,c=apply_needle(DATA["budget"],DATA["candidates"],NEEDLES[0])
        self.assertEqual(b["cpu_units"],DATA["budget"]["cpu_units"]+5)
        self.assertEqual(DATA["budget"]["cpu_units"],14)
        self.assertEqual(DATA["budget"]["cash_cents"],0)
    def test_cache_reduces_cost_not_budget(self):
        b,c=apply_needle(DATA["budget"],DATA["candidates"],NEEDLES[-1])
        orig=next(x for x in DATA["candidates"] if x["work_id"]=="fresh_source_retrieval")
        new=next(x for x in c if x["work_id"]=="fresh_source_retrieval")
        self.assertEqual(b,DATA["budget"])
        self.assertEqual(new["resources"]["cpu_units"],orig["resources"]["cpu_units"]-2)
    def test_return_is_not_spendable(self):
        r=compare(DATA)
        self.assertEqual(r["live_budget_increase"],0)
        self.assertEqual(r["cash_spent_cents"],0)
        self.assertEqual(r["new_workers_started"],0)
        self.assertEqual(r["current_known_budget_source"],"SYNTHETIC_FIXTURE_NOT_LIVE_INVENTORY")
        self.assertEqual(r["empirical_efficiency_improvement"],"NOT_MEASURED")
    def test_all_needles_have_source_hypotheses(self):
        self.assertTrue(all(f["hypothesis"] and f["forecast_only"] and f["observed_new_resource"]=="NOT_OBSERVED" for f in compare(DATA)["forecast_cases"]))
    def test_no_budget_leak(self):
        r=compare(DATA)
        self.assertEqual(r["baseline_budget"]["human_minutes"],0)
        self.assertEqual(r["joint_forecast"]["budget_if_all_available"]["cash_cents"],0)
        self.assertEqual(r["joint_forecast"]["budget_if_all_available"]["human_minutes"],0)
    def test_all_forecast_scores_at_least_baseline(self):
        r=compare(DATA)
        self.assertTrue(all(x["projected_gain"]>=0 for x in r["forecast_cases"]))
    def test_forecast_recomputed(self):
        r=compare(DATA)
        for n,v in zip(NEEDLES,r["forecast_cases"]):
            b,c=apply_needle(DATA["budget"],DATA["candidates"],n)
            self.assertEqual(plan(c,b)["projected_utility_score_pctpoints"],v["projected_score"])
    def test_deficit_diagnostics_types(self):
        r=compare(DATA)
        for item in r["insertion_deficits_not_shadow_prices"].values():
            self.assertTrue(all(x in DATA["budget"] and v>0 for x,v in item["resource_deficits"].items()))
            self.assertIsInstance(item["collision_with_selected"],bool)
    def test_no_global_shadow_price_claim(self):
        self.assertIn("SINGLE_NEEDLE_NE_ENTIRE_BOTTLENECK",NONCLAIMS)
        self.assertIn("FORECAST_NE_LEASE_OR_AUTHORIZATION",NONCLAIMS)
    def test_deterministic(self):
        self.assertEqual(compare(DATA),compare(DATA))
    def test_empty_candidate_fixture(self):
        f={"budget":copy.deepcopy(DATA["budget"]),"candidates":[]}
        # Named cache target isn't present; must fail rather than invent source.
        with self.assertRaisesRegex(ValueError,"UNBOUND_EFFICIENCY_TARGET"):compare(f)
    def test_source_not_authority(self):
        self.assertIn("CASH_BUDGET_NE_SPENDING_AUTHORITY",NONCLAIMS)
        self.assertIn("ZERO_HUMAN_MINUTES_NE_ABSENCE_OF_GOVERNANCE",NONCLAIMS)
if __name__=="__main__":unittest.main()
