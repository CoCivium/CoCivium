# CoArtifactContinuity+ / CoVirtualCLI+ / CoSurfaceDensity R0

**State:** `CANDIDATE_SURFACE_SUBSTRATE_CONTRACT__NO_RUNTIME_OR_PUBLIC_EFFECT`

## Lead

A generated artifact is not durable merely because it is visible in a chat, downloadable from a session, or rendered in a browser.

A command-line interface is not a user workflow merely because an implementation currently exposes commands.

A dense payload is not a better payload merely because more state can be crammed onto one surface.

These are one family of surface/substrate mistakes: implementation details being mistaken for durable custody, user intent, or useful information.

## CoArtifactContinuity+

Default rule:

`SESSION_ATTACHMENT_NE_DURABLE_CUSTODY`

`DOWNLOADABLE_NE_DURABLE_CUSTODY`

`RENDERED_ARTIFACT_NE_LANDED_ARTIFACT`

A downloadable may remain a convenience projection, but it SHOULD NOT be the only surviving copy of a material artifact when a machine-owned durable destination is authorized and available.

Preferred lifecycle:

`CREATE -> HASH -> LAND_DURABLY -> RECEIVER_READBACK -> OPTIONAL_DOWNLOAD_PROJECTION`

If no authorized durable destination exists:

`CREATE -> HASH -> HOLD_EPHEMERAL_WITH_EXPLICIT_RISK`

not:

`CREATE -> DOWNLOAD_LINK -> ASSUME_PRESERVED`

Artifact completion SHOULD expose:

- artifact identity;
- exact digest;
- durable destination class;
- receiver/readback state;
- currentness;
- confidentiality;
- retention/expiry;
- successor/supersession;
- explicit ephemeral status when durable custody is absent.

Session close, provider failure, browser-tab loss, or conversation deletion must not silently become an artifact deletion mechanism.

`SESSION_TERMINATION_NE_ARTIFACT_RETIREMENT`

`UI_DISAPPEARANCE_NE_AUTHORIZED_DELETION`

## Human transport

The human should not be required to download, re-upload, copy, paste, rename, or file-pick routine artifacts merely to keep the system's own work alive.

`HUMAN_NE_ARTIFACT_TRANSPORT_LAYER`

`DOWNLOAD_REQUIRED_FOR_MACHINE_CONTINUITY_NE_ACCEPTABLE_DEFAULT`

A human download is an optional personal export, not the canonical machine handoff.

## CoVirtualCLI+

CLI remains useful as a substrate and operator/debug surface, but SHOULD be virtualized away from ordinary user UX when equivalent intent can be expressed safely at a higher level.

Preferred relation:

`USER_INTENT -> TYPED_ACTION -> POLICY/AUTHORITY_GATE -> VIRTUAL_CLI_OR_API_ADAPTER -> RECEIPT`

not:

`USER -> REMEMBER_COMMAND -> SHELL -> HOPE`

Rails:

`CLI_NE_USER_WORKFLOW`

`COMMAND_NE_INTENT`

`USER_NE_SHELL_OPERATOR`

`VIRTUALIZED_NE_REMOVED`

`HIDDEN_NE_UNAUDITABLE`

The CLI may remain visible when explicitly elected for:

- break-glass recovery;
- diagnostics;
- development;
- reproducibility;
- advanced/operator use;
- environments where no richer surface exists.

Ordinary users should see intent, state, exceptions, provenance, and receipts rather than command syntax.

## Invisible substrate / CoSubstrateMark+

A compact symbol may denote "there is additional substrate/provenance/context beneath this projection."

Candidate rendering token:

`⊂`

This is **not** a redefinition of the mathematical proper-subset operator. In user-facing mathematical contexts, ordinary mathematical meaning wins.

Therefore the safer semantic name is:

`CoSubstrateMark+`

Possible projection meaning:

`visible object ⊂ richer typed substrate`

In virtual/session UX, it may behave like a fold/unfold cue rather than literal typed text.

`VISUAL_DELIMITER_NE_KEYPRESS`

`SUBSTRATE_MARK_NE_HIDDEN_AUTHORITY`

`COMPRESSION_NE_ERASURE`

A metaphorical blank-line / Enter-like separation may be rendered around the substrate marker, but should not imply an actual keyboard event.

## CoSurfaceDensity+

Payload density should adapt to receiver and task.

Candidate density states:

`GLANCE | COMPACT | WORKING | DEEP | FORENSIC`

A useful surface optimizes for:

