# CoContextWare bounded source-pack R0 (candidate)

This is a **source compiler** for the existing CoContextRail+ R1, not an extra CoOrb product, tokenizer, provider adapter, memory service, or physical input hook. It accepts **explicit JSON on stdin**, returns one self-contained **bounded JSON context packet** on stdout, or fails closed without executing side effects. Public/private scope and source pointers are declared, not independently verified here.

```sh
node --test test_context_budget_r0.cjs
node CoContextBudgetR0.cjs < fixture_128.json > /tmp/context-pack.json
```

The default test input is synthetic. The compiler never enumerates local files, inspects the clipboard, calls a model, starts agents, or schedules itself. `budget_bytes` (1,536 to 32,768) is an **exact bound on the whole compact JSON packet**, NOT a real tokenizer's model-token limit. Source excerpts are capped at 4 KiB each, up to 128 declared candidates and at most 16 selected packets. Unverified source hashes and excerpts are explicitly labelled. Direct permission/rights checks and receiver readproof are separate gates. No packet becomes a grant of authority.

The query is ranked heuristically for keywords; this is a retrieval baseline, not semantic understanding. `FAIL`, `FAIL_SCOPED`, and `HELD` records are reserved first when eligible, and the compiler emits a **HELD** state with no selected snippets if required negative information cannot fit. `PASS_PUBLICATION_ONLY` cannot be promoted to runtime proof. Sensitive and unknown-privacy candidates are filtered; public output never includes declared private-local excerpts. The packet retains status counts, source refs, exact excerpt digests and redacted raw query.

Re-use: `CoContextRailR1.js` provides the one-gesture shadow action choice; this bounded packet feeds a future **authorized** model/task worker only after another adapter verifies the full source bytes, rights, freshness, and target context budget. Large files stay in CoPayload+, not inline text. Nothing here changes X2/RickBar, CoStead or provider credentials.

**Non-equivalences:** `LOGICAL_POSSIBILITY_NE_UNBOUNDED_RESOURCES | COMPACT_BYTES_NE_EXACT_TOKENS | POINTER_NE_SOURCE | DECLARED_SHA_NE_READPROOF | PACKET_NE_RECEIVER_ACK | SHADOW_NE_EXECUTION | NEGATIVE_NOT_DROPPABLE | REPLAYABLE_NE_CUSTODIED`.
