# CoSessionSubscription+ R0

**State:** `PUBLIC_BOOTSTRAP_ROUTING__NO_GLOBAL_CONTENT_PUSH`

The shared evolution fabric is useful only if sessions can stay current **without ingesting all of CoAll**.

CoSessionSubscription+ defines receiver-relative HOT/WARM/DIGEST/SLEEP relationships between a session role and evolving domains.

## Temperatures

- **HOT** — read current deltas before material work; likely mutation/challenge target.
- **WARM** — inspect when dependencies, contradictions, or currentness indicate relevance.
- **DIGEST** — receive compact summaries/highlights rather than raw lane traffic.
- **SLEEP** — do not ingest by default; retain wake relations.

Temperature is role-relative and may change through CoTime+.

`HOT_NE_IMPORTANT_FOR_EVERYONE`

## Bootstrap rule

A new or reconstructed session should:

`identify role/profile -> read SESSION_BOOTSTRAP -> load matching subscription profile -> resolve current domain pointers -> bind only needed objects -> work -> emit bounded CoEvoDelta+`

Do not clone or ingest every repository merely to become “current.”

`FULL_REPO_INGEST_NE_BOOTSTRAP`

## Subscription and authority

A subscription grants **attention/currentness**, not mutation authority.

A HOT lane may still be read-only for a session whose authority ceiling does not permit writes.

`SUBSCRIPTION_NE_AUTHORITY`

## Profile evolution

Profiles are defaults, not castes.

A session may:

- add a temporary HOT relation because a contradiction crosses domains;
- cool a lane when work externalizes;
- inherit a successor profile;
- split into specialist virtual sessions;
- receive digest-only projections under CoPressure+;
- sleep almost entirely while retaining exact wake predicates.

## CoPressure

When fan-in/currentness load rises, first reduce raw subscriptions and increase compaction/digests. Do not spawn more live sessions merely to consume the extra notifications.

`PRESSURE_NE_SPAWN_PERMISSION`

## Current profile set

The machine registry currently seeds:

- CoTheory
- CoLanguage
- CoUX
- CoOps
- CoIndex
- CoFuture
- CoPublic
- CoHumour
- CoGeneralist

The registry is intentionally extensible.

## R0A — virtual-session profile binding

A virtual-session record may now carry an optional `subscription_profile_binding` relation:

`profile_id | registry_ref | registry_blob_sha | observed_at`

This is deliberately separate from the existing `subscriptions[]` field.

- `subscription_profile_binding` identifies the profile source and, when available, the exact registry blob observed by the receiver.
- `subscriptions[]` remains the receiver-specific effective domain binding carried by that virtual-session record.
- a profile binding may be absent for legacy, synthetic, or deliberately unprofiled sessions;
- a profile binding does not grant mutation authority;
- a newer registry blob does not silently rewrite an already-bound virtual session;
- rebinding should be explicit when profile currentness materially changes.

`PROFILE_BINDING_NE_AUTHORITY`  
`PROFILE_ID_NE_EFFECTIVE_SUBSCRIPTIONS`  
`NEWER_PROFILE_REGISTRY_NE_SILENT_REBIND`  
`BOUND_PROFILE_NE_GLOBAL_CONTENT_PUSH`

## Next

Compile one bounded virtual-session fixture from an exact profile binding and effective `subscriptions[]`, then route only the receiver-specific delta packet through a CoAllPulseField-compatible delivery object or equivalent bounded currentness carrier.

Do not infer a live event bus, provider push, or runtime adoption from the schema relation.

`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`  
`SLEEP_NE_IGNORE_FOREVER`  
`PROFILE_BINDING_NE_LIVE_DELIVERY`