`decision_value / attention_cost`

not byte count, term count, or relation count.

`PAYLOAD_DENSITY_NE_VALUE`

`MORE_VISIBLE_STATE_NE_MORE_CURRENTNESS`

`COMPRESSION_NE_SUMMARIZATION_TRUTH`

`HIDDEN_DETAIL_NE_DELETED_DETAIL`

A compact surface SHOULD retain traversable provenance to deeper layers when that depth exists.

## CoConvergeSpiralLoop+

Not every recurring process should be a closed loop.

A healthier recurring relation is often a spiral:

`OBSERVE -> RELATE -> PROVE -> ACT/HOLD -> RECEIVER -> REOBSERVE_AT_CHANGED_STATE`

The next traversal occurs at a different time, evidence state, receiver state, or authority state.

`LOOP_NE_PROGRESS`

`SPIRAL_REVISIT_NE_DUPLICATE_RETRY`

`CONVERGENCE_NE_STASIS`

`REOPEN_REQUIRES_MATERIAL_DELTA`

This supports continuous learning without requiring permanent wakefulness or recursive thrash.

## CoOps+ / CoMythOps+ bridge

Operational and mythic/speculative layers may overlap without collapsing.

`CoMythOps+` may generate metaphors, hypotheses, counterfactuals, values, and unexplored relation candidates.

`CoOps+` may operationalize only what has an appropriate evidence, authority, safety, and receiver path.

Bridge:

`MYTHIC_OR_SPECULATIVE_CANDIDATE -> TRANSLATION -> TESTABLE_QUESTION -> EVIDENCE -> OPTIONAL_OPERATIONALIZATION`

Rails:

`MYTHIC_GENERATION_NE_OPERATIONAL_TRUTH`

`METAPHOR_NE_MECHANISM`

`SPECULATION_NE_EXECUTION_AUTHORITY`

`OPS_NE_COMPLETE_REALITY_MODEL`

## Inventory / CoInventory+

Inventories should evolve from static lists toward relational indexes.

Each material inventory item SHOULD be able to expose:

`identity | source | currentness | authority | receiver | state | successor | retirement | evidence`

Static exports remain valid projections, but:

`INVENTORY_NE_WORLD`

`LISTED_NE_CURRENT`

`UNLISTED_NE_NONEXISTENT`

`INVENTORY_COMPLETENESS_REQUIRES_SCOPE`

## Massive parallelism

Parallelism remains useful for independent discovery/proof lanes.

Default:

`PARALLELIZE_UNCERTAINTY__SERIALIZE_CONFLICTING_AUTHORITY_OR_MUTATION`

Concurrency SHOULD adapt to:

- proof capacity;
- receiver capacity;
- compute/resource pressure;
- failure-domain independence;
- coordination overhead;
- blast radius.

`MORE_PARALLEL_NE_MORE_PROGRESS`

`ACCELERATION_NE_PROGRESS`

`THROUGHPUT_NE_VALUE`

## Nonclaims

This document does not:

- install a persistence service;
- redirect artifact output automatically;
- delete existing downloadable behavior;
- remove CLI access;
- redefine mathematical symbols;
- claim all sessions have a durable receiver;
- make CoMythOps claims factual;
- authorize public, financial, credential, or destructive effects.

## Rails

`SESSION_ATTACHMENT_NE_DURABLE_CUSTODY`  
`DOWNLOADABLE_NE_DURABLE_CUSTODY`  
`SESSION_TERMINATION_NE_ARTIFACT_RETIREMENT`  
`HUMAN_NE_ARTIFACT_TRANSPORT_LAYER`  
`CLI_NE_USER_WORKFLOW`  
`VIRTUALIZED_NE_REMOVED`  
`HIDDEN_NE_UNAUDITABLE`  
`VISUAL_DELIMITER_NE_KEYPRESS`  
`PAYLOAD_DENSITY_NE_VALUE`  
`HIDDEN_DETAIL_NE_DELETED_DETAIL`  
`LOOP_NE_PROGRESS`  
`SPIRAL_REVISIT_NE_DUPLICATE_RETRY`  
`MYTHIC_GENERATION_NE_OPERATIONAL_TRUTH`  
`INVENTORY_COMPLETENESS_REQUIRES_SCOPE`  
`PARALLELIZE_UNCERTAINTY__SERIALIZE_CONFLICTING_AUTHORITY_OR_MUTATION`  
`ACCELERATION_NE_PROGRESS`  
`VALIDATION_IS_NOT_ACCEPTANCE`
