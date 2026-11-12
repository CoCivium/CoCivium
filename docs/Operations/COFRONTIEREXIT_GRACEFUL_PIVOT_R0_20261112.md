# CoFrontierExit+ | Graceful provider migration R0

**Date:** 2026-11-12. **State:** PUBLIC_SAFE_PROOF_BOUND_PLAN; no provider billing change, cancellation, export, account migration, X2 deployment, CoStead receiver ACK, CoAll canon, or production cutover. **Owner scope:** CoModelFabric+ / CoLocal+ / rickBar continuity + CoReGroup evidence, not a new control plane.

## CoHereNow

A user reports irregular or session-specific frontier-service usage allowances, including extended periods of service unavailability. This is a field observation; provider motives, undisclosed quota mechanics, and account-specific limits are **not established** here.

Published provider documentation already establishes variable usage allowances and an announced future shared allowance architecture. A fluctuating limit is an engineering risk even when the provider is acting reasonably. The objective is not to defeat limits; it is to stop losing CoCivium work when a service is unavailable.

**Architecture inversion:** `WORK_IDENTITY > PROVIDER_SESSION`. A model can be replaced; WorkID, provenance, permissions, and authorized durable state must remain reconstructable.

## Reuse instead of rebooting the whole architecture

| Existing owner/source | Reusable evidence or code | Missing native proof |
| --- | --- | --- |
| [CoModelFabric adapter contract](../Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md) | provider identity, capability, privacy, lease, cost, latency, evidence | X2 effective multi-provider routes |
| [Local model worker R3](COLOCAL_MODEL_WORKER_R3.md) | public-only loopback Ollama candidate worker | actual current X2 model canary |
| [rickBar Continuity R1](../Architecture/RICKBAR_CONTINUITY_R1_20261108.md) | SQLite WorkID/TurnID, model fencing, restart test design | native rickBar/X2 model integration; independent receiver recovery |
| [CoReGroup](../Evolution/COREGROUP_PEER_EVIDENCE_CONTRACT_R0.md) | source-bound multi-worker fan-in and elected writer | live cross-session adoption |
| [CoLocal X2 foreground incident](../../ai/currentness/colocal-x2-foreground-interruption-20261112-r0.json) | typed unresolved UI safety blocker | actual popup causality / quiet input acceptance |

**New bounded executable:** [Provider Exit Readiness R0](../../examples/comodelfabric/provider_exit_readiness_r0.py), [26 synthetic negative controls](../../examples/comodelfabric/test_provider_exit_readiness_r0.py), [existing CoModelFabric workflow](../../.github/workflows/comodelfabric-ollama.yml). This is a *pure classifier*, not an exporter, router, installer, daemon or cancellation robot.

## CoHP+ vs CoHp+ | future-pull then proof

**CoHP+ human aim:** At any time, a consenting human can recover a private, comprehensible, responsive CoCivium experience on their available authorized hardware without needing a particular frontier subscription. Specialized paid providers may still be optionally engaged for demonstrably valuable tasks.

**CoHp+ execution:** Advance only when each stage is verified with the correct receiver, provenance and consent.

| Stage | Must be shown | Blocker / downgrade |
| --- | --- | --- |
| S0 Preserve | Provider-independent WorkID and source-bound public/private manifests; baseline archived separately | A public repository pointer does not contain private conversation history |
| S1 Local shadow | One actual authorized loopback model output on a harmless public-safe task, with pinned version, privacy/terms preflight and local checkpoint | Source or synthetic CI is not a live X2 model |
| S2 Continuity | Restore same WorkID and checkpoint after process restart, fenced epochs, one durable receiver-origin exact-object readproof | Same-host save, model response or self-generated receipt is insufficient |
| S3 Local primary **pilot** | A measured real user task on rickBar/CoAll surface, zero unsolicited foreground steals in a qualified window, native fallback and Stop tested; compare latency, task success, energy, cost and human relay | X2 popup issue remains open; no blind model switch |
| S4 Data portability | Authorized account-owner export or admin-supported data-access process, encrypted custody, scope/coverage verification, rights and retention review | Chat export cannot be assumed universal, complete, or a session rehydration |
| S5 Subscription review | Paid dependency no longer required for the tested baseline; billing/terms reviewed; explicit human approval per account and retirement date | No automatic financial/credential/account effects |
| S6 Monitor and evolve | Periodic requalification triggered by meaningful evidence or availability changes, not new foreground PS7 polling loops | CI and published notes do not replace real receiver status |

**No automatic phase promotion.** Any missing gate remains HELD. S1 may progress in a disconnected X2 environment only after a *real* authorized local endpoint can be observed. No pretend X2 pass.

## Provider allocation without provider captivity

The reference router should **propose** resource classes in this order, conditioned on task fit, permissions and measured quality, not a hard-coded provider preference:

1. deterministic functions or existing local indexes/tests where a model is unnecessary;
2. small local model for bounded classification, summarization or extraction;
3. qualified stronger local worker when latency, quality, memory and energy justify it;
4. an explicitly approved, distinct hosted provider when local confidence or capability fails;
5. a human decision gate for irreversible, financial, privacy, safety or publication consequences.

Never silently fall back from private/local to a hosted provider. No multiple-account quota evasion. Retry budgets must be bounded, shared-task mutation single-writer, and any unavailable worker may yield a truthful HOLD rather than fabricating an answer.

