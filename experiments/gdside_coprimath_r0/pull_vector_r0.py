"""G_dSide pull-vector R0: explicitly plural, bounded, falsifiable backcasting.

This is a finite toy planning operator, not a revealed ideal, welfare oracle,
proof of real causality, or permission to act on people.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

MAX_HORIZON = 6
MAX_OBJECTIVES = 12
MAX_ACTIONS = 16

@dataclass(frozen=True)
class Objective:
    key: str
    unit: str
    target: float
    weight: float
    floor: float
    evidence_ref: str

@dataclass(frozen=True)
class Action:
    key: str
    cost: float
    effects: tuple[tuple[str, float], ...]
    evidence_ref: str
    rights_ok: bool = True

def assess(current: dict[str, float], objectives: tuple[Objective, ...],
           actions: tuple[Action, ...], *, horizon: int = 1,
           budget: float = 1.0, effect_reliability: float = 1.0) -> dict:
    """Compare candidate *expected* objective-distance changes.

    Effects are declared toy predictions; no true future is inferred.
    The baseline is no action, and 'G_dSide' is a label for a test lens only.
    """
    if not 1 <= horizon <= MAX_HORIZON or not 0 <= budget < 1e9:
        raise ValueError("BOUND_REQUIRED")
    if not 0 <= effect_reliability <= 1 or not isfinite(effect_reliability):
        raise ValueError("INVALID_RELIABILITY")
    if not 1 <= len(objectives) <= MAX_OBJECTIVES or len(actions) > MAX_ACTIONS:
        raise ValueError("BOUNDED_OBJECTS_REQUIRED")
    keys = [o.key for o in objectives]
    if len(keys) != len(set(keys)) or any(not o.key or not o.unit or not o.evidence_ref
            or o.key not in current or not all(isfinite(x) for x in
               (o.target,o.weight,o.floor,current[o.key])) or o.weight < 0
            for o in objectives):
        raise ValueError("INVALID_OBJECTIVE")
    if len({a.key for a in actions}) != len(actions):
        raise ValueError("DUPLICATE_ACTION")
    def distance(values):
        return sum(o.weight * max(0.0, o.target-values[o.key])
                   for o in objectives)
    baseline = distance(current)
    candidates = []
    for a in actions:
        if not a.key or not a.evidence_ref or not isfinite(a.cost) or a.cost < 0:
            raise ValueError("INVALID_ACTION")
        if len({k for k,_ in a.effects}) != len(a.effects):
            raise ValueError("DUPLICATE_EFFECT")
        if any(k not in keys or not isfinite(v) for k,v in a.effects):
            raise ValueError("UNBOUND_EFFECT")
        projected = dict(current)
        for key, delta in a.effects:
            projected[key] += delta*effect_reliability*horizon
        floor_ok = all(projected[o.key] >= o.floor for o in objectives)
        viable = a.rights_ok and a.cost <= budget and floor_ok
        improvement = baseline-distance(projected) if viable else None
        candidates.append({"action":a.key,"viable":viable,"expected_gain":improvement,
                           "rights_excluded":not a.rights_ok,
                           "source":a.evidence_ref, "cost":a.cost,
                           "uncertainty_unverified":True})
    # A zero-gain outcome is never forced to take action.
    viable = [x for x in candidates if x["viable"] and x["expected_gain"] > 0]
    best = sorted(viable,key=lambda x:(-x["expected_gain"],x["cost"],x["action"]))
    return {"baseline_distance":baseline,"candidates":candidates,
            "proposed_action":best[0]["action"] if best else None,
            "expected_gain":best[0]["expected_gain"] if best else 0.0,
            "effect_executed":False,"receiver_ack":False,
            "epistemic_class":"SYNTHETIC_DECLARED_EFFECTS_NOT_CAUSAL_PROOF"}

def fixture(*, misleading: bool = False) -> dict:
    objectives=(Objective("learning","competency points",80,1,0,"fixture:learning"),
                Objective("ecology","stock points",70,1,45,"fixture:ecology"),
                Objective("access","accessible percent",90,1,50,"fixture:access"))
    actions=(Action("teach",3,(("learning",20),("access",12)),"fixture:teach"),
             Action("extract",2,(("learning",15),("ecology",-30)),"fixture:extract"),
             Action("share",2,(("access",22),("learning",4)),"fixture:share"),
             Action("coerce",1,(("learning",100),),"fixture:coerce",rights_ok=False))
    current=dict(learning=55,ecology=60,access=58)
    if misleading:
        # Falsifier: a superficially attractive policy overstates gains.
        actions=(Action("hype",1,(("learning",100),("access",100)),"fixture:false-forecast"),)+actions
    return assess(current,objectives,actions,budget=3)
