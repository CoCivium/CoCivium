# CoDoodle+ R0 | CoElse+ / CoNotElse+ experiment-seed compiler

**State: LOCAL SYNTHETIC CANARY; ZERO EXECUTION; NO DEVICE/PROVIDER INTEGRATION.**

The point is not to simulate unlimited sentience, silently read keystrokes, or spawn a million workers. CoDoodle takes one explicitly provided UTF-8 text file and emits a small bounded set of source-linked, disconfirmable experiment *descriptors*. It preserves raw input by hash and offsets, labels speculation, and produces explicit counterhypotheses. It neither rewrites nor publishes the original text.

## Run without installation

Requires Python 3.10+ and standard library. From this directory:

```sh
python3 codoodle.py --input sample_synthetic.txt
python3 codoodle.py --input sample_synthetic.txt --output my_first_report.json
python3 -m unittest discover -s tests -v
python3 benchmark.py
```

The optional `--output` uses exclusive creation and will not overwrite an existing file. The input is supplied explicitly, no clipboard, screen, OS key events, secrets or network are inspected. Input files over 64 KiB and symlink input paths are refused. Candidate count is capped at 8 per call.

## Pipeline and exact existing integration seam

`RAW_Doodle -> source_sha256 -> lexical patterns and exact text offsets -> 5 lane diversity -> 8 candidate descriptors -> CoExperimentSelector+ after evidence-backed annotations -> bounded CoTurtle -> static/replay test -> only separately authorized effects`

The existing [CoExperimentSelector R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SELECTOR_R0.md) requires **ten quantitative dimensions, each with an explicit evidence reference**. CoDoodle deliberately returns `UNSCORED_INPUT_NOT_YET_VALID`. It does not fabricate those estimates or pretend that selecting a seed executes an experiment. This is a *front-end candidate compiler*, not a competing selector.

Related donors:

- [CoNotSpace evidence distinctions](https://github.com/CoCivium/CoCivium/blob/main/examples/conotspace/README.md): unknown != refuted; evidence can support both sides in scope.
- [CoPredictiveInput / CoInbetween](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md): preserve raw input, separate shadow predictions and authorized effects.
- [CoTurtles](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SPACE_TURTLES_R0.md): finite recursion, inherited budgets and no extra effect authority.

## Output and epistemic rail

Each selected seed contains `candidate_id`, `concept_family`, `source_span_chars`, a matched source token, proposed question, counterhypothesis (`CoNotElse+`), local test proposal, explicit evidence class, suggested experiment lane and a no-effect boundary. The source text is *not* included in the resulting JSON. Candidate names are lexical matches, **not** semantic interpretation, independent citations, quantified probability, or proof of new physical effects.

Planck/quantum references need operational experiments to justify any physical application. G_d/ET/aura/spiritual story relations remain `SYMBOLIC_OR_SPECULATIVE` until a separate source and qualified test demonstrate something more. This respects cultural/philosophical exploration without allowing an appealing story to become a measurable claim by typography alone.

`CoElse+` means genuine alternatives and testable surprises. `CoNotElse+` means disconfirmation and negative knowledge, **never** absence inferred solely from missing observation.

## Benchmarks (2026-10-24, isolated Linux x86_64 / Python 3.13.5)

| Text fixture | Hot trigger median | Full compiler median | Scope |
| --- | ---: | ---: | --- |
| Early-match synthetic, 923 B | 0.071 us | 135.329 us | 12 lexical families, 8 selected |
| Repeated synthetic, 3692 B | 0.071 us | 137.427 us | Fast early matches |
| No-match synthetic, 3692 B | 3.095 us | 553.960 us | No lexical matches |
| No-match synthetic, 65536 B | 52.734 us | 10078.960 us | Near the maximum input budget |

Details, iteration counts, p95/p99 and limitations: `benchmark_receipt.json`. **This is not an X2 measurement, an I/O latency measurement or an end-to-end experiment run.** The fast trigger merely notices that a candidate might exist; it may false-positive. Real scientific falsification, media decoding, device integration, review, communication and receiver acceptance operate on vastly different time scales.

## Anti-firehose gates

- Do not create a worker per keystroke or per alternate glyph.
- Idle time normally means *rest*; no inferred consent from pause.
- Deduplicate the same concept family in one source; preserve distinct source SHA and semantic-change evidence over time.
- Spend attention budget on a few explicit, evidence-qualified proposals; park the rest.
- All effects remain at zero; only a separate permissioned, observed receiver can perform them.
- Untrusted model/story suggestions do not receive authority, regardless of fluency.
- Preserve negative findings, private/unknown edges, tests, and earlier versions.

`LEXICAL_MATCH_NE_SEMANTIC_COMPREHENSION | CANDIDATE_NE_EXPERIMENT | UNKNOWN_NE_FALSE | MODEL_NE_MEASUREMENT | SOURCE_NOT_PUBLISHED_BY_DEFAULT | POINTER_NE_ACK | NOT_RUN_NE_PASS`

## Next smallest meaningful integration

One private no-effect hook from an already-authorized, visible CoThumb/CoInbetween event into this bounded compiler. Compare the candidate JSON against the existing selector's required annotated input. No new global keyboard hook, unsolicited broadcast, background agent or endless session spawning. Live X2 device adoption and independent receiver ACK remain unverified.
