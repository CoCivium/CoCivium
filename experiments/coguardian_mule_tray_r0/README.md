# CoGuardian Mule SHADOW | native tray candidate R0

**Status: SOURCE REVIEW ONLY. NOT INSTALLED. NOT A LIVE AGENT.**

This candidate is attached to the existing [CoDesktop / CoGuardian owner #181](https://github.com/CoCivium/CoCivium/issues/181) and [first-use acceptance #453](https://github.com/CoCivium/CoCivium/issues/453). The November 14 X2 source audit found no qualifying native CoGuardian mule tray icon, and the disabled legacy minute tick only refreshes files. This candidate creates an **actual WinForms NotifyIcon in source** with the explicit title **CoGuardian Mule SHADOW**, no foreground window, no automatic balloon, and an explicit context-menu Stop. It is not another CoBar.

The tray displays a truthful `HOLD_SOURCE_UNBOUND` until an authorized owner places a public-synthetic `evidence/mule-observation.json` next to the application. A sample can be marked `SOURCE_FRESH__RECEIVER_UNVERIFIED` under a 1–600 second TTL; it can **never** promote itself to authenticated receiver ACK or useful work. Unknown, private, stale, malformed, duplicate-key, future-dated, elevated-effect and claimed-positive ACK records fail closed. All samples are read **only on explicit menu refresh**, not polled.

## Candidate first-use contract

- The app runs only when voluntarily launched in a Windows user session. It has no scheduler, service registration, Run key, task, X2 file mutation, native CoBar activation, provider-session control or model invocation.
- One per-session Windows named mutex suppresses **duplicate launches of this same shadow app**. This is **not** cross-origin effect fencing of CoBar R5/R6/R8, another mule build, or provider sessions.
- The only actions are `Refresh local evidence (read-only)` and `Stop tray shadow (no WorkID changes)`. Stopping never closes a chat, kills R5/R6/R8, revokes a live task or changes accounts.
- The icon is deliberately a system information glyph, **not green**, and the menu always says receiver ACK **UNPROVEN**. No fake status bars or "100% autonomous" labels.
- Its trust ceiling is a local read-only display. It does not authenticate evidence publishers, verify source hashes, lease any effect, or independently recover work.

## Source-safe build and test

```sh
dotnet run --project experiments/coguardian_mule_tray_r0/tests/CoGuardianMule.ContractTests.csproj -c Release
dotnet build experiments/coguardian_mule_tray_r0/CoGuardianMule.Shadow.csproj -c Release
```

GitHub Actions source CI can compile the Windows target and optionally publish a **candidate, unsigned executable as an ephemeral workflow artifact**; that is neither installation nor acceptance. No automatic deployment to X2.

The application reads only a size-bounded local file next to the binary, if provided. Example synthetic shape (the timestamp is illustrative, not a current sample):

```json
{
  "schema": "CoGuardian.Mule.Observation.R0",
  "work_id": "synthetic:mule-check",
  "data_class": "PUBLIC_SYNTHETIC",
  "observed_at_utc": "2026-11-14T17:39:30Z",
  "ttl_seconds": 120,
  "receiver_ack": false,
  "effect_class": "OBSERVE_ONLY"
}
```

## Promotion gates, under the elected #181 owner only

1. Verify one signed/identity-qualified **pre-effect** lease, PID/HWND/source preconditions, consent/quiet input, STOP and rollback **across different origins**. A same-app mutex does not provide this.
2. Stage exactly one voluntary native first-use in an idle, authorized Windows user-session envelope. Check tray discoverability including Windows overflow, real icon/HWND, source/time wording, no popups or keyboard focus theft and Stop.
3. Check after Explorer restart and fresh user logon; reconcile the one legacy startup owner. Do not reenable the seven quarantined scheduled tasks for this candidate.
4. Show **one genuine useful low-effect result** with authenticated receiver-origin exact-object readproof before removing SHADOW or changing semantic version.

Do not install or ship merely because GitHub build is green. `SOURCE_PASS_NE_GUI_ACCEPTANCE | TRAY_ICON_NE_WORKER | SINGLETON_NE_CROSS_ORIGIN_LEASE | USER_STOP_NE_SESSION_DELETE | RICK_RELAY=0`.
