# CoSneak+ Bounded Local Census R0A

**State:** `PASS_BOUNDED_COSNEAK_CANDIDATE_CENSUS__CAUSALITY_UNPROVEN`

## Scope

A fresh read-only X2 census inspected two UX/currentness roots:

- `D:\CoCivium\CoStacks\RickBar`
- `D:\CoCivium\CoSteadLocalFacade\latest`

Observed at `2026-10-02T21:11:20Z`.

## Aggregate evidence

- total files: `265`
- files older than 30 days: `264`
- files with `LATEST` in the name: `216`
- `LATEST`-named files older than 30 days: `216`
- duplicate filename groups across the bounded roots: `0`

Exact local census receipt SHA-256:

`E6F7A20E6A94CA4CAC9BCD3325B02900E6B167F92BC376ABD173EB87563B5A4D`

The oldest RickBar-facing artifacts observed were roughly 175-184 days old. Examples include `status.json`, `rickbar.html`, `rickbar_live.html`, queue/intake/output `LATEST` files, runtime panel data, heartbeat/currentness tickers and the control view.

## Candidate CoSneak relations

The census supports candidate relations:

- `STALE_VISIBLE_CURRENTNESS`
- `LATEST_LABEL_WITH_OLD_CONTENT`
- `VISIBILITY_DEFICIT`

It does not by itself prove that every old file is harmful, obsolete, or causally responsible for perceived lag.

`STALE_FILE_NE_STALE_SEMANTIC_STATE`

`LATEST_LABEL_NE_CURRENTNESS_PROOF`

`AGE_NE_CAUSAL_BLOCKER`

## Strongest finding

The dominant candidate is not duplicate filename ambiguity. It is the mismatch between naming and currentness:

`LATEST` is being used as a filename convention even when the visible object is months old.

That is a classic CoSneak because it can quietly reduce trust and make stale state appear current without an explicit failure.

## Next

Do not mass-delete or rewrite these surfaces.

Prefer:

1. currentness metadata on every visible projection;
2. explicit `STALE` disclosure;
3. receiver pickup/readback proof;
4. supersession pointers;
5. retirement only after a fresher receiver is proven.

## Rails

`COSNEAK_NE_MALICE`  
`CANDIDATE_FRICTION_NE_CAUSAL_PROOF`  
`STALE_FILE_NE_STALE_SEMANTIC_STATE`  
`LATEST_LABEL_NE_CURRENTNESS_PROOF`  
`AGE_NE_CAUSAL_BLOCKER`  
`READONLY_CENSUS_NE_REPAIR`  
`NO_MASS_DELETE_FROM_STALENESS_CENSUS`  
`VALIDATION_IS_NOT_ACCEPTANCE`
