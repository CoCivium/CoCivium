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

## Next proof and nonclaims

**Next:** One overdue, harmless WorkID, resumed by an already qualified worker after a missed wake, with duplicate suppression and separately generated receiver proof. **No new scheduler, no console process, no subscriber account mutation, no private publication.**

A new source file, repository commit, test pass or visible dashboard is not product deployment, independent receiver acceptance, account cutover, global session synchronization or governing CoAll canon.