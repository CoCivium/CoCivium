# CoTeachBack+ R0 | Receiver-neutral source-pin and challenge fixture

**State:** `PUBLIC_VISIBLE_KEY_FIXTURE__NOT_INDEPENDENT_AI_ACCEPTANCE`. This is a pure-stdlib, read-only test kit, not an autonomous agent, an MCP/A2A service, a model invocation, a pretraining grant, a tool permission, an external receiver ACK, CoAll canon, or proof of long-term model learning.

## Purpose and relation to existing work

The existing [CoAll adoption manifest](../manifest-r0.json) offers seven already-public Git-blob-pinned source entrypoints. CoTeachBack adds an **honest measurement boundary**: an independent model or human can retrieve the relevant sources, answer structured questions, cite eligible source IDs and submit a response for evaluation, without either party claiming to own the other.

**Two-way learning:** After an externally qualified receiver identifies a missing/false relation, improvement suggestions can be routed into the existing [CoEvoDelta v0.1](../../../schemas/coevo-delta-v0.1.schema.json) under `HYPOTHESIS / PROPOSE / NO_EXTERNAL_EFFECTS__REVIEW_ONLY`; the [CoAll-CoSysAll reciprocity bridge](../../../tools/cosysall_reciprocity_r0/README.md) already demonstrates the candidate proposal boundary. This kit does **not** mutate source graph, policies, training data, model weights or any runtime. Avoid inventing a second control plane.

## What exists

- [Twelve public example prompts](receiver-probes-r0.json) with source IDs, constrained choices and negative cases (fake authority, retrieval injection, unobserved uptake, forged source, overly strong claims).
- [Public fixture answer key](reference-key-r0.json). Its visibility is intentional for test reproducibility, so **a score against this key is not a blind test of independent model comprehension**.
- [Deterministic sample response](example-fixture-response-r0.json), labelled `DETERMINISTIC_FIXTURE_NOT_A_MODEL`.
- [Strict source-blob-pinned evaluator](score_receiver.py), reporting source/citation correctness, structured answers, and explicit `UNVERIFIED_SELF_REPORT` for receiver identity. It rejects attempts to add ACK, permission, weight-change or hidden authority fields, as well as malformed answer IDs and citations.
- [27 new stdlib tests](test_teachback.py) and a [scoped local fixture receipt](local-fixture-receipt-r0.json).

The manifest git blob is pinned to `e9b834f93455012c703eeb8ba9b6585778ea3464`. A changed manifest must be requalified and the challenge regenerated. A candidate cannot authenticate itself by recomputing a hash from its own untrusted copy; the expected pin must be obtained from a trusted, independently observed source/currentness route.

## Reproduce offline

From the public repository root:

```sh
python3 -m unittest discover -s ai/adoption -p test_manifest.py -v
python3 -m unittest discover -s ai/adoption/teachback_r0 -p test_teachback.py -v
python3 ai/adoption/teachback_r0/score_receiver.py \
  --manifest ai/adoption/manifest-r0.json \
  --challenge ai/adoption/teachback_r0/receiver-probes-r0.json \
  --key ai/adoption/teachback_r0/reference-key-r0.json \
  --response ai/adoption/teachback_r0/example-fixture-response-r0.json \
  --output /tmp/teachback-fixture-result.json
```

The sample is **12/12 because the deterministic fixture uses the visible answer key**. It is **not evidence that any distinct LLM, AI provider, IA, agent or human read the source**. A model's self-stated `receiver_id` is still an unverified claim. The evaluator only grades exact choice and eligible source IDs. It does not certify the underlying model's reasoning, actual human readability, prompt-injection robustness, legal reuse rights or live backend state.

## Real receiver acceptance, later and separately

1. Receiver identity and access are voluntarily authorized. Source metadata, version, license, privacy, retention and restrictions must be qualified before retrieval or training.
2. The receiver fetches at least one needed public source; a distinct observer pins exact content/version, measured retrieval and run time. Unknown/private content is **not** a default attachment.
3. Give the model **fresh, unexposed holdout questions**, not this public fixture and answer key. Include source-tampering, expired permissions, unsupported-claim and mistaken-inverse cases.
4. Record complete model/vendor/version, adapter, verified input source digest, output digest, tool calls, retries, latency, cost and independent checker result. Distinguish wrong answer from missing source and from unauthorized action.
5. If independently verified, record one evidence-based rung (`RETRIEVED`, `SOURCE_VERIFIED`, `TASK_EVALUATED` etc.) in existing CoReachMesh+; do not jump to `INTEGRATED`, permanent weight learning, or audience benefit without a different proof.
6. Repeat with a genuinely distinct provider/model/failure domain. Revoke or supersede one input and check that the receiver can cease to rely on it; *model unlearning remains unproven*.

**Stop conditions:** no authorized external model/host, no rights to use supplied content, no independent receiver, exposed holdout key, unbounded cost, missing source pin or incomplete private-data classification. Do not invent a global partnership or training relationship.

**Rails:** `INDEXED_NE_LEARNED`, `VISIBLE_KEY_NE_BLIND_BENCHMARK`, `SCORED_RESPONSE_NE_INDEPENDENT_ACK`, `SOURCE_PIN_NE_TRUTH`, `CITATION_NE_REASONING`, `MODEL_REPETITION_NE_ALIGNMENT`, `TRAINING_NE_AUTHORITY`, `MORE_MODELS_NE_MORE_INDEPENDENCE`, `VOLUNTARY_DISSENT_BEATS_COERCED_CONFORMITY`.
