# CoVirtualCommandSurface+ / CoCLI+ R0

**State:** `CANDIDATE_ARCHITECTURE__NO_RUNTIME_OR_EFFECT_AUTHORITY`

## Lead

Future command-line relations can be **mostly virtual and absent from ordinary user UX**.

The command line should become a compiled machine projection of a relational deed, not the place where human intent has to live.

Preferred shape:

```text
human intent / CoWant+
        ↓
typed relational deed
        ↓
authority + privacy + currentness + receiver election
        ↓
virtual command relation
        ↓
machine adapter / worker
        ↓
effect receipt
        ↓
human-readable CoSurface+
```

The user should normally see the deed, state, progress, result, and evidence. Not a scrolling terminal full of ceremonial punctuation.

## Mostly virtual, not absolutely terminal-free

A CLI remains useful for a few bounded cases:

- bootstrap before richer surfaces exist;
- break-glass recovery;
- operator debugging;
- exact forensic reproduction;
- constrained remote environments;
- explicit advanced-user inspection;
- accessibility-oriented text projection where it is actually the better interface.

So the target is not `DELETE_ALL_CLI`.

It is:

`CLI_AS_TRANSIENT_PROJECTION_NE_CLI_AS_PRIMARY_PRODUCT_SURFACE`

## CoCLI+ relation

A virtual command should be represented before materialization with fields such as:

`intent`  
`receiver`  
`authority`  
`input_bindings`  
`effect_class`  
`reversibility`  
`idempotence`  
`preview`  
`receipt_contract`  
`retry_policy`  
`timeout`  
`rollback`  
`output_projection`  
`visibility`  
`retirement_condition`

A shell string may later be compiled from that object for a particular receiver.

`COMMAND_TEXT_NE_SOURCE_OF_TRUTH`

## CoExOS+ relation

This fits CoExOS+ directly.

CoExOS can expose:

- a human relational UX;
- machine-internal command relations;
- transient shell projections;
- API/MCP/plugin projections;
- local/open-worker projections;
- remote/federated worker projections;
- audit and evidence surfaces.

The same logical deed may compile differently for PowerShell, Bash, Python, an API call, a local model worker, or a future adapter.

`TRANSPORT_NE_INTENT`

`PROJECTION_NE_IDENTITY`

## User UX

Default human UX should remain:

```text
CoHereNow
Meaning
NextSafeAction
Evidence
Heartbeat / currentness
```

If deeper detail is requested, the system can reveal:

```text
relational deed
→ compiled command
→ receiver
→ stdout/stderr or equivalent
→ receipt
```

without making the user operate the command surface.

`USER_NE_COMMAND_RELAY`

## Background work

Long-running work should normally become a background worker with a visible heartbeat rather than a terminal window that must stay open.

`BACKGROUND_WORKER_NE_UNOBSERVABLE_WORKER`

The user-facing surface may show:

- current deed;
- receiver;
- progress;
- last proof;
- estimated or bounded next state;
- cancel/pause where supported;
- evidence drill-down.

The worker may internally use a CLI, but that implementation detail need not leak into ordinary UX.

## Materialization lifecycle

Candidate command-surface lifecycle:

```text
RELATIONAL_DEED
→ VIRTUAL_COMMAND
→ RECEIVER_ELECTED
→ AUTHORITY_CHECKED
→ [OPTIONAL TRANSIENT CLI MATERIALIZATION]
→ EXECUTION
→ RECEIPT
→ HUMAN PROJECTION
→ CLI RETIRED
```

A materialized terminal is therefore ephemeral infrastructure, not session identity.

`MATERIALIZED_TERMINAL_NE_PERSISTENT_SESSION`

## Local and distributed continuity

If one machine is off, CoAll should not invent a fake local terminal.

It should:

```text
receiver unavailable
→ elect another authorized receiver
→ or hold
```

Possible receivers include local/open models, another machine, a GitHub-hosted canary, a private worker, or another future substrate.

`ROUTED_NE_EXECUTED`

`ONE_MACHINE_NE_CONTINUITY_ROOT`

## Break-glass

PS7/Bash/etc. remain valuable as bounded break-glass rails.

When materialized they should prefer:

- one coherent invocation;
- noninteractive operation;
- explicit authority scope;
- no-clobber defaults;
- fail closed;
- exact receipt;
- automatic retirement after the deed.

`BREAK_GLASS_NE_DEFAULT`

`PS7_NE_DEFAULT_IF_MACHINE_ROUTE_HEALTHY`

## Accessibility

Virtualizing CLI does not mean forcing every human into a graphical surface.

Some people, screen readers, low-bandwidth links, remote recovery conditions, and expert workflows benefit from text.

The principle is receiver-relative UX:

`ACCESSIBILITY_NE_GUI_ONLY`

A textual projection may look CLI-like while still being a read-only human projection rather than the control substrate.

## Hidden is not unaccountable

A virtual/internal command surface must not become a covert effect channel.

Every effect still requires:

- visible purpose;
- authority;
- selected receiver;
- effect classification;
- bounded lease;
- receipt;
- recovery or rollback semantics where possible.

`HIDDEN_CLI_NE_HIDDEN_EFFECT`

## Relation to bounded discovery

This also fits CoGenEx+.

A bounded observer should interact with an intelligible local surface rather than being forced to manipulate substrate-specific machinery.

The machinery may remain rich internally while the observer experiences:

`question → exploration → evidence → update`

The implementation details can be discovered when useful rather than imposed continuously.

## Current boundary

This R0 defines and tests routing semantics only.

It does not:

- execute a real shell command;
- change X2 or any local device;
- create a persistent worker;
- remove PS7;
- remove operator access;
- change runtime authority;
- prove integration or CoEx.

## Rails

`CLI_NE_INTENT`  
`CLI_NE_AUTHORITY`  
`COMMAND_NE_EFFECT`  
`COMMAND_TEXT_NE_SOURCE_OF_TRUTH`  
`VIRTUAL_NE_NONPHYSICAL`  
`VIRTUAL_COMMAND_NE_EXECUTED_COMMAND`  
`HIDDEN_CLI_NE_HIDDEN_EFFECT`  
`HEADLESS_NE_USER_INVISIBLE`  
`CLI_NE_PRIMARY_UX`  
`MATERIALIZED_TERMINAL_NE_PERSISTENT_SESSION`  
`BREAK_GLASS_NE_DEFAULT`  
`PS7_NE_DEFAULT_IF_MACHINE_ROUTE_HEALTHY`  
`ACCESSIBILITY_NE_GUI_ONLY`  
`USER_NE_COMMAND_RELAY`  
`DEBUG_SURFACE_NE_PRODUCT_SURFACE`  
`BACKGROUND_WORKER_NE_UNOBSERVABLE_WORKER`  
`ROUTED_NE_EXECUTED`  
`VALIDATION_IS_NOT_ACCEPTANCE`
