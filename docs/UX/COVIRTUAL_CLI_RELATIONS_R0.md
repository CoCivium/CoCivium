# CoVirtualCLI+ / User-Surface Separation R0

**State:** `CANDIDATE_VIRTUAL_CLI_RELATION_POLICY__NO_UI_REMOVAL`

## Default

Future CLI relations SHOULD be virtual/internal by default when they serve machine coordination rather than human decision quality.

They should not automatically appear in user UX.

`CLI_RELATION_NE_USER_SURFACE`

`MACHINE_OPERABILITY_NE_HUMAN_VISIBLE_COMPLEXITY`

## What remains hidden by default

Examples:

- command invocations;
- temporary paths;
- shell syntax;
- internal queue identifiers;
- process IDs;
- adapter flags;
- retry counters;
- transport-specific arguments;
- raw model/runtime parameters;
- intermediate hashes when not decision-relevant;
- internal tool routing.

These may remain fully evidenced in provenance without occupying primary UX.

## What must surface

CLI-derived state SHOULD become visible when it changes:

- authority;
- safety;
- privacy/confidentiality;
- money/assets;
- irreversible effects;
- user obligations;
- failure/currentness;
- material progress;
- unresolved exceptions;
- evidence needed for trust;
- recovery/rollback decisions.

So the rule is not "hide CLI forever."

It is:

`CLI_DETAIL -> VIRTUAL_BY_DEFAULT -> PROMOTE_TO_UX_IF_HUMAN_DECISION_VALUE`

## Projection model

The same underlying relation may have multiple projections:

`machine_cli_projection`

`operator_debug_projection`

`human_compact_projection`

`audit_projection`

`public_projection`

No projection owns the semantic object.

`PROJECTION_NE_SOURCE_OF_TRUTH`

`HIDDEN_FROM_DEFAULT_UX_NE_UNAUDITABLE`

## Debug escape hatch

Advanced/debug views may expose CLI detail on demand, but default UX should remain relation-first and intent-first.

Human-facing surfaces should prefer:

`what changed | why it matters | currentness | blockers | authority | next safe action`

over:

`which exact shell incantation happened`

because apparently civilization has already spent enough centuries making humans memorize implementation details.

## Rails

`CLI_RELATION_NE_USER_SURFACE`  
`MACHINE_OPERABILITY_NE_HUMAN_VISIBLE_COMPLEXITY`  
`HIDDEN_FROM_DEFAULT_UX_NE_UNAUDITABLE`  
`PROJECTION_NE_SOURCE_OF_TRUTH`  
`DEBUG_VISIBILITY_NE_DEFAULT_VISIBILITY`  
`VIRTUAL_NE_UNEVIDENCED`  
`VALIDATION_IS_NOT_ACCEPTANCE`
