"""CoRegenerative+ R0: offline, unitless feedback-loop *illustration*.

No people, networks, devices, data sources, or AI runtimes are touched.
Numbers are synthetic and cannot be construed as observed audience or physical energy.
"""
from dataclasses import dataclass, asdict
from math import isfinite


@dataclass(frozen=True)
class State:
    useful: float = 8.0
    reserve: float = 25.0
    capacity: float = 25.0
    cumulative_spend: float = 0.0


@dataclass(frozen=True)
class Offer:
    label: str
    quality: float
    risk: float
    consent: bool = True
    current: bool = True
    public_source: bool = True
    attention: float = 0.0


@dataclass(frozen=True)
class Policy:
    retention: float = 0.92
    capacity_retention: float = 0.995
    capacity_per_spend: float = 2.5
    capacity_limit: float = 110.0
    spend_cap: float = 4.0
    benefit_per_spend: float = 2.0
    reserve_from_benefit: float = 0.5  # voluntary social reinvestment assumption
    quality_floor: float = 0.7
    risk_ceiling: float = 0.2


def _validate(state, offer, policy, external_inflow):
    for value in list(asdict(state).values()) + [offer.quality, offer.risk, offer.attention, external_inflow] + list(asdict(policy).values()):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError('NONFINITE_OR_INVALID_NUMERIC')
    if min(asdict(state).values()) < 0 or external_inflow < 0 or offer.attention < 0:
        raise ValueError('NEGATIVE_RESOURCES')
    for v in (offer.quality, offer.risk, policy.retention, policy.capacity_retention,
              policy.reserve_from_benefit, policy.quality_floor, policy.risk_ceiling):
        if not 0 <= v <= 1:
            raise ValueError('RATE_OUT_OF_RANGE')
    if any(v < 0 for v in (policy.capacity_per_spend, policy.capacity_limit, policy.spend_cap, policy.benefit_per_spend)):
        raise ValueError('NEGATIVE_POLICY')
    if state.capacity > policy.capacity_limit:
        raise ValueError('CAPACITY_EXCEEDS_LIMIT')


def tick(state: State, offer: Offer, policy: Policy = Policy(), external_inflow=0.0, mode='evidence'):
    """Bounded synthetic transition with an explicitly *held* status.

    mode='attention' is a deliberately poor comparison strategy, never a recommendation.
    Benefits converting to reserves models *opt-in human reinvestment*, not free energy.
    """
    _validate(state, offer, policy, external_inflow)
    if mode not in ('evidence', 'attention'):
        raise ValueError('UNKNOWN_MODE')
    authorized = offer.consent and offer.current and offer.public_source
    eligible = authorized and offer.quality >= policy.quality_floor and offer.risk <= policy.risk_ceiling
    if mode == 'evidence':
        approved = eligible
    else:
        # Intentionally naive challenger: clicks cannot override consent/currentness/privacy.
        approved = authorized and offer.attention > 0
    spend = min(state.reserve, policy.spend_cap) if approved else 0.0
    produced = spend * policy.benefit_per_spend * offer.quality
    capacity = min(policy.capacity_limit, state.capacity * policy.capacity_retention + spend * policy.capacity_per_spend)
    useful = min(capacity, state.useful * policy.retention + produced)
    reserve = state.reserve - spend + external_inflow + produced * policy.reserve_from_benefit
    # risk is a qualitative hold gate. This is NOT a calibrated quantitative harm model.
    result = State(round(useful, 8), round(reserve, 8), round(capacity, 8), round(state.cumulative_spend+spend, 8))
    reason = ('INVEST' if spend > 0 else ('HELD_NO_PERMISSION_OR_CURRENT_SOURCE' if not authorized else
               'HELD_LOW_VERIFICATION_OR_HIGH_RISK' if not eligible else 'HELD_NO_RESERVE'))
    return result, {'reason':reason, 'spend':round(spend,8), 'produced':round(produced,8),
                    'quality':offer.quality, 'risk':offer.risk, 'authorized':authorized,
                    'accepted':eligible and spend > 0}


def simulate(state, offer, policy=Policy(), external_inflow=0.0, turns=24, mode='evidence'):
    if type(turns) is not int or not 0 <= turns <= 1000:
        raise ValueError('BOUNDED_TURNS_ONLY')
    records=[]
    for i in range(turns):
        before=state
        state, detail=tick(state,offer,policy,external_inflow,mode)
        records.append({'turn':i+1,'before':asdict(before),'after':asdict(state),'decision':detail})
    return records


def qualify_highlight(asset, declared_goal):
    """Source-link candidates only. Never infer identity, publish, or grant authority."""
    if not isinstance(asset,dict) or declared_goal not in ('default','words','relationships','civic','build','play'):
        raise ValueError('INVALID_ROUTE')
    if asset.get('source_state')!='GITHUB_BLOB_VERIFIED' or asset.get('privacy')!='PUBLIC' or asset.get('requires_registration'):
        return {'status':'HELD', 'reason':'UNQUALIFIED_SOURCE_OR_PRIVACY'}
    if asset.get('independent_first_use') is not None:
        # This sample does not collect or verify user outcomes.
        return {'status':'HELD', 'reason':'UNKNOWN_EXTERNAL_OUTCOME_SCHEMA'}
    score = int(asset.get('goal')==declared_goal)+int(declared_goal=='default' and asset.get('goal')=='default')
    return {'status':'CANDIDATE_SOURCE_ONLY','rank':score,'reason':'NO_INDEPENDENT_USER_OUTCOME'}
