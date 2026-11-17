# CoTalkItOut+ | Human-Optional Operations R0 (public-safe candidate)

**As of:** 2026-11-12. **State:** DESIGN_CANDIDATE / REVIEW_ONLY. This document is **not** a runtime, public-launch authorization, installed input system, independent receiver acknowledgment, accessibility certification, or account/provider migration.

## Outcome

A person should be able to let permitted routine work continue without keeping a ChatGPT conversation, screen, keyboard, mouse, or one particular device running. Each interaction surface remains optional, accessible, reversible, privacy-respecting, and available when useful. Eliminating the need for manual session tending is the objective, not eliminating human control or accessibility.

## Causal order

1. **Quiet interaction:** Identify actual focus/input interruptions and the responsible launcher or event. Fix one source with a reversible test, not another polling daemon.
2. **Durable intent and state:** WorkID, source revision, authority, inputs, evidence, checkpoints, idempotency keys, next wake and stop condition survive the originating tab or model.
3. **Independent custody:** Preserve enough durable information and lawful recovery keys to reconstruct the work when a host, storage device or provider is unavailable.
4. **One elected execution path:** Read-only and independently scoped work may run in parallel; conflicting effects require one fenced actuator. A model answer is not effect authority.
5. **Crash/replay safety:** A crash after a possible external effect must produce receiver verification or explicit HOLD, not an automatic repeat.
6. **Real receiver acceptance:** Distinguish created, tested, committed, published, picked up, independently accepted and beneficial.
7. **Replaceable capabilities:** Qualify deterministic code, local/open models, and optional hosted models per task, privacy, cost, capability, licensing and failure domain.
8. **Headless worker:** Run a single authorized harmless task without a foreground UI, while retaining traceable status and a safe stop path.
9. **Optional multimodal interaction:** Keyboard, pointer, touch, voice, switches, screen reader and audio are alternative interfaces to the same semantic task and authority, not separate state owners. Use documented operating-system accessibility donors before rebuilding them.
10. **User-optional pilot:** Prove unattended continuation, interruption recovery, safe refusal and lower measured human burden through a representative trial with rollback.

## One logical name; not one mutable file

- **Semantic key:** `WorkID + artifact_kind`. It identifies the work independently of filenames, vendor sessions, models and devices.
- **Immutable revision:** `artifact_kind_R<revision>_<date>` plus content hash, exact source revision and predecessor reference. A parallel proposal can fork without clobbering the accepted head.
- **Public orientation path:** a stable, reviewed pointer resolves to the *accepted* revision. Do not make newest-wins the definition of current.
- **Private evidence:** unreleased internal planning, credentials, personal records, private communication, protected datasets and unverified security-sensitive information stay in their proper access domains.
- **Public-safe twin:** publish only the reviewed, lawful, accessible explanation/test case. Publication does not promote private evidence to public authority.
- **Collision rule:** parallel readers/proposers allowed; shared mutations require source-bound currentness, an elected writer, predecessor comparison and exact readback.

## Publication acceptance

`DISCOVER -> CLASSIFY -> DEDUPE -> SOURCE_BIND -> REVIEW_RIGHTS_PRIVACY -> BRANCH -> VERIFY -> APPROVE -> PUBLIC_WRITE -> EXTERNAL_READBACK -> UPDATE_ACCEPTED_POINTER -> MONITOR_STALE`

Any uncertainty in privacy, rights, currentness, authorization or external effect leads to HOLD. No global model/session agreement, number of comments or shared filename substitutes for authorization or independent evidence.

## Failure tests that matter

- Concurrent writers target the same logical filename and try to overwrite one another.
- A publication candidate accidentally includes private evidence or source paths.
- A newer source is unreviewed but a status screen calls it current.
- An external effect occurred before a crash but no acknowledgment was journaled.
- A model claims a receiver accepted a result without the receiver's evidence.
- A no-work condition is mistaken for proof that interrupted work was reconciled.
- A supposedly headless diagnostic steals keyboard focus.
- A voice-only mode disables an accessible fallback or ignores withdrawn mic consent.
- A provider quota, a local power failure or a GitHub outage removes the only surviving work state.

## Metrics, not decorative progress

Measure: independent useful outcomes, recovery success and time, human manual touches, duplicated or missed effects, source freshness, accessibility task completion, interruption rate, privacy incidents, cost, proof debt, and improvement-cycle overhead. Without matched observations report UNKNOWN, not zero or success. A benchmark or isolated test does not prove product deployment.

## Existing public anchors

- [CoAll evergreen cross-repo currentness](https://github.com/CoCivium/CoCivium/issues/24)
- [CoAll one-input and source/receipt verification](https://github.com/CoCivium/CoCivium/issues/317)
- [CoBar/RickBar receiver acceptance](https://github.com/CoCivium/CoCivium/issues/453)
- [CoDesktop productization](https://github.com/CoCivium/CoCivium/issues/181)
- [CoSurface multimodal projections](https://github.com/CoCivium/CoCivium/issues/178)
- [RickBar continuity candidate](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/RICKBAR_CONTINUITY_R1_20261108.md)

**Boundary:** This is a public-safe architecture *proposal*. No source-only candidate is promoted to canon, installed runtime, live session synchronization or public service adoption. An immutable Git revision is useful custody, not sole or independent failure-domain recovery.
