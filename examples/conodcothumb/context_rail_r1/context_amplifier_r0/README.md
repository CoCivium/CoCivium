# CoContextAmplifier R0 | source-bound finite-context selector

**State:** LOCAL ISOLATED SHADOW PASS. Not a tokenizer, provider integration, source rehydrator, model context-window expansion, X2 mouse/CoOrbWare runtime, external receiver, CoEx or canon.

## Why this exists

CoVirtualSession, CoAllPulseField, CoLineageCompactor, CoResourceAttractor, CoPayload P0-P6 and CoContextRail already define durable identity, selective subscriptions, source preservation, source-bound handoff and prompt-independent continuity. R0 donates **one small missing proof**: selecting a finite, source-linked candidate working set without pretending the entire corpus fits in a model prompt.

`durable sources -> qualified pointers -> budgeted proposal -> receiver reads/verifies exact bytes (future) -> actual tokenizer (future) -> model call (future) -> cited result -> checkpoint + receipt`

Use across providers only after independent adapter acceptance. A synthetic budget unit is **NOT** a token from GPT, Claude, Pi, Ollama or any model. The selected references are not loaded text. A SHA-256 string supplied as metadata is not independently verified. A plan is not a send, execution, provider receipt or larger context window.

## Demo and checks

```
node --test CoContextAmplifierR0.test.mjs
```

The JS module exports `planContext(req)` and `SCHEMA`. `req` contains a synthetic `work_id`, positive integer `budget_units`, `headroom_units`, and <=256 metadata-only source descriptors. PUBLIC/current sources require `id`, `source_ref`, 64-hex-character `sha256`, synthetic `cost_units`, `utility` (0..100), `kind` (SUPPORT, COUNTER, OPERATIVE, PRIOR), and `freshness`. `required` sources block incomplete proposals if stale, unavailable or over budget.

The module performs **no network, filesystem, provider, clipboard, OS, mouse or account operations**. It never reads or modifies source bytes, and creates no worker. A PUBLIC-only first canary excludes non-PUBLIC/unknown-privacy sources without surfacing their identities, counts or presence. Colliding IDs fail the entire proposal. Same exact source digest with the same argumentative role may be deduplicated; identical bytes with differing argumentative roles remain distinct. Counterevidence is considered before discretionary supporting material and omission is reported. It retains only references and cost estimates.

## Measured isolated proof

- 29/29 Node 22.16.0 policy fixtures PASS (test_run.tap).
- Tested source SHA-256: `7535c2c13fe3b0016e1fc3efc27518642083095f28b204d79b2ca5b7f7914c3a`.
- Test source SHA-256: `97619f021a6edcd6889e03f4daff6075d2fa87e7480a5e96f16afd7c2ad9dd62`.
- These checks are deterministic synthetic policy checks, not a measurement of token gain, retrieval recall, answer truth, energy, cost, latency under real models, or privacy outside this code's contract.

## What 'amplify' can and cannot mean

An old session can **rehydrate relevant context** via persistent exact sources, lineage pointers, role-scoped pulses and checkpoints instead of replaying all chats. Independent authorized tools/models can challenge and compare outputs without merging their authority or claiming provider context windows combine. CoTurtle can run bounded repeated selection, challenger tests, and fail-safe recovery; CoStretch can elect measured parallelism. The useful resource universe can expand while a particular model's finite context and actual budget remain explicit.

**HELD gates:** independently recompute hashes from retrieved actual source bytes; compare supplied context costs with model-specific real tokenizer; prove no loss of required contradictions under truncation; run a provider-local and provider-swap answer quality benchmark against a fixed baseline; prove a real X2 CoThumb -> CoContextRail preview -> explicit selected source -> exact receiver-origin readback; prove local CoStead recovery after interruption.

`REFERENCE_NE_CONTENT | TOKEN_ESTIMATE_NE_ACTUAL_TOKENS | RETRIEVAL_NE_TRUTH | PRIVATE_METADATA_NE_PUBLIC | SUMMARY_NE_SOURCE | NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF | LOGICAL_INFIN_NE_PHYSICAL_INFIN`.
## R1 actual-byte rehydration (2026-10-25)

**State:** \`PASS_LOCAL_SOURCE_BYTE_REHYDRATION__SHADOW_ONLY\`. This is a typed donor to the same CoContextRail / CoThumb / CoOrbWare PR. It is not a new OS controller or model context-window hack. R0 metadata selection remains unchanged. The R1 source adapter requires an explicit \`explicitLocalRead:true\` decision, an elected local root, a PUBLIC/current R0 plan, and separate per-file and aggregate byte limits.

### Code and reproducibility

- [CoContextRehydratorR1.mjs](CoContextRehydratorR1.mjs): standard-library-only Node 22 local file reader, SHA-256 recomputed from **actual source bytes**. \`includeText\` is false by default. UTF-8 text is exposed to the explicit local caller only when \`includeText:true\`.
- [CoContextRehydratorR1.test.mjs](CoContextRehydratorR1.test.mjs): 31 adversarial and positive fixtures covering opt-in, source mutation, incorrect hash, missing and oversized files, path escapes, Windows-style escapes, final/intermediate symlinks, invalid UTF-8, stale/private metadata, evidence role separation, explicit nonclaims, bounded headroom and deterministic receipts.
- [CoContextRehydratorR1.benchmark.mjs](CoContextRehydratorR1.benchmark.mjs): generates 24 short synthetic PUBLIC text files in a disposable temporary root, selects 5 with the R0 algorithm, verifies only the selected actual bytes, compares the materialized-byte total against the full generated corpus, and cleans the temporary files.
- [R1 machine evidence](benchmark_evo_r1.jsonl): local PASS, model-tokenization/provider-quality/runtime and receiver gates HELD.

Run within \`examples/conodcothumb/context_rail_r1/context_amplifier_r0\`:

\`\`\`sh
node --test CoContextRehydratorR1.test.mjs
node CoContextRehydratorR1.benchmark.mjs
\`\`\`

### Measured isolated evidence

- Source SHA-256: \`7f591c47d013340a2c58504e216369cc1f3ffefe1fff6b9e474236f8dd9e190b\`
- Test SHA-256: \`6e7a43c87cc41e6ce8aee6ba7cb5642683715d3f30ecb02b2fdf0d5a07742e24\`
- Benchmark-source SHA-256: \`2da127480f3e0ffcbac70579cbd5b46fdb151b1c2e0482a7b42d5e4bef59258b\`
- **31/31 isolated Node 22.16.0 R1 tests PASS.** An initial test-file syntax failure was corrected before this passing run; do not silently reclassify early failures as software-runtime defects.
- **10/10 independent benchmark checks PASS**, 24 synthetic descriptors; 5 selected exact local text files, 2,205 source bytes verified vs 10,584 generated corpus bytes (79.17% of bytes not materialized), required and opposing evidence retained; no network, sends, device effects, source mutations or provider calls. Synthetic timing is not an X2 or real-media performance result.

**Remaining HELD:** actual GPT/Claude/Pi/Llama model-specific tokenizer and input/output reservation; quality and retrieval recall vs a blind/full-context baseline; independent recipient-readproof; native X2 thumb mapping; CoStead durable custody; Windows filesystem race-hardening. Current path checks are a defensive Node canary, **not** a general filesystem sandbox or Windows security certification.

\`RETRIEVED_BYTES_NE_MODEL_TOKENS | SOURCE_HASH_NE_TRUTH | SELECTION_NE_QUALITY | LOCAL_READ_NE_PROVIDER_CONTEXT | SHADOW_NE_RUNTIME | POINTER_NE_ACK | NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF\`
