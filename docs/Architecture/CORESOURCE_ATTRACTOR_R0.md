# CoResourceAttractor+ R0

**State:** CANDIDATE_ARCHITECTURE__PUBLIC_WORKING_NOTE

## Purpose

Make useful resources increasingly findable, qualifiable, composable, optional, reusable, challengeable, and recoverable without pretending every possible resource is known or that every relation is material/physical.

`CoResourceAttractor+` is not a mystical force. It is a design pattern for increasing the probability that a useful resource is discovered and correctly connected to work that can benefit from it.

## Core flow

`UNKNOWN -> DISCOVERED -> DESCRIBED -> QUALIFIED -> COMPOSABLE -> OPTIONAL -> SELECTED -> USED -> RECEIPTED -> REEVO`

Every transition is evidence-bearing. A pointer, mention, similarity, model suggestion, or public URL is not qualification or adoption.

## Resource descriptor

A resource may be a file, repository, model, tool, person, service, device, dataset, test, renderer, workflow, hypothesis, representation, historical artifact, or other bounded object.

Each descriptor SHOULD carry:

- resource_id
- class
- source / provenance
- currentness
- authority / consent boundary
- capabilities
- interfaces
- constraints
- cost / resource demands
- privacy class
- locality
- dependencies
- evidence strength
- failure modes
- known alternatives
- optionality / exit path
- lifecycle state
- hashes / immutable references where applicable
- receiver relevance
- relations to other resources

Unknown values stay unknown.

## CoAttractorPull+

A resource becomes more attractable when it has:

1. strong descriptors;
2. stable identifiers;
3. machine-readable interfaces;
4. reproducible tests;
5. low-friction adapters;
6. clear provenance;
7. explicit constraints;
8. independent evidence;
9. cheap discovery indexes;
10. reversible integration;
11. export / fork paths;
12. historical lineage.

The pull is therefore informational and operational, not evidence of a new physical field.

## CoCopy+ / CoThumb+

A user gesture such as a middle/thumb mouse control MAY become a bounded resource action surface.

Candidate actions:

- capture selected object + provenance;
- copy as canonical resource packet;
- copy as citation;
- copy as task input;
- copy as experiment seed;
- copy relation only;
- send to local queue;
- fork locally;
- inspect alternatives;
- compare historical/current;
- generate receipt.

Default action should be reversible and visible. No hidden outward broadcast.

## CoGlukey+

Development/build descriptors can form reusable relation keys:

`capability x interface x evidence x environment x authority x currentness`

A CoGlukey is useful only if it improves lookup, composition, or verification. It must not become decorative ontology debt.

## CoTurtle+ relation

Every resource selector can itself be evaluated:

`resource -> descriptor -> selector -> selector benchmark -> challenge -> receipt`

Recursive selection is bounded by aggregate budget, authority, and marginal value.

## CoStretch+ relation

Max stretch means maximizing useful frontier discovery per scarce resource, not maximizing raw utilization.

Prefer:

`cache/deterministic -> tiny local -> strong local -> remote -> frontier -> human gate`

Do not spend expensive intelligence on a question a cheaper turtle can settle.

## Resource classes

Demonstrated classes:
- software
- files
- repositories
- devices
- models
- tools
- tests
- data
- people/roles with consent
- services
- historical artifacts
- renders / representations

Experimental classes:
- synthetic environments
- alternative representations
- counterfactual resources
- anti-resources / negative evidence
- null resources / explicit absence
- hypothetical substrates

Speculative/non-material language such as `CoSpirit+` MAY exist as a representation or hypothesis class. It MUST NOT be promoted to a demonstrated physical mechanism without independently reproducible evidence.

## Null / anti / alternative resources

Absence can itself be useful:

- NULL: expected resource is unavailable or intentionally absent;
- ANTI: evidence against a candidate/resource relation;
- ALTERNATIVE: substitute resource with different tradeoffs;
- COUNTERFACTUAL: resource used only in simulation;
- DEPRECATED: historical resource retained for lineage;
- BLOCKED: potentially useful but unavailable under current authority/access.

These states reduce repeated rediscovery and improve routing.

## Million-session relation

Prefer vast logical resource/session populations with a small active frontier.

`large addressable reserve -> evidence-backed selector -> bounded workers -> receipts -> dormancy/reuse`

No fake-human swarms, rate-limit evasion, covert account farms, or uncontrolled provider spend.

## Historical ReEvo

Historical resources remain immutable inputs. Current successors are compared against pinned predecessors.

A newer model, agent stack, or adapter earns promotion only through measured improvement without unacceptable regressions.

## High-bar tests

Candidate resource-attractor experiments SHOULD measure:

- discovery precision / recall on a fixed corpus;
- time-to-qualified-resource;
- duplicate suppression;
- stale-resource rejection;
- alternative recovery after failure;
- cost / latency / energy where measurable;
- independent reproduction;
- correct authority handling;
- graceful loss of provider/device/network;
- receiver value;
- reduction in unnecessary human relay.

## Working values

LoLs = lots of layers, laughs, love, learning.
Pay forwards + sideways.
FOSS Forever.
CoGoAll.
Working Together Respectfully.
Privacy-by-design.
Inclusive, respectful, optional participation.
Display required where evidence/identity status must be visible; wear optional.
FFFF / zero holdings is a design phrase, not an audited financial state.

## Rails

`FINDABLE_NE_QUALIFIED`
`RELATED_NE_CAUSAL`
`MODEL_SUGGESTION_NE_EVIDENCE`
`POINTER_NE_ACK`
`OPTIONAL_NE_ACTIVE`
`SPECULATIVE_NE_PHYSICAL`
`LOGICAL_SCALE_NE_LIVE_SCALE`
`NEWER_NE_BETTER`

## Next bounded deed

Build a deterministic resource-descriptor scorer over a small public corpus, compare against random/keyword-only selection, and write PASS/FAIL/HOLD to `ai/benchmark-evo.jsonl`.
