# CoAll+ Golden Braid: one-input / two-local-receiver canary R0

**State:** SYNTHETIC_SAME_RUNNER_TRANSPORT_CANDIDATE__NOT_CROSS_SURFACE_DELIVERY__NOT_HUMAN_ACCEPTANCE__NOT_ALWAYS_ON

**Primary tracker:** [CoAll issue #317](https://github.com/CoCivium/CoCivium/issues/317).  
**Existing source donor:** [CoEvoShared+ draft delta](../../ai/evolution-deltas/2026-10-26/coevo-shared-draft-bridge-r0.json) from draft PR #305.  
**Existing mechanics to reuse later:** [CoSession write-back/fan-in R1](../../docs/Evolution/COSESSION_WRITEBACK_FANIN_R1.md) and the existing `CoEvoReceiverFanoutPlanner.py` / `CoEvoReceiverPacketCompiler.py`.

## Purpose

A large supply of ideas and "wise words" is useful only when the system can qualify, relate, route, verify, preserve, reuse and retire them without losing provenance, overriding consent or swamping its owners. This canary tests **only the first transport/recovery slice**: reuse one real, already source-controlled public-safe CoEvoDelta as a synthetic input; copy the exact bytes to two different local test directories; have a separate local test process read each destination and write its own bounded readback; deliberately fail destination beta once; replay without duplicating alpha; and reconstruct the status in a fresh process.

Do **not** interpret the two folders as independent providers, humans, other ChatGPT sessions, two machines or CoStead. The controller and both "receiver" processes run on **one GitHub runner** and share its filesystem. A separate process is not an independently governed receiver.

## Reader/writer stages

1. `SOURCE`: the exact checked-in CoEvoShared+ delta, expected Git blob SHA-1 `e0cc145c692c3615b277b8457d924da5d8a46000`, remains the only semantic machine source. No rival wisdom ontology is created.
2. `QUALIFY`: require public confidentiality, proposal-only authority, source references, evidence class and known delta identity. Anything private, unproven or effect-bearing fails before routing.
3. `PACKET`: bind original source bytes/length, SHA-256, delta ID, two named test destinations and authority `SAME_RUNNER_SYNTHETIC_ONLY` in `packet_manifest.json`.
4. `ATTEMPT`: write exact bytes at most once to each local destination. Identical replay is a no-op; conflicting content is **HELD**, never overwritten.
5. `RECEIVER READBACK`: use a separate Python process to inspect its local inbox and create a per-destination same-runner receipt. The receipt *never* claims external delivery, human pickup or authority.
6. `FAIL+RECOVER`: inject beta failure before writing; observe alpha's receipt and beta's `ABSENT` state; retry beta; verify alpha was not duplicated.
7. `FRESH-PROCESS STATUS`: a newly launched process reconstructs both receipts from files alone and reports `cross_surface_integration: UNPROVEN`.

The pipeline exercises finite, deterministic mechanics. It neither reads nor writes inboxes, OS devices, Substack, agents, private CoStead storage, X2 or real destination APIs.

## Commands

From the repository root:

```sh
python3 -m unittest discover -s examples/coall_golden_braid_r0 -p 'test_*.py' -v
python3 examples/coall_golden_braid_r0/canary.py demo --workspace /tmp/coall-golden-braid-r0
python3 examples/coall_golden_braid_r0/canary.py status --workspace /tmp/coall-golden-braid-r0
```

For the demo, use a **new empty workspace**; it deliberately does not overwrite previous evidence. GitHub Actions runs the tests and publishes its synthetic result and separate receiver receipts as **CI evidence artifacts**, not as an externally landed CoEx receiver result.

## CoOrb+/CoAll+ evolution projection (not implemented dashboard)

A read-only CoOrb view could show:
- **source**: exact bytes/version, source scope, evidence type, provenance, conflicts;
- **transport**: per-destination attempt, local inbox state, local readback and independently verified receiver state as separate fields;
- **evolution**: benefit hypothesis, next falsifier, cost/maintenance owner, renewal or retirement criterion;
- **health**: stale source, consent/revocation, unowned work, impossible promise, duplicate lineage or no receiver;
- **status**: `PROPOSED` / `LOCAL_SYNTHETIC` / `HELD` / `INDEPENDENT_RECEIVER_VERIFIED` (only with actual receiver-origin evidence);
- **impact**: real human time saved, recurring handoffs eliminated, independent first-use completions and cost, not counts of words/ideas.

The "wise-words" intake policy remains: `DISCOVER -> QUALIFY -> RELATE -> CHALLENGE -> TEST -> PRODUCE -> RECEIVER -> LEARN -> EVERGREEN / RETIRE`. Preserve useful dissent, nulls, negative findings and provenance. CoEnerget+ should track maintenance/compute energy and cost; CoTurtle+ tests claimed compounding; G_d remains stewardship/metaphor/hypothesis unless separate empirical evidence supports a mechanism.

## Acceptance and promotion

This R0 can pass **same-host synthetic data-transport, replay, no-clobber and fresh-process status reconstruction**. It cannot satisfy issue #317's wider independent route/currentness or cross-session acceptance requirements.

The next promotion requires two **actually authorized, independently scoped** destinations and a receiver-origin exact-object acknowledgment for each, followed by a real failure/recovery demonstration and replay from a new session without manual relay.

`WISDOM_CANDIDATE_NE_TRUTH | INTAKE_NE_INTEGRATION | FANOUT_ATTEMPT_NE_DELIVERY | LOCAL_READBACK_NE_RECEIVER_ACK | GROWING_KNOWLEDGE_NE_UNBOUNDED_COMPUTE | SOURCE_IS_NOT_RECEIVER | COORB_PROJECTION_NE_RUNTIME | PERMISSION_NE_PERPETUAL_AUTHORIZATION`