**In-between state matters:** `AVAILABLE / DEGRADED / LIMITED / UNAVAILABLE / UNKNOWN` is a route observation, not an identity or content state. A hosted outage does not change who owns the WorkID, what has landed, or what has been consented to.

## Metrics / CoMeasure+

Record as candidate typed units, **not measured performance**:

| Candidate measure | Unit / evidence |
| --- | --- |
| CoProviderDependency+ | percent of indispensable tasks that require one specific vendor, sampled over defined WorkIDs |
| CoQuotaInterrupt+ | interrupted tasks / eligible tasks; unavailable duration in minutes, with observed source |
| CoRecoverability+ | recoverable committed WorkIDs / scoped WorkIDs after a true cold restart and independent receiver check |
| CoTaskParity+ | matched task completion and correctness against an authorized reference, with holdout cases |
| CoLatencyP95+ | seconds from accepted request to usable output; include device and model version |
| CoJoulesPerProof+ | measured joules per qualified result, not per model token |
| CoHumanRelay+ | manual prompts/copies/restarts per completed WorkID |
| CoAttentionIntrusion+ | unexpected foreground/focus changes per defined active-input interval |
| CoExitFriction+ | elapsed effort and rights/authority steps from export request to verified recoverable corpus |
| CoCrownRisk+ | count of irreplaceable single-provider continuity dependencies; bound by capability and failure domain |

Good values are **lower provider dependence, lower interruption, higher recoverability, maintained quality, and fewer human steps**. The baseline measurements are UNKNOWN until actually collected.

## CoInEx+ and privacy boundary

Public: publish architectural contracts, synthetic test fixtures, redacted provider status, model cards/licenses, source hashes and candidate CoPaths.

Private/restricted: keep credentials, conversations, health/family/financial contents, billing, exported archive bytes and private CoStead manifests in access-controlled custody. Export links and raw account histories must never be used as public Seed content.

`DISCOVERED -> VERIFIED_LOCAL -> LANDED -> PICKED_UP -> INTEGRATED -> COEX` is a proof sequence, **not** a synonym for upload. Producer hashing cannot provide a receiver-origin readproof. CoAll/adoption is a later transition requiring explicit acceptance.

**Account export caveat:** OpenAI's Help Center says eligible personal plans support ChatGPT data export and that Business/Enterprise self-service export is unavailable. An actual account/workspace owner must check the applicable route. Archive exports are references, not automatic restoration of ChatGPT workspace history or permissions. Retire subscriptions only after qualified recovery, reviewed billing, and explicit human authorization. No provider-specific claims about the user's actual workspace have been established here.

## CoInversion+, CoBetween+, CoTurtle+ / CoTalkItOut+

- **Inversion:** Start with 'provider disappears for 24 hours' and test whether WorkID remains usable. Start with 'cancel safely' and work backward through export coverage, receiver custody, local quality and human assent. Start with 'X2 keyboard usable' and challenge every focus-stealing launch.
- **Between:** Model workers and WorkIDs, export requests and actual bytes, local checkpoints and receiver acceptance, UX visibility and real usability, user permission and provider contractual scope are separate relations.
- **Turtles:** Recheck the model benchmark's references, the receiver receipt's source, and the routing decision's uncertainty. Bound recursion by independent information gain and a single elected effect owner.
- **CoTalkItOut+:** Competing sessions must submit distinct falsifiable proposals and evidence with source SHA; consensus among copied prompts is not independent proof.

## Migration readiness decision semantics

The evaluator accepts one pre-qualified, fresh `CoAll.CoModelFabric.ProviderExitEvidence.R0` JSON assessment and returns a typed decision with `HOLD`, `SHADOW`, `LOCAL_PRIMARY_PILOT_ELIGIBLE`, or `HUMAN_RETIREMENT_REVIEW_READY_NO_ACTION_AUTHORIZED`. It never accesses providers or stores. It emits neither account exports nor input prompts nor credentials. Even the strongest state explicitly has `subscription_retirement_authorized=false`.

**Source-only CI passing does not certify X2 hardware, local model deployment, user interface recovery, export completeness, or subscription cancellation.**

## Actual next safe deed

**When X2 has an authorized machine-observable path:** execute a single existing-model, PUBLIC-only, loopback local-model canary through the already published CoLocalModelWorker R3, preserve a hash/readback for the resulting WorkID, and test the same WorkID against rickBar continuity. Do not modify the scheduled CoAll Desktop R5 launcher or add recurring PS7 tasks while the popup source is still unqualified.

If the direct host path remains unavailable, pursue only public-safe synthetic source improvements and HOLD live acceptance. Do not require the human to paste prompts into many sessions.

### Source references

- [OpenAI model and usage limits](https://help.openai.com/en/articles/20001354-gpt-56-in-chatgpt)
- [Understanding ChatGPT and Codex usage limits](https://help.openai.com/en/articles/20001625-understanding-chatgpt-and-codex-usage-limits)
- [ChatGPT data export](https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data)
- [ChatGPT account transfer limits](https://help.openai.com/en/articles/9106926-transferring-conversations-from-1-chatgpt-account-to-another-chatgpt-account)
- [vLLM compatible server security boundary](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/): compatibility is not a security guarantee.

**Nonclaims:** `LOCAL_IS_NOT_LANDED`; `VALIDATION_IS_NOT_ACCEPTANCE`; `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`; `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`; `HASHING_IS_NOT_SEMANTIC_INGESTION`; `DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`.
