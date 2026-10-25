# CoDoodle R0: jumble -> addressable experiments -> shadow tests

**2026-10-24 | Synthetic, local, executable candidate generator | NOT a live agent fleet**

## CoHereNow

A jumble of CoAll symbols, questions, device concerns, counterfactuals and unusual stories can be an input to a **bounded experiment-descriptor generator**.  Its purpose is to expose candidate tests, alternatives and missing evidence quickly, not to prove that an idea is valid or to execute every possible effect.

Reuses the design logic of existing [CoExperimentSpace+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SPACE_TURTLES_R0.md), [CoExperimentSelector+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SELECTOR_R0.md), [CoResourceAttractor+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORESOURCE_ATTRACTOR_R0.md) and the previously built **private** CoInterstice shadow policy.  This package does not create a competing scheduler or governance system.

## Pipeline

`EXPLICIT CoDoodle bytes -> SHA256 + keyword hints -> focused/open logical address space -> sparse deterministic sample -> else/not-else/inversion/challenge/replay variants -> no-effect static micro-canary -> UNSCORED selection handoff -> (future evidence-backed scorer) -> (future authorized micro-canary) -> receipt`

- Original input bytes are never embedded in the descriptor output. Source identity is bound by SHA256; a hash is not publisher authentication.
- Input is limited to 64 KiB and rejects recognizable assigned secrets/private keys. This is a **partial safeguard**, not a complete privacy classifier. Never provide private information or third-party correspondence without consent.
- One generated sample explores **2,016,000 addressable syntactic combinations** via mixed-radix decoding and coprime strides without enumerating that space.
- Source-keyword hints allocate **75%** of samples to detected topic families and preserve a **25% open lane** for unusual hypotheses. This is a fixed design choice, not learned relevance.
- Explicit sample limit: **256**; benchmark loop limit: **200,000**. No workers, OS hooks, network, clipboard reads, passwords, model calls, external services or scheduled background execution.
- `ELSE`: an alternative to test. `NOT_ELSE`: a negative-space or contrary path to examine, **not evidence of absence**. `INVERT`: an assumption to challenge. `BETTER`: a comparative hypothesis, **not measured improvement**. `REPLAY`: comparison against a pinned historical state. `CHALLENGE`: an adversarial test candidate.
- `EVENT_ORDER` and `LOGICAL_ORDER` are computational representations. These are not claims of timeless physical computation, quantum discoveries or predictions outside ordinary time.
- `ET_FICTIONAL` can make a valuable **fictional alternate narrator** for imaginative story exchange; it does not represent real extraterrestrial communication. `G_d`, energetic aura and quantum foundations remain interpretive/speculative lenses unless independent evidence is supplied.
- Descriptors have `authority=NONE`, `external_effects=0`, and `state=DESCRIPTOR_ONLY__NOT_EXECUTED`.
- CoExperimentSelector explicitly requires evidence-backed benefit/penalty scores. This engine deliberately outputs **unscored / HELD** (not fake expected value) until those exist.

## Run

```sh
python3 -m unittest -v test_codoodle
python3 codoodle.py --text-file synthetic_doodle.txt --out output --limit 64 --seed coall-oct24 --bench
```

Optional isolated adapter to the existing private CoInterstice policy, if that policy's source is authorized and provided alongside the adapter:

```sh
node bridge_interstice.mjs output/preview.json output/interstice_bridge_receipt.json
```

This adapter sends only a **synthetic, explicitly opted-in packet** to a policy function. It does not read a real key press, pause or mouse event, and it cannot grant execution authority. The upstream `CoIntersticeShadowR0.mjs` is a separate private draft from prior CoCivium work; public GitHub packaging should not silently imply publication rights or license parity.

## Proof, not theatre

See `output/benchmark.json`, `output/static_microcanary.json`, `output/interstice_bridge_receipt.json`, `test_output.txt`, and `benchmark_evo.jsonl` for exact scoped results. The benchmark separates:

1. **Address arithmetic only.** A cheap candidate number, not the candidate.
2. **Mixed-radix descriptor decoding.** A typed configuration from an address, not a meaningful tested hypothesis.
3. **Complete 24-candidate preview.** Hashing, constructing and validating JSON objects in one Python process.
4. **Real testing and use.** **UNPROVEN** for device control, scientific conclusions, real user time saved, receiver pickup and off-provider recovery.

The timing is measured on one transient shared container, not X2, and is not a hard real-time guarantee, 99th percentile task deadline, energy benchmark or permission to flood models with sessions.

## Candidate promotion gate

`DESCRIPTOR -> STATIC_VALIDATION -> SHADOW -> one authorized MICRO_CANARY -> REPEATED_TEST -> INDEPENDENT_COMPARISON -> RECEIVER_VALUE -> cautiously considered integration`

CoTurtle+ challenges stay within parent budget and authority; recursive review depth at most two and rounds at most two. Failed, unmeasured and contradictory results are preserved. Every high-impact external or private effect retains its own receiver and authorization gate.

**Next human-time test:** once X2's exact receiver is qualified, choose ONE opt-in actual Perixx/mouse preview and measure false activations, task completion, cancellation and human time saved against no assistant. Do not activate a million sessions to test the typing rhythm of one person.

**Nonclaims:** `ADDRESS_NE_WORKER | DESCRIPTOR_NE_EXPERIMENT | FAST_LOOP_NE_FAST_VALUE | LOGICAL_TIME_NE_PHYSICS | ET_STORY_NE_CONTACT | G_D_SYMBOL_NE_CAUSAL_EVIDENCE | SOURCE_NE_RIGHTS | PREDICTED_NE_AUTHORIZED | NO_X2_CONTROL | NO_AUTONOMOUS_CONTINUATION`.
