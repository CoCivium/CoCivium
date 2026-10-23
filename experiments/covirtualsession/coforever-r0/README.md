# CoForever+ / CoProcessField+ / CoOrbWare+ R0

**CoHereNow:** A small, local demonstration proves that a very large *logical* address space can be managed through a tiny, bounded physical working set. It includes an offline CoOrbWare-style viewer, source-bound checkpoints and a no-effect multiprocess probe. This is **not** an installed scheduler, daemon, CoOrbWare desktop, hosted service, AI swarm or production release.

## Five-minute first use

Open [`CoOrbWare_offline.html`](CoOrbWare_offline.html) locally. Start with **Glance**, then use **Working set** to inspect synthetic tasks, **Time / wake** to see what sleeps, and **Proof / limits** to see exactly what has and has not been established. Buttons change only the displayed projection. There is no network fetch, clipboard access, OS remapping, provider interaction or global process control. Private/unknown task IDs and even their counts are not exposed to the browser view.

## One reusable control pattern

`ADDRESSABLE -> SOURCE_BOUND -> WAKE_ELIGIBLE -> RESOURCE_AND_AUTHORITY_CHECK -> SHORT_LEASE -> LOCAL_RESULT -> VERIFY -> CHECKPOINT -> SLEEP`

CoOrbWare renders a receiver-relative view of this pattern. It does **not** own source identities, authorize execution or infer liveness from animation. The index is `16^20 = 1,208,925,819,614,629,174,706,176` *syntactic* virtual addresses. They are not experiments, processes, entities, unique useful ideas or total coverage of CoAll. Only 12 records are instantiated in the demo. The deterministic work selector can lease at most 2 synthetic work items, and `live_probe` launches at most 2 actual short-lived local subprocesses at once, with a total hard cap of 8 possible child jobs.

A review turtle has maximum depth 2. An over-depth task is held. Authority is `NONE`: external-effect jobs are held. `HIGH` pressure elects 0 additional items, `MEDIUM` elects at most 1 and `LOW` at most 2. A duplicate task with the same source is idempotent; a conflicting source is held. Lease expiry is NOT an acknowledgment; an unreceipted lease returns to the waiting frontier. Restart requires a SHA-pinned checkpoint and the exact versioned source spec. No resident loop is installed.

## Why this is more than a trillion names

- **Scale:** mixed-radix addressing samples 1,024 ranks without enumerating the logical set; actual memory and CPU are dominated by at most 40 touched work records and 2 short-lived child processes.
- **Time:** logical continuity is recoverable across stopped embodiments, but only if actual durable checkpoint and current authority/receiver constraints are later proven.
- **Multiprocessing:** the one-shot probe uses finite real Python child processes on the host; it measures its observed peak, verifies deterministic results and waits for all children to exit. It does not benchmark model inference or sustained distributed throughput.
- **CoOrbWare:** the same public-redacted `demo_state.json` supplies a quiet status, working-set list, synthetic orbital map, temporal narrative and evidence pane. The `index.html` equivalent has no chat/account requirement. This is a **preview**, not Windows wallpaper or CoBar integration.
- **Interspace / CoNull / G_dRes:** unknown, intentionally private, simulated, expired and forecast states remain typed candidates rather than magically connected facts. A residual may justify a new bounded question; never automatically a new recursive watcher.
- **FOSS/provider-neutrality:** the source uses Python standard library and Node standard library for default tests. Browser page has zero external assets. Claude, Pi, Ollama and future models are optional adapters with distinct gates, not checked working replacements.

## Verified local checks

Run from this directory:

```sh
python3 -m unittest -v test_coproc.py
node test_ui.cjs
python3 verify_release.py
```

The initial local environment passed **42/42 Python assertions** (including the one-shot real child-process probe) and **8/8 Node simulated-DOM checks**. The demo's `benchmark_evo.jsonl` has **6 PASS and 6 NOT_RUN** scoped records. Inspect `RECEIPT.json` for exact outputs and the archive receipt for hashes. `test_ui.cjs` is a *mock DOM*, not an actual browser acceptance test. An attempted headless Chromium screenshot stalled and a Playwright launch was blocked by a missing browser binary. This has been recorded as `BROWSER_VISUAL_QA_BLOCKED`, rather than quietly turned into PASS.

CI on GitHub, independent Windows/X2 replay, real energy and memory measurements, cross-host lease fencing, identity-bound receiver ACKs, privacy with human bystanders, screen-reader acceptance, OS mouse/CoOrbWare installation, paid-provider migration and account retirement remain separate gates. `receiver_ack=UNPROVEN` and `effect_authority=NONE` in all snapshots.

## Existing CoCivium roots (not a second platform)

- [CoVirtualSession / SessionMorphology](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md): stable logical identity, leased embodiments, sleep and wake.
- [CoAlwaysInheritance / CoTurtleStop](https://github.com/CoCivium/CoSteward/blob/main/docs/session_backchannel/evolution/CoAlwaysInheritance_TurtleStop_20261017_R0.json): semantic persistence without immortal execution.
- [CoRelationalUX / CoOrbWare](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md): a single source, many privacy-aware projections.
- [CoExperimentSpace / CoTurtles](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SPACE_TURTLES_R0.md): enormous address spaces with hard depth/round and resource limits.
- [CoPulseCapacity R0G](https://github.com/CoCivium/CoCivium/blob/main/docs/Operations/COPULSE_CAPACITY_PROVENANCE_R0G.md): distinct virtual identity, actual process liveness, source attestation.

## Next high-bar deed

Reproduce the finite subprocess and source-bound checkpoint test on X2 and an independent second environment, then hand the same public-safe state to one *real authorized CoOrb/CoBar receiver* and obtain exact-object readproof plus a five-minute usability comparison against a plain list. Do not introduce a 24/7 worker or retire provider accounts before receiver-level recovery and authority have been tested.

`ALWAYS_NE_ALWAYS_RUNNING` · `DESCRIPTOR_NE_EXPERIMENT` · `LOGICAL_WORK_NE_LIVE_PROCESS` · `LEASE_NE_EFFECT_AUTHORITY` · `ANIMATION_NE_LIVENESS` · `LOCAL_NE_LANDED` · `RENDER_NE_ACK` · `REPLAY_NE_PROVIDER_EXIT`