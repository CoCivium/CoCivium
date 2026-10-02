# CoCivium Resource Observer Projection R0

**State:** `CANDIDATE_OBSERVER_PROJECTION_RECEIVER__NO_COBAR_DELIVERY_NO_RUNTIME_ADOPTION`

## CoHereNow

PR137 already has a machine-readable resource interface and an exact GitHub-hosted receiver readproof.

The remaining visible-journey gap is not more resource ontology. It is a quiet CoCivium-facing projection that can eventually be consumed by CoBar without making Rick inspect schemas, workflow logs, or receipt ledgers.

This R0 adds exactly that bridge.

## Shape

```text
current PR137 resource-interface readproof
        ↓
GitHub Actions artifact
        ↓
distinct observer-projection receiver job
        ↓
exact receipt hash + head/time verification
        ↓
CoCivium observer projection payload
        ↓
GitHub Actions artifact
        ↓
future CoBar pickup / Rick-visible readback
```

The future CoBar step remains unproven here.

## Visible brand

The projection uses:

`VISIBLE_ROOT_BRAND = CoCivium`

Internal resource semantics may retain historical CoAll-labelled source paths for provenance, but the observer payload does not present CoAll as the visible root brand.

## Projection contract

The output provides, in order:

1. `CoHereNow`
2. `Meaning`
3. `NextSafeAction`
4. `Evidence`

It also binds:

- PR number;
- candidate branch;
- exact head SHA;
- exact commit time;
- source receiver identity;
- source receipt SHA-256;
- source exact-object blob SHAs;
- bounded lifecycle interpretation;
- UX acceptance state;
- nonclaims.

## Lifecycle

The source resource-interface receipt is first uploaded by the validation job.

The observer job downloads that exact artifact and verifies its receipt state, exact head, exact-object readproof, and `integration_state = UNPROVEN`.

A successful observer job therefore supports:

`PICKED_UP_BY_PR137_COCIVIUM_OBSERVER_PROJECTION_RECEIVER`

for that exact source receipt.

The generated observer projection becomes `LANDED` only after its own artifact upload succeeds.

No CoBar pickup, integration, runtime adoption, canon, or CoEx follows automatically.

## Current next safe action

After this candidate passes, the remaining high-value proof is:

```text
landed observer projection
-> current authorized local receiver
-> current CoBar projection
-> Rick-visible readback
```

with the same exact source head/time visible at the destination.

The current environment does not prove that local receiver route, so this R0 stops before it.

## Rails

`VISIBLE_ROOT_BRAND_IS_COCIVIUM`  
`OBSERVER_PROJECTION_NE_NEW_RESOURCE_ONTOLOGY`  
`SOURCE_RECEIPT_PICKUP_NE_RESOURCE_RUNTIME_ADOPTION`  
`PROJECTION_ARTIFACT_NE_COBAR_PICKUP`  
`COBAR_POINTER_NE_RICK_VISIBLE_READBACK`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`UX_ACCEPTANCE_UNPROVEN_UNTIL_VISIBLE_READBACK`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
