# CoSession Projection to CoEvo Compiler R0

**State:** `PUBLIC_CANDIDATE__DETERMINISTIC_COMPILER__ZERO_TARGET_EFFECTS`

## Purpose

This is the executable rung between a session-friendly relational projection and the canonical CoEvoDelta+ evolution fabric.

It consumes `schemas/cosession-relational-delta-v0.2.schema.json` and emits one `CoEvoDelta v0.2` candidate per typed operation.

The compiler does not decide whether an idea is observed, inferred, hypothetical, preferred, metaphorical, mythic, humorous, or otherwise. The session projection must say so explicitly.

`UNDER_TYPED_INPUT_NE_SAFE_TO_INFER`

## Required semantic bindings

The v0.2 session projection requires:

- `projection_of = CoEvoDelta+`;
- `confidentiality`;
- one or more target domains;
- explicit `epistemic_class` per operation;
- explicit `mutation_class` per operation;
- authority ceiling;
- public-safety class;
- intended next receiver;
- next gate.

Current-base and receiver-readproof bindings remain optional in the schema but emit review flags when absent.

## Deterministic mapping

Each operation becomes a child CoEvoDelta candidate with:

- a stable parent-derived child ID plus operation hash;
- source session and observed time;
- sorted domain and target-surface projections;
- subject, relation, object and typed operation;
- explicit epistemic and mutation class;
- merged source/evidence refs;
- confidentiality and public-safety qualifiers;
- current-base, collision, next-receiver and readproof relations;
- exact source projection file SHA-256;
- exact source projection ID, record index, operation index and operation SHA-256.

No target surface is mutated by the compiler.

## Bounded canary

The exact candidate bytes were executed locally before landing.

Fixture:
`docs/Operations/fixtures/cosession-to-coevo-r0-input.json`

Observed result:

- input SHA-256: `4737C0984760D61865D66A06ACF0E49D427174222DD1790C2C277687D8684E2B`
- accepted projection records: 2
- compiled CoEvoDelta candidates: 3
- rejected records: 0
- review flags: 0
- canonical compiled SHA-256: `9A790C7915791B7DB4B979C149AC02B9EA4A6CBA331E0AFEF2928609B5E57BB2`
- rendered output file SHA-256: `E360269720683F917A7DAAEC08B759CB263B3E7A9687BDEFF0B7CC3D0F16CD5C`
- same fixture bytes at a second filesystem path produced byte-identical output: PASS
- v0.2 projection schema validation: PASS
- v0.2 CoEvo output schema validation: PASS

Negative canary: an operation lacking `epistemic_class` produced zero compiled deltas and one rejected record.

This proves bounded mechanical behavior for these fixtures. It does not prove semantic truth, receiver pickup, integration, correct target fanout, or canon.

## Effects

The output declares zero:

- target-surface mutations;
- automatic fanout;
- integration claims;
- receiver-pickup claims;
- canon changes.

## Receiver-relative fanout now implemented

The next planning rung now exists as [CoEvoReceiverFanoutPlanner R0](COEVO_RECEIVER_FANOUT_PLANNER_R0.md), with [reference implementation](../../scripts/CoEvoReceiverFanoutPlanner.py) and [machine output schema](../../schemas/coevo-fanout-plan-v0.1.schema.json).

It proposes both repository receiver routes and HOT/WARM/DIGEST session-profile interest while performing zero target mutations or provider-session pushes.

## Next gate

`BIND_TARGET_HEADS + BIND_RECEIVER_INSTANCES + REVIEW_HOLDS -> ELECT_BOUNDED_RECEIVER_PACKETS`

The next implementation should compile exact receiver packets only for already-bound targets/instances, preserving delivery != pickup and exact readproof before any receiver-uptake claim.

## Rails

`COMPILATION_NE_ACCEPTANCE`  
`COMPILATION_NE_FANOUT`  
`COMPILATION_NE_INTEGRATION`  
`DELIVERY_NE_PICKUP`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`MERGED_NE_CANON`
