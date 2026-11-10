# What actually got better?

**CoSpeedo NeedleTrails** shows which CoCivium engineering checks passed, which failed, and which still need evidence. **It is not a live dashboard.**

> **Right now:** Public source and bounded automated checks are available. A working independent receiver, 24-hour survival, and measured human time saved are **not yet proven**.

## The one-minute answer

**What works:** You can inspect the [R1 historical needle-trail source](needle-trails-r1.html) and the [archived evidence](../../docs/Metrics/COSPEEDO_RECEIPT_CENSUS_R0_20261027.json). The source and chart checks passed in [main-branch CI](https://github.com/CoCivium/CoCivium/actions/runs/42750710011).

**What a browser actually showed:** The source prototype passed [four-screen-size browser QA](https://github.com/CoCivium/CoCivium/actions/runs/42744256246). That test does not establish a deployed CoCivium website or a useful outcome.

**What remains held:** Continuous tracking across devices, independent receiver recovery, and survival beyond 24 hours have not been demonstrated. See the [acceptance rail](https://github.com/CoCivium/CoCivium/issues/317).

**What is unknown:** We do not yet have a comparable human outcome baseline for time saved or comprehension. See the [seven-day scorecard](../../docs/Metrics/COSPEEDO_7DAY_SCORECARD_R0_20261026.json).

## The needle trail, without the jargon

These are recorded **test activities**, not people helped or proof of growing usefulness. Passed means a bounded check passed. Held means evidence is missing. Failed means a check failed.

- **2026-10-23:** 38 passed, 16 held, 10 failed.
- **2026-10-24:** 40 passed, 26 held, 3 failed.
- **2026-10-25:** 3 passed, 2 held, 0 failed.
- **2026-10-26:** 3 passed, 3 held, 1 failed.

**October 20–22 have no captured ledger rows.** That is **unknown coverage**, not proof that nothing happened. The four observed dates contain 145 entries in the [exact archived census](../../docs/Metrics/COSPEEDO_RECEIPT_CENSUS_R0_20261027.json). Fewer passed checks on a later day may simply mean fewer checks ran.

## Check newer engineering evidence

The dated needle history above is **not live**. For more recent technical results, GitHub updates these existing workflow run lists as checks execute. They show CI activity, **not** X2 health, independent receiver acceptance or human benefit.

- [CoLoop safety tests](https://github.com/CoCivium/CoCivium/actions/workflows/coloops-safety.yml): versioned recovery, safety and historical-source regressions.
- [Receiver reconciliation tests](https://github.com/CoCivium/CoCivium/actions/workflows/receiver-reconciliation.yml): bounded source-side reconciliation, **not** external receipt acceptance.
- [CoMVP first-use canary](https://github.com/CoCivium/CoCivium/actions/workflows/comvp-copre-cli-pilot-r0.yml): isolated newcomer-oriented task tests, **not** a verified X2 rollout.
- [CoPre Synth/Bio/G_d qualification](https://github.com/CoCivium/CoCivium/actions/workflows/copre-synth-bio-gd-r1.yml): source-side candidate checks, **not** scientific confirmation or canon.

These are **selected fronts**, not a complete or continuously monitored inventory. A red run must remain visible alongside green runs; later fixes do not erase earlier failures.

## What would prove a real improvement?

A useful needle should connect **a real intention → a bounded action → a receipt → an independent receiver → an observed human benefit**. The first few links exist in source-side experiments. The full chain, cost comparison and durable restart recovery are not yet verified.

For details, inspect the [R1 plotted HTML prototype](needle-trails-r1.html), the [measurement contract](../../docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md) and the [browser-QA run](https://github.com/CoCivium/CoCivium/actions/runs/42744256246). GitHub may show the HTML *source*, not a hosted application.

**Next proof:** An independently operated receiver recovers the exact work, an uncoached reader understands the status, and recovery is measured across an actual interruption.

*Source snapshot: 10 November 2026. No automatic refresh, external tracking, background microphone/camera capture, service deployment, or independent receipt is claimed.*
