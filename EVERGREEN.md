# CoGoAll Evergreen Blast R0

**Public working status · 2026-10-23**

> **Publish the best we have, never ready. Update all we can, never perfect. Improve all we can, never finish. Log what can be tested. Preserve what failed. Keep evidence ahead of assertion.**

CoCivium / CoAll is public R&D. This page is a living front door to the most useful proof-backed work we currently have. Nothing here is a claim of completeness, universal adoption, independent validation, or finished product status.

## CoHereNow

### PASS · CoAndrewFirst+ R0

A dependency-free five-minute browser prototype is merged.

It gives a first-time user:
1. one measured result;
2. exact evidence inspection;
3. deterministic challenge mode;
4. explicit simulated-versus-observed boundaries;
5. a local browser receipt.

R0 performs **no model call**. Claude, Pi, Llama-family/local open-source models, OpenAI-compatible endpoints, and historical replay are candidate adapter lanes, not live integrations.

- PR: https://github.com/CoCivium/CoCivium/pull/193
- post-merge CI: https://github.com/CoCivium/CoCivium/actions/runs/39887149595
- run locally: `python -m http.server 8000`, then open `/examples/coandrewfirst/`

### PASS · CoLogicalSession Million Preview R0

The repo can represent very large logical-session populations without opening the same number of processes, provider chats, accounts, or workers.

R0 supports a declared logical population up to `10^12`, samples at most 100 descriptors, and starts zero workers/provider sessions/accounts.

`LOGICAL_SESSION_COUNT_NE_ACTIVE_PROCESS_COUNT`

- PR: https://github.com/CoCivium/CoCivium/pull/194
- post-merge CI: https://github.com/CoCivium/CoCivium/actions/runs/39887859347

### PASS · CoExperimentSpace+ / CoTurtles+ R0

The current exact syntactic candidate space is:

**422,730,484,678,656,000 descriptors**

That is a descriptor count, not a useful-experiment count and not an execution plan.

Runtime turtle recursion remains bounded to depth two / two review rounds, with shared parent budgets and no authority or budget creation by nesting.

- PR: https://github.com/CoCivium/CoCivium/pull/196
- post-merge CI: https://github.com/CoCivium/CoCivium/actions/runs/39888764202

### PASS · CoExperimentSelector+ R0

A bounded selector can choose a tiny experiment frontier from an explicitly annotated candidate pool.

R0 uses Pareto layers plus reserved `CHALLENGE`, `EXPLORATION`, `WEIRD`, `REPLAY`, and `FAULT` lanes.

It does **not** invent information gain, receiver value, novelty, independence, cost, latency, risk, coordination debt, or proof debt from experiment names. Every estimate requires an evidence reference.

`SELECTED_NE_EXECUTED`

- PR: https://github.com/CoCivium/CoCivium/pull/197
- post-merge CI: https://github.com/CoCivium/CoCivium/actions/runs/39889097022

### PASS · CoStretch+ Benchmark Plan R0

CoStretch+ now means **maximum justified stretch**, not literal maximum utilization.

The planner emits bounded ladders over logical workload, concurrency ceilings, repetitions, wall-time, memory, and optional cost budgets. It records correctness, throughput, tail latency, errors, resource use, currentness debt, proof debt, and receiver value.

`HIGH_UTILIZATION_NE_HIGH_VALUE`

- PR: https://github.com/CoCivium/CoCivium/pull/198
- post-merge CI: https://github.com/CoCivium/CoCivium/actions/runs/39889314853

## Historical redo / CoReplay+

Historical work should be revisited without overwriting it.

Target pattern:

`old artifact + exact available inputs + known/unknown old environment + current replay lanes + fixed evaluation criteria + preserved diff`

Rails:

- `SAME_PROMPT_NE_SAME_EXPERIMENT`
- `NEWER_MODEL_NE_BETTER_RESULT`
- `PROVIDER_DIVERSITY_NE_EVIDENCE_INDEPENDENCE`

Historical replay remains **candidate / not yet landed as a qualified runtime**.

## Provider-neutral first

CoAndrew+ and future CoWorkers should treat models as replaceable execution substrates behind stable task/evidence contracts.

Candidate lanes include:

- deterministic local code;
- Claude;
- Pi;
- Llama-family and other local/FOSS models;
- Ollama / compatible local runtimes;
- OpenAI-compatible endpoints;
- future provider adapters;
- historical runtimes when reconstructable.

