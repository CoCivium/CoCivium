# CoAll Public Pulse R0 | 2026-10-23

**State: public R&D update, with reproducible examples; not a general product release.**

CoCivium is testing how people and AI systems can work together more openly, respectfully, and with less dependence on any single provider. The useful unit is an inspectable result, not a large count of tabs, agents, prompts, or promises.

## What is available now

1. **CoAndrewFirst+ R0**, a five-minute, account-free browser demonstration with five stages: result, evidence, challenge, boundaries, receipt. [View the source and run instructions](../../examples/coandrewfirst/). [PR #193](https://github.com/CoCivium/CoCivium/pull/193) is merged. The model selections in its UI are non-executing adapters; the demonstration runs local browser logic.
2. **CoStretch+ benchmark_evo R0**, a Python-standard-library evidence log and validator. [README and run commands](../../benchmarks/costretch/README.md); [machine-readable JSONL](../../benchmarks/costretch/benchmark_evo.jsonl); [validator](../../scripts/validate_benchmark_evo_r0.py); [regression tests](../../tests/test_benchmark_evo_r0.py). [PR #199](https://github.com/CoCivium/CoCivium/pull/199) was merged at `943056fd56c9cf77b2821ed6795426f5186671ba`. [GitHub Actions run 39890388584](https://github.com/CoCivium/CoCivium/actions/runs/39890388584) reported success.
3. **Unflattering outcomes remain visible.** The benchmark's four rows are deliberately **synthetic examples: 2 PASS, 1 FAIL, 1 HOLD**. They exercise a structural validation contract, not the ability of Andrew, Claude, Pi, Llama, Ollama, or a human reviewer. Unmeasured resource metrics remain `null`.

## What can be tried

From a local repository checkout, with Python 3.9+:

```sh
python3 -B -m unittest discover -s tests -p 'test_benchmark_evo_r0.py' -v
python3 scripts/validate_benchmark_evo_r0.py benchmarks/costretch/benchmark_evo.jsonl
python3 -m http.server 8000
```

Then open `http://localhost:8000/examples/coandrewfirst/` in a browser. Run from the repository root; do not send private inputs to unapproved services.

## Next high-bar tests

- Let an interested developer run one bounded task on their own authorized device using their chosen model, such as Claude, Pi, or a local/open-weight Llama-family model, with explicit permission, versions, budgets and a reproducible baseline.
- Revisit one privacy-classified historical artifact with current tools, preserving the original and recording both improvements and failures. A re-run is not proof of improvement.
- Compare throughput, p95 latency, energy, resource usage, verification effort, risk and human attention on matched workloads. Parallel logical candidate space is not a claim of a trillion live workers.
- Test a distinct-substrate receiver reading an exact durable object and writing its own acknowledgement before any pickup or integration claim.

## Broadcast and receiver boundary

The public repository is a **pull/discovery surface** for AI agents, developers, nodes, sites, CoVIA/CoDot frontends and other readers that choose to subscribe. A file landing on GitHub does **not** push it into those runtimes, deliver Gmail, update a website, or establish acceptance. Each must have an authorized adapter and its own receipt.

No unsolicited mass-contact, no hidden prompt injection, no deceptive personas, no covert device takeover, no secrets, no assumed participant consent.

**FOSS-first; working together respectfully; privacy by design; inclusion without requiring a wearable device.** Playful layers and metaphors may inspire experiments, but they do not replace evidence.

## Evidence boundaries

`MERGED_NE_CANON` | `SYNTHETIC_PASS_NE_REAL_WORLD_SUCCESS` | `DISCOVERABLE_NE_RECEIVED` | `RECEIPT_NE_INDEPENDENT_ACK` | `TRILLION_LOGICAL_OPTIONS_NE_TRILLION_JOBS`

This pulse is a small public entry point, not a declaration that Civ2+ has been globally adopted. It is meant to be challenged, corrected, and evolved.
