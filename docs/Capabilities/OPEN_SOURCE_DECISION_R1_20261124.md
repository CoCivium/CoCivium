# CoOSS / CoStacks / CoModelFabric | Reuse before reinvention R1

**State:** `PUBLIC_REVIEW_BRANCH_ONLY__NO_RUNTIME_INSTALL__NO_MERGE__NO_COEX_CANON`  
**Date:** 2026-11-24  
**Typed source twin:** [7-donor machine-readable crosswalk](../../ai/donors/open-source-qualification-crosswalk-r1-20261124.json).  
**Predecessor:** [Original 8-donor registry](open_source_donors_r0.json) and [R0 donor ecology](OPEN_SOURCE_DONOR_ECOLOGY_R0.md). The older candidates are **preserved**, not replaced.

## First decision

Prioritize existing local and deterministic capability. The reusable sequence is:

`INTENT -> TASK FIXTURE -> BASELINE -> RIGHTS/UPSTREAM PIN -> OPTIONAL ADAPTER -> COMPARE -> PRIVACY/EFFECT GATE -> EVIDENCE -> ROLLBACK`

**Source identity is not installation identity.** A public GitHub HEAD, a license blob, an installed GGUF digest, and a working Windows service are four separate claims. Require independent evidence for each.

### Seven newly qualified *research candidates*, not seven new services

| Upstream and observed license | Candidate value | What to do now |
| --- | --- | --- |
| [Ollama](https://github.com/ollama/ollama) · MIT | Existing local inference entry, stable adapter for CoModelFabric | **Prioritize** bounded context/timeout and task-correctness tests on the *existing* runtime. Do not update the observed pre-release merely because a newer upstream exists |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) · MIT | Potential fallback for compact GGUF runtime | **Conditional only**. Test in a disposable context if the incumbent Ollama task benchmark proves a recoverability or performance gap; do not start a second permanent daemon |
| [uv](https://github.com/astral-sh/uv) · MIT or Apache-2.0 | Reproducible Python packaging and disposable builds | **Qualify a small fixture** for lock/replay and rollback; no global install or project migration |
| [Syft](https://github.com/anchore/syft) · Apache-2.0 | SBOM for traceable dependencies | **Read-only synthetic package scan** after defining redaction and notice handling; no secret-bearing private workspace scans by default |
| [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) · Apache-2.0 | Instrument observed WorkID steps, retries and receipts | **Defer until one actual WorkID** completes with a bounded receiver receipt and privacy-safe traces |
| [NATS server](https://github.com/nats-io/nats-server) · Apache-2.0 | Pub/sub and bounded cross-node messaging | **Defer until two separately controlled nodes** pass a typed handoff, idempotency and partition/recovery test |
| [Temporal server](https://github.com/temporalio/temporal) · MIT | Durable workflow replay and timing | **Defer complexity** until a tested requirement exceeds the existing fenced SQLite queue; no speculative production cluster |

Exact pinned upstream commit, license-blob SHA and license-file link for each candidate are in the JSON twin. These are observations at one date, **not** a compliance opinion or permission to copy a donor.

### Real local observation: prefer a parameter fix over a shopping spree

On the current authorized X2, the Ollama loopback endpoint returned version `0.40.18-rc0` and eleven installed model entries. A read-only API inventory demonstrated installation, but did not prove inference.

**Bounded inference canaries, one harmless synthetic evidence task:**
- The earlier long/default context trial yielded 35-second timeouts for `qwen3:4b` and a RickBar-derived 4B model. Preserve R0 negative receipt.
- A later `num_ctx=2048` trial classified one evidence item correctly using `qwen3:4b` in **2.08 s**.
- The derived RickBar model returned a malformed classification in **2.69 s**, despite completing the request.
- At the time of inspection, one loaded 4B model reported a 262,144-token context and an allocation far larger than its on-disk model file. This motivates context-budget review but does **not** prove the timeout's cause.

These observations are private X2 custody receipts, not public model-serving acceptance, CoStead-native ACK, second-host failover, or permission to expose private material.

## Proper placement

- **CoStacks:** existing [shadow/report-only repository](https://github.com/CoCivium/CoStacks). Add read-only evidence/validation adapters here only after review. Do not silently rebrand a shadow report as an autonomous control plane.
- **CoStax+:** no separately verified implementation found in the reviewed source. Treat as proposed alias/idea, not a new fork.
- **CoModelFabric+:** use [existing task routing and authority contract](../Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md) and [owner #277](https://github.com/CoCivium/CoSteward/issues/277).
- **GRAILS+:** the [CoLocal CoRelGRAILS source](../CoLocal/CoLocal2601109_CoRelGRAILS_CoSeed_R0.md) says its expansion is **tentative**. Preserve that uncertainty, rather than minting a controlling acronym without original-source reconciliation.

## Selection and diminishing-returns control

1. **Hard veto first:** missing rights/notice, private-data expansion, unqualified task correctness, effect/recovery fault, or unapproved external authority means HOLD regardless of score.
2. **Benchmark against what already works:** count task completion, corrections, latency, privacy, energy when measurable, user minutes saved, maintenance/recovery cost and independence of failure domains. A deterministic implementation must be in the baseline.
3. **Adopt the least dependent adequate implementation:** unchanged upstream CLI/API -> adapter -> upstream contribution -> provenance-preserving fork only when economically justified -> independent reimplementation only if necessary.
4. **Retest only on meaningful change:** upstream security advisory, license/ABI/API/weight update, task requirement change, or measured reliability gap. Never auto-pull a model or dependency simply because a tag moved.
5. **Stop when marginal benefit disappears:** after **two consecutive bounded sweeps** yield no new qualified ability, material security correction or measured net improvement, pause that candidate family. Keep critical advisories eligible to reopen it.
6. **Pay forward exactly one acceptance pattern:** a typed capability interface, pinned source/version/license, fixture suite, negative controls, chosen adapter, receipt, rollback and documented successor. The owner can reuse that across CoBar, CoGuardian, GroupBuild, RepoZipper and other work without inheriting claims of live runtime.

**Next elected proof:** complete a small representative CoModelFabric fixture set under bounded `num_ctx`, then verify one durable WorkID receipt independently. Only introduce a new local server, durable execution engine or event bus when the existing path fails a reproducible requirement.

**No effects by this artifact:** no upstream code imported; no installation, service restart, DNS mutation, public deployment, model-weight redistribution, model update, financial change, private data publication, external send or effect authority granted.
