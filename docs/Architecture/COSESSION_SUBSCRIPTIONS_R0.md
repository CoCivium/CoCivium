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

## Next

Bind these profiles into virtual-session records and CoAllPulseField delivery so the control plane can compute receiver-specific delta packets.

`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`  
`SLEEP_NE_IGNORE_FOREVER`
