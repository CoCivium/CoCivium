# CoSpeedo+ / CoVal Growth First View R0

**Status:** source-pinned, offline-first visual canary. Not an installed X2 dashboard, streaming service, accepted outcome-growth proof, or audited CoVal metric. No polling or background jobs.

## Open it

Download [index.html](index.html) and open the local file in any modern browser. The source snapshot is embedded. No network, accounts, servers, external JS/CSS, extensions, mouse hooks or provider sessions are needed. External source links are optional.

The three working views:

1. **Evidence activity** shows seven-day coverage, with 145 source-ledger rows from Oct 23–26 (84 PASS, 47 HELD, 14 FAIL). Oct 20–22 stay UNKNOWN.
2. **Receiver value** stays UNKNOWN. The authoritative [CoSpeedo scorecard](../../docs/Metrics/COSPEEDO_7DAY_SCORECARD_R0_20261026.json) has no receiver-qualified useful-outcome time series.
3. **Growth exponents** distinguishes temporal lambda for positive useful value over time from scale-law beta for useful value versus independently measured resource/participant scale. At least four comparable, independently receiver-verified, cost-qualified data points are needed for a candidate fit. Math fixture fits are not actual CoCivium history.

The file is a static snapshot with an explicit timestamp. Opening it on X2 is not evidence of native CoBar, CoOrbWare, a real middle/thumb gesture, or a connected Desktop Commander.

## Source identity and limits

- The source file ai/benchmark-evo.jsonl has 145 strict rows, with its exact Git blob pinned in [snapshot.json](snapshot.json).
- The Oct 26 seven-day CoSpeedo policy has seven calendar windows and no receiver-useful numeric series; exact blob is pinned.
- [Existing CoSpeedo ledger repair PR #296](https://github.com/CoCivium/CoCivium/pull/296) is a separate unmerged draft fixing the secondary benchmarks/evo.jsonl delimiter. This view deliberately does not combine the secondary ledger or double count it.

All counts describe heterogenous scoped evidence records, not independent useful closures, user success or economic value. CoVal remains a provisional measurement question, not a canonically defined scalar or financial amount. No value curve or forecast is invented.

## Repeatable tests

Run from repository root using Node 22 or later:

    node --test examples/cospeedo-growth-r0/test_dashboard.cjs

The 22 offline cases verify input Git blob hashes; historical counts and seven-day unknown coverage; HTML/JSON exact equality; all three functional view controls; λ and β math; fail-closed missing data and insufficient time-series gates; no network, auto-polling, secret/device access, or invented outcome claim.

[Oct 26 proof contract](../../docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md) makes useful receiver closure, atomic debt and human-time cost the outcome variables, not activity volume.

## Next high-value measurement

Bind one stable work item to independently accepted receiver use, baseline, effect, event timestamp, owner/authority, evidence, human-relay minutes and compute cost. Repeat across comparable windows; retain negative outcomes and uncertainty.

SOURCE_PASS_NE_USEFUL_CLOSURE | ACTIVITY_COUNT_NE_VALUE | UNMEASURED_NE_ZERO | STATIC_VIEW_NE_NATIVE_X2 | LAMBDA_NE_BETA.
