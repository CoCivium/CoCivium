# CoRunnerPopupObserver R0

**Status:** candidate diagnostic source, **not executed on X2**, not a popup fix, not a deployment.

## Why
Persistent PS7 mini-panels may come from scheduled tasks, wrapper processes, or legitimate operator windows. Killing all PowerShell windows or disabling Task Scheduler would destroy useful work and obscure causation.

## How this diagnostic behaves
`scripts/CoRunnerPopupObserverR0.ps1` is **read-only**. It queries local PowerShell/terminal-related processes (PID, parent PID, start time and whether a main window handle exists) plus scheduled-task launcher basenames and basic hidden/noninteractive flags. It does not capture raw command-line arguments, private files, screens, credentials or keystrokes. It does not spawn processes or GUI windows by itself, change tasks, stop services, create scheduled work or modify startup.

When an *authorized X2 observer* can execute in an **already open** PowerShell terminal, run:

```powershell
& 'scripts/CoRunnerPopupObserverR0.ps1' | Out-File -LiteralPath '.\popup-observation-local.json' -Encoding utf8
```

The file stays **local** and may contain task names or other environment information. Never publish unreviewed output or upload it to GitHub. No instruction here requires Rick to relay it. The eventual machine-owned local receiver should inspect it and send only a reviewed, safe summary and evidence digest.

## Interpretation and follow-up
- `possible_foreground_console=true` means a launcher could open a console, not that it caused any observed popup.
- `has_main_window` is only a sampled window-handle signal; not a reliable mapping to actual distracting mini-panels.
- Attribute a *specific real popup* by timestamp, foreground window PID, ancestry and its launch trigger. This script alone **cannot prove that causal link**.
- Preserve utility, logs, identity and recovery path before changing a verified offender.
- A fix should change exactly one identified launch policy with a reversible fallback, then verify continued task function and no unsolicited popup after restart.
- No new always-on observer or scheduler should be created as part of this investigation.

## Current boundary
Remote Desktop Commander X2 bridge was offline at last check. The machine's actual running state is separate. There is no live process inventory from November 10 here and no actual popup fixed.

`DIAGNOSTIC_SOURCE_NE_FIELD_OBSERVATION | POTENTIAL_OFFENDER_NE_CAUSE | NO_POPUPS_NE_NO_FUNCTION | LOCAL_SCHEDULER_NE_CLOUD_DEPENDENCY | USER_NO_RELAY`
