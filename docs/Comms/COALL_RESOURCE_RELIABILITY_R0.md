# CoAll Resource Reliability R0

**State:** `CANDIDATE__SYNTHETIC_RELIABILITY_POLICY__NO_PERSON_RANKING_NO_RUNTIME_AUTHORITY`

## Purpose

CoAll may learn that a particular contributed resource is more or less reliable for a bounded class of work without converting that observation into social rank, truth weight, governance power, or generalized trust in the contributor.

The intended object is a resource-scoped evidence profile, not a reputation score for a person.

`RESOURCE_REPUTATION_NE_PERSON_REPUTATION`

`TRUSTED_RESOURCE_NE_TRUSTED_OWNER_FOR_ALL_SCOPE`

## Resource reliability profile

A candidate `CoResourceReliability+` SHOULD bind:

- exact grant ID;
- exact resource ID;
- resource class;
- task class / purpose;
- observation window;
- attempts;
- completed attempts;
- receipt completeness;
- invariant preservation;
- failure count and failure classes;
- stale/currentness failures;
- latency / availability where relevant;
- declared loss;
- receiver verification;
- confidence;
- evidence refs;
- valid-from / valid-to;
- revocation state.

No scalar "good participant" score is implied.

## Routing use

Reliability evidence MAY influence resource selection only inside the same bounded task/resource scope where the evidence is relevant.

Examples:

- a storage mirror that repeatedly returns exact bytes may become preferred for public artifact replication;
- a compute worker that repeatedly preserves invariants may be preferred for the same canary class;
- a translator with verified domain-specific review receipts may be preferred for that language/domain pair.

It MUST NOT imply:

- governance authority;
- correctness outside the measured scope;
- personal trustworthiness;
- truth weight;
- moral merit;
- eligibility for unrelated private data;
- authority to act without an active grant.

`RELIABILITY_NE_AUTHORITY`

`RELIABILITY_NE_TRUTH`

`LOCAL_RELIABILITY_NE_GLOBAL_TRUST`

`PAST_SUCCESS_NE_FUTURE_PERMISSION`

## Diversity guard

A scheduler SHOULD avoid collapsing all work onto the numerically highest reliability profile when that would create correlated failure, capture, monoculture, privacy concentration, or single-owner dependency.

Selection may consider:

- reliability;
- current availability;
- failure-domain diversity;
- ownership diversity;
- locality;
- privacy compatibility;
- cost / energy;
- current load;
- recency of evidence;
- declared task requirements.

`BEST_SCORE_NE_ONLY_ROUTE`

`RELIABILITY_OPTIMIZATION_NE_MONOCULTURE`

## Decay and currentness

Reliability evidence expires or decays in usefulness as:

- software or model versions change;
- hardware changes;
- network conditions change;
- grant scope changes;
- the task class changes;
- long periods pass without verification.

`HISTORICAL_RELIABILITY_NE_CURRENT_RELIABILITY`

A stale profile MAY remain provenance, but SHOULD NOT dominate routing until refreshed.

## Revocation

If the underlying grant is paused, revoked, or expired, reliability does not keep the resource eligible.

`RELIABILITY_NE_ACTIVE_GRANT`

`REVOKED_RESOURCE_NE_ROUTABLE_BECAUSE_REPUTATION_HIGH`

## Fairness

Resource contribution and reliable performance do not buy control.

`RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY`

`RELIABILITY_NE_VOTING_POWER`

`RESOURCE_REPUTATION_NE_SOCIAL_RANK`

The system SHOULD expose enough evidence for a contributor to understand why a resource was selected or not selected without exposing unrelated participant data.

## First safe canary

A synthetic canary SHOULD prove:

1. a higher-reliability resource may be preferred for a matching task;
2. a revoked high-reliability resource is excluded;
3. a high score in one task class does not transfer to an unrelated task class;
4. two independently owned resources may both remain eligible to preserve failure-domain diversity;
5. governance weight remains zero regardless of reliability score.

No real contributor ranking or runtime resource election is authorized by R0.
