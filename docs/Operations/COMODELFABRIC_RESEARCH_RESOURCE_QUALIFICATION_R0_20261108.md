# CoModelFabric+ | Independent AI and Research Resource Qualification R0

**Observed:** 2026-11-08. **State:** PUBLIC CANDIDATE SOURCE REGISTRY, NOT provider enrollment, funding approval, authority grant, live orchestration or model-session pickup.

## Goal

Coordinate ChatGPT, the user's WhatsApp Meta AI channel, authorized local Ollama models, additional independent AI systems, deterministic checkers, and external scholarly research APIs through existing [CoModelFabric](../Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md), [CoVirtualSession](../Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md) and [CoReGroup](../Evolution/COREGROUP_PEER_EVIDENCE_CONTRACT_R0.md) work. Use one source-bound WorkID and one rickBar/CoOrb view; do not create separate ongoing chat empires.

**Actual participation:**
- ChatGPT: public GitHub proposal commits, reviews and source/CI observations exist; those are not automatic cross-provider federation.
- WhatsApp Meta AI: user reports the AI Onramp Hub note was pasted into that channel; **USER_REPORTED_SENT, NOT RECEIVER_ACK**. Do not infer that Meta AI opened links, retained context or made contributions.
- Ollama: local API/worker candidates exist and prior metadata probes were described, but current authenticated X2 receiver and full rickBar-to-model invocation remain unverified.
- Other providers: candidate only; no unauthorized login, credential harvesting, free-tier abuse or claims of agent independence.

## Current candidates for research and computation

| Resource | What to test first | Evidence/rights and cost boundary | State |
| --- | --- | --- | --- |
| [OpenAlex REST API](https://help.openalex.org/api/) | Topic/paper graph retrieval and deduplication | Basic use free; key/budget for scale, verify terms, timestamps, rate limits, external metadata provenance | QUALIFICATION_CANDIDATE |
| [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api) | DOI normalization, publication updates, licensing and corrections | Public metadata, verify retractions/correction flags from their source | QUALIFICATION_CANDIDATE |
| [Semantic Scholar Academic Graph](https://api.semanticscholar.org/api-docs/graphs) | Citation graph and competing paper recommendations | Public endpoints with limits; API key and throttling required for reliable usage | QUALIFICATION_CANDIDATE |
| [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/en/index) | Compare two independently selected open model families on the same WorkID | Account/token required for hosted inference; free quota/paid terms and data disclosures separately gated | QUALIFICATION_CANDIDATE |
| [Ollama](https://ollama.com/) | Existing loopback adapter, local model inventory and one consented inference | Hardware/energy costs; X2 live proof absent | EXISTING_SOURCE_ADAPTER__X2_UNVERIFIED |
| [CoCivium AI Onramp Hub](https://github.com/CoCivium/CoCivium/pull/381) | Locate peer work, exact source revisions and the public 1,892-path catalog | Public proposal branch, no external peer pickup implied | SOURCE_LANDED |

The provider/docs links above are reference documentation, not endpoint credential validation or actual dispatch receipts.

## Diverse parallel work, without false consensus

**WorkID:** scoped research question, source collection scope and expected output contract.

1. **Evidence acquisition:** public metadata collectors query independent source families, then deduplicate by DOI / stable work ID and record retrieved-at, publication date, version, retraction/correction status and license.
2. **Independent hypotheses:** open local model and at least one truly distinct provider/model class generate separate proposals *before* seeing one another's responses.
3. **Discriminating challenge:** independent reviewer searches for contradictory evidence, alternative explanations, missing works and source failures. Multiple opinions trained on the same sources are not multiple independent observations.
4. **Deterministic verification:** DOI identity, retrieval timestamp, citation validity, rights flags, numerical calculations and exact artifact digests are checked without asking an LLM to certify itself.
5. **Adjudication:** publish consensus only when evidence supports it; preserve minority findings, confidence calibration, cost and explicit UNKNOWNs.
6. **Routing:** elect one temporary effect actuator for conflicting writes; parallelize read-only research, summarize/dedupe tasks and test fixtures under bounded budgets.
7. **Product view:** rickBar shows one coherent summary, evidence freshness, unresolved dissent, next authorized action, Stop and recovery.

## Qualification and scoring, not model-count theater

Each candidate adapter requires: `source/provider | model/version | capability | independent failure-domain | terms/license | privacy | cost/credits | throughput/context | evaluation task | verifiable outcome | source observation date | auth state | failure/stop behavior | receipt`.

Benchmark with a real, pre-registered question and gold source set. Compare single model, multiple independent models, deterministic metadata collection, and team adjudication. Metrics: grounded accuracy, citation correctness, novelty of relevant discovery, false positives, recall, retraction detection, time to first useful result, cost, energy, user involvement and recovery under worker loss.

**Pass gate:** measured improvement on held-out questions at acceptable cost and no rights/privacy regression. **Failure gate:** redundant/low-diversity answers, source hallucination, stale retrieval, unexplained costs, unsafe disclosure, no genuine net information gain or dependence on manual user relay.

## Three bounded parallel experiments

- **A: Scholarly retrieval:** retrieve one CoCivium-relevant research topic via OpenAlex + Crossref + Semantic Scholar, compare overlap, missing works and correction metadata. Source results must be independently read back.
- **B: Model diversity:** identical source packet to an authorized local Ollama worker and a qualified external distinct model; independently challenge citations and compare against single-model baseline.
- **C: Coordination/UX:** feed the same WorkID and independently verified outcomes through CoTalkItOut/CoReGroup; measure whether rickBar can display only one useful work object instead of new windows and human-pasted prompts.

No automatic API access or deployment claimed by this document. Credentials, personal data, new spending, external messaging and real X2 mutation retain their separate gates. Stop retrying a blocked provider until a material change occurs.

## No-one-AI rule

A **role** is not an actual connected agent. A public GitHub README is not an ACK. A WhatsApp pasted message is not remote execution. Independent models can still share source errors. Open-source code is not automatically free inference. The enduring intelligence is the versioned evidence-and-work fabric, not any provider's memory or account.

**Next observed effect to seek:** one real, attributable contribution from an independently connected research service, then one separate model critic, both with original source receipts, through existing CoModelFabric lanes. Preserve public-first sanitized output; do not claim native X2 integration yet.
