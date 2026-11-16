# CoForeground+ R0 | Quiet boot and functionality salvage
**Date:** 2026-11-10. **State:** PUBLIC SOURCE-ONLY CANDIDATE; NO X2 REMEDIATION OR INSTALLED CONTROLLER.  
**Parent:** [CoRunner issue #181](https://github.com/CoCivium/CoCivium/issues/181). **Code lane:** [CoForeground PR #451](https://github.com/CoCivium/CoCivium/pull/451).

## Immediate problem
A user reports worsening transient PS7 mini-panels that interrupt browser composition, fragment messages, and invite frequent PC reboots. This is a high-priority **UX failure observation**, not an attributed process diagnosis. The connected X2 Desktop Commander observer was OFFLINE as of this wave (last seen 54 hours before the 2026-11-10 17:48 UTC check), so current Task Scheduler state, live PID/window ancestry, process owner and popup source **cannot** be proven from this conversation. A reboot can clear processes temporarily but can also re-trigger a startup launcher.

## Architectural election: native first, providers optional
- One **local, permissioned, reversible** host bootstrapper, eventually elected on CoStead/X2, should own the lifecycle lease and process budget. A native OS service or Task Scheduler entry may be an **initial boot mechanism only** after current host inspection, with no new automatic startup created from this draft.
- Real work uses persistent local queue/receipts; event-triggered headless workers only. Frontend CoBar/CoOrb should be a separately controllable GUI with an explicit user-initiated show/hide and immediate native fallback. No background worker owns the active foreground window.
- Hosted GitHub/ChatGPT schedules can challenge, report or provide recovery evidence, but **must not be the sole clock, sole store, sole actuator, or availability dependency** of local continuity. Provider outage must leave a useful offline experience, recoverable queue, and bounded backlog.
- One elected actuator per conflicting local effect, independent read-only challengers; no timer proliferation or "always busy" loop. On failure, backoff/quarantine and an explicit HOLD, not repeated windows or perpetual restarts.
- Genuine user privacy, privileges, public communication, credentials, family device permissions and destructive actions remain gated. A human may disarm or switch to native Windows UI.

## Salvage matrix (historical evidence, not current installation truth)

| Existing named role | Historical pointer | Preserve / migrate | Current effect |
| --- | --- | --- | --- |
| CoThumb R1 visible file picker + explicit file-drop clipboard control + local receipt viewer | [source](../../scripts/CoThumbCoCopyR1.ps1) | Keep *user-initiated* affordances in CoBar/Orb; visible `-Mode UI` only; default is `HOLD` on PR #451 | SOURCE-ONLY |
| CoThumb R1 file-processing Worker / receipt writer | same source | Preserve bounded job functionality; move behind one locally supervised **headless** worker | SOURCE-ONLY |
| `CoCiviumExeDevMuleResidentTick1Min` | [issue #181](https://github.com/CoCivium/CoCivium/issues/181), November 7 host evidence | Keep local health/receipt semantics, but distinguish DevMule from actual product; no popup | HISTORICAL_HOST_OBSERVATION |
| `CoPing_CopyBlock_InboxProcessor_1min_V05` | same issue | Preserve copyblock queue processing and evidence; local worker, not another panel | HISTORICAL_HOST_OBSERVATION |
| `CoCiviumExeProductShellWatchdog5Min` | same issue | Historically **disabled**. Do not revive automatically; inspect owner/rollback first | HISTORICAL_DISABLED_AS_OF_NOV7 |
| `CoEyesStructuralReview10Min` | same issue | Historically **disabled**. Preserve state until independently requalified | HISTORICAL_DISABLED_AS_OF_NOV7 |
| Unidentified PS7 panels, launchers and parent processes | user report Nov 10 | Need current task/action fingerprints plus **actual foreground event PID and parent chain** before source attribution; other vendors may be involved | UNKNOWN |

Neither retaining a function nor reusing a historical task name proves host adoption, safety or desirability.

## Nonintrusive classification candidate
`scripts/coforeground_launcher_triage_r0.py` accepts a **supplied typed snapshot**, does not query the OS, spawn `pwsh`, open windows, kill processes, disable tasks or modify startup. It marks:
- automatic `UI` mode as `P0_AUTOMATED_VISIBLE_UI_RISK`;
- automated PS7 without hidden/noninteractive declarations as `P1_AUTOMATED_PS7_CONSOLE_RISK`;
- hidden+noninteractive declarations as `HEADLESS_FLAGS_PRESENT_FOCUS_UNVERIFIED`;
- disabled tasks as `DISABLED_AS_OBSERVED_NOT_CURRENTNESS`.

The typed action SHA is for collision tracking, **not** proof of source authenticity or a real process. Only an existing explicitly authorized host observer may gather a current snapshot; never publish command-line strings, environment variables, personal paths, window titles or private screenshots as part of public CI. Source tests use synthetic fixtures only. The CLI with no `--snapshot` performs no work.

## Acceptance / rollback rail
1. **Observe** actual X2 readiness and current startup inventory without launching another panel. Record observation time, exact task/action and local-only function to preserve. Distinguish Task Scheduler state from process effect.
2. **Attribute** one real intrusion to foreground window owner PID, parent PID/launcher, timestamp and repeat trigger (if observable), without logging private text or assuming correlation equals causation.
3. **Challenge** a *single* qualified candidate launcher with static policy and a reversible, owner-approved **local** quiet-run migration. Keep functional receipts. Do not mutate other tasks or kill a process tree on guessed ownership.
4. **Prove** same outcome/receipt with no unwanted window in a supervised restart/relaunch test, then recovery after >24h with one elected process; demonstrate instant rollback or native fallback.
5. **Measure** unrequested foreground count, lost typing/focus events, restarts required, function completeness, user time saved and whether the local system still works during external provider outage. Missing observations are UNKNOWN rather than green.

**Work in this PR cannot itself stop the current live popups.** The X2 observer is offline, and no source patch lands on the machine until a permissioned install, restart-safe rollback and user-visible acceptance occur. No X2 task, process, registry, service, DNS or scheduler was modified from this source review.

**Nonclaims:** `LOCAL_IS_NOT_LANDED`; `VALIDATION_IS_NOT_ACCEPTANCE`; `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`; `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`; `HASHING_IS_NOT_SEMANTIC_INGESTION`; `DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`; `SOURCE_INVENTORY_NE_LIVE_FOREGROUND_ATTRIBUTION`; `WINDOWSTYLE_HIDDEN_NE_GUI_IMPOSSIBLE`.
