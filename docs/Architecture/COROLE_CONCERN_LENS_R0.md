# CoRole Concern Lens R0 | Civ2+ optional concerns

**State:** `PUBLIC_SAFE_CANDIDATE__UNASSIGNED_NONEXECUTING_PANEL__NO_MEASURED_STORAGE_GAIN`

## Why this extends the existing role space

[CoRoleSpace Preview R0](COROLE_SPACE_PREVIEW_R0.md) already projects 6,320,160 raw single-choice tuples from six existing axes at its pinned input snapshot. That is a finite syntactic configuration count, **not all meaningful possible roles**. New constraints, missions, cultures, modalities, times, contexts and relations leave the descriptive role universe open-ended. Neither an invented new axis nor indiscriminate Cartesian enumeration proves any actual role's utility.

A role describes function. A seat describes a review contribution. A participant assignment binds an actual identity. An authority contract bounds effects. None follows automatically from the others.

## Answer: Does every role worry?

**No.** A concern is a typed *object-task relation*, not a necessary feeling of the bearer of a role.

Reusable kinds are defined once in `ai/corole-concern-lens-r0.json`:

- `RISK`: what might be harmed
- `UNCERTAINTY`: what is not established
- `DISSENT`: why a conclusion is challengeable
- `DUTY_OF_CARE`: what protective duty is actually authorized
- `HYPOTHESIS`: a testable interpretation
- `NARRATIVE_WORRY`: a literary, spiritual or cultural expression
- `SUBJECTIVE_WORRY`: a voluntary human report with consent and provenance, never inferred from an AI role
- `NONE`: explicitly no concern assigned

A `QUIESCENT_RESERVE` can have **zero** assigned concerns and no monitoring mandate. `TRANSLATOR` may preserve ethical, experiential, mythological, speculative nonphysical and spiritual perspectives as perspectives, without turning them into scientific evidence of beings or mechanisms.

This does not prohibit good-faith discussion of spiritual experiences or culture. It requires that a reported experience, physical hypothesis and metaphor remain separately labeled.

## Review panel

Seven **unassigned** design seats reuse existing CoSpawn operational roles: proposal, formal check, empirical check, challenge, perspective, provenance and synthesis. Shared role-definition refs and concern-kind refs are stored once, rather than duplicating full prose at each seat. A panel is built only for a bounded question and returns no executable CoSpawn contracts. Seven seats are not seven independent sources.

```sh
python3 scripts/CoRoleConcernPanelR0.py --question "What evidence would disprove CoPriMath novelty?"
python3 scripts/CoRoleConcernPanelR0.py --question "Where could this policy harm someone?" --max-seats 3
python3 -B -m unittest discover -s tests -p test_role_concern_lens.py -v
```

The CLI reads only `ai/corole-concern-lens-r0.json` and `schemas/cospawn-contract-v0.1.schema.json`. Source SHA-256 bindings and question determine the panel ID. The script writes no files, starts no workers, grants no authority, performs no network calls, and has no discretionary budget or autonomous recursion.

## Storage and CoOrbWare direction, unproven

A candidate relational shape is:

`immutable source objects + versioned role definitions + typed concern vocabulary + panel-instance reference edges + receiver-specific materialized views`.

Test it against straightforward normalized tables and ordinary documents before claiming an improvement. Metrics: **all stored bytes including indexes, reconstruction byte equality, query-result equivalence, query latency, update/rebuild cost and staleness**. Semantic equivalence is a separate review decision; shared hashes alone prove neither truth nor universal deduplication. Privacy-compatible sources only. Code contains no new storage engine or benchmark.

CoOrb/CoCluster can use the compact projection for role-oriented review routing later, but present output is solely logical. Parallel reviews require task-specific separate source lineages, independently evaluated evidence, shared aggregate budgets, collision control and actual authorized executors. No "567 agents" are launched. Nested review depth remains at most two, with no worker materialization in R0.

## Decision

Advance one question through the existing review/evidence/CoPulse path, obtain exact receiver pickup and record useful criticism before considering expansion.

**Nonclaims:** `CONCERN_NE_EMOTION`; `ROLE_NE_PERSONHOOD`; `ROLE_NE_PERMISSION`; `PERSPECTIVE_NE_PHYSICAL_EVIDENCE`; `RAW_CONFIGURATION_NE_MEANINGFUL_JOB`; `PANEL_PLAN_NE_REVIEW_EXECUTED`; `REFERENTIAL_STORAGE_NE_BENCHMARK_GAIN`; `NO_WORKER_OR_RUNTIME_INTEGRATION`.
