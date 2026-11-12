# CoStel R5 R0 synthetic supervisor contract

**State:** Candidate, simulation only. No Windows service, OS-startup registration, X2 mutation, GUI, network listener, or CoOrb integration.

This experiment contributes bounded executable negative controls to [CoDesktop/CoStel architecture #181](https://github.com/CoCivium/CoCivium/issues/181), [X2 surface acceptance #178](https://github.com/CoCivium/CoCivium/issues/178), and [fan-in #317](https://github.com/CoCivium/CoCivium/issues/317). It does **not** replace any existing operational supervisor.

## Run locally

Requires stock Python 3.11+; no external dependencies.

```sh
python -B -m unittest discover -s experiments/costel_r5_r0 -p 'test_*.py' -v
python -O -B -m unittest discover -s experiments/costel_r5_r0 -p 'test_*.py' -v
```

CI candidate: `.github/workflows/costel-r5-supervisor-r0.yml`, triggered by the synthetic test and workflow paths. A workflow file is not evidence of an executed or passing GitHub Actions run.

## Contracts this fixture probes

- A process being present is insufficient if its endpoint is unresponsive.
- Stale remote-observer status does not imply the X2 host or R5 is down.
- Healthy worker receives no restart request.
- A failed worker receives at most one configured attempt, then enters HOLD.
- Explicit user Stop always beats automatic restart.
- A second owner must not trigger duplicate attempts.
- An attempted restart is **not** a verified successful effect.
- Every modeled decision emits a record.

## CoColdOpen+ | one headless readiness decision (2026-11-12)

**Motivating observed gap:** After the user restarted X2, the remote observer briefly reported Online and then became unresponsive/Offline. Private screenshots exposed disconnected desktop composition, Windows-owned wallpaper, audio returning muted and missing input-utility behavior. A screenshot or bridge status is **not** machine startup attestation. Do not publish user screenshots, infer X2 power state from bridge absence, or burden the user with manually cycling sessions.

A new **pure, no-effect classifier** consumes the exact JSON produced by the existing [read-only CoRunner startup inventory](../../scripts/CoRunnerStartupInventoryR0.ps1). It produces one small human sentence and the matching typed machine result from one source, with no second watcher, account action, process start, Windows task, OS query, network request, storage or wallpaper mutation.

Example on a **separately authorized Windows host with the project source available** (never proof by merely displaying the command):

```powershell
pwsh -NoProfile -NonInteractive -File scripts/CoRunnerStartupInventoryR0.ps1 | python -B experiments/costel_r5_r0/cold_open_readiness.py
```

The result always remains `HOLD_USABLE_DESKTOP_UNPROVEN` until actual, independent post-login user-experience and receiver observations are established elsewhere. It distinguishes boot time and snapshot age from a usable desktop, audio services from actual unmute, mouse-process presence from mapped-button functionality, model/process existence from useful work, video-driver dimensions from per-monitor DPI and layout, and desktop background appearance from a CoCivium-owned surface. Never treat a local sample or GitHub CI as an independent X2 restore.

**Contract:** `CoAll.CoColdOpenDecision.R0`, stable `CoDesktopPresence:ColdOpen:R0` identity, no user data echoed, no startup mutations, one `next_safe_probe`. Regression cases cover stale/missing/bogus clocks, false PASS injection, hostile extra fields, privacy and deterministic output. The baseline is **fail-closed** and intentionally does not claim a working X2, a permanent automation or CoEx.

**Next material acceptance:** once X2 is reachable through an authorized receiver, run the existing inventory locally, bind to its exact source/boot timestamp, then test real keyboard focus, mouse mappings, chosen audio state, monitor layout, one local model task, and automatic restoration without asking for a ChatGPT turn. Qualify receiver-origin readproof before promoting any result.

## CoArrival inverse acceptance tree | 2026-11-12

The cold-open classifier now reuses the same read-only snapshot and **walks backward from the desired human result** `COARRIVAL_USABLE_DESKTOP` through bounded, typed prerequisites:

`ARRIVAL -> boot cohort | input mapping | intended audio | scaling/focus/CoBar/background | one useful local task | automatic pre-session restoration`

This is a **dependency-and-uncertainty projection**, not a second monitoring service or acceptance authority. It is explicitly designed to catch failures where Windows services and processes are present but the user-facing experience is broken.

- Known Windows inventory facts may be labelled `REPORTED_IN_SNAPSHOT` only when the same boot epoch and a fresh observation qualify; expired readings are `STALE_SNAPSHOT`, everything else remains `UNKNOWN`.
- Nested dependencies are traversed with **hard cycle and resource bounds**, preserving the exact inverse path to each missing proof. A shared requirement may occur in sibling branches without being mistaken for a cycle.
- Missing leaf = `UNKNOWN`, not a fabricated PASS. Even a fully populated *synthetic* tree cannot claim actual human acceptance, native runtime, independent receiver pickup, or authority for autostart.
- `first_missing_dependency` is an **explanation**, not an instruction to edit Windows. Real `next_safe_probe` stays under the pre-existing cold-open authority and currentness policy.
- Every branch may be rendered by humans as a short comprehensible gap or by machines as the same typed `inverse_path` array, without duplicating truth stores.
- New standalone inverse tests: **17** checks for false PASS injection, stale/missing boot, mouse utility missing, audio/DPI/CoBar mismatch, focus, historical paths, cycles, depth/node budgets, unknown/malicious evidence, reused sibling prerequisites, privacy, source immutability, and deterministic zero-effect output.

These tests are pure synthetic code. **No real X2 reboot, input interaction, native desktop renderer, audio endpoint, background/foreground focus or receiver was changed or attested.** Their purpose is to shrink the causal gap so the first authorized X2 proof can test the correct failure modes instead of relying on running-process vanity metrics.

## Known limitations / next proof

This is an in-memory state-machine fixture. The lease is not persisted, crash-resistant, monotonic-time-based, or distributed. The restart is a modeled *attempt*, not an actual process launch. Receipts are in-memory, not signed or independently delivered. There are no actual Windows integration tests, uptime metrics, command authorization, UI/no-popup tests, uninstall/rollback tests, network changes, or cross-device ACKs. These must be independently qualified before runtime promotion.

## CI and promotion

A reviewer must inspect the exact source revision and actual Actions run logs for this PR. Subsequently challenge state transitions, reboot survival, simultaneous supervisor races, lease expiry, repeated failure, privacy/consent, and restore-to-native-desktop safety. A PASS here demonstrates only that this synthetic model satisfies these bounded expectations. Do not promote it to X2 live supervisor status.

## Separate-job artifact pickup test (CoGoAll R0)

The public workflow now declares `handoff-producer` and dependent
`handoff-receiver` jobs. The first produces a canonical, public synthetic
work object plus a SHA-256 claim, uploads it using `upload-artifact@v4`, and
the second downloads it using `download-artifact@v4`, recomputes source bytes
and hash, verifies GitHub run/attempt/commit identity, and emits a distinct
receiver-job observation receipt.

- Bounded fixture: `ci_artifact_handoff.py` and `test_ci_artifact_handoff.py`.
- Locally reproducible negative controls: wrong run, revision, attempt,
  producer/receiver role, forged content/hash/length, noncanonical JSON,
  overwritten destination, and asserted cross-provider recovery.
- A genuine pass requires BOTH separate GitHub Actions jobs green **and** the
  receiver-produced receipt artifact bound to that exact run. Source and
  test presence alone never count as `PICKED_UP`.
- The receiver job still runs at the SAME GitHub Actions provider. A verified
  pickup is thus `CI_SCOPE_DIFFERENT_JOB_READBACK`, not independent failure
  domain, CoEx, X2 native reception, useful work acceptance or a real
  cold-recovery test. There is no actual ChatGPT-session fanout.
- Avoid public publication of private task IDs, user messages or device data.
  Synthetic source and receipt are safe for the public repository.
