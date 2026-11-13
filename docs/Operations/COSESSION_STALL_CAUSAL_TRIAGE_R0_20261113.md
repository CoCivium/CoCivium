# CoSession+ Causal Stall Triage and Provider-Independent Recovery R0

**Observed:** 2026-11-13. **Status:** PUBLIC-SAFE RESEARCH RUNBOOK; UNEXECUTED PROVIDER-UI A/B PROTOCOL; NOT INCIDENT ROOT-CAUSE PROOF, RUNTIME, CANON, ACCOUNT-MIGRATION AUTHORIZATION, OR GLOBAL CENSUS.

## CoHereNow

A participant reports that numerous long-lived manual ChatGPT conversations take hours to become usable after attempting to resume. This is real user-experience evidence, but **not** an instrumented backend trace or proof of provider "resynchronization." Claims of token exhaustion, DOM overload, internal context compaction, throttling, or deliberate provider interference remain **HYPOTHESES**. No exact count of affected sessions, context tokens, affected tabs, or recurring error codes has yet been independently sampled.

**Goal:** separate the causes of apparent session unresponsiveness and demonstrate that a CoAll WorkID survives any affected provider conversation and renderer.

## Donor architecture: reuse, do not spawn a rival controller

- [CoSessionAutocycle](../Architecture/COSESSION_AUTOCYCLE_R0.md): virtual-first, shadow-only provider mutation.
- [CoReGroup](../Evolution/COREGROUP_PEER_EVIDENCE_CONTRACT_R0.md): CoGrace/CoZombie triage; evidence of overdue obligation *and* stale progress required before declaring stalled.
- [CoHereNow convergence](../Architecture/COHERENOW_CONVERGENCE_R0_20261027.md): shared UI does not erase source identities.
- [CoBrowser renderer substitution](../Architecture/COBROWSER_RENDERER_SUBSTITUTION_R0_20261027.md): renderer != WorkID.
- [CoSession Git lifecycle crosswalk](../Evolution/COSESSION_GIT_LIFECYCLE_CROSSWALK_R0_20261113.md): merge/fork/cherry-pick/squash/cold rehydrate vs deletion.
- [CoFrontierExit](COFRONTIEREXIT_GRACEFUL_PIVOT_R0_20261112.md): account-specific provider exit and restore proof.
- [CoGoAll outstanding register](COGOALL_OUTSTANDING_REGISTER_20261108.md): prioritize actual X2 WorkID and receipt UX over more watchers.
- Exact three-public-donor source test on draft PR #490: **Git source roundtrip and X2-local one-shot receiver are distinct from browser recovery and independent failure-domain acceptance**.

## External evidence, not case-specific diagnosis

- OpenAI troubleshooting: browser extensions, network/socket problems, long conversations, local profile state, transient server failures, clean-window tests: https://help.openai.com/en/articles/7996703-troubleshooting-chatgpt-error-messages
- OpenAI incident log shows recent conversation or login incidents; incidents do not establish today's case: https://status.openai.com/history
- Main-thread tasks and input/render jank (where browser instrumentation supports it): https://developer.mozilla.org/en-US/docs/Web/API/PerformanceLongTaskTiming
- Long-context retrieval can degrade by evidence position in tested models; does not imply the browser or model is currently hung: https://aclanthology.org/2024.tacl-1.9/

## Causal strata and falsifiers

| Candidate mechanism | Expected signature | Distinguishing negative control |
| --- | --- | --- |
| CLIENT_RENDER / DOM / JS long task | keypress and scroll delays, main-thread stalls, long render after response already arrives | same work in fresh renderer/profile, network and backend normal |
| DEVICE_RESOURCE / CONTENT_PROCESS | unusually high per-process working set, page faults, memory pressure, CPU/GPU contention | memory/CPU below pressure with same long chat still failing |
| NETWORK / WEBSOCKET / PROXY | socket failure or stalled stream, requests pending/aborted; UI may remain responsive | same time/network alternate website and new chat tests; separate transport from server |
| AUTH / SESSION HYDRATION | specific old conversation fails to load or authorize despite healthy new chat | same account fresh chat works, old conversation loads in other browser? |
| SERVICE / MODEL / TOOL | model response absent/delayed across browsers while UI responds; incident/window correlations | fresh, same-model request at similar time; compare tool-free turn |
| ACCOUNT ALLOWANCE / THROTTLE | explicit rate-limit, allowance or retry metadata; account-wide symptoms | don't infer motives or hidden limits from long spinner; record actual codes |
| LONG_CONTEXT / COMPACTION | old context not faithfully used, error/latency tied to input size, middle facts lost | short reconstruction of same task, same model/version; measure answer fidelity not spinner |
| COORDINATION / USER-WORKFLOW | repeated prompt loops, too many active work fronts and manual session relays | WorkID with durable checkpoint and one leased worker completes without old chat |

**Key rule:** symptom clusters do not identify a unique cause. A large desktop process count is a machine observation, not a tab-to-chat attribution. Context-window size, raw transcript size, model input, rendered DOM length and server token/allowance billing are **five different quantities**.

## Minimal bounded test design

Use a consented, nonprivate diagnostic task and 1-3 representative *already existing* long conversations; do not create a load-test swarm.

