# CoStretch+ benchmark_evo R0: interoperable evaluation receipts

**State: PUBLIC-SAFE REFERENCE CANDIDATE.** Real developer/Claude/Pi/Ollama tests, historic replay improvements, runtime installation, and independent receiver ACK are **NOT TESTED** here.

This is a **log and validator**, not another CoStretch scheduler or role registry. It complements CoRoleSpace R0, CoResearchGate Extraordinary, CoAndrewFirst R0, and CoStretch's privately prepared synthetic prototypes. The append-only intent applies to a real system of record: this validator reads input and writes nothing unless asked to write a new report with Python's no-overwrite `x` mode.

## Run (Mac/Linux/Windows, Python 3.9+, no packages)

```sh
python3 -B -m unittest discover -s tests -p 'test_benchmark_evo_r0.py' -v
python3 scripts/validate_benchmark_evo_r0.py benchmarks/costretch/benchmark_evo.jsonl
```

Use `py -3` on Windows if Python is installed that way. The sample is **synthetic and illustrative**. It includes PASS, FAIL and HOLD rows to show a ledger must preserve losses and uncertainty. The sample describes **no actual call** to Claude, GPT, Ollama, Pi.dev, Andrew or a Raspberry Pi. It makes **no measured latency, price, joule, RAM, tokens or developer-benefit claim**.

To record a permitted real experiment, append a **new event** with correct `evidence_class`, exact task and fixture hashes, model name/version and execution receipt for `MODEL_RUN`, source lineage for `HISTORICAL_REPLAY`, individual checks, measured resource values where instrumented, and explicit unknowns (`null`) otherwise. Never copy private or NDA material to public tests or remote models. A hash alone is not source authentication. Independent review must test the substantive claims.

## Comparison and test gates

A `comparison_group` needs at least two records, distinct methods, matching task and fixture SHA-256, and the **same evidence class**. A structural PASS does not say a model won, that the source is truthful, that Andrew installed anything, or that a NAS receiver acknowledged a handoff. The `verdict` is the *record author's* declared test outcome; the validator checks structural consistency and forbids a PASS that conceals a failed/held subcheck.

`resource` fields accept a nonnegative observed number or `null`, **never substitute zero for an unmeasured physical quantity**. Synthetic logical cases require all meters `null`, no permission to start effects, and `LOGICAL_ONLY` custody. Even when a hash field is present, `PICKED_UP` also requires a named receiver and separately verified origin, which this schema cannot independently attest.

## Next high-bar tests

1. Run the developer-first task on an authorized clean Mac with Pi + his chosen Claude or local model, measure elapsed time and task completion, and obtain *his* receiver readproof; do not infer acceptance from GitHub.
2. Carry one privacy-classified, immutable historical artifact forward, retain original unchanged, compare with a strong deterministic or human baseline and an explicitly versioned model; record failures as eagerly as wins.
3. Use matched fixtures, held-out outcomes, blind grading and repeated seeds for estimates with uncertainty. Reject wins that appear only in crafted fixtures or disappear under miscalibration or provider outage.
4. Measure actual CPU/GPU seconds, joules, network, storage including indexes, reviewer minutes, and p95 latency under predeclared budget. Do not use synthetic credits as dollars, energy or value.
5. Prove an independently controlled receiver ACK before promoting any object beyond `LANDED`; verify source content, lease and authority on resume.

`TRILLION_LOGICAL_OPTIONS_NE_TRILLION_JOBS` | `SYNTHETIC_PASS_NE_MODEL_QUALITY` | `RECEIPT_NE_RECEIVER_ACK` | `PRESERVE_FAILURES_AND_SUPERSEDED_ARTIFACTS` | `FOSS_OPTIONALITY_NE_UNAUTHORIZED_PROVIDER_TESTING`
