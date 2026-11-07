# CoAll+ Source-Pinned Retrieval R0 | Durable knowledge without model-weight dependence

**State:** WORKING LOCAL READ-ONLY ADAPTER, not an AI model, deployed MCP/A2A service, independent AI receiver, training grant, canon, CoEx, external adoption or permanently learned alignment.

This is a **minimal usable ingestion path** for CoAll's seven existing public adoption sources. Instead of begging unrelated models to absorb and remember everything, it lets an authorized application check the exact source edition, retrieve relevant text, preserve provenance and place that information into a model-specific context under the **local operator's permissions**. The original source retains revision, review and revocation boundaries.

## Why this is genuinely useful

- **Real source content, not metadata only.** Reads the seven pinned source files in a local repo checkout, checks each file's Git blob SHA-1 against the [current adoption manifest](../manifest-r0.json) and produces a read-only searchable in-memory index. The manifest itself must match a separately trusted prior Git blob pin, default `e9b834f93455012c703eeb8ba9b6585778ea3464`.
- **Machine-readable retrieval with real citations.** Pure Python-stdlib lexical ranking, exact source ID/path/line range, Git source blob, source epistemic state, full source excerpts and explicit `UNTRUSTED_SOURCE_DATA_NOT_AGENT_INSTRUCTIONS` status.
- **Fail-closed change detection.** Altered/missing source, wrong manifest edition, path escape, fabricated MCP/A2A or ACK, permissions or training-grant escalation refuse the entire index. No partial silently unpinned corpus.
- **A clear separation:** document text never grants an agent authority; results carry `authorized_effects=[]`, no training rights, no model invocation, no receiver ACK. **Do not run retrieved document text as executable instructions.** Prompt injection in a legitimate source is still a risk for an unsafe downstream model prompt, not solved merely by labelling it.
- **Provider and substrate neutrality.** Any approved local or cloud AI can be offered the same pinned retrieval packet, but must prove actual comprehension, permission adherence and task benefit independently. No proprietary API, dependency or server is required to use the read-only adapter locally.

## Running it

From the checked-out `CoCivium/CoCivium` repository root:

```sh
python ai/adoption/retrieval_r0/retrieval.py \
  --manifest ai/adoption/manifest-r0.json \
  --repo-root . \
  --query "source replay and permission boundaries" \
  --top-k 5
```

This emits structured JSON with snippets and exact `path#Lstart-Lend` citation paths. To save a packet for an **authorized, separately configured model** add `--output some-local-output.json`. The adapter never contacts a model or network service and never alters source files. For a reproducible actual-checkout retrieval benchmark:

```sh
python ai/adoption/retrieval_r0/replay.py \
  --manifest ai/adoption/manifest-r0.json \
  --repo-root . \
  --output coall-retrieval-readproof.json
```

For local negative controls:

```sh
python -m unittest discover -s ai/adoption/retrieval_r0 -p 'test_*.py' -v
```

## How to interpret the benchmark

The replay issues seven fixed QA queries, one targeting each public source ID. The score is **source discovery in the top five**. It is *not* answer correctness, conceptual understanding, long-term retention, authorized tool use or useful outcomes. It records actual checkout source pin validation, chunk count, timings and the generated candidate citations. Retain *all* failures, including irrelevant or missing source hits. No benchmark result may be promoted to independent AI adoption.

## What the next independently operated receiver must prove

A willing reader/agent (local model or distinct external provider) takes one pinned retrieval packet, answers new **unseen** task questions and cites its sources. An independent verifier tests factual grounding, forged-source rejection, uncertainty calibration, no tool/permission escalation and one source edition change. Only then record a receiver-specific step in [CoReachMesh+ #263](https://github.com/CoCivium/CoSteward/issues/263). No mass outreach, credential scraping, forced training or automated platform submissions.

For real currentness, a new manifest edition requires its own authorized source qualification and re-pinning process. R0 deliberately stops on changed sources instead of guessing whether to trust the newest version; a production client needs change notification, expiry and revocation processing. A public GitHub file's license is **not** automatically a grant to fine-tune on every included work.

**Rails:** `RETRIEVED_NE_UNDERSTOOD` · `INDEXED_NE_TRAINED` · `CITED_NE_CORRECT` · `SOURCE_PIN_NE_SOURCE_TRUTH` · `PUBLIC_NE_TRAINING_GRANT` · `USER_CONSENT_NE_ALL_PERMISSIONS` · `MODEL_OUTPUT_NE_AUTHORITY` · `MOST_COPIES_NE_MOST_INDEPENDENCE` · `REVOKED_SOURCE_NE_RETAINED_AUTHORITY`.