- **A (baseline):** fresh short test conversation in a clean profile with no extensions. Record UI input-to-echo, history load-to-interactive, send-to-ack, first-visible-output and completion times.
- **B (long vs short):** one eligible existing long thread, same account/model/browser. Do not paste private transcript into diagnostics; use approved neutral probe only.
- **C (renderer/profile):** same long conversation after user-authorized alternate Firefox/Edge clean-profile access. Test without creating/closing provider tabs without explicit authority.
- **D (provider exit):** reconstruct the same bounded, public-safe WorkID in a freshly started *local* worker or deterministic renderer using only durable source pointers. Require exact receiver-generated receipts and a useful output.
- **E (no-working-provider):** simulate an unavailable provider adapter with a synthetic fault. Demonstrate queued work is not lost, duplicate effect is fenced, and healthy dormant workers stay asleep.
- **F (semantic):** small key/reference retrieval with a fact placed at start, middle and end; compare error rate and references across length/summarization conditions. No inference from a single answer.

Do **three separated observations per eligible condition** if practical, not hundreds of concurrent browser requests. If any condition violates privacy, account terms, resource ceilings, or cannot be instrumented, mark **NOT_TESTED**.

## Capture contract (private raw evidence; public only aggregate)

`test_id | work_id | environment_class | browser_app_version | account_scope_pseudonym | conversation_class (short/long) | client_observed_time | provider_status_at_time | page_input_latency_ms | page_load_ms | request_ack_ms | first_output_ms | completion_ms | ui_long_tasks_count? | process_working_set_mb? | host_available_memory_mb? | socket_http_error_class? | rate_limit_evidence? | source_digest | screenshot_or_trace_private_ref? | source_cost | consent | confidence | last_healthy | retry_count | disposition`.

Never store passwords, cookies, access tokens, live chat contents, HAR with authorization headers, private conversation IDs, full page HTML, or raw private transcript in a public repository. Raw browser diagnostics are private and can contain secrets even when an export appears innocuous.

## Decision rules

- **CLIENT_CAUSAL_SUPPORT** only with repeatable client latency/jank evidence and comparative improvement without source or network change.
- **TRANSPORT_CAUSAL_SUPPORT** only with actual failed/delayed transport evidence and controls.
- **SERVER_CAUSAL_SUPPORT** only with repeatable cross-client failures or direct provider-specific error evidence; an outage dashboard alone is a possible confounder.
- **CONTEXT_CAUSAL_SUPPORT** only with measured source/input size and loss, latency or refusal tied to context under adequate controls. A large chat is not proof of the actual model prompt.
- **MULTIFACTOR** is allowed, especially client memory pressure plus long-context model limitations plus service load.
- **UNKNOWN / HOLD** default when evidence is sparse.
- **HEALTHY_QUIET** must not be mislabeled zombie solely because no recent messages exist.

## Product acceptance instead of infinite diagnosis

For a sampled work packet, compare **legacy-chat baseline** to **CoAll WorkID successor**:

1. Task completion and semantic correctness, with source references.
2. Time to recover after page refresh, renderer switch and worker crash.
3. Human copy/paste and resynchronization steps (target zero where adapter-authorized).
4. Work surviving loss of original live chat, browser, account or model.
5. Privacy/authority violations, duplicate effects, rollback success.
6. P50/P95 input latency, usable-first-response time, receiver-readproof time, CPU/RAM/token cost.
7. Count of actual active provider embodiments, not virtual WorkIDs or preserved source records.
8. Falsification: if the alternate does not improve a measured outcome or loses source fidelity, retain baseline and mark **NOT_YET_BETTER**.

**Receiver UX:** one CoHereNow/CoOrb front with currentness age, task state, next safe action, one Stop/recovery control and optional evidence; no wall of machine telemetry or pop-up PS7 loops.

## Inversions / turtles / stop

- **CoNonChat:** useful work with no persistent conversation.
- **CoNoResync:** reload only validated WorkID deltas, not an entire chat transcript.
- **CoAntiWake:** quiet is success where obligations are satisfied.
- **CoGrace vs CoZombie:** genuine stale obligation with proof vs merely old tab.
- **CoUnmerge:** every compacted donor can be source-rehydrated while custody persists.
- **CoAntiMonitor:** observability itself must not overwhelm the browser or system.
- **CoFailureAsFixture:** sanitize source-bound incidents into reproducible negative controls.
- **CoExitProof:** measurable independent restore and takeover, not symbolic migration.
- **CoUXReceipt:** recovery must be useful to a human receiver, not simply hash-correct.
- **CoTurtleStop:** no new coordinating meta-level unless marginal verified benefit exceeds added maintenance and attention cost; retire recursive diagnosis when it does not change decisions.

## Bounded status

Existing local X2 one-shot public-donor verification is a **local source-recovery rung**, not this browser diagnostic experiment. This document does not claim user sessions instrumented, causes established, chat histories exported, account exit-ready, continuous automation proven, or model backend access.

**Next elected test:** one privacy-safe, consented A/B comparison of **fresh short** vs **one long** conversation with browser responsiveness measured separately from request/stream state; preserve resulting private evidence and publish only anonymous aggregate observations. If provider-interaction adapter is absent, test a standalone local WorkID recovery with no claims about the provider's root cause.
