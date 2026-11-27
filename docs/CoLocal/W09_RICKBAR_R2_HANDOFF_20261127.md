# rickBar R2 on X2: state and how to resume (W09 GUARDIAN, 2026-11-27)

Any session can stop at any moment. This note is the restart point; chat memory is not canon.

## What runs on X2 now
| Item | Where | Notes |
|---|---|---|
| rickBar R1 | `127.0.0.1:8766` | untouched; R2 reuses its continuity store code, fenced turns and receipts |
| rickBar R2 | `127.0.0.1:8767`, `C:\Users\Owner\CoCivium\Sessions\rickbar_web\rickbar_local_web_r2.py` | source and tests in this folder: `examples/comodelfabric/rickbar_local_web_r2.py`, `test_rickbar_local_web_r2.py` |
| Boot check | `D:\CoCivium\W09\boot\` (`EXPECTED_STATE.json`, `X2-BootCheck.ps1`), Startup shortcut + task `W09_X2BootCheck15Min` | verifies 10 items, restarts only what is missing (max once per hour), never kills |
| CoTime sampler for CoBar R5 | `D:\CoCivium\W09\cotime\`, task `W09_CoTimeSample10Min` | replaced the producer disabled on 2026-11-14 |
| Journal | `D:\CoCivium\OpenWebUI\COOPS_JOURNAL.jsonl` | one line per wave |

## rickBar R2 behaviour (layers)
- L0 chat; L1 always-on badge "answered by MODEL · stayed on X2"; L2 opt-in "Show how it works" (turn, WorkID, receipt, route).
- Picking another model performs R1's explicit `elect()` (epoch bump, recorded as `route_change`). Stale requests get 409 FENCED.
- Fast by default: models that support it run with thinking off; "Think harder" turns reasoning on.
- Live progress (`/api/progress/<cid>/<tid>`): loading → thinking (reasoning preview) → answer appears word by word.
- 180 s per-turn limit; empty answers are failures with a plain reason; nothing is ever resent automatically.
- Each prompt starts with a labelled rickBar note: local model on X2, nothing leaves the computer, X2's clock.
- Models stay loaded 30 min (`keep_alive`); default model is warmed at start; cut-off PENDING turns are marked unanswered at start.
- Cloud-named models are listed but refused (403). Loopback only (client, Host and Origin checked).

## How a new session resumes
1. Read this note and `D:\CoCivium\W09\HANDOFF_FOR_OTHER_SESSIONS.md` on X2 (via a wave or the desktop app).
2. Until the desktop app is linked to X2 with a folder added, work by one PS7 paste per wave; each wave writes `D:\CoCivium\W09\waveN-*.txt` and copies it to the clipboard.
3. Ship R2 changes as gzip+base64 with SHA-256 check, backup, compile check with automatic restore, restart only the R2 process, self-test, boot check.

## Open (owner gates; do not proceed without Rick)
- Cloud model routes and keys (Bitwarden); web search that sends queries off X2 (proposed as an explicit per-question opt-in with its own badge).
- InSeed PR/merge; Cloudflare token item; code-signing spend for an installer; retiring older Co* task families.
- Bundles w01 and w10 stay unpushed until their authors remove the flagged hazards.
- Currency-like products (e.g. CoUSD) are a separate legal track.

## Next technical steps
- Benchmark each local model in fast mode (time to first word, total time, reasoning leakage) and pick the default from data.
- Optional web lookups: self-hosted metasearch or Open WebUI search, opt-in per question, badge "searched the web".
- Generic loopback OpenAI-compatible provider adapter (LM Studio, llama.cpp, vLLM) for in-house models.
- Package boot check + manifest as a CoGuardian installer (signing is an owner gate).
