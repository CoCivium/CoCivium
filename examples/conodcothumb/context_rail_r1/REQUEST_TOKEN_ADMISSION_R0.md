# CoContextWare R0 | Exact-request token-count admission (shadow)

This is a **small guard for the existing CoContextRail R1 + CoContextBudget R0**, not a tokenizer, a new model endpoint, another CoOrb product or a new background agent. It accepts an **exact serialized model request**, a separately supplied count receipt, a caller-declared model context window, an explicit **max_output_tokens** request limit, and a conservative guard reserve. It validates the binding and computes whether the declared full-request input tokens fit the configured budget.

**No request is sent.** It cannot authenticate the count provider, verify live model limits, grant model/network/device authority or enlarge a model context window. Every output carries `model_call_authorized: false`. For a real receiver to act, an independently authenticated provider adapter must obtain a count for the **same exact request** and establish current model limits, source/privacy/permission rules and execution authority.

## Why this is not a character-count trick

OpenAI's current [input-token counting guide](https://developers.openai.com/api/docs/guides/token-counting) describes an API that accepts the same full Responses inputs as a model call and counts framing, tools and supported non-text content. Local text tokenizers and byte estimates alone are insufficient for all request modes. Actual models may have different tokenizers, context limits, output limits and reasoning-token usage. Use the authenticated provider's input count or an appropriately qualified model-local complete-request counter, never infer universal conversion ratios from bytes.

## Pure interface

`CoRequestTokenAdmissionR0.cjs` is a pure CommonJS module with `gate(input)`, a bounded JSON stdin/stdout runner, and 43 synthetic regression tests. **Required input**:

- `request_json`: *the exact UTF-8 serialized request body that the sending adapter intends to submit*. Must parse as a nonempty Responses-like JSON object with `model`, nonempty `input`, and explicit integer `max_output_tokens`. Up to 256 KiB. The request is never echoed into output.
- `target`: `model_id`, caller-declared `context_window_tokens`, `reserved_output_tokens` **equal to the request's `max_output_tokens`**, and `reserved_guard_tokens` >= 128. Caller must independently verify model limits and reserve conservatively.
- `count_receipt`: `method=PROVIDER_FULL_REQUEST_COUNT`, `scope=FULL_REQUEST`, `model_id`, exact `request_sha256`, `request_bytes`, `input_tokens`, and UTC observation time. These fields are evidence supplied by a caller, *not a signature or authenticated provider attestation*. For tests, use `SYNTHETIC_FIXTURE`; for text-only tokenizers, use `LOCAL_TEXT_TOKENIZER` and `TEXT_ONLY` (held for full-request admission).
- `observed_at_utc` and `maximum_count_age_seconds` (1..3600): compare the count's timestamp with the caller's observation time to reject stale/future fixtures. This is not independent clock trust.

Guard computes `input_ceiling = context_window_tokens - reserved_output_tokens - reserved_guard_tokens`. It refuses mismatched digests, model IDs, byte counts, stale/future counts and insufficient capacity; it also rejects missing/incorrect output reservation. Even a mathematically fitting declared count returns `SHADOW_FITS_DECLARED_PROVIDER_COUNT__AUTH_UNVERIFIED`, not runtime authorization.

## Tests and next receiver proof

Run `node --test test_request_token_admission_r0.cjs`. Includes over-budget controls, output-reserve mismatch, private prompt non-echo, UTF-8 exact hash, CLI process roundtrip, and no-effect assertions. No network, tokenizer installation, identity lookup, file scan, mouse hook, provider call or inference.

Next eligible canary once an authenticated model adapter is available: create one complete immutable request from CoContextBudget, count that exact request with the model's authorized count endpoint, verify payload hash and model/window limits, return a provenance-bound count receipt, and compare against actual request acceptance/usage. Then evaluate omission and quality, not token savings alone. Without provider counts and actual acceptance, **TOKEN_WINDOW_RECEIVER=HELD**.

Nonclaims: `LOGICAL_SOURCE_POOL_NE_LIVE_TOKEN_WINDOW | BYTE_SIZE_NE_REQUEST_TOKEN_COUNT | COUNT_RECEIPT_NE_PROVIDER_AUTHENTICATION | FITS_MATH_NE_MODEL_AUTHORITY | CONTEXT_ADMISSION_NE_BENEFIT | MODEL_LIMIT_NE_UNBOUNDED_COMPUTE | COMPACTION_NE_LOSSLESS_SOURCE_UNLESS_RECONSTRUCTIBLE`.