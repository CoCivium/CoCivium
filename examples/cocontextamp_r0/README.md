# CoContextAmp R0 | Finite-window, source-bound context amplifier

**State:** PASS_LOCAL_SYNTHETIC_SOURCE_AND_POLICY, not production, not a real provider model context extension, not a native CoOrbWare runtime, and not a receiver handoff.

## Purpose

Reuse CoContextWare, CoPayload P0-P6, CoPulse R0D/R0E, CoStretch and CoTurtle without minting an imaginary infinite-token resource. Instead of loading all source material into one provider's finite context window, create a small source-verifiable working set on demand. Restore exact omitted bytes only when a qualifying question needs them and the requester has the proper authority.

The visible flow is:

`' -> task / query -> approved public manifest -> exact source/hash qualification -> relevance/evidence ranking -> bounded exact excerpts -> explicit loss+recovery pointers -> optional later qualified model -> test -> receipt -> sleep`

## Run the public synthetic canary

Requires Node 22+ (standard library only):

```sh
node --test tests/check.mjs
node CoContextAmpR0.mjs fixture/manifest.json 'How does CoContextWare assemble context and verify source evidence?' 900
```

* Only explicitly enumerated `PUBLIC`, `READ_ONLY_PUBLIC`, `DECLARED_CURRENT` local UTF-8 sources are eligible. Currentness is declared by manifest, **not independently observed**.
* Exact whole-source SHA-256 is required before a snippet is offered. Every selected paragraph retains byte offsets and an exact SHA-256. `replaySlice` independently checks source and fragment hashes.
* Syntactic term matching, **not** semantic reasoning or answer generation; ranked matches require human/independent testing before claims of usefulness.
* Excerpt **byte** budget is finite (128-8192), 1-8 selected slices. This is *not* a measured token count for any model tokenizer.
* Privacy/authority, unavailable, stale, oversized, tampered, path traversal or outside-root symlink cases fail closed or produce specific `HOLD` entries; no silent dropping or negative truth inference.
* No network, model calls, worker fan-out, system hooks, mouse controls, credentials, source mutation, receiver ACK or external sends.

## Exact-source contract

`source_id | relative_path | source_sha256 | declared_currentness | privacy | authority | source_ref`

A returned excerpt carries `source_id`, whole-source SHA-256, exact byte start/end, segment SHA-256, relevance-term matches and explicit loss. A content hash or pointer **never** means the receiver has the bytes or can reconstruct a deleted source.

### Interoperability

* CoContextWare: compile a small context packet from task, rights, exact source and currentness.
* CoPayload: keep large objects file-backed/content-addressed/streamed rather than pasted into prompts.
* CoPulse digest: preserve manifests and recover omitted exact source before promoting a compact representation.
* CoStretch: select lowest adequate local or provider resource after qualification.
* CoTurtle: challenge selected evidence and rankers under inherited finite budgets.
* CoOrbWare: show context, omitted evidence, recovery, costs and reasons for HELD.
* CoOmni+: an addressable resource graph, not unlimited currently available devices, paid tokens, models or authority.

## Measured local result

`21/21` Node tests PASS in a bounded isolated container. Test cases include deterministic replay, source and fragment SHA checks, exact UTF-8 spans, budget ceiling, expected relevance on a tiny synthetic corpus, privacy and authority blocking, stale and missing inputs, traversal/symlink avoidance, id collision, bad input, unknown query and zero effects. Synthetic fixture is not real-world retrieval quality or human acceptance evidence.

**Acceptance frontier:** compare precision/recall against a fixed public corpus and naive baseline, quantify actual tokenizer budgets for each independently authorized model, then prove one complete source -> chosen model task -> output citations -> independent readback. Repeat with lost provider and device before claiming resilience or saved human time.

Rails: `ADDRESSABLE_NE_LOADED | TOKEN_AMP_NE_INFINITE_CONTEXT | BYTE_BUDGET_NE_MODEL_TOKENS | SNIPPET_NE_SOURCE | LOSS_NE_ZERO | SOURCE_HASH_NE_AUTHENTICATED_PUBLISHER | SOURCE_PLAN_NE_PROVIDER_EFFECT | RELATED_NE_TRUE | CANDIDATE_NE_PRODUCT | LOCAL_PASS_NE_INDEPENDENT_ACCEPTANCE | NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.
