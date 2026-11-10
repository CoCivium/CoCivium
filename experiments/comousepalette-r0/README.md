# CoMousePalette+ R0 | MX Master 4 first-use candidate

Status: windows-only, GUI runtime unverified on X2; exact script is reviewable and independent Windows CI self-test is requested.

## Purpose

A small, visible, account-free CoCopy+ palette appears near the mouse. It classifies the hovered app by process name and the screen region (left/center/right + top/bottom). Nothing is read from other windows except a process name for context; no text is scraped from a page, the screen, or another program.

The user can type or explicitly click `Preview clipboard`, edit the text, then `Copy capsule` or `Copy text only`. Pasting and sending remain manual. Preview is capped at 4,000 characters. Clipboard is not read until that button is pressed; clipboard content is never saved to disk by this script. The pre-existing clipboard can contain sensitive information: do not load it when others can see your screen.

## Windows PowerShell 7

```powershell
pwsh -NoProfile -STA -File .\CoMousePalette_R0.ps1 -SelfTest
pwsh -NoProfile -STA -File .\CoMousePalette_R0.ps1
```

Exit by `Close`, the window's X, or Escape. No daemon, tray process, hook, registry entry, autorun, network call, or remote action is installed.

## MX Master 4

Logi Options+ supports MX Master 4 Smart Actions, app-specific settings and an Actions Ring. Only after the local palette canary, map the chosen thumb action to **open** a local launcher for this PowerShell script. Preserve the top-middle Easy-Switch mapping and the established three-spaces/apostrophe/Enter CoNod macro until its current hardware behavior is independently verified. Avoid replacing unmodified middle-click (browser link/open-tab or autoscroll). A physical thumb mapping remains NOT RUN.

When a launcher is assigned, its underlying window context may be reported as Logitech's overlay or a shell process instead of the intended application; context is advisory, not authorization. A resource, mouse zone, persona or context label cannot grant file, security, financial, or outward-send permission.

## Context examples

- Edge/Chrome/Firefox/Brave: `SOURCE / BROWSER`.
- VS Code/PowerShell/Windows Terminal: `BUILD / CODE`.
- Explorer: `FILES / LOCAL`.
- WhatsApp/Signal/Slack/Teams/Outlook: `PRIVATE COMMUNICATION`.
- Password managers: `PRIVACY HOLD`.
- Anything else: `GENERAL / UNKNOWN`.

All categories still require explicit preview and explicit copy. No hidden paste, pixel capture, or cross-app dispatch.

## Evidence gates

- `SelfTest` runs nine deterministic parser/helper checks, compiles Win32 interop on Windows, and reports external requests 0 (by code inspection and contract, not packet capture), mouse-hook false, physical hardware NOT TESTED.
- GitHub Actions Windows CI can verify compilation and helper tests, but cannot verify physical MX Master 4 button input, clipboard privilege differences, app focus, screen zoom, or accessibility.
- First-use X2 acceptance needs actual mouse gesture, cursor context at 3 targets, explicit clipboard preview, reversible close, and observed no unexpected outbound effects.

`COPY_NE_SEND | MOUSE_GESTURE_NE_AUTHORITY | X2_SOURCE_NE_X2_RUNTIME | POINTER_NE_ACK`
