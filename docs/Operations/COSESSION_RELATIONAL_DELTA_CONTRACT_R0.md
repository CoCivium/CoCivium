# CoSession Relational Delta Projection R0

**State:** `PUBLIC_CANDIDATE__SESSION_PROJECTION_OF_COEVO__NOT_PARALLEL_SEMANTIC_STANDARD`

## Purpose

Every useful CoCivium session should be able to return bounded relational deltas to the shared evolution fabric without carrying the whole project or receiving blanket mutation authority.

The canonical shared evolution object already exists: **CoEvoDelta+**, defined by `docs/Evolution/COALL_GITHUB_EVOLUTION_FABRIC_R0.md` and `schemas/coevo-delta-v0.1.schema.json`.

**CoSessionRelationalDelta is a session/receiver projection of CoEvoDelta+, not a competing semantic standard.**

`COSESSION_RELATIONAL_DELTA_IS_COEVO_PROJECTION_NE_PARALLEL_SEMANTIC_STANDARD`

## Why this projection exists

The session projection adds receiver-facing and fan-in mechanics that are useful at the provider/session edge:

- a compact list of typed operations;
- explicit public-safety qualification;
- collision-domain qualification;
- observed base/currentness binding;
- next gate and intended receiver;
- receiver exact-readproof gate;
- progressive-disclosure UX guidance.

These fields should compile into CoEvoDelta+ objects or feed a later CoEvoDelta schema revision. The current R0 fan-in compiler does not yet perform that semantic compilation; it only compacts and reviews the session projection. They must not silently create a second source of semantic truth.

## Projection mapping

| Session projection | CoEvoDelta+ relation |
| --- | --- |
| `source_session` | `session_id` |
| `created_at` | `observed_at` |
| `target_domains` | `domain` |
| operation `subject` | `subject` |
| operation `relation` | `relation` |
| `source_refs` / operation evidence | `source_refs`, tests/evidence projection |
| `candidate_surfaces` | `target_surfaces` |
| `authority_ceiling` | `authority_ceiling` |
| `public_safety` | qualifies `confidentiality` plus publication readiness |
| `collision_domain` | collision/reconciliation qualifier |
| `observed_base_ref` | currentness/base qualifier before mutation |
| `next_receiver` | `next_receiver` |
| `receiver_readproof_gate` | receiver pickup proof requirement |
| `next_gate` | receiver-relative next transition |

Typed operations are projection hints:

`ADD | QUALIFY | CHALLENGE | LINK | INDEX | HIGHLIGHT | DEPRECATE | RESTRUCTURE | PROJECT`

They do not independently grant effect authority.

## Domains

This projection may carry bounded work across CoTheoryAll+, CoLex+, CoIndex+, CoAll+, CoOps+, CoMythOps+, CoPriMath+, CoGibberTru+, architecture, repository/folder structures, README/docs, RickBar/CoDesktop/CoCivia, UX/surfaces, humour/memeables, highlights, research, evidence, strategy, onboarding, and future typed domains.

`DOMAIN_NE_REPOSITORY`

## Default route

`DISCOVER_RELEVANT_CURRENTNESS -> BIND_OBSERVED_BASE -> PRODUCE_SESSION_PROJECTION -> FANIN_PROJECTION -> COMPILE_TO_COEVO -> REVIEW -> TARGETED_FANOUT -> RECEIVER_READPROOF`

Do not ingest the whole repository by default.

Do not fan one idea across many READMEs, schemas, indexes, or repositories merely because they are writable.

## Fan-in before fan-out

Before broad fanout, compact and reconcile:

1. exact duplicates;
2. semantic near-duplicates;
3. collision candidates;
4. source/provenance gaps;
5. stale observed-base refs;
6. public/private/readiness holds;
7. receiver-relative projection needs;
8. target-surface collisions.

Prefer one source relation with many typed projections over copy-pasted independent edits.

`FANIN_NE_FANOUT`
`NO_NEWEST_WINS`

## Pickup and custody

A landed branch object or durable delta is delivery evidence, not proof that the intended receiver read or integrated it.

`DELIVERY_NE_PICKUP`
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`
`GITHUB_NE_CUSTODY_ROOT`

## UX rule

Human-facing surfaces should normally project:

1. CoHereNow;
2. meaning;
3. one next safe action;
4. optional evidence drill-down.

Raw relation graphs, hashes, receipts, collision ledgers, and session deltas belong behind progressive disclosure unless they are themselves the requested product.

## Nonclaims

- NOT_CANON
- NOT_GLOBAL_SESSION_PICKUP_PROOF
- NOT_AUTOMATIC_FANOUT
- NOT_AUTHORITY_TRANSFER
- NOT_PERMISSION_FOR_UNBOUNDED_MULTI_REPO_REWRITES
- NOT_PROOF_OF_RECEIVER_PICKUP
