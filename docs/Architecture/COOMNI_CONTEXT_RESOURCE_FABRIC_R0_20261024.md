# CoOmni+ / Context & Resource Fabric R0

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NOT_INFINITE_CONTEXT__NOT_UNLIMITED_COMPUTE__NOT_RUNTIME  
**Observed:** 2026-10-24

## Core thesis

CoOmni+ should mean **omni-addressable, rehydratable, provider-neutral and resource-pooled**, not physically infinite.

`COOMNI = ADDRESSABLE + RETRIEVABLE + REHYDRATABLE + ROUTABLE + RECOVERABLE`

not:

`COOMNI = ALL_BYTES_RESIDENT + ALL_WORKERS_ACTIVE + UNLIMITED_AUTHORITY`

## Context extension

A large work identity may exceed any one model/session/context window.

Use:

```
durable work id
+ exact source refs
+ typed summaries
+ retrieval index
+ relation graph
+ lineage
+ deltas
+ proof receipts
+ recovery pointers
-> context compiler
-> bounded working set
-> model/tool
-> receipt + delta writeback
```

This yields effectively unbounded **addressability**, while each active invocation remains bounded.

## CoContextCompiler+

Inputs:
- intent / work object;
- source refs;
- relevant priors;
- recent material deltas;
- evidence / uncertainty;
- authority / privacy;
- receiver;
- contradictions / dissent;
- recovery;
- resource availability;
- time/currentness.

Output:
- smallest sufficient context packet for the selected worker/surface.

`ALL_CONTEXT_ADDRESSABLE_NE_ALL_CONTEXT_LOADED`

## CoMemoryField+

Candidate layers:
- exact immutable sources;
- append-only receipts;
- current structured state;
- typed summaries;
- indexes;
- embeddings / search aids where appropriate;
- cached compiled packets;
- negative knowledge;
- historical priors;
- future/counterfactual branches;
- recovery checkpoints.

Compression is allowed only when exact sources or rehydration paths remain available.

`SUMMARY_NE_SOURCE`
`COMPRESSION_NE_FORGETTING_IF_REHYDRATABLE`

## CoResourcePool+

Resources may include:
- deterministic CPU;
- GPU / accelerator;
- storage;
- local FOSS models;
- provider models;
- search/retrieval;
- code tools;
- human reviewers;
- scientific/public data;
- devices;
- network;
- caches;
- time;
- energy;
- money;
- attention;
- optionality.

Lifecycle:

`DISCOVER -> QUALIFY -> AUTHORIZE -> LEASE -> USE -> OBSERVE EFFECT -> RELEASE / RECOVER`

Each lease carries:
- scope;
- identity;
- budget;
- expiry;
- authority;
- privacy;
- expected value;
- failure domain;
- recovery;
- receipt target.

`RESOURCE_POOL_NE_GLOBAL_AUTHORITY`

## CoSynergy+

Synergy means the composed result measurably exceeds isolated use after accounting for coordination cost.

Candidate tests:
- duplicate work avoided;
- evidence gain;
- latency reduction;
- recovery gain;
- model disagreement value;
- human-time saved;
- cross-substrate reuse;
- energy/cost per useful delta.

`MANY_RESOURCES_NE_SYNERGY`
`SYNERGY_NE_FREE_COMPUTE`

## CoAmp+

Amplification may mean:
- reuse one proof across many compatible consumers;
- compile one source into many projections;
- share caches/indexes;
- fan-out independent proposal work;
- fan-in challenge/review;
- rehydrate instead of restart;
- use local/offline capacity before scarce provider turns.

Amplification must preserve provenance and effect ceilings.

## CoOmniContext+

Target property:

> Any relevant prior/source/tool/resource may be discoverable and bindable when needed, without requiring it to remain resident or active.

This enables:
- huge logical session populations;
- deep historical recall;
- cross-provider continuation;
- device substitution;
- large relation fields;
- future worker substitution.

`OMNI_ADDRESSABLE_NE_OMNI_RESIDENT`

## CoOmniResource+

Target property:

> Many qualified resources can be elected dynamically for one work object under separate authority, cost, privacy and failure-domain constraints.

Not every resource runs.
Not every resource sees every datum.
Not every resource may act.

## CoOmniProjection+

