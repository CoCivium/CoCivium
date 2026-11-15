"""CoWave R0: coverage-preserving quality-diversity election.

Synthetic selection contract, not a live scheduler or an agent launcher.
A wave selects a bounded *portfolio of deeds*, not a compulsory change to
every front. Distinctiveness is a preference after proof, rights and recovery
constraints, never a requirement that would discard important maintenance.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Deed:
    deed_id: str
    front_id: str
    work_id: str
    source_revision: str
    method: str
    expected_evidence: str
    cost: int = 1
    collision_domain: str = ""
    authority: str = "READ_ONLY"
    blocked: str = ""
    priority: int = 1


@dataclass(frozen=True)
class Wave:
    wave_id: str
    deeds: Tuple[Deed, ...]


def features(deed):
    return frozenset((("front", deed.front_id), ("method", deed.method),
                      ("evidence", deed.expected_evidence)))


def similarity(first, second):
    a = set().union(*(features(d) for d in first.deeds))
    b = set().union(*(features(d) for d in second.deeds))
    return len(a & b) / len(a | b) if a or b else 1.0


def choose_wave(candidates, previous, *, max_deeds=3, max_cost=5,
                continuity_fronts=()):
    """Rank proof-safe distinct work; return explicit holds for ineligible work."""
    if max_deeds < 1 or max_cost < 1:
        raise ValueError("positive bounded election required")
    last = previous[-1] if previous else Wave("none", ())
    previous_fronts = {d.front_id for wave in previous for d in wave.deeds}
    selected, held, domains, work_ids, spent = [], [], set(), set(), 0
    def score(deed):
        prior_features = set().union(*(features(d) for d in last.deeds))
        novelty = len(features(deed) - prior_features)
        first_coverage = 1 if deed.front_id not in previous_fronts else 0
        required = 1 if deed.front_id in continuity_fronts else 0
        return (-required, -first_coverage, -deed.priority, -novelty, deed.cost, deed.deed_id)
    for deed in sorted(candidates, key=score):
        if not all((deed.deed_id, deed.front_id, deed.work_id,
                    deed.source_revision, deed.method, deed.expected_evidence)):
            held.append((deed.deed_id, "MISSING_EVIDENCE_POINTER"))
        elif deed.blocked:
            held.append((deed.deed_id, "BLOCKED:" + deed.blocked))
        elif deed.authority not in ("READ_ONLY", "REVERSIBLE"):
            held.append((deed.deed_id, "AUTHORITY_GATE"))
        elif not deed.collision_domain:
            held.append((deed.deed_id, "UNKNOWN_COLLISION_DOMAIN"))
        elif deed.collision_domain in domains or deed.work_id in work_ids:
            held.append((deed.deed_id, "DUPLICATE_EFFECT_HOLD"))
        elif len(selected) >= max_deeds or spent + deed.cost > max_cost:
            held.append((deed.deed_id, "BUDGET_OR_CAPACITY_HOLD"))
        else:
            selected.append(deed)
            domains.add(deed.collision_domain)
            work_ids.add(deed.work_id)
            spent += deed.cost
    current = Wave("synthetic-next", tuple(selected))
    return {
        "wave": current,
        "holds": tuple(held),
        "used_cost": spent,
        "novelty_vs_previous": 1.0 - similarity(current, last) if selected and last.deeds else None,
        "no_worker_execution_claimed": True,
        "uncovered_required_fronts": tuple(sorted(set(continuity_fronts)
                                                  - {d.front_id for d in selected})),
    }
