# CoGoAll Outstanding Register R0 | 2026-11-08

**Scope:** evidence-bound priorities, not an exhaustive inventory or claim of runtime adoption. Reuse [AI/IA onramp](../Onramp/AI_IA_COORBWARE_EVERGREEN_R0.md), [public rebound hub](../Onramp/COGOALL_PUBLIC_REBOUND_HUB_20261108.md), and [Evergreen](../../EVERGREEN.md). No separate boss or fixed worker hierarchy; elect a temporary writer only for conflicting effects.

**States:** VERIFIED (independent readproof/result); SOURCE_ONLY (code or config exists, not proven deployed); BLOCKED (named external gate); PROPOSED (design without demonstrated implementation). All items require evidence URI, observer, time, successor, and nonclaims to advance.

| Priority | Work / acceptance evidence | Current state | Next autonomous work |
|---|---|---|---|
| P0 | RickBar input -> local Ollama -> output visible in existing bar -> restart recovery | SOURCE_ONLY | Locate actual host receiver and bind adapter; preserve native fallback |
| P0 | Ollama gateway and CLI combined tests with exact exit codes and CI run URLs | SOURCE_ONLY | Execute full isolated tests; record failures, not assumed PASS |
| P0 | WorkID receipt persistence, conflict, provenance, and independent readback | SOURCE_ONLY | Add end-to-end tests and source hashes |
| P0 | Live observer freshness: X2 machine vs remote bridge vs CoBar receiver distinguished | BLOCKED: verified execution path to X2 unavailable from current tool context | Reuse existing observer, no duplicate daemon |
| P0 | CoLoopGuard fault injection and bounded stop/restart semantics | SOURCE_ONLY | Verify CI, crash-before/after-commit, stale lease, concurrency |
| P1 | CoMindshare R0: two independent model proposals + challenge + dissent + adjudication | PROPOSED | Build deterministic synthetic benchmark, then real authorized models |
| P1 | Provider-neutral model registry: capabilities, license, privacy, cost, latency | PROPOSED | Implement typed adapter contract, loopback default |
| P1 | CoStead-owned durable work queue, checkpoints, fencing, recovery after >24h | PROPOSED | Prove persistence, lease correctness, 24h real uptime |
| P1 | RickBar one-screen WorkID, model status, receipts, latency, fallback | SOURCE_ONLY UX contract | Compare first-use UX with browser baseline |
| P1 | Independent CI+ run receipts, artifact hashes, regressions and failure triage | SOURCE_ONLY workflow | Read actual Actions results; fix failures |
| P1 | Automated public change feed and versioned highlight catalog | PROPOSED | Generate deduped source index with freshness and broken-link checks |
| P1 | AI/IA onramp -> rebound hub -> outstanding register navigation | SOURCE_ONLY | Bind canonical onramp to this register |
| P1 | WhatsApp/Meta AI delivery and reading | USER-REPORTED SEND, ACK UNVERIFIED | Wait for independently evidenced receiver acknowledgment; no manual chat relay |
| P2 | G_dSide future-directed valuation against equal-budget baselines | PROPOSED | Benchmark with counterexamples and falsification |
| P2 | CoPriMath typed primitives and CoLexicon compiler | PROPOSED | Formal semantics, dimensional consistency, property tests |
| P2 | CoMap/CoOrb evidence-linked visual projection | SOURCE_ONLY prototypes | Receiver-relative measured UX tests |
| P2 | Privacy/consent/publication gates across CoVIA | PROPOSED | No personal data or secrets in public feeds |
| P2 | Federated model cost, reliability, diversity and quality dashboard | PROPOSED | Baseline first; no invented speedups or intelligence gains |
| P2 | Provider independence and open-source licensing compliance | PROPOSED | Audit adapter terms, redistribution rights and export paths |
| P2 | Board/public demonstration and onboarding metrics | SOURCE_ONLY board narrative | Record one real, reproducible first-use outcome |

## Operating rules
1. Advance only on new evidence. Repeated assent or unchanged observation is not progress.
2. No unbounded loop, automatic external send, credential use, public publication of sensitive material, or irreversible effect without applicable authority.
3. Parallelize independent work; one elected actuator per conflicting write; recover with idempotency, fencing and receipts.
4. Mark unexecuted tests as NOT_RUN. Do not infer a pass from a test source file.
5. Every task may be revised, merged, superseded, or closed with provenance. No fixed 1000-item theater.
6. User-reported WhatsApp paste establishes SEND_REPORTED, not RECEIVER_ACK or MEMORY_SYNC.

**Next product proof:** one X2 RickBar prompt, one real local Ollama response, durable WorkID, receiver display, restart recovery and independent timing readback.