One durable work object may project through:
- headless JSON;
- CoMap;
- CoOrb;
- CoBar;
- browser;
- phone;
- tablet;
- VR;
- email;
- messaging;
- public web;
- research view;
- machine verifier.

`PROJECTION_NE_TRUTH_STORE`

## CoOmniFuture+

Maintain addressable:
- forecasts;
- scenarios;
- counterfactuals;
- recovery futures;
- successors;
- wake conditions.

Only materialized branches consume active work.

## CoOmniChallenge+

For important conclusions, keep addressable:
- inverse;
- null;
- alternative;
- falsifier;
- dissent;
- outside-view;
- adversarial;
- historical fail;
- negative result.

This protects against context compilers becoming confirmation machines.

## Relation to CoTurtle∞+

CoTurtle∞+ means recursive challenge eligibility, not infinite recursive execution.

Each turtle layer carries:
- depth budget;
- evidence gain;
- cost;
- stop rule;
- recovery;
- receipt.

`COTURTLE_INFINITY_NE_INFINITE_RECURSION`

## Relation to latch

Candidate compact form:

```
∞ [ EVO ALL BETTERS + ] ∞
CoTurtle∞+ ⇄ CoOrbWare+
CoOmni+ = addressable context + pooled resources + rehydration + recovery
```

## Rails

`CONTEXT_EXTENSION_NE_INFINITE_CONTEXT`
`TOKEN_POINTER_NE_UNLIMITED_CONTEXT`
`OMNI_ADDRESSABLE_NE_OMNI_RESIDENT`
`RESOURCE_POOL_NE_GLOBAL_AUTHORITY`
`MANY_WORKERS_NE_INDEPENDENT_EVIDENCE`
`MANY_RESOURCES_NE_SYNERGY`
`SYNERGY_NE_FREE_COMPUTE`
`INFIN_NE_INFINITE_COMPUTE`
`ALL_NE_ALL_ACTIVE`
`PERSISTENT_IDENTITY_NE_PERSISTENT_PROCESS`

## Next proof

Build a local reference context compiler over one durable work object:
1. exact source refs;
2. typed summary;
3. retrieval index;
4. prior + delta selection;
5. contradiction lane;
6. worker-specific packet;
7. deterministic rehydration;
8. packet-size / retrieval-latency / source-recall benchmark;
9. zero external effects;
10. receipt.


## R0.1 missing-but-reused relations

The existing CoAll corpus already supplies several important relations that belong inside CoOmni+ rather than as new standalone systems.

### CoCapabilityMarket+
Resources advertise bounded capabilities; needs bind to capabilities rather than provider names.

`CAPABILITY_NE_PROVIDER`  
`OFFER_NE_PROMISE`

This allows provider/model/device substitution without redefining the work object.

### CoSubstitution+
Maintain equivalent or degraded paths for:
- model;
- tool;
- device;
- human reviewer;
- protocol;
- storage;
- network;
- renderer.

A preferred resource disappearing should reduce capability gracefully, not collapse the work identity.

### CoBackpressure+
Resource selection must account for:
- concurrency;
- fairness;
- recovery reserve;
- correlated failure;
- cost;
- energy;
- latency;
- human attention;
- queue depth.

`AVAILABLE_NE_SHOULD_RUN`

### CoHerdAvoidance+
When many nodes discover the same attractive resource:
- lease;
- stagger;
- use canary cohorts;
- randomize backoff;
- fan-in evidence;
- avoid mass adoption from one early result.

`POPULAR_OPTION_NE_BEST_OPTION`

### CoProofBudget+
Proof effort should scale with:
- blast radius;
- irreversibility;
- uncertainty;
- affected parties;
- replacement difficulty.

Do not spend more proving a trivial reversible canary than the decision is worth.

### CoRecipeCache+
Every proven resolution may emit:

```
NeedPattern
+ Context
+ ResourceBundle
+ Preconditions
+ Canary
+ ObservedEffect
+ FailureModes
+ Rollback
+ Currentness
+ Provenance
```

This is the main compounding mechanism for CoPayback+ and CoFactory+.

`RECIPE_NE_UNIVERSAL_TRUTH`

### CoNegativeLearning+
Failures should return reusable knowledge:
- incompatibility;
- misleading metric;
- bad dependency;
- stale assumption;
- failure signature;
- wasted route.

