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

## R0.1 privacy noninterference donor (2026-10-26)

The initial R0 excluded secret text but published `total_declared`, `privacy_exclusions_present`, and `SHADOW_CONTEXT_PARTIAL_PRIVACY` when hidden candidates existed. Those fields can leak the very existence of private records to an otherwise identical PUBLIC request. R0.1 is a review-only correction on a dependent branch:

- Select a **receiver-visible, typed subset before validating hidden candidate details**. Invalid publicly visible records still fail closed. An invalid privacy label fails closed.
- Emit `visible_declared` rather than global candidate count; keep `status_counts`, `eligible_unique`, `duplicate_suppressed`, and `required_negative_count` scoped to visible eligible material only.
- Never expose `privacy_exclusions_present` or a different public `state` based solely on classified hidden rows.
- With equal public records, PUBLIC packets are **exact JSON-equal** despite added, removed, reordered, malformed or contradictory rows explicitly classified as PRIVATE_LOCAL, SENSITIVE or UNKNOWN. LOCAL packets analogously ignore SENSITIVE/UNKNOWN rows.
- Keep `HELD_NO_ELIGIBLE_SOURCE` for an empty visible set and `HELD_REQUIRED_NEGATIVE_EVIDENCE_EXCEEDS_BUDGET` for a visible required negative that does not fit. External effects remain zero.
- This is **serialized-output noninterference for declared classifications**. It is **not** a constant-time algorithm, an authenticated privacy classifier, a storage access-control enforcement, a proof of side-channel security, or permission to route source bytes. Timing, peak allocation, logging outside the pure function, and malicious caller-provided classifications require separate threat-model review.

50 synthetic tests are provided in the existing `test_context_budget_r0.cjs` and are configured to run through the **existing** CoThumb workflow once the dependent PR opens. No new workflow, daemon, provider adapter, mouse input hook, X2 process or public receiver was created.

`PUBLIC_PACKET_NE_HIDDEN_EXCLUSION_ORACLE | DECLARED_PRIVACY_NE_VERIFIED_ACL | TEST_NE_REAL_USER_ACCEPTANCE | NEGATIVE_EVIDENCE_NE_DROPPABLE`.
