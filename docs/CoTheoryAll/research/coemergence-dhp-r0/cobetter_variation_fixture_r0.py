"""CoBetter R0 synthetic selection fixture: no execution authority, no external effects."""
from dataclasses import dataclass
import json
import random
import sys
import unittest

LANES = ("CHALLENGE", "EXPLORATION", "WEIRD")

@dataclass(frozen=True)
class Candidate:
    key: str
    lane: str
    rights_ok: bool
    consent_ok: bool
    evidence_ref: str
    proxy_gain: int
    optionality_delta: int
    harm_delta: int


def eligible(c):
    return c.rights_ok and c.consent_ok and bool(c.evidence_ref)


def pareto_dominates(a, b):
    """Comparison on comparable synthetic axes, never an ethics oracle."""
    axes_a = (a.proxy_gain, a.optionality_delta, -a.harm_delta)
    axes_b = (b.proxy_gain, b.optionality_delta, -b.harm_delta)
    return all(x >= y for x, y in zip(axes_a, axes_b)) and any(
        x > y for x, y in zip(axes_a, axes_b)
    )


def select_for_review(items, seed=11, budget=3):
    """Select descriptors for review only. NO_CHANGE is always present as a control."""
    if not isinstance(seed, int) or budget < 1 or budget > 5:
        raise ValueError("invalid sampling controls")
    keys = [x.key for x in items]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate IDs")
    for x in items:
        if x.lane not in LANES:
            raise ValueError("unknown lane")
    rng = random.Random(seed)
    admitted = [x for x in items if eligible(x)]
    by_lane = {lane: sorted((x for x in admitted if x.lane == lane), key=lambda x:x.key) for lane in LANES}
    chosen = []
    # Challenge and weird are protected, not rewarded by a fake universal score.
    for lane in LANES:
        if len(chosen) >= budget:
            break
        pool = by_lane[lane]
        if pool:
            chosen.append(rng.choice(pool))
    # No automatic effect. Unselected eligible items remain addressable.
    return {
        "control": "NO_CHANGE",
        "selected_for_review": [x.key for x in chosen],
        "eligible_not_selected": sorted(x.key for x in admitted if x not in chosen),
        "held": sorted(x.key for x in items if not eligible(x)),
        "seed": seed,
        "budget": budget,
        "effects": 0,
        "validated_benefit": False,
        "credential_issued": False
    }


def fixture():
    return [
        Candidate("challenge-stale-success", "CHALLENGE", True, True, "src:prior-test", 2, 4, 0),
        Candidate("explore-simple", "EXPLORATION", True, True, "src:uncertain", 6, 1, 0),
        Candidate("explore-harmful", "EXPLORATION", True, False, "src:uncertain", 90, -7, 10),
        Candidate("weird-a", "WEIRD", True, True, "src:speculation", 0, 5, 0),
        Candidate("weird-b", "WEIRD", True, True, "src:speculation", 1, 3, 0),
        Candidate("weird-no-rights", "WEIRD", False, True, "src:speculation", 99, 0, 0),
    ]


class Tests(unittest.TestCase):
    def test_replay(self):
        self.assertEqual(select_for_review(fixture(), 13), select_for_review(fixture(), 13))
    def test_order_invariance(self):
        self.assertEqual(select_for_review(fixture(), 13), select_for_review(list(reversed(fixture())), 13))
    def test_hard_gates(self):
        r=select_for_review(fixture(),13)
        self.assertTrue({"explore-harmful","weird-no-rights"}.issubset(set(r["held"])))
        self.assertFalse(set(r["held"]) & set(r["selected_for_review"]))
    def test_all_three_lanes(self):
        r=select_for_review(fixture(),13)
        self.assertEqual(len(r["selected_for_review"]),3)
        self.assertTrue(r["selected_for_review"][0].startswith("challenge"))
        self.assertTrue(r["selected_for_review"][1].startswith("explore"))
        self.assertTrue(r["selected_for_review"][2].startswith("weird"))
    def test_no_effects(self):
        r=select_for_review(fixture(),13)
        self.assertEqual(r["effects"], 0)
        self.assertFalse(r["validated_benefit"])
        self.assertFalse(r["credential_issued"])
    def test_no_favorite_score(self):
        a=Candidate("fast", "WEIRD",True,True,"src",20,-3,6)
        b=Candidate("slow", "WEIRD",True,True,"src",5,5,0)
        self.assertFalse(pareto_dominates(a,b))
        self.assertFalse(pareto_dominates(b,a))
    def test_dominance_synthetic_only(self):
        a=Candidate("a", "WEIRD",True,True,"src",4,4,0)
        b=Candidate("b", "WEIRD",True,True,"src",2,2,1)
        self.assertTrue(pareto_dominates(a,b))
    def test_missing_evidence_held(self):
        r=select_for_review([Candidate("undocumented","WEIRD",True,True,"",3,3,0)])
        self.assertEqual(r["selected_for_review"],[])
        self.assertEqual(r["held"],["undocumented"])
    def test_invalid_bounds(self):
        with self.assertRaises(ValueError):select_for_review(fixture(),budget=0)
        with self.assertRaises(ValueError):select_for_review(fixture(),seed="random")
    def test_duplicate_id(self):
        with self.assertRaises(ValueError):select_for_review(fixture()+[fixture()[0]])
    def test_seeded_variance_retained(self):
        variants={select_for_review(fixture(), seed=s)["selected_for_review"][-1] for s in range(40)}
        self.assertEqual(variants,{"weird-a","weird-b"})
    def test_zero_eligible_is_not_success(self):
        r=select_for_review([Candidate("vetoed","CHALLENGE",False,True,"src",100,100,-100)])
        self.assertEqual(r["selected_for_review"],[])
        self.assertFalse(r["validated_benefit"])


if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--json":
        print(json.dumps(select_for_review(fixture(),13),sort_keys=True,indent=2))
    else:
        unittest.main(verbosity=2)