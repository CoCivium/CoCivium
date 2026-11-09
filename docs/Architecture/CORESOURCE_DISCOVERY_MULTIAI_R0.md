# CoResourceDiscovery+ / CoModelFabric+ R0

**Status:** public research and onboarding contract; not a claim that listed providers are connected, licensed for every use, or contributing live results.

## Objective
Find, qualify, compare, and continually reconsider useful AI, IA, human, data, compute, library, research, simulation, visualization, and verification resources. No single provider, model, researcher, or worldview has permanent authority. Discovering a resource is not authorization to use it.

## Resource classes
- Local/open-weight language, code, reasoning, embedding, reranking, OCR, speech, vision, multimodal and small specialist models.
- Authorized hosted model APIs and research assistants, including long-context analysis, web-grounded discovery, scientific literature, mathematics, theorem proving, code, security, data and image/video capabilities.
- Open research indexes, archives, scholarly APIs, citations, public datasets, knowledge graphs, reproducible benchmarks, package registries and standards.
- Human domain experts, open communities, universities, peer reviewers and citizen researchers, with consent.
- Deterministic tools: search, parsers, static analyzers, formal solvers, simulators, unit tests, CI, provenance and reproducibility tools.
- Hardware, compute, storage and execution substrates, including local X2, CoStead, and explicitly authorized remote services.

## Candidate discovery venues (not integrations)
- [Hugging Face Models](https://huggingface.co/models) and [Datasets](https://huggingface.co/datasets): model cards, licenses, tasks, evaluation and provenance.
- [Ollama model library](https://ollama.com/library): local model candidates, check actual installed model/version and terms.
- [OpenRouter models](https://openrouter.ai/models): multi-provider model discovery, subject to service policies, price and privacy.
- [arXiv](https://arxiv.org/), [OpenAlex](https://openalex.org/), [Semantic Scholar](https://www.semanticscholar.org/), [Crossref](https://www.crossref.org/), [PubMed](https://pubmed.ncbi.nlm.nih.gov/): scholarly discovery and citation cross-checking; access and redistribution terms differ.
- [Papers with Code](https://paperswithcode.com/) and [GitHub](https://github.com/): benchmark/code candidates; popularity is not validity.
- [Zenodo](https://zenodo.org/), [Internet Archive](https://archive.org/), [Wikidata](https://www.wikidata.org/): archival, dataset and linked-knowledge candidates; check item-specific licenses and quality.
- [OpenML](https://www.openml.org/) and [Kaggle](https://www.kaggle.com/datasets): benchmark/data candidates; inspect usage terms and privacy.

## Resource candidate schema
```text
resource_id | class | provider | endpoint_or_source | capabilities[]
access_state | auth_scope | cost_currency | estimated_cost | context_limit
license | redistribution | privacy | retention | geographic_constraints
version | observed_at | evidence_refs[] | benchmarks[] | uncertainty[]
failure_domain | reliability | latency | source_coverage | known_biases[]
effect_authority | consent | status | successor | reviewer
```

Unknown fields remain UNKNOWN, never guessed. Do not put credentials, private prompts, or personal data in the public registry.

## CoResearchBraid: independent discovery to usable evidence
1. Form a typed question, source scope, date horizon, budget and success criterion.
2. Retrieve with two or more genuinely distinct sources/methods when worthwhile; label shared upstream dependencies.
3. Preserve original citations, access times, exact claims, contradictions, missing evidence and negative results.
4. Run specialist methods (dedup, entity resolution, temporal comparison, statistics, code/formal verification).
5. Assign independent challenge or adversarial review, including alternative explanations and falsification.
6. Curate evidence graph and uncertainty; retain dissent, superseded versions and rights boundaries.
7. Produce a receiver-specific artifact: RickBar answer, CoMap relation, public source-linked brief, dataset, experiment or work ticket.
8. Verify recipient/readback and measured usefulness; schedule refresh only when new evidence or a real trigger warrants it.

## Anti-monoculture and anti-fabrication rails
- Model count is not independence. Different wrappers may call the same upstream model or share training data.
- Source citation is not validation; a cited claim may be wrong, stale, or misinterpreted.
- Search volume and graph size are not progress metrics. Measure coverage, accuracy, contradiction discovery, reproducibility, latency, cost, provenance and user outcome.
- Reserve explicit human gates for rights, safety, private information, external publication/sending, credentials, financial effects and irreversible actions.
- Prefer local/private processing when source terms and task sensitivity permit. Never use unapproved external APIs with sensitive content.
- Keep competing candidates; no permanent boss, automatic winner, or forced consensus.
- If tools or credentials are absent, produce a reproducible candidate/evaluation plan, not a fabricated integration.

## First operational benchmark
Compare three research routes on the same ten public-domain questions:
(A) one general model;
(B) two independently sourced retrieval methods plus one model;
(C) specialist retrieval, independent model challenge and deterministic citation/claim checks.
Predeclare scoring: factual accuracy, source traceability, contradiction coverage, hallucinations, latency, cost, freshness and reproducibility. Include questions where the simplest route wins. Publish only evidence-backed outcomes.

## Integration anchors
- [AI/IA Evergreen Onramp](../Onramp/AI_IA_COORBWARE_EVERGREEN_R0.md)
- [CoGoAll Rebound Hub](../Onramp/COGOALL_PUBLIC_REBOUND_HUB_20261108.md)
- [CoModelFabric adapters](COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md)
- [CoGoAll Outstanding Register](../Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md)
- [CoGoldenBraid research](../Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md)

**Promotion gate:** A candidate becomes AVAILABLE only with actual authorized access proof; CONTRIBUTING only with WorkID, source/adapter identity, input/output provenance and independent readback; VERIFIED only with measured task outcome. WhatsApp text and GitHub source publication alone do not satisfy these gates.
