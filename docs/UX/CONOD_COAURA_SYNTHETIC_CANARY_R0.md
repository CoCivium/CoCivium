# CoNod+ / CoAura+ Synthetic Product Canary R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__SYNTHETIC_ONLY__NO_RUNTIME_CANON_OR_PUBLIC_RELEASE_APPROVAL`  
**CoCivium base observed:** `7b08c68bae6ec76c33d70eabbd5afa1a2e41429b`  
**CoAura master observed:** `7326ad5812d4d3954fc7add29afc25831594fda6`

## Purpose

Turn the current CoNod/CoAura architecture into one bounded, testable product canary without claiming runtime integration.

The canary models one synthetic CoNod:

`' -> one maximal safe bounded CoWave -> visible CoAura fan-out/fan-in -> quiet`

It deliberately uses synthetic identities and synthetic work lanes.

## User-visible story

A small synth CoAvNim sits beside a participant-relative bar.

When a CoNod is received:

1. the CoAura wakes;
2. logical lanes appear as restrained orbiting/branching marks;
3. a smaller number of physical-work marks materialize;
4. challenge/evidence relations become visible;
5. fan-in arcs contract toward a compact result;
6. unresolved conflicts remain visible;
7. the aura settles back to quiet;
8. the human sees one compact receipt and can expand evidence.

The human is not asked to manage individual workers.

## Synthetic state sequence

```text
QUIET
  -> ACK_REWISE
  -> REBIND
  -> FANOUT_LOGICAL
  -> MATERIALIZE_ADAPTIVE_WIDTH
  -> WORKING
  -> FANIN
  -> COMPACTING
  -> RECEIPT
  -> QUIET
```

## Required visual relations

The canary should expose only semantic projections with machine twins:

- current state;
- currentness;
- logical lane count;
- materialized physical width;
- fan-in pressure;
- evidence returned;
- unresolved challenge count;
- CoPressure;
- CoEnerget;
- true human gate if any;
- stop/revoke control if an effectful implementation later exists;
- compact receipt.

## Cognitive projection classes

Allowed in the canary:

- `DECLARED_INTENT`
- `SURFACED_REASONING_SUMMARY`
- `HYPOTHESIS`
- `OPTION`
- `UNCERTAINTY`
- `QUESTION`
- `CHALLENGE`
- `PLAN_STATE`
- `TOOL_EVENT`
- `WORK_LANE`
- `EVIDENCE_SIGNAL`
- `CURRENTNESS_SIGNAL`
- `MODEL_SUMMARY`
- `INFERRED_STATE` only when visibly qualified
- `PREDICTED_NEXT` only when visibly qualified
- `UNKNOWN`

Forbidden field:

- raw/private hidden chain-of-thought.

`COGNITIVE_PROJECTION_NE_HIDDEN_CHAIN_OF_THOUGHT`

## Parallelity fixture

The paired machine fixture uses:

- 32 logical lanes;
- 6 materialized physical workers;
- 4 challenge lanes;
- 8 evidence lanes;
- 4 provenance/currentness lanes;
- 4 UX/accessibility lanes;
- 4 CoTheoryAll/CoMythOps relation lanes;
- 4 compaction/fan-in lanes.

This demonstrates:

`LOGICAL_PARALLELITY_GT_PHYSICAL_WIDTH`

without asserting that either number is optimal.

## CoOomph+ behavior

The canary must be able to project a width change caused by synthetic backpressure:

```text
width 6
 -> fan-in pressure HIGH
 -> width 3
 -> compaction increases
 -> fan-in pressure NORMAL
 -> width 5
```

This is a visualization/contract fixture only.

`COOOMPH_NE_MAX_COMPUTE`

## CoLUE+ acceptance

The front door should require one human gesture and no worker-by-worker management.

Acceptance target:

```text
HUMAN_ACTIONS_FOR_WAVE = 1
WORKER_MANAGEMENT_ACTIONS = 0
EVIDENCE_DRILLDOWN = OPTIONAL
```

`MORE_MACHINE_WORK_NE_MORE_HUMAN_CLICKS`

## CoAckRewise+ projection

The aura may briefly show that the human gesture was interpreted, for example:

`' -> BOUNDED_CONTINUATION / NO_AUTHORITY_EXPANSION`

It must not visually imply that acknowledgement equals acceptance, adoption or unrestricted consent.

`COACKREWISE_NE_AUTHORITY_PROMOTION`

## CoTime+ projection

The canary must keep distinct:

- gesture issue time;
- observation time;
- fan-out time;
- lane event times;
- fan-in time;
- receipt time.

A timeline scrubber may replay the synthetic wave.

`ISSUED_TIME_NE_OBSERVED_TIME_NE_EFFECT_TIME`

## CoMeteo+ / CoSignal+ / CoSong+ optional projection

Optional visual mapping:

- pulse = material state change;
- orbit = active relation;
- front = approaching collision;
- fog = low observability;
- rhythm = fan-out/fan-in cadence;
- weather = aggregate field condition.

These remain presentation metaphors.

`METAPHOR_NE_MECHANISM`

## Accessibility

The same canary requires:

- reduced-motion mode;
- static text state;
- screen-reader labels;
- non-colour-only cues;
- low-bandwidth mode;
- machine-readable twin.

`GRAPHIC_NE_ONLY_INTERFACE`

## Acceptance checks

A conforming prototype should prove, using only synthetic state:

1. one CoNod can represent one bounded CoWave with more logical lanes than physical workers;
2. width can change without changing authority;
3. fan-in and unresolved conflict remain visible;
4. the aura can settle to quiet;
5. every visual state has a machine-readable relation;
6. every important visual state has a text/accessibility equivalent;
7. no hidden chain-of-thought field exists;
8. no visual cue is treated as cryptographic identity or authority;
9. the same relation object can render differently for different observer/accessibility profiles;
10. the canary can be replayed from its synthetic fixture deterministically enough for UI testing.

## Destination relation

Current CoAura repository semantics already define CoAura as the renderable AI-first interface envelope and elect CoAura as a CoUX/CoSurface evolution laboratory.

Therefore this canary is a candidate donor for a future **CoAura receiver PR**, not proof that CoAura has picked it up.

`COAURA_TARGET_NE_COAURA_PICKUP`  
`PROJECTION_NE_OBJECT`

## Nonclaims

- no X2 execution;
- no MCP pickup;
- no PS7 execution;
- no real participant data;
- no hidden reasoning access;
- no runtime;
- no canon;
- no public product release approval;
- no authority transfer.
