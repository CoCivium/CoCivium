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

## 2026-11-10 | CoAll Desktop user-logon repair candidate

**User observation:** After a forced Windows reboot, CoAll Desktop required a manual relaunch, and several web services required fresh sign-ins. This is a P0 user-facing continuity failure, but it does not reveal the root causes or the exact installed desktop executable.

**Existing owner:** [CoDesktop/CoRunner issue #181](https://github.com/CoCivium/CoCivium/issues/181). The Desktop Commander X2 observer route is currently OFFLINE, so no local registration, process, Windows task or browser authentication state was inspected or changed.

[CoStelDesktopLogonR0.ps1](CoStelDesktopLogonR0.ps1) is a **candidate per-user Windows Task Scheduler adapter**, not a second CoAll service:

- Default `-Mode Audit` reports only whether the CoStel task and CoAll-like duplicate startup entries are present, without emitting executable paths, task command-line arguments, secrets or provider data.
- `-Mode Plan -DesktopExe <local-absolute-.exe> -ExpectedSha256 <exact-64-hex>` verifies an explicitly identified native executable and proposes a current-user, least-privilege logon task. No task or process is created.
- Only `-Mode Install` with the same verified path/hash **and** `-ConfirmChange` may register one GUI startup task. It HOLDs on conflicting task ownership, competing startup names, unknown source identity, UNC paths, reparse points or digest drift. This mutation is **not** authorized for blind remote execution and was not applied to X2.
- `-Mode Disable -ConfirmChange` disables only its owned task for rollback, without terminating the running application or touching other tasks.
- OS registration uses a single user logon trigger, limited permissions, `IgnoreNew` multiple-instance behavior, at most one restart attempt and no startup console wrapper. The GUI starts **after interactive Windows sign-in**, not from a privileged Session 0 service.
- No automatic credential vault access, cookie extraction, MFA bypass, false cross-provider session restore or persistent remote administration.
- The script cannot prove that the executable stays healthy, that the right CoAll Desktop binary was selected, that startup was quiet, or that any user session was restored. These require separate **native X2** readbacks.

**Source tests:** [test_costel_desktop_logon_r0.ps1](test_costel_desktop_logon_r0.ps1) contains 16 Windows read-only/negative cases; existing CoStel CI runs it on a `windows-latest` runner. Test results must be inspected before any PASS is claimed.

**Next native gate:** an authorized existing X2 observer must do a **read-only first census** of actual CoAll Desktop binary/hash, its Task Scheduler/Startup/Run entries, owner conflicts, logon type, startup delays, crash/event logs and real credential-policy prompts. Elect just one owner, register only with current machine-authority proof, capture pre/post reboot source hashes and first usable visible response, Stop and rollback. Accept only when manual starts=0, no duplicate popups, actual CoAll visible state returns, and previously valid identities reconnect where providers permit. A revoked token or MFA event remains a legitimate human security gate.

`SCHEDULED_LOGON_NE_GUI_RECOVERED` · `REMOTE_BRIDGE_OFFLINE_NE_X2_HOST_OFF` · `CREDENTIAL_PERSISTENCE_NE_AUTH_BYPASS` · `CI_PASS_NE_NATIVE_INSTALL` · `AUTOSTART_NE_UNKILLABLE`.
