# CoTalkItOut+ | Screen-optional autonomy R1 (2026-11-12)

**Status: PUBLIC-SAFE PLANNING CANDIDATE.** It is not a deployed worker, canonical control plane, X2 repair, CoEx, real receiver ACK or product release.

## Why this revision exists

An existing privately held R0 spreadsheet defines 128 design operations and 139 edges, all classified as mandatory precedence. **The exact R0 graph contains a strongly connected cycle spanning 41 operations** (phases 08-13); therefore its mandatory execution order is impossible as written. The predecessor is preserved. R1 adds 56 *coarser proof milestones*, a separate acyclic typed dependency graph, explicit human gates, and comparisons of incumbent systems. Neither count is deployed throughput.

The R1 mandatory graph has 120 edges, 7 independent roots, and a longest structural chain of 12 milestone nodes. R0 has no valid mandatory critical path until its cycle is resolved. These are *planning relationships*, not elapsed time or delivered capability.

## CoGlyphRail | One useful task first

1. Keep X2 keyboard/mouse input quiet. No new popup-generating watchers while [existing #181](https://github.com/CoCivium/CoCivium/issues/181) incident containment is being qualified.
2. Reuse [CoOwnedWork #450](https://github.com/CoCivium/CoCivium/issues/450) and the [existing fenced SQLite queue](https://github.com/CoCivium/CoCivium/blob/main/examples/cotalkitout/due_work_catchup_r0.py) for one small WorkID.
3. Make a missed scheduled wake recover overdue work **exactly once** on a later authorized wake, with an independent receiver-origin readback. [CoGoAll #317](https://github.com/CoCivium/CoCivium/issues/317) remains the owner.
4. Link that useful effect to the native [CoBar/CoSpeedo #453](https://github.com/CoCivium/CoCivium/issues/453), including true source freshness, Stop, recovery and human first-use acceptance.
5. Test actual reboot and different-failure-domain cold recovery before demoting chat/provider sessions. [CoFrontierExit](https://github.com/CoCivium/CoCivium/blob/main/docs/Operations/COFRONTIEREXIT_GRACEFUL_PIVOT_R0_20261112.md) remains proof gated.
6. Keep the same WorkID available as typed headless data, native/visual interface, and optional voice/hardware input, rather than removing all fallback surfaces.

## Parallel work that should **not** block the above

- Evidence/cadence audits and CoNeedle denominator design.
- [CoModelFabric](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md) local-model qualification on a harmless benchmark, after foreground safety.
- Optional screenless voice, privacy and accessibility research, without live microphone activation.
- [CoOomph fan-in #467](https://github.com/CoCivium/CoCivium/pull/467) independent-proposal benchmarking without multiple effect writers.
- Public-safe source discovery and consumer pickup measurements.

## Public-safe publication protocol

The correct shared interface is **one stable public index path with a versioned, content-addressed object behind it**, not the same filename written concurrently by many ChatGPT sessions. Public data is an explicit non-sensitive projection; private prompts, contacts, exact local paths, credentials and raw session content remain private. Only an elected writer may update a shared index after predecessor/currentness comparison. Every external consumer must independently read and acknowledge an exact source object before `PICKED_UP` can be claimed. The present document itself is only source discovery, not a broadcast ACK.

## Comparison: fit, not a silver bullet

| System | Reusable idea | What it cannot prove for CoAll by installation alone |
| --- | --- | --- |
| [Temporal](https://docs.temporal.io/tasks) | Durable Task Queues, timers, activities, retries | CoAll authority, human UX, independent useful effect |
| [Windmill](https://www.windmill.dev/docs/core_concepts/worker_groups) | Worker/job queues, scripts, schedules, approvals | Correctly attributed CoAll WorkID; not every late schedule tick is replayed |
| [n8n](https://github.com/n8n-io/n8n-docs/blob/main/docs/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode.md) | Workflow/integration fabric and queue workers | Receiver-origin provenance and safe dedupe without design |
| [LangGraph](https://github.com/langchain-ai/langgraphjs/blob/main/docs/docs/agents/human-in-the-loop.md) | Agent checkpoint and interrupt/resume | Independent backend control-plane uptime or permission |
| [Home Assistant Assist](https://www.home-assistant.io/voice_control/) | Local voice intent and accessible device control | General task custody and cross-host handoff |
| [Node-RED](https://nodered.org/docs/user-guide/context) | Event flow and optional persistent context | Durable state by default; external-effect safety |

## Inversions and CoTurtles

- `SESSION_COUNT != AUTONOMOUS_WORKER_COUNT`.
- `PROMPT_REPEAT != MACHINE_WAKE`.
- `SCHEDULE_CONFIGURED != OBSERVED_EXECUTION`.
- `PUBLIC_FILE != ALL-SESSION_ACK`.
- `NO_SCREEN != NO_USER_INPUT`.
- `SOURCE_HASH != SEMANTIC_TRUTH`.
- `SAFE_IDLE != FAILURE`.
- `MANY_READERS_ONE_ELECTED_ACTUATOR`.
- Stop recursion at `SOURCE -> WORKID -> FENCED ACTOR -> VERIFIED RECEIVER EFFECT -> QUIET`, or record why the edge is held.

## 2026-11-13 build-order election: capability before breadth

**Source-bound priority correction; not a new controller, deployed cycle, governance change, or claim of 99% local task coverage.** Reuse the existing WorkID/CoOwnedWork #450, single fenced queue, #317 receiver, #181/#453 native CoBar, CoModelFabric adapter, and CoFrontierExit gates. The earlier R1 mandatory dependency graph is not replaced by a new graph.

**Critical sequence**: `DURABLE_WORKID -> ONE_QUIET_LOCAL_DEED -> EXACT_SOURCE_AND_EFFECT_RECEIPT -> INDEPENDENT_RECEIVER_READBACK -> COBAR_VISIBLE_RESULT_AND_STOP -> COLD_RESTORE -> MEASURED_AUTOCYCLE`. Admit work in that order; a step with missing proof remains HOLD. Existing open-source or deterministic systems are preferred over new model-generated orchestration when sufficient.

**What moves earlier**: source preservation and exact recovery, deterministic verification, the existing local Ollama route on one harmless useful task, R6 input/result/Stop without focus theft, a single elected actuator, and a quiet scheduled/event wake with exactly-once effects. Measure user effort, wall-clock completion, quality, unattended useful tasks, recovery success and resource cost.

**What moves later**: more model instances, large virtual fleets, additional product/theme engines, new schedulers/watchers, hosted private-history ingestion, mass migration and autonomous provider chat deletion. RepoZipper [draft PR #493](https://github.com/CoCivium/CoCivium/pull/493) is a source-tested synthetic onramp; preserve it, but do not make it a prerequisite for the first local WorkID cycle.

**99% local-first is an elective target, not a verified adoption rate.** Reserve a measured, explicitly authorized frontier-model challenge lane when local quality or safety is insufficient. Distinguish FOSS runtime code from model-weight licenses; qualify each model's actual license and permissions. Model count, task count and GitHub commits are not independence or useful effect.

**Evidence already observed, bounded**: the Nov. 11 X2 `CO_SESSION_RECOVERY_X2_LOCAL_MODEL_SUBSTITUTION_RECEIPT_R0_20261111.json` reports 4/4 local Ollama HOLD-decision probes with qwen3:4b and gemma3:12b, no provider calls or actual session recovery. The Nov. 13 CoDesktop R6 renderer status reported a visible dock but `engine_state=COLD` and `receiver_ack=NOT_ESTABLISHED`. An attempted live model inventory on Nov. 13 suffered PowerShell quoting errors, so its empty model list is **INVALID_PROBE**, not evidence of absent models. These facts do not prove unattended inference, model-lineage independence, or CoBar acceptance.

**CoInversions and CoTurtles**: optimize *human relay removed per independently useful recovered effect*, not number of sessions. Keep healthy workers dormant; run exact tasks with deterministic code; minimize the number of effect writers; challenge one loop before recursively creating another; stop recursion when measured benefit fails to exceed cost/complexity. An independent second execution domain is still required before claiming X2 can disappear.

**Human scope**: routine preparation, source tests and reversible read-only canaries need no manual relay. Retain person-specific gates for deletion, privacy expansion, credentials, spending, public publication and authority. User absence must fail closed, not deadlock harmless research or fabricate consent.

**Next elected deed**: resume or elect **one existing** harmless WorkID through the current fenced queue, execute a deterministic or local-model task, preserve an exact receipt and independently read back the result without creating another daemon or stealing focus. Do not escalate to high parallelism until that path has a measured restart/Stop result.

## 2026-11-13 clarification: high-yield bounded ambition, not atomic minimalism

The preceding single-WorkID trial is a **qualification gate**, not an organizational ceiling, small-task-only policy or instruction to defer all ambitious parallel research. **CoEutomation+** means automated reliable work ownership and lifecycle, not continual dependence on a ChatGPT tab or a person relaying prompts. **CoLazy+** means avoiding *waste* through reuse, caching, sleep and better algorithms, not reducing the magnitude of outcomes. **CoLeasty+** applies to manual labour, coercion, blast radius, unverified assertions and needless resource consumption, not to the value of opportunities attempted. **Atomicity** applies to shared-state commits/effect boundaries, not idea size or total development scale.

**Election:** maximize `EXPECTED_VERIFIABLE_VALUE / (HUMAN_RELAY + RISK + TIME + COST)` with explicit downside and confidence fields; retain independent meaningful objectives rather than letting this ratio become a universal rank. Admit independent read-only research, source reviews, proof construction and local-model challenges **in parallel** within measured budgets. Serialize *only* true shared-mutation and consequential-effect collision domains, fenced by WorkID, currentness and authority. Preserve minority findings and negative tests through a bounded fan-in; no new always-on watcher or worker is inferred by writing this rule.

**First qualifying proof:** exercise the existing bounded WorkID queue in one local, useful, interruption-tolerant cycle with real result and readback. When qualified, this is reusable as a **parallelizable production primitive** across CoGuardian, CoBar, RepoZipper and other preexisting modules, rather than a reason to delay all useful development until a mythical total framework exists.

**Inversions/turtles:** challenge the need for a model (deterministic code may suffice), need for a worker (reuse a receipt), need for a new component (wrap upstream), need for a new schedule (wake on an existing event), and need for user approval (only genuine authority gates). Each recursion has evidence gain, resource ceiling, stopping condition and exact predecessor, so more recursion never means unlimited autonomous effects.

**Nonclaims:** no 99% local task-completion measurement, autonomous session takeover, second-host failover, independent CoStead ACK or deployed CoBar intelligence is established by this clarification.

## Next proof and nonclaims

**Next:** One overdue, harmless WorkID, resumed by an already qualified worker after a missed wake, with duplicate suppression and separately generated receiver proof. **No new scheduler, no console process, no subscriber account mutation, no private publication.**

A new source file, repository commit, test pass or visible dashboard is not product deployment, independent receiver acceptance, account cutover, global session synchronization or governing CoAll canon.