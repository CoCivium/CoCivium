# CoAll Evolution Convergence R0

**State:** `PUBLIC_BRANCH_CANDIDATE__PR23_SCHEMA_UNION_PENDING_CI__NO_MAIN_MERGE_NO_RUNTIME_NO_CANON_NO_AUTHORITY`

Observed `main`: `d3e7e6f2063bb9d3aa6a0954cd6bd219ea93edcd`

Current branch relation at validation: **10 ahead / 0 behind** main.

## Convergence result

The branch is now refreshed against the observed mainline and two previously open compatibility questions have been turned into executable candidates rather than remaining architecture prose.

### Schema union: PASS as a candidate

`schemas/coevo-delta-v0.2-union-candidate.schema.json` combines:

- the exact v0.1 core and required set from main;
- PR #32 effect typing:
  `effect_classes | effect_gate | effect_scope`;
- PR #37 richer extension:
  `materiality | subscription_context | pressure | energet | want_projection | route | close_readiness | nonclaims`;
- PR #23 session-writeback / projection-provenance extension:
  `$schema | object | typed_operation | evidence_refs | public_safety | qualifiers | collision_domain | observed_base_ref | next_gate | receiver_readproof_gate | source_projection_id | source_projection_file_sha256 | source_projection_record_index | source_operation_index | source_operation_sha256`.

The candidate keeps v0.1 objects valid, requires effect typing for `EFFECT_GATED`, requires `materiality` when rich PR #37 context is present, accepts PR #23 compiled write-back/provenance fields without changing the v0.1 required set, and permits extended objects to down-project to their unchanged v0.1 core.

`SCHEMA_UNION_CANDIDATE_NE_SCHEMA_ACCEPTANCE`

### Intake surface election: PASS as a candidate

Primary machine intake is now elected as:

`ai/evolution-deltas/<YYYY-MM-DD>/`

because main already uses that surface and PR #33 extends it directly.

`docs/Evolution/deltas/` is retained only as a possible documentation/index/example projection. It should link or project to the primary object rather than create an independently owned object with the same `delta_id`.

`ONE_DELTA_ID_ONE_PRIMARY_MACHINE_OBJECT__MULTIPLE_READABLE_PROJECTIONS_ALLOWED`

## CI evidence

Prior GitHub Actions run `35856946977` completed **successfully** with read-only contents permission for the PR #32 + PR #37 union. The newly added PR #23 write-back/provenance extension requires a fresh CI run before the expanded union can claim PASS.

Validator result:

`PASS_COEVO_CONVERGENCE_R0`

- current main v0.1 deltas accepted by the union: **1/1**
- v0.1 core changed: **no**
- PR #32 effect semantics carried: **yes**
- PR #37 rich extension carried in prior PASS: **yes**
- PR #23 write-back/projection-provenance extension added: **yes; fresh CI pending**
- missing effect fields for `EFFECT_GATED`: **rejected**
- rich extension without materiality: **rejected**
- rich extension with materiality: **accepted**
- primary intake: `ai/evolution-deltas/<YYYY-MM-DD>/`
- docs intake: documentation/index/example projection
- canon: `UNPROVEN`
- runtime: `UNPROVEN`
- authority: `NONE`

`CI_PASS_NE_CANON`

## Descendant satisfaction

Main already contains CoFleet/RickBar R4A and CoSessionSubscription+ R0.

Therefore:

- basic HOT/WARM/DIGEST/SLEEP subscription temperatures are no longer unique to #34/#37;
- #37 remains useful for cursor/wake/materiality/receiver-state/subscription-receiver mechanics;
- broad donor branches should shrink as mainline descendants satisfy their relations.

`DESCENDANT_SATISFACTION_REDUCES_DONOR_SCOPE`

## Remaining unique donor work

The PR #23 schema-name collision is now structurally reconciled in the union candidate, but the expanded union remains pending fresh CI. Non-schema donor fan-in remains after that gate.

Still to carry or explicitly reject before any main-merge election:

- #34: repo-role/currentness registry, highlight registry, broad relational R1 crosswalk, validator/CI donor ideas;
- #23: write-back/projection schema fields now represented in the union candidate; fan-in/projection compiler, packet compiler, and receiver-fanout mechanics remain live donor material;
- #28: CoRepoField+, CoProjectionGraph+, CoInteropEcology+, lifecycle and binding relations;
- #29: machine-routable lane extensions not on main;
- #37: richer currentness/receiver machinery;
- #41: interop/meta-relational challenger material;
- #42: currentness documentation donor;
- #43: bounded schema-aligned CoSessionSurvival donor evidence.

#32 and #33 are now materially represented by the schema-union and intake-surface candidate respectively.

## Next

`CARRY_OR_EXPLICITLY_REJECT_REMAINING_UNIQUE_NONSCHEMA_DELTAS -> VALIDATE -> MAIN_MERGE_REQUIRES_SEPARATE_EXPLICIT_GATE`

No merge, donor closure, runtime activation, canon promotion, CoEx, public outreach, credential action, financial/privacy effect, deletion, or authority transfer is performed by this convergence result.

`FANIN_BEFORE_MORE_PARALLEL_MUTATION`  
`PR_COUNT_NE_PROGRESS`  
`NO_NEWEST_WINS`  
`GITHUB_WRITE_ACCESS_NE_GLOBAL_AUTHORITY`
