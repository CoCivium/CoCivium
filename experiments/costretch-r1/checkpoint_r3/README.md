# CoStretch+ R3 | Version-bound historical replay checkpoints

**Research candidate.** Offline Python 3.10+ and optional Node.js 18+. No AI account, API key, Pi installation, model download, or network required. Runs on macOS, Linux and Windows where Python is installed, but **no independent macOS execution has yet been observed**.

## Why it exists

The earlier CoTurtleIndex R1 assigns numerical addresses to 50,164,531,200,000 possible combinations. That's a compact **logical** space, not completed experiments, workers, viable authorized plans, or scientific results.

A real weakness was demonstrated: swap two role labels in the manifest, keep every dimension cardinality identical, and `index=0` now means a different role. A bare index would silently replay different work. **R3 refuses the stale checkpoint** by binding the exact raw manifest SHA-256, including every option label and its order. Even whitespace-only edits create a new namespace deliberately. This favors safe false rejects over unsafe silent reinterpretation.

The source manifest is copied unchanged from `CoAndrewReplayLab_v0.3/benchmarks/coevo_experiment_space.json` (GPLv3 family). Its raw SHA-256 in this release is `41bdf00efe874b4565c1787e178657013a552953730bafe09edb4b677b36a706`.

## Andrew: first 60 seconds, no AI required

Open a terminal in the unpacked directory and run:

```sh
python3 -m unittest -v test_turtle_checkpoint.py
python3 turtle_checkpoint.py verify --space space_manifest.json --checkpoint checkpoint_R3_seed0.json
python3 turtle_checkpoint.py peek --space space_manifest.json --checkpoint checkpoint_R3_seed0.json --count 3
```

If Node is installed, cross-check without Python:

```sh
node verify_checkpoint.mjs space_manifest.json checkpoint_R3_seed0.json
```

To create a **new** checkpoint without replacing existing files:

```sh
python3 turtle_checkpoint.py init --space space_manifest.json --out my_first_checkpoint.json
python3 turtle_checkpoint.py advance --space space_manifest.json --checkpoint my_first_checkpoint.json --count 4 --out my_next_checkpoint.json
```

`peek` lists descriptions and their holds. `advance` moves **only the logical cursor**, not an execution or deployment state. Existing destination files cause a no-clobber failure. No network, files on other machines, live AI, accounts, or people are contacted. Python and Node can both verify the resulting checkpoint, but their agreement does not authenticate its author.

## What the high bar actually found

- Prior **bare-index stability criterion: FAIL**. Semantic labels changed while the combinatorial count remained unchanged.
- R3 manifest-binding regression: PASS. Both verifiers reject the changed namespace, edited cursor, rehashed policy escalation and duplicate-key checkpoint cases.
- **25/25** local Python regression tests passed, including strict input bounds, no-clobber, exhaustion and CLI roundtrips.
- The portable combined `benchmark_evo_R3.jsonl` retains all **28 original R2 events** and appends **12 R3 events**, with a pinned `HEAD_R3.sha256`. It includes the baseline FAIL and honest NOT_RUN gates.
- The local timing measures in `R3_REPORT.json` cover only hash/decode/verification of small data structures. They establish no distributed scalability, real model productivity, inference latency, or energy benefit.

Verify the combined ledger:

```sh
python3 verify_evo_ledger.py benchmark_evo_R3.jsonl HEAD_R3.sha256
node verify_evo_ledger.mjs benchmark_evo_R3.jsonl HEAD_R3.sha256
```

You can regenerate a *new* evidence run without overwriting this frozen one:

```sh
mkdir independent_reproduction
python3 build_evidence_R3.py --out-dir independent_reproduction
```

New timing measurements and therefore the generated hash head may differ. Compare the invariant test outcomes and evidence source, not an assumed byte-identical benchmark ledger. Running the helper again may take a few seconds, primarily for the 25 Python tests.

## Claude, Pi.dev and Ollama compatibility

This packet is a **model-independent base layer**, not a working Claude/Pi/Ollama plugin. Any authorized model or agent can inspect its plain JSON files. The next separate engineering canary is a PI.dev tool or Claude/Ollama adapter **reading** a version-bound checkpoint and returning a proposal; deterministic R3 code must verify the resulting packet. Neither a model reply nor the presence of `AGENTS.md` proves the adapter was installed or executed. Don't scan API keys or credentials for an onboarding benchmark.

For historical redo work, store the frozen old manifest, original evidence, original model/agent identifier if reliably known, plus exact replay checkpoint and new comparison results. Never overwrite the historic record, silently upgrade an old score, or treat today's model as automatically superior.

## Explicit limits

- **No shared-writer lease.** Two people can independently advance the same checkpoint into different files. `parent_checkpoint_sha256` identifies a fork, but this code does not reconcile it or prevent duplicate live work.
- **No actual workers** are launched, and no model, network, hardware, email, CoVIA, or web endpoint is called.
- **No authorization increase.** `PUBLIC/PRIVATE`, authority and effect labels are synthetic coordinates; the advisory `holds` list is not permission to execute anything. Real adapters must separately enforce current privacy, consent, capability and resource budgets.
- A plain hash chain proves consistency relative to a trusted separately retained head, not authorship, scientific truth or verified recipient pickup.
- The Node verifier intentionally fails closed for namespaces whose capacity exceeds JavaScript's safe integer range. The current 50.16T-address namespace is within that range.
- Tested locally on a Linux sandbox. No Mac/Pi compatibility timing, Claude access, Ollama parse latency, media thumb/blackdetect or receiver delivery measurements are claimed.

**FOSS / commons intent:** GPLv3 family, preserve attribution and license. Voluntary use, privacy by design, accessible text-first interface; physical wearables optional; no false claims of holdings, endorsement, or running sessions. 

`INDEXABLE_NE_EXECUTED | SOURCE_HASH_NE_SEMANTIC_TRUTH | SAME_CARDINALITY_NE_SAME_NAMESPACE | POINTER_NE_ACK | RECEIPT_BEATS_ASSERTION`