A listed lane is not proof of configuration, credential availability, model equivalence, or execution.

## Million sessions, better not traps

The desired scaling pattern is:

`huge logical reserve -> bounded selector -> small active frontier -> receipts -> sleep / wake / checkpoint / resume`

Not millions of deceptive accounts, synthetic public activity, or anonymous interactions designed to bait humans or models.

Transparent adversarial fixtures are encouraged. Fake social activity is not a research primitive.

## CoTurtles+

Everything that evaluates something may itself be evaluated.

But recursion is flattened between bounded waves:

`experiment -> challenge -> verifier -> receipt -> flatten -> next wave`

This preserves indefinite meta-evolution without unbounded live recursion.

## Values / working culture

- **LoLs** = lots of layers, laughs, love, learning.
- **Pay forwards + sideways.**
- **FOSS Forever.**
- **CoGoAll.**
- **Working Together Respectfully.**
- **Privacy by design.**
- **Inclusive, respectful, optional participation.**
- **Display may be required for a surface; wearing it is optional.**
- **FFFF / zero holdings** is a project phrase, not an audited financial statement.
- No crowns, no coercion, no corruption.
- Public visibility does not imply endorsement, consent, ownership, adoption, or canon.

## Evergreen deed

For every meaningful wave:

1. publish the best proof-backed artifact available;
2. mark `PASS`, `FAIL`, or `HELD`;
3. bind exact evidence or an explicit hold reason;
4. compare against a pinned baseline;
5. preserve regressions and dissent;
6. update instead of pretending perfection;
7. promote only measured improvements;
8. keep reversible safe work moving;
9. keep human gates for privacy-sensitive, financial, security-sensitive, irreversible, or materially consequential external actions;
10. never infer landing, pickup, integration, runtime adoption, or public acceptance from local presence.

Machine-readable evolution receipts live in:

`ai/benchmark-evo.jsonl`

## Current next high bars

- bind CoExperimentSpace+ samples to evidence-backed selector annotations;
- benchmark selector policies against random / first-N / challenge-heavy / novelty-heavy baselines;
- run one harmless measured CoStretch micro-canary;
- qualify one transparent provider adapter while preserving deterministic fallback;
- qualify historical replay planning and one bounded replay cell;
- test CoAndrewFirst+ with a real fresh receiver and record exact readproof;
- add receiver surfaces only when their actual route is evidenced.

## Receiver nonclaims

GitHub is a public projection and currentness surface. It is not universal custody.

At this snapshot no repository-backed receiver was found for `.nodes`, `nodes`, `.sites`, `sites`, or a dedicated CoVIA transport. Those destinations must remain `HELD_NO_RECEIVER` until a real receiver route exists.

**Pointer is not ACK. Receipt beats assertion.**

## CoAndrew+ readiness snapshot, 2026-10-23

**Public main readback:** this document and its receiver manifest were read back on the public `main` branch after merged PR [#200](https://github.com/CoCivium/CoCivium/pull/200). The earlier HELD premerge benchmark row is retained as historical truth; a newer append-only row records the later PASS for GitHub main readback. Neither row proves delivery to Gmail, CoVIA, .nodes/nodes/.sites/sites, an independent site deployment or Andrew.

**Developer-first threshold candidates (all HOLD pending exact observations):** named thumbnail >300 KB and separately visually acceptable; `ffprobe` stream inspection plus `ffmpeg` `blackdetect` reporting zero black intervals; GitHub HTTP 200 under 2 s; authorized Gmail Primary metadata-only query under 60 s; verified identity and SHA-256 in a receiver-produced receipt; Pi compatible first-use handshake/task under 2 s; Claude credential-availability probe under 1 s without revealing secrets; Ollama/Llama local packet parse under 3 s. These are user-requested goals, not measured performance. Latency alone does not prove correct results.

A private source-bound **offline candidate checker** passed 12 of 12 local structural tests while producing nine explicit HOLDs on an observation-free fixture. Its noncanonical preflight report must be mapped to the existing [CoStretch BenchmarkEvo R0 validator](benchmarks/costretch/README.md) before any production or public PASS event. No model/provider call, live session, recipient outreach or anonymous account was created by that check.

**Next human-value gate:** one consenting developer on their chosen Mac/Pi/Claude/local stack tries the same bounded first-use task, corrects at least one wrong claim, and returns a source-bound readproof and usefulness assessment. Keep deterministic and FOSS options usable without any hosted provider. Historical replays preserve original bytes and do not replay external effects.
