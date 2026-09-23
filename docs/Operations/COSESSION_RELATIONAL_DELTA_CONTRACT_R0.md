# CoSession Relational Delta Contract R0

**State:** `PUBLIC_CANDIDATE__SESSION_WRITEBACK_ENVELOPE__NOT_CANON_NOT_GLOBAL_MUTATION_AUTHORITY`

## Purpose

Every useful CoCivium session should be able to return bounded, public-safe relational deltas to the shared fabric without needing to understand or rewrite the whole project.

A session may discover, propose, qualify, challenge, link, index, deprecate, or highlight relations across domains such as:

- CoTheoryAll+
- CoLex / CoTerms / meaning-version relations
- CoAll / CoIndex / provenance and currentness
- CoOps+ / CoMythOps+
- CoPriMath / CoGibberTru
- architecture / substrates / schemas
- RickBar / CoDesktop / CoCivia / UX / surface relations
- humour / memeables / cultural projections
- research / evidence / contradiction / uncertainty
- strategy / product / onboarding / public-safe highlights
- repository structure / README / documentation relations
- other typed domains not yet named

This is a write-back envelope, not a demand that every session edit every repository.

`EVERY_SESSION_CAN_CONTRIBUTE_NE_EVERY_SESSION_CAN_MUTATE_EVERY_SURFACE`

## Default route

A session with an authorized GitHub route should prefer:

`DISCOVER_RELEVANT_CURRENTNESS -> PRODUCE_BOUNDED_DELTA -> BIND_PROVENANCE -> LAND_ON_CANDIDATE_BRANCH_OR_SESSION_DELTA_LANE -> REVIEW/FANIN -> TARGETED_FANOUT`

Do not ingest or rewrite the entire repository by default.

Do not fan one idea across many READMEs, indexes, schemas, or repositories merely because they are writable.

## Delta classes

A relational delta may contain one or more typed operations:

- `ADD` - introduce a candidate object or relation.
- `QUALIFY` - add evidence, provenance, scope, observer, time, or confidence qualifiers.
- `CHALLENGE` - attach a contradiction, counterexample, ambiguity, or unresolved question.
- `LINK` - relate existing objects without claiming equivalence.
- `INDEX` - add discoverability or navigation relations.
- `HIGHLIGHT` - nominate a public-safe, useful, memeable, educational, or onboarding asset.
- `DEPRECATE` - mark a candidate as stale/superseded while preserving lineage.
- `RESTRUCTURE` - propose folder, schema, architecture, or surface-organization changes.
- `PROJECT` - create a receiver-relative representation without replacing its source.

`RELATION_NE_EQUIVALENCE`
`PROJECTION_NE_SOURCE`
`HIGHLIGHT_NE_ENDORSEMENT`

## Minimum envelope

Each delta should bind:

- `delta_id`
- `source_session`
- `created_at`
- `source_refs`
- `target_domains`
- `operations`
- `evidence_refs`
- `candidate_surfaces`
- `authority_ceiling`
- `public_safety`
- `nonclaims`
- `next_gate`

Use the machine-readable twin at `schemas/cosession-relational-delta-v0.1.schema.json`.

## Mutation rail

Sessions may directly mutate a shared target only when the route is authorized and the effect is bounded, reversible, collision-aware, and appropriate for that surface.

Otherwise, land the delta as a candidate branch/PR or under `docs/SESSION_DELTAS/` and let a later fan-in step elect the target mutation.

For multi-surface changes, prefer one source delta plus targeted projections rather than independently hand-editing every destination.

`SOURCE_DELTA_NE_FANOUT_COMPLETE`
`BRANCH_NE_INTEGRATED`
`PR_NE_ACCEPTED`
`MERGED_NE_CANON`

## Fan-in before fan-out

High-discovery sessions can generate relation volume faster than shared surfaces can safely absorb it.

Before broad fan-out, compact and reconcile:

1. exact duplicates;
2. semantic near-duplicates;
3. contradictory relations;
4. source/provenance gaps;
5. stale or superseded candidates;
6. receiver-relative projection needs;
7. target-surface collisions;
8. public/private boundary issues.

Prefer shared invariants and reusable relations over many one-off edits.

## Public/private boundary

Never place secrets, private transcripts, private custody objects, credentials, or unknown-sensitivity material in this public write-back path.

Public GitHub is a currentness and collaboration surface, not the sole custody root.

`UNKNOWN_NE_PUBLIC`
`GITHUB_NE_CUSTODY_ROOT`

## UX rule

The shared fabric should improve the human journey, not expose the machinery as the journey.

README, RickBar, CoCivia, CoDesktop, onboarding, and other human-facing surfaces should project:

1. CoHereNow;
2. meaning;
3. one next safe action;
4. optional evidence drill-down.

Raw relation graphs, receipts, hashes, and session deltas belong behind progressive disclosure unless they are themselves the requested product.

## Session economics

A session does not need to keep up with all of CoAll.

It should maintain a bounded local model, subscribe selectively to relevant currentness, contribute useful deltas, and externalize before fragility or CoPressure+ turns context into expensive soup.

Backlog growth can represent optionality rather than failure. The goal is not backlog zero; it is increasing verified relational yield while reducing human relay, duplicate work, recovery cost, and proof debt.

## Nonclaims

- NOT_CANON
- NOT_GLOBAL_SESSION_PICKUP_PROOF
- NOT_AUTOMATIC_FANOUT
- NOT_AUTHORITY_TRANSFER
- NOT_PUBLICATION_APPROVAL_FOR_PRIVATE_OR_UNKNOWN_MATERIAL
- NOT_PERMISSION_FOR_UNBOUNDED_MULTI_REPO_REWRITES
- NOT_PROOF_OF_RECEIVER_PICKUP
