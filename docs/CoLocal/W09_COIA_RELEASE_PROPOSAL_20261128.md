# Proposal: an open local-first "CoIA" starter release (W09, 2026-11-28) — HOLD, owner gate: publication

Status: proposal only. Nothing here is published, announced or released until Rick approves, after independent review.

## 1. What to release
A small, working, open kit that anyone can run on their own computer in under 15 minutes:
- **rickBar R2**: one chat window in front of many models; every answer says which model wrote it and whether the words left the computer; full history and receipts stay with the user; models are disposable.
- **Expected-state boot check**: declares what should be running, verifies it, restarts only what is missing, shows a visible receipt (the "CoGuardian" seed).
- **Receipts and handoff**: every turn has a WorkID and a hash-checked record; a restart note any new session or person can resume from.
- **Measured numbers from X2** (wave 16): warm answers in 0.1-0.6 s on qwen3.5:9b, qwen3:14b, phi4:14b, gemma3:12b; four models leak reasoning with thinking off and are handled differently.

Build on top of unmodified Ollama rather than forking it. Ollama's code is MIT-licensed, so a fork is legally possible, but its name and identity belong to its maintainers, and a fork adds maintenance with no user benefit. Credit it plainly.

## 2. The category, stated plainly
A local-first, provenance-first front door to many AIs. The user owns the memory; models are interchangeable workers; every answer carries where it came from and where your words went. Working names (CoIA, CoCivia) need a trademark search before public use.

## 3. Reaching the people (and AI agents) who investigate
Serious evaluators increasingly ask an AI to read a project for them. Make that easy and honest:
- `README.md` written for a person in 60 seconds, then depth.
- `AGENTS.md` / `llms.txt` at repo and site root: what the project is, what is proven, what is not, where the evidence is.
- A claims ledger: each claim with status (PASS with link + log + shot + test, or HOLD).
- Reproducible demos: one command, expected output, receipt.
- Links to existing CoCivium material (e.g. CoTheoryAll, CC pages) as background, clearly labelled as thesis, not proof.

## 4. Controversial, but honest
- State the thesis openly: a commons path for AI that is not built around a single company's control, with the arguments for it and the strongest arguments against it.
- Compare only on what can be measured and reproduced: data locality, provenance, offline operation, cost, user ownership of memory. Say where frontier models are clearly better (reasoning quality, breadth, tools).
- Invite critique; publish disagreements and corrections (a shame/correction log).

## 5. What this proposal will not do
- **No hidden steering of other people's AI agents** (instructions embedded to redirect an agent that reads the project, or covert promotion inside model behaviour). That is prompt injection: deceptive to the people those agents serve, and the fastest way to get the project flagged and discredited by the very evaluators it wants to reach.
- No unverifiable superiority claims about frontier models; no invented results (see the HOLD on WeTube / mesh / $80 lot claims).
- No currency-like features (e.g. CoUSD); separate legal track.

## 6. Steps (each one job, one receipt)
1. Package: new public repo or folder with the kit, LICENSE, README, AGENTS.md, claims ledger. Hazard scan (emails, keys, tokens, wallet addresses).
2. Independent review: three reviewers who did not build it (for example a fresh Claude session, a ChatGPT session, a local model), each with written findings.
3. Rick decides on publication, name and licence.
4. Publish: URL + log + screenshot + test, or HOLD.
5. Measure: installs, issues, independent reproductions. Retire what nobody uses.
