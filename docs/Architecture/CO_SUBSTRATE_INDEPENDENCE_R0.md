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

## Multi-substrate federation

Substrate independence eventually permits more than migration. Multiple compatible instances may coexist across different substrates under one proven lineage.

R0 does not require one globally privileged "current instance."

Instead, a federation may contain read-only replicas, bounded writers, failover instances, or diverged branches that require reconciliation.

Concurrent writable instances MUST NOT silently collapse through newest-wins or host-priority rules.

A failover may continue work for scope without implying that personal identity, consciousness, or a metaphysical self moved between machines.

`MULTI_INSTANCE_NE_MULTI_IDENTITY`

`ONE_LINEAGE_NE_ONE_ACTIVE_INSTANCE`

`CONCURRENT_WRITES_NE_AUTOMATIC_MERGE`

`FAILOVER_NE_IDENTITY_TRANSFER`

`MERGE_NE_HISTORY_ERASURE`

`AUTHORITY_IS_INSTANCE_SCOPED_WHERE_DECLARED`

`LINEAGE_NE_AUTHORITY_INHERITANCE`

`FAILOVER_NE_AUTHORITY_TRANSFER`

A derived or failover instance does not inherit effect authority merely because it shares lineage or state. Authority must be separately present and sufficient on the acting instance.

## Cross-OS receiver proof

The first receiver-side proof MAY use distinct CI operating-system hosts as a bounded intermediate step before any model-runtime migration claim.

The same exact semantic object is reconstructed independently on Linux and Windows runners. Each receiver emits an attestation containing the semantic digest, authority state, required/observed invariants, receiver identity, accepted continuity scope, and explicit nonclaims. A fan-in job accepts only matching semantic digests, object identity/version, authority state, and two distinct OS receiver families.

This can prove a bounded cross-host representational continuity claim. It does **not** prove migration between model runtimes, production hosts, consciousness, personal identity, or provider-independent CoAll runtime continuity.

`CROSS_OS_CI_NE_MODEL_RUNTIME_MIGRATION`

`SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE`

`CI_RECEIVER_PROOF_NE_PRODUCTION_RUNTIME`

## Cross-language runtime proof

A second bounded receiver proof uses two different implementation runtimes, Python and Node.js, on independent CI jobs. Both parse the same semantic object, independently recompute the canonical semantic digest, verify authority and invariants, emit attestations, and converge through a fan-in check.

This reduces dependence on one language/runtime implementation and tests semantic portability across implementation substrates.

It still does **not** prove model-runtime migration, live agent continuity, production failover, consciousness, or personal identity.

`CROSS_LANGUAGE_RUNTIME_NE_MODEL_RUNTIME_MIGRATION`

`IMPLEMENTATION_RUNTIME_NE_SEMANTIC_IDENTITY`

`SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE`

## Continuity claim boundaries

An accepted migration supports only the continuity claims actually proved for scope.

Candidate claim classes:

- representational continuity;
- functional continuity, when separately validated;
- lineage continuity, when provenance is exact;
- authority continuity, when authority is unchanged.

It MUST NOT automatically imply:

- identical runtime instance;
- personal-identity continuity;
- subjective-experience continuity;
- consciousness continuity;
- numerical equivalence across different substrates.

`CONTINUITY_NE_IDENTITY`

`FUNCTIONAL_CONTINUITY_NE_SUBJECTIVE_CONTINUITY`

`LINEAGE_CONTINUITY_NE_IDENTICAL_INSTANCE`

`MIGRATION_ACCEPTED_NE_CONSCIOUSNESS_CONTINUITY`

`AUTHORITY_CONTINUITY_REQUIRES_AUTHORITY_PRESERVATION`

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

The initial migration fixture, adversarial migration checks, CoSubstrateField projection binding, continuity-claim guard, and synthetic multi-substrate federation canary now exist at candidate/CI scope.

The next useful proof is **not** another taxonomy expansion. It is a bounded executable handoff between two genuinely different runtimes or hosts where:

1. the same exact semantic object is reconstructed;
2. substrate requirements are checked rather than assumed;
3. authority remains equal or narrower;
4. declared invariants are verified independently at the receiver;
5. any divergence is retained as lineage rather than overwritten;
6. the result is accepted only for a declared continuity scope.

Until such a receiver-side proof exists:

`SYNTHETIC_FEDERATION_PASS_NE_RUNTIME_FEDERATION`

`CI_PASS_NE_CROSS_HOST_CONTINUITY_PROOF`

The useful eventual proof remains:

`SEMANTIC_CONTINUITY_ACCEPTED_FOR_DECLARED_SCOPE_WITH_EXPLICIT_LOSS_AND_AUTHORITY_PRESERVED`.
