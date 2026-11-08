# CoSurface R0 | rickBar-first browser canary

**Naming:** `rickBar` has a lowercase `r` because it is named for rick. This is the preferred human-facing label; historic `RickBar` file paths or prior citations are retained as historical identifiers, not silently rewritten.

**Evidence class: PUBLIC DRAFT + CI BROWSER CANDIDATE. NOT installed in X2 R5.**

The default surface is a quiet teal background, one bottom CoAll rail, one Orb. The stitched workspace starts hidden. Orb click/keyboard and right-click legacy menu project the same working destinations: **Here / Evidence / Future**. No remote data, messages or operating-system control. **CoMap is disabled** until an authenticated data source exists; empty placeholder zones are not shown. Escape, Hide workspace, and Windows fallback are fundamental.

`index.html` runs as a standalone local browser preview; `preview.ps1` launches that file explicitly on an authorized Windows machine. `preview.ps1 -NoLaunch` checks required source markers and prints a local hash without opening a window. This is not a native installer, service or replacement for R5.

## Local Ollama integration seam, without a new agent

The repo **already has** [CoLocalModelWorker R3](../../scripts/CoLocalModelWorkerR3.py) for explicit bounded, advisory-only inference and its [operational contract](../../docs/Operations/COLOCAL_MODEL_WORKER_R3.md). Reuse it. Do not create another autonomous model process.

`ollama_status.ps1` is a PowerShell 7 **local-only status observer** intended to be invoked by the *existing authorized rickBar/R5 producer*. It makes only `GET http://127.0.0.1:11434/api/tags` with a three-second default timeout and outputs one JSON status object. It **does not** start Ollama, pull models, send prompts, create services or install anything. It does not infer X2 status from the Ollama endpoint.

Read-only invocation from an existing authorized local runner:
```powershell
pwsh -NoProfile -File .\ollama_status.ps1
```
Optional `-OutFile` creates one brand-new JSON observation file, never overwrites an existing one. A producer can consume that file **only after** explicitly mapping it to its existing status feed and validating source, age, revision and receiver; the live feed schema and exact R5 binding have **not** been verified. Keep model status out of the quiet rail unless it blocks an actual user task; expose it under evidence/drill-down otherwise.

**Do not run direct browser-to-Ollama JavaScript:** it would introduce cross-origin, local-network and prompt-consent problems. Real user-authorized inference should flow rickBar -> existing local receiver -> existing CoLocalModelWorker R3 -> loopback Ollama -> candidate output -> independent effect review. No automatic human-message sending or provider-session impersonation.

## What CI actually tests

- Python source contracts and synthetic concurrent SQLite Seed attempt election;
- headless Chromium rail, Orb, conventional navigation, Stop, Escape and visible screenshots;
- portable HTML/PS7 preview packaging and upload.

CI does **not** prove an installed Windows R5, real local Ollama reachability, renderer restart on X2, >24h continuous operation, machine-owned autostart, a real authenticated receiver ACK or user benefit. Current screenshots are CI Chrome output, not X2 output.

**Next acceptance:** identify the already-running R5 producer/launcher on X2, map one returned Ollama observation into its *existing* CoSpeedo/rickBar feed, independently read back that feed, and provide user-visible local and fallback evidence. No extra windows, no duplicate watchers.

Related: [CoDesktopPresence #181](https://github.com/CoCivium/CoCivium/issues/181), [R5 supervisor draft #374](https://github.com/CoCivium/CoCivium/pull/374), [CoLocalModelWorker R3](../../scripts/CoLocalModelWorkerR3.py).
