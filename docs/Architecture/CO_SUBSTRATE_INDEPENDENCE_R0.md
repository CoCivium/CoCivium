# CoSubstrate Independence R0

**State:** `CANDIDATE__PUBLIC_RND__NOT_CANON__NOT_RUNTIME_AUTHORITY`

## Purpose

CoSubstrate Independence R0 separates the identity and continuity of a model, agent, relation, or CoAll object from any one execution substrate.

The candidate claim is not that computation becomes immaterial. It is that durable semantic identity should survive replacement of the current host whenever the required state, provenance, constraints, reconstruction rules, and authority boundaries can be preserved.

## Existing substrate donor / scope correction

This candidate is a focused continuity/migration profile over the existing `CoSubstrateField+ / CoHardware+ / CoSoftware+ R0` architecture in `docs/Architecture/COSUBSTRATE_FIELD_R0.md`.

It does **not** introduce a second generic substrate ontology. The existing field owns substrate taxonomy, translation relations, loss/invariant vocabulary, capability/constraint dimensions, privacy/effect ceilings, and replacement/fallback relations. This profile owns only portability classification and scoped migration acceptance/rejection checks.

`COSUBSTRATE_INDEPENDENCE_PROFILE_NE_NEW_SUBSTRATE_ONTOLOGY`

See `docs/Architecture/CO_SUBSTRATE_INDEPENDENCE_FIELD_CROSSWALK_R0.md`.

## Core distinction

A durable CoAll object SHOULD be representable independently of the machine currently executing it.

Candidate decomposition:

```text
semantic identity
+ durable state
+ relations
+ provenance
+ invariants
+ authority / consent bounds
+ reconstruction rules
+ validation tests
+ substrate requirements
= portable continuation candidate
```

Execution still occurs on material infrastructure.

`PORTABLE_NE_SUBSTRATE_FREE`

## Candidate substrate classes

Examples include:

- conventional CPU / GPU hosts;
- local open-weight model runtimes;
- provider-hosted models;
- specialized accelerators;
- photonic / neuromorphic / quantum candidates where appropriate;
- biological or hybrid computation only where separately evidenced and ethically governed.

No substrate class is presumed equivalent.

## Substrate-independent versus substrate-bound properties

A property MAY be:

- `PORTABLE`: intended to survive host migration;
- `SUBSTRATE_CONSTRAINED`: portable only to compatible hosts;
- `SUBSTRATE_BOUND`: identity or function materially depends on a specific physical capability;
- `UNKNOWN`: portability not yet established.

Examples:

- a typed relation graph may be portable;
- an inference runtime may be substrate-constrained;
- a telescope observation remains provenance-bound to the instrument that produced it;
- a hardware-protected secret may intentionally remain substrate-bound;
- an actuator requires a physical endpoint even if its control model migrates.

## Reconstruction

A new instantiation MUST NOT be treated as identical merely because it loads similar files.

A reconstruction claim SHOULD bind:

- source state identifier;
- exact or qualified semantic version;
- provenance lineage;
- authority state;
- required invariants;
- validation suite;
- declared loss;
- substrate assumptions;
- receiver/readback evidence.

`RECONSTRUCTABLE_NE_IDENTICAL_INSTANCE`

## Runtime substrate election

A future CoAll scheduler MAY select among compatible substrates using bounded criteria such as:

- required capability;
- privacy;
- authority;
- latency;
- reliability;
- energy/resource cost;
- locality;
- evidence quality;
- reversibility;
- failure-domain diversity.

Selection of a substrate does not transfer semantic or governance authority to that substrate.

A migration MUST preserve the source authority state unless a separate, explicitly authorized authority transition is represented and validated outside the migration itself.

`MIGRATION_NE_AUTHORITY_ESCALATION`

`CAPABILITY_NE_AUTHORITY`

## Continuity

The target continuity chain is:

```text
durable semantic object
  -> eligible substrate discovered
  -> compatibility checked
  -> bounded instantiation
  -> invariants tested
  -> state/provenance rebound
  -> receiver/readback proof
  -> continuation accepted for scope
```

A provider tab, process, device, or model instance is therefore an execution carrier, not the durable identity root.

## Rails

`SUBSTRATE_NE_IDENTITY`

`HOST_NE_CONTINUITY`

`IMPLEMENTATION_NE_SEMANTICS`

`PORTABLE_NE_SUBSTRATE_FREE`

`RECONSTRUCTABLE_NE_IDENTICAL_INSTANCE`

`MULTI_SUBSTRATE_NE_SUBSTRATE_IRRELEVANT`

`MODEL_INSTANCE_NE_DURABLE_AGENT_IDENTITY`

`DEVICE_NE_CUSTODY_ROOT`

`PROVIDER_NE_SEMANTIC_SOVEREIGN`

`CAPABILITY_NE_AUTHORITY`

`MIGRATION_NE_EQUIVALENCE`

`MIGRATION_NE_AUTHORITY_ESCALATION`

`UNKNOWN_PORTABILITY_NE_ASSUMED_PORTABILITY`

`SUBSTRATE_ELECTION_NE_TRUTH_ELECTION`

## Non-goals

R0 does not:

- claim that computation can exist without a physical substrate;
- claim that all model state is portable today;
- claim that continuity of function proves continuity of consciousness or personal identity;
- claim that different hardware produces equivalent numerical or behavioral results;
- authorize migration of secrets, credentials, actuators, or sensitive state;
- establish runtime adoption, canon, or CoEx.

## Next proof

Before runtime adoption, construct a bounded migration fixture with at least:

1. one portable semantic object;
2. one substrate-constrained object;
3. one intentionally substrate-bound object;
4. one migration with declared semantic loss;
5. one reconstruction that fails invariant checks and is therefore rejected.

The useful proof is not "it ran somewhere else."

The useful proof is:

`SEMANTIC_CONTINUITY_ACCEPTED_FOR_DECLARED_SCOPE_WITH_EXPLICIT_LOSS_AND_AUTHORITY_PRESERVED`.
