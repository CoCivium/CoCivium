# CoAll Golden Braid R0 / CoGbx UX first door

**State:** OFFLINE_TWO_RECEIVER_CONFORMANCE_PASS__NO_GLOBAL_SYNC__NO_COGBX_LIVE_SITE__NO_X2_INSTALL.

This is a bounded test against [CoCivium issue #317](https://github.com/CoCivium/CoCivium/issues/317). It is **not a new global control plane**. It complements the earlier [CoPulse two-receiver R0B](https://github.com/CoCivium/CoCivium/blob/main/docs/Operations/COPULSE_TWO_RECEIVER_R0B.md) and [per-receiver ACK R0C](https://github.com/CoCivium/CoCivium/blob/main/docs/Operations/COPULSE_ACK_BACKFILL_R0C.md) canaries. Those already demonstrate independent local receiver pickup and ACK cursors in a bounded fixture. R0 focuses on a different golden-learning task packet, retries, missing ACK recovery, explicit Stop, and one user-facing projection.

## One-work-object test

A canonical, pinned **synthetic public** insight packet is submitted to two locally permitted destinations, each as a separate OS process. Each writes a delivery file and its own origin-side ACK file containing the task and delivery hashes. A deliberately injected beta failure remains queued while alpha stays complete. Retrying beta succeeds, and a third dispatch skips both as already complete. A fresh Python process reopens the task/pointer/journal and reconstructs the result without an in-memory session. The operator-controlled root has a single-process lock and a Stop file.

**What this does not prove:** independent organizations, off-host storage, cryptographic recipient authentication, crash-safe distributed transactions, real delivery, multi-agent fleet/currentness, an operating CoOrbWare runtime, service continuity if GitHub fails, or user success. The local hashes prove consistency under ordinary accidental tampering, **not trusted identity**. Do not place private data in this fixture.

## Reproduce in Python 3.11+ (standard library only)

```sh
python3 -m unittest discover -s tests -v
python3 run_demo.py --out output/my_fresh_run
python3 verify_output.py --out output/my_fresh_run
```

Use a **new empty** output directory. Runs refuse a nonempty root rather than clobbering it. The test packet lives at `fixture/task_packet.json`. No network requests, model calls, external messages, or device changes are made by the Python core.

### CoGbx candidate (same work, three views)

Open `ux/CoGbx_OneWork_Exemplar_R0.html` locally or via a supported static browser viewer. It is an **offline, no-account** projection with:

- `CoHereNow`: current step and one next safe action;
- `CoMap`: task -> alpha/beta local receiver relationships;
- `List`: screen-reader- and small-screen-friendly text view;
- `Time`: three *logical* phases, not an actual realtime 3D/CoTime engine;
- optionally tilted 2.5D CSS map, not true 3D, VR, AR, or holography;
- explicit local copy of a synthetic evidence capsule with no silent clipboard read;
- clearly labelled blocked and unproved delivery states.

The default 2D/list modes should remain first-class. Nobody should need expensive graphics hardware, high energy use, motion tolerance, or specialist terminology to make progress. Any new 3D+CoT option must beat the accessible text/2D baseline on real comprehension tasks before promotion.

```sh
python3 ux/build.py
node --test ux/test_logic.cjs
# Optional browser dependency: playwright Python + Chromium
python3 ux/browser_canary.py
```

The browser canary uses headless Chromium `set_content` to avoid network access; it is not a test of actual X2 or `https://cogbx.org`. It captures desktop/mobile screenshots, detects JS errors and external requests, and exercises mode, timeline, depth and copy controls.

## X2 -> global exemplar acceptance (proposal, not deployment)

| Boundary | Minimum proof |
| --- | --- |
| Source | One stable `work_id`, exact source hash, parent lineage, schema/permissions |
| Windows/X2 | One **current** local observer connection; quiet CoBar; one contextual CoOrb; Stop, hide and undo |
| Other devices | Same work identity and outcomes across Windows, Mac, Linux, mobile, and headless read-only view |
| Levels | Whole work -> task -> evidence -> receipt recursively, with explicit parent/child provenance |
| Time | Recorded, predicted and counterfactual state cannot be confused; explicit logical vs wall-clock time |
| Spatial | Text/2D first; 3D/depth optional and reduced-motion; no hidden meaning encoded solely by color or z-axis |
| Predictive | Opt-in, local-first, inspectable, accept-to-commit; no unsolicited effect |
| Personalization | Local, editable/resettable preferences, consent-bound, no covert tracking/pressure |
| Anti-capture | Portable state/export, alternate providers, independent custodian readback, right to fork/leave |
| Redundancy | Cold restore from an independent failure domain, tested when provider host is unavailable |
| Coordination | Local file ACK != third-party delivery; exact receiver-origin readproof, permissions, Stop |
| Value | An uncoached user finishes one meaningful task faster/more safely than existing UI |

`CoGbx.org` appears as **a planned exchange/reference role** in `plans/MasterPlan.md`, not a verified currently deployed landing. Serving this candidate there requires domain/DNS/TLS/hosting ownership checks, current security/right-to-publish review, and authorized deployment. Prior HTTPS inspection returned an error, so do not claim this site is online.

## Reviews / TODO

1. Independently re-run the local Python + Node tests and inspect one failure.
2. Compare Golden Braid R0 against CoPulse R0B/R0C and deduplicate shared machinery. Do not install a second bus.
3. Keep issue #317 open until a truly independent destination/source-disconnected recovery and actual receiver pickup is demonstrated.
4. On X2 reappearance, first inspect existing CoBar/CoThumb processes; do **not** install another global hook or overwrite an existing service.
5. One newcomer on X2 and one on a phone complete one task on both a text view and spatial view. Measure task success, time, confusion, Stop, battery use and attention.
6. Only consider a public CoGbx landing after authority, accessibility, DNS, security, and origin-independent recovery evidence.

## Receipts and limitations

- `output/demo/benchmark_evo.jsonl` + `HEAD.sha256`: initial 11-event synthetic benchmark; intentionally injected FAIL is preserved.
- `output/demo/acceptance_report.json`: exact task/journal heads, retry, reader equality and explicit nonclaims.
- `ux/browser_canary_report.json`: browser `PASS` checks, but no real X2 interaction.
- `release/RELEASE_REPORT.json`: package and validation summary.

Public-source documentation from CoCivium informs the design. Source identifiers are not claims of contributor endorsement or deployment. This package is a test donor and does not alter existing GitHub source without separate review.

`ONE_WORK_ID | MANY_VIEWS | PROJECTION_NE_RUNTIME | ACK_NE_ADOPTION | SOURCE_NE_AUTHORITY | RIGHT_TO_FORK | RICK_NE_HEARTBEAT`
