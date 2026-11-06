# CoSpeedo+ / CoValue R1 — Source-bound growth dashboard

**Status:** OFFLINE_STATIC_CANDIDATE, not an installed X2 dashboard or live growth service.

- Open `index.html` on any local computer. No server, login, network, external fonts or JS libraries.
- `evidence_snapshot.json` is an *aggregate* derived from the GitHub sources pinned by commit and Git blob. The full 145-row JSONL ledger is not bundled.
- Historical counts by day (PASS/HELD/FAIL): Oct 23 38/16/10; Oct 24 40/26/3; Oct 25 3/2/0; Oct 26 3/3/1. Totals 145 (84/47/14). Unique IDs: 145.
- Seven-day scorecard has five UNKNOWN days and two PARTIAL days; even Oct 26 lists null for all 10 normalized metrics. Unknown is not zero.
- CoValue exponent is **unavailable**. The dashboard does not fit exponential curves to artifact counts, commits, events or tests.
- Activity/CoValue toggle, evidence/proof cards and CSV export are local and browser-only. CSV is **log entries**, not real outcomes.
- Provenance links point to exact public sources and Git blob SHA-1, rather than claiming current branch or independent acceptance.
- X2 remote observer was offline at the source check. This is not an OS performance diagnosis.

## Refresh contract

Replace aggregate snapshot **only** after rerunning a verified source census, checking source Git blob, revision time and metric definitions. Do not replace missing values with zeros or infer recipient usefulness from benchmark PASS. This dashboard requires a deliberate rebuild; there is no scheduler or background worker.

## Requirements for an exponential-candidate report

At least 4 comparable independent receiver/outcome windows with stable definitions, positive values, cost/human-time normalization, uncertainties/confounders and suitable non-exponential comparisons. See `docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md` in CoCivium.

## Limits

No independent receiver ACK, real CoValue trend, actual revenue valuation, clinical claims, global adoption, X1/X2 runtime installation, X2 benchmark, remote process control, background refresh or live measured growth.

`ACTIVITY_NE_COVALUE` · `PASS_NE_ADOPTION` · `UNKNOWN_NE_ZERO` · `OBSERVED_SOURCE_NE_REALTIME` · `RENDER_PASS_NE_PRODUCT_ACCEPTANCE`.
