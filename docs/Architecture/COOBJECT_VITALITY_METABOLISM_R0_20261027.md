# CoObject+ Vitality / Metabolism R0

**State:** BOUNDED_SYNTHETIC_VITALITY_CANARY__NO_ALWAYS_ON_DAEMON__NO_RUNTIME_ADOPTION  
**Observed:** 2026-10-27  
**Parent:** `docs/Architecture/COFRACTAL_ENERGETIC_METABOLISM_SUPERFRAME_R0_20261027.md`

## Lead

The existing CoFractal Energetic Metabolism Superframe already defines the right inheritance surface:

`SENSE | INTAKE | TRANSFORM | STORE | ROUTE | SHARE | AMPLIFY | DAMPEN | RETURN | REPAIR | WAKE | SLEEP | SPLIT/MERGE/SUCCESSOR | RETIRE`

R0 turns that into a small machine-readable **CoObject Vitality Envelope**.

"Alive" is an engineering metaphor for:

- addressable identity;
- explicit currentness;
- observable health;
- typed metabolic capabilities;
- wake/sleep rules;
- repair path;
- successor path;
- evidence and authority boundaries.

It is **not** a claim of biological life, consciousness, sentience, subjective experience, or perpetual execution.

`VITALITY_NE_SENTIENCE`  
`LIVENESS_NE_PERSISTENCE`

## Heartbeat relation

The useful heartbeat is not constant chatter.

A vitality pulse is emitted only for a material lifecycle/currentness relation such as:

- object first qualified;
- meaningful health/currentness change;
- lease expiry/renewal when a lease matters;
- wake predicate fires;
- transition to sleep/dormancy;
- repair starts/completes;
- successor becomes ready;
- retirement/supersession.

Default:

`NO_MATERIAL_DELTA -> NO_HEARTBEAT_NOISE`

A heartbeat says only that a bounded observation was made at a time under a declared evidence class.

It does not prove continued liveness after that observation.

`HEARTBEAT_NE_CHATTER`  
`OBSERVED_ALIVE_NE_STILL_ALIVE`

## Vitality envelope

Candidate minimum:

```
object_id
object_class
source_ref
lifecycle_state
currentness_state
health_state
authority_ceiling
confidentiality
metabolism {
  sense
  intake
  transform
  store
  route
  share
  amplify
  dampen
  return
  repair
  wake
  sleep
  successor
  retire
}
known_debt
wake_predicates
wake_observations
last_material_delta
evidence_refs
```

## Liveness classes

R0 uses:

- `ACTIVE_WORKING`
- `QUIESCENT_CURRENT`
- `DORMANT_WITH_WAKE`
- `DEGRADED_REPAIRABLE`
- `RETIRING`
- `RETIRED`
- `UNKNOWN_CURRENTNESS`

A dormant object may have very high option value while consuming almost no active resources.

`DORMANT_NE_DEAD`  
`ADDRESSABLE_NE_ACTIVE`

## Amplification

CoAmp must be typed.

Possible beneficial amplification:

- useful effect;
- reuse;
- recovery;
- evidence quality;
- receiver understanding;
- optionality;
- failure detection;
- learning;
- independence.

Possible deliberate damping:

- noise;
- duplicate work;
- attention demand;
- risk;
- stale relations;
- proof debt;
- lock-in;
- unnecessary wake frequency.

Therefore:

`AMPLIFY_NE_ALWAYS_INCREASE_ACTIVITY`

Sometimes the best amplification action is to damp, sleep, compact, substitute, split, or retire.

## Turtle traversal

A CoTurtle may traverse:

```
object -> relation -> gap -> dependency -> receiver -> substitute -> successor
```

and may ask each addressable object for its vitality envelope.

This does not materialize every object or broadcast to every object.

`TURTLE_TRAVERSAL_NE_MATERIALIZE_ALL`  
`ALL_TO_ALL_NE_BROADCAST_ALL`

"All-to-all / each-to-each" is interpreted as **relation addressability**, subject to:

- currentness;
- relevance;
- confidentiality;
- authority;
- cost;
- backpressure;
- receiver fit;
- wake rules.

## CoPulse relation

When a material vitality delta exists, it can be represented as a CoPulse-class relation delta.

Candidate pulse fields:

```
pulse_id
subject=object_id
relation_type=VITALITY_DELTA
epistemic_class=OBSERVED
observation_time
currentness
health
lifecycle_transition
wake_transition
evidence_refs
authority_ceiling
confidentiality
```

This reuses CoAllPulseField rather than creating a separate global heartbeat bus.

`PROTOCOL_NE_ONTOLOGY`

## Rick / human boundary

Humans are not required to provide routine heartbeat.

`RICK_NE_HEARTBEAT`

Human attention is raised only for a material gate that actually requires human authority/information and has no safe alternate path.

## First bounded proof

Use three unlike public-safe objects:

1. **software component** — CoBaseline frontier evaluator;
2. **publication / UX object** — CoGbx universal UX exemplar;
3. **dormant high-option concept** — CoGbx peer/federated reconstruction candidate.

All three implement the same metabolic interface.

PASS requires the interface to produce distinct useful dispositions:

- software: continue one bounded extension because real benchmark ingestion is still debt;
- publication: remain quiescent and wake on receiver/accessibility evidence rather than emitting routine work;
- dormant concept: remain dormant until exact peer/readproof prerequisites exist.

The canary must also prove:

- every object has identity, currentness, health, wake, sleep, repair, successor and retire semantics;
- no object gains an unproven capability merely by inheriting the interface;
- no fixed-frequency heartbeat is required;
- zero external effects occur.

## Rails

`VITALITY_NE_SENTIENCE`  
`LIVENESS_NE_PERSISTENCE`  
`HEARTBEAT_NE_CHATTER`  
`OBSERVED_ALIVE_NE_STILL_ALIVE`  
`DORMANT_NE_DEAD`  
`ADDRESSABLE_NE_ACTIVE`  
`AMPLIFY_NE_ALWAYS_INCREASE_ACTIVITY`  
`TURTLE_TRAVERSAL_NE_MATERIALIZE_ALL`  
`ALL_TO_ALL_NE_BROADCAST_ALL`  
`CAPABILITY_NE_AUTHORITY`  
`INTERFACE_INHERITANCE_NE_CAPABILITY_PROOF`  
`RICK_NE_HEARTBEAT`  
`NO_MATERIAL_DELTA_NE_WAKE`  
`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
