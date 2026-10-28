# CoAliveObject+ R0a | Bounded heartbeat / relation engine

**Status: OFFLINE SHADOW CANDIDATE · NOT DEPLOYED · NOT A DAEMON**  
**Parent:** `CoCivium/CoCivium` `docs/Architecture/COFRACTAL_ENERGETIC_METABOLISM_SUPERFRAME_R0_20261027.md` (source Git blob `4f6453b46332131938d18e6fed4d385211af2e7f`).

A `CoObject` can carry a stable identity, relations, wake conditions, source provenance, and self-maintenance expectations **without** requiring an always-running process. A *logical pulse* evaluates a finite number of candidate checks; it does not grant the objects agency or authority. Every relation output is a **proposal**.

## What is actually implemented

The Python stdlib-only `engine.py` performs:

- exact-byte namespace binding to `manifest.json` via SHA-256;
- three public-source exemplars: **software** (`CoMousePalette`), **public first-use route** (`CoSpiff`), and **dormant recovery option** (`CoScaleMorph`), each pinned to an inspected Git blob;
- three separate unknown/held gaps: X2 currentness, physical mouse gesture, and independent first-use;
- logical ticks and explicit *synthetic* source-delta/failure/receiver-gap events;
- per-object review periods, bounded queue and bounded graph fan-out;
- duplicate event suppression, duplicate per-wave proposal suppression, explicit cycle suppression, and revocation;
- fail-closed namespace-bound snapshot recovery;
- no network, model calls, OS input hooks, clipboard reads, external messaging, physical action or scheduling.

Pulse 0 with no changes makes **zero proposals**. At tick 4, a synthetic failure produces **four finite proposals** and leaves some work queued. The engine does not treat its own proposals as completed external effects.

## Reproduce

From this directory, with Python 3.11 or newer:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 verify_evidence.py
python3 verify_browser_addendum.py
python3 engine.py --no-event --tick 0
python3 engine.py --tick 4
```

`output/benchmark_evo.jsonl` is the original 20-event chain (11 PASS / 1 FAIL / 3 HOLD / 5 NOT_RUN). `output/benchmark_evo_R0a.jsonl` is an **append-only successor**, preserving those first 20 events byte-for-byte, with the browser and three viewer regressions: **23 total, 13 PASS / 1 FAIL / 3 HOLD / 6 NOT_RUN**. The heads are in `HEAD.sha256` and `HEAD_R0a.sha256`. They demonstrate self-consistency, **not** authorship or independent scientific validity.

The recorded browser canary uses Playwright + headless Chromium, with **20/20 interactions passed** on desktop and mobile, no observed HTTP(S) calls and no JavaScript errors. Direct `file://` navigation was **blocked by this test environment** and remains NOT RUN. The [standalone viewer](./CoAliveObject_Viewer.html) has no external assets; it projects a *frozen recorded pulse trace*, not a live running scheduler.

The single failed research criterion was `ONE_PULSE_COMPLETES_ALL_RELATIONS`: under a one-proposal cap, one proposal is selected and at least one remains pending. This is expected, and the high-bar claim is false. Don't inflate it into a positive test of unlimited amplification.

## Proposed metabolism and scale layers

`CoSense → CoNeed/CoSurplus → CoPrioritize → CoWake → CoExperiment → CoChallenge → CoVerify → CoPreserve → CoReturn → CoSleep/CoRetire`

Each object or relation may *declare* sensing, intake, transformation, preservation, repair, release, challenge, and wake pathways; declaration does not prove implementation.

**Amplify** useful progress by better evidence, reuse, referrals and recovered capacity. **Dampen** noise, duplicate notifications, effect collisions, privacy risk and unproductive compute. Track both. In a cyclic graph, amplifying every edge independently would cause an echo storm. The engine therefore caps work per pulse, traversals, queue growth and event history.

**Horizontal (more objects):** dormant descriptors, event subscriptions, deduplicated candidates.  
**Vertical (deeper):** evidence, exact source, challenges, richer tests, recovery.  
**Temporal:** snapshot, version, observed time, wake condition and explicit expiry.  
**Substrate:** app, local process, public site, peer server or human participant, only where a real adapter and permission exist.  
**G_d / CoSpirit / hypothetical:** optional explanation or question-generation projections only, never presumed physical effect, authority, or an energy source.

## Next gates

1. Independent Mac/X2 reproduction. X2 Desktop Commander was **offline** at the recent check; that remains a separate blocker, not a synthetic test failure.
2. Read-only CoPulse / repository delta adaptor with a stable receive identity; no new hourly host task needed because CoEvoAll Pulse already exists and is enabled.
3. Deduplicated receiver pull with independent readproof. GitHub commit or notification != receiver acknowledgment.
4. True bounded worker execution with leases and process-death recovery through **CoScaleMorph R1**, not an accidental second controller.
5. Empirical useful-outcome, attention and energy tests against simpler baseline workflows. Retire this candidate if it adds bureaucracy without value.

## Privacy and authority

Only explicitly marked **synthetic shadow** events are accepted. Signals with unexpected fields, private scope, stale source identity, or unauthorized event types are held without processing the data. All outputs have `effect_authority: NONE`, `receiver_ack: NOT_OBSERVED`, and **zero** provider calls/external effects. No user identity, secret, WhatsApp content, or local file inventory is included.

**`ALIVE_DESCRIPTION_NE_RUNNING_PROCESS | HEARTBEAT_NE_NEW_WORK | PROPOSAL_NE_EFFECT | POINTER_NE_ACK | AMPLIFY_USEFULNESS_DAMPEN_NOISE | INFINITE_ADDRESS_SPACE_NE_INFINITE_COMPUTE`**

License: GNU GPLv3, matching the previously packaged CoCivium FOSS prototype license text included as `LICENSE`. Attribution to the CoCivium research lineage is retained.