`FAILED_CANARY_NE_FAILED_LEARNING`

### CoEventWake+
Prefer event-driven material wakes over permanent polling when possible.

Wake classes include:
- source delta;
- receiver feedback;
- expired currentness;
- resource availability;
- failure;
- changed authority;
- newly qualified substitute;
- scheduled bounded checkpoint.

### CoMultiObserver+
Preserve multiple observer-relative projections without forcing premature collapse into one viewpoint.

### CoMultiSubstrate+
Test important concepts across admissible:
- humans;
- deterministic software;
- local models;
- provider models;
- institutional processes;
- devices;
- physical experiments.

`MULTISUBSTRATE_NE_ALL_SUBSTRATES_REQUIRED`

### CoAmp+ governed tuning

Reuse the existing CoAmp contract:

`Target | Goal | Baseline | Direction | Magnitude | Constraint | Evidence | UserControl | StopRule | Rollback`

Amplify:
- comprehension;
- capacity;
- accessibility;
- recovery;
- evidence;
- beneficial reach;
- contribution readiness.

Dampen:
- overload;
- coercion;
- false certainty;
- dependency;
- noise;
- framework sprawl;
- unsafe urgency.

`AMP_NE_MAXIMIZE_EVERYTHING`

## Betterment vector

Prefer changes that increase:

`CAPABILITY + RECOVERY + OPTIONALITY + INDEPENDENCE + FAIRNESS + CURRENTNESS + RECEIVER_FIT + UX + LEARNING_RETURN`

while reducing:

`HUMAN_RELAY + CAPTURE + FRAGILITY + COST + EXTERNALITY + PRIVACY_RISK + MAINTENANCE_DEBT + PROOF_DEBT + STALENESS_DEBT`

No scalar score overrides consent, rights, authority or safety.

## CoOmni operating equation

```
NEED
<-> CAPABILITY
<-> RESOURCE
<-> RECIPE
<-> AUTHORITY
<-> PROOF
<-> WAKE
<-> LEARNING
```

with:

```
wide address space
-> tiny elected frontier
-> leased embodiment
-> measured effect
-> reusable receipt/recipe
-> release
-> sleep
```

This is how CoOmni can compound without requiring literal infinite compute.


## R1 bounded local reference compiler (2026-10-25)

An **isolated dependency-free Python 3 reference compiler** was tested against a wholly synthetic 9-object context corpus. It binds exact source SHA-256 digests and a manifest identity; filters by declared worker privacy class (illustrative classification, **not authentication**); elects a small packet while retaining a CHALLENGE and a DELTA lane; enforces byte budgets and source path/symlink rejection; checks exact local source rehydration; and performs **zero** network calls or external effects.

Bounded test evidence: **38/38 PASS** after a retained initial test-expectation FAIL; 7 public-eligible sources containing 4,702 raw bytes, 3 source-linked selections in a **1,287-byte packet** under a 1,500-byte limit. Four 300-packet batches on Linux Python 3.13 measured median amortized **0.573 ms per packet**. This is representation-size reduction, *not* measured tokenizer savings, semantic answer improvement, independent user benefit or context-window extension.

[Scoped machine FAIL/PASS/HELD ledger](../../ai/benchmarks/coomni-context-r1/benchmark_evo.jsonl) records exact package/script SHA-256 and limitations. The ZIP source package is attached to the originating private conversation and verified **locally**, **not published into this GitHub repository, not landed on CoStead, and not installed on X2**. X2's connected Desktop Commander path was offline at the last check. Future source publication should use a reviewed repository branch, preserving byte-identity and third-party rights.

**Next acceptance:** compare one authorized real task using its full source versus the smaller source-bound packet. Measure exact factual recall, hallucinations, latency, model tokenizer usage, correction burden, source recovery, confidentiality and cost. A receiver must independently accept its own packet and produce readproof; local verification is not receiver pickup.

LOCAL_SOURCE_VERIFICATION_NE_DURABLE_LANDING | SUMMARY_NE_SOURCE | BYTE_REDUCTION_NE_MODEL_TOKEN_EXTENSION | SOURCE_HASH_NE_SOURCE_TRUTH | STATIC_TEST_NE_X2_RUNTIME | POINTER_NE_ACK.
