# CoModelFabric+ | X2 read-only preflight R0

**Candidate only, not installed on X2 and not a Claude account.** Intended as the smallest X2 acceptance step toward the pre-existing [CoModelFabric+ architecture](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md) and [CoAll I/O Mesh #233](https://github.com/CoCivium/CoCivium/issues/233).

## One useful first step

Run in PowerShell 7 from this folder:

```powershell
pwsh -NoProfile -File ./Test-CoModelFabricX2R0.ps1 -Mode SelfTest
pwsh -NoProfile -File ./Test-CoModelFabricX2R0.ps1 -Mode Check
```

The `Check` command reads `http://127.0.0.1:11434/api/tags` with a two-second timeout and prints a JSON report only to the current terminal. It reports **model count**, not names or prompts, and does not read credentials, clipboard, browser cookies, or private files.

If the local check is acceptable and the person at X2 wants Claude on screen:

```powershell
pwsh -NoProfile -File ./Test-CoModelFabricX2R0.ps1 -Mode OpenClaude
```

This **only opens https://claude.ai/** in the user's normal browser. If already authenticated, that browser may already have the person's own account session. If not, the person must log in; no account is created or impersonated. The browser session is **not automatically bridged to CoOrbWare**. 

To inspect CoOrb-related published source without running an app:

```powershell
pwsh -NoProfile -File ./Test-CoModelFabricX2R0.ps1 -Mode OpenOrbSource
```

For completely offline parser/format checking without a network probe:

```powershell
pwsh -NoProfile -File ./Test-CoModelFabricX2R0.ps1 -Mode Check -SkipOllama
```

## Provider identity and permissions

Claude's interactive subscription and Claude Console/API are separately authenticated products. A third-party CoOrb adapter should use its legitimately authorized **API** route and scoped secret store, not replay or harvest interactive browser cookies or use additional accounts to evade provider limits. OpenAI, Pi and other hosted adapters are **HELD**, not connected by this source.

The supplied `CoWorkObject_R0_example.json` is a *public-safe fixture* with two total active workers, one maximum paid-provider session, **zero automatic spend**, a 60-second deadline, and no effects. It never dispatches a model call by itself.

## Probe/report limits

- `OBSERVED_LOCAL_API` means a syntactically valid response from the local Ollama tags endpoint. It does **not** prove inference capacity, speed, safe handling of private data, or X2 device health.
- `HELD_LOCAL_API_UNREACHABLE` is an endpoint-specific check, not a claim that Ollama isn't installed.
- `AUTH_UNKNOWN_NOT_PROBED` for Claude does not imply signed in or signed out.
- There is no secret reading or token logging, no browser remote-control, no privilege escalation, no state file, no registration, no background loop, and no global input hook.
- Commands operate only when the person or an actually authorized device receiver launches them. Source publication is not machine installation.

## What must happen after the local test

A trusted X2-origin receipt of the read-only report. Then one explicitly authorized local Ollama task and one separately authorized Claude API task on the same **public-safe** source, with cost, latency, dissent, model identity, and a human-readable task outcome. CoOrbWare should own the work object, preserve disagreements, and allow cancellation. A live X2 mouse/keyboard binding and independent receiver acceptance are separate gates.

For ET candidate signals use observational technosignature science, independent instruments, ordinary interference analysis, replication and a false-positive ledger. For G_d and reverence interpretive lenses, preserve voluntary ethical/cultural/spiritual dialogue without labelling it a device that detects a deity or established physics.

**No false claims:** `BROWSER_NE_API` · `ACCOUNT_NE_WORKER` · `ROLE_NE_IDENTITY` · `MULTI_PROVIDER_NE_INDEPENDENT_EVIDENCE` · `SOURCE_NE_X2_RUNTIME` · `MODEL_TAGS_NE_TASK_PASS` · `ET_HYPOTHESIS_NE_CONTACT` · `SYMBOL_NE_SCIENTIFIC_MEASUREMENT`.
