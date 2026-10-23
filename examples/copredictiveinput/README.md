# CoPredictiveInput+ / CoMap+ Shadow Canary R0

**State:** public, dependency-free, local-only candidate canary. No provider integration, desktop input hook, account change, receiver pickup, or runtime adoption is implied.

This is the first bounded implementation of the next deed recorded in `CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md`.

## What it demonstrates

- exact raw input remains visible and inspectable;
- a deterministic local rule prepares a candidate continuation beyond the cursor;
- accept/reject is explicit;
- acceptance mutates only the local input field;
- every decision can emit a `CoQuanta.PredictiveInput.R0` receipt;
- the lineage is rendered as a compact CoMap/CoOrb-style trail;
- network/provider/external effect counters remain zero;
- no persistent browser storage is used;
- export is an explicit local download only.

Run from the repository root:

```bash
python -m http.server 8000
```

Then open:

`/examples/copredictiveinput/`

Smoke test:

```bash
node examples/copredictiveinput/tests/smoke.cjs
```

## RAW / rewrite boundary

The prototype follows:

`RAW_INPUT -> ACK_RAW -> SHADOW_PREDICT -> PROPOSE -> EXPLICIT_DECISION -> LOCAL_RECEIPT`

The raw text is not replaced by a rewritten canonical source. Accepted continuation is a local edit with preserved before/after values in the receipt.

## Latency accounting

Measured in-browser:

- decision latency;
- accepted candidate length / keystrokes avoided.

Counterfactual time saved is **unknown by default**. An estimate is calculated only when the user supplies a measured typing baseline in milliseconds per keystroke.

`ESTIMATED_LATENCY_NE_MEASURED_COUNTERFACTUAL`

## CoMap / CoOrb boundary

The SVG is a receiver-relative projection. It does not own the source state.

The canary renders:

`RAW -> ACK -> SHADOW -> DECISION -> RECEIPT`

and a separately visible local-effect branch.

Future desktop/background/wallpaper/screensaver projections should consume the same typed packet rather than inventing parallel state.

## Virtual-session relation

This canary is compatible with the existing rule:

`many virtual sessions -> few materialized workers -> one coherent relational UX`

It does **not** prove provider-session replacement, provider parity, safe account deletion, or lossless historical reconstruction.

## Predictive-forward boundary

The candidate may be prepared early. Nothing is sent or executed early.

`PREDICTED_NE_TYPED`
`PREDICTED_NE_AUTHORIZED`
`PRECOMPUTED_NE_EXECUTED`

A future authorized receiver may accept a clearly marked forecast pointer, but that requires a separate receiver contract and receipt.

## Next gates

1. real first-use acceptance/rejection calibration;
2. keyboard/mobile/accessibility testing;
3. local X2 CoThumb/centre-button canary that creates a **visible local capsule only**;
4. virtual-session reconstruction after closing the provider-native UI;
5. CoMap projection from the same packet into a low-attention ambient surface;
6. provider-substitution benchmark before any paid-account retirement.

## Nonclaims

`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`  
`HASHING_IS_NOT_SEMANTIC_INGESTION`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`
