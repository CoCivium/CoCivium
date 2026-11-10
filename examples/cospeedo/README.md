# What actually got better?

**CoSpeedo NeedleTrails** is a plain-language record of what CoCivium has tested, what has failed, and what remains unknown. It is not a live dashboard.

> **Right now:** The source is publicly readable and some bounded automated checks passed. A working independent recovery service, 24-hour survival, and measured human time saved are **not yet proven**.

| Question | Current answer | Evidence |
| --- | --- | --- |
| Can I inspect the work? | **Yes.** The R1 source and archived measurements are on public GitHub. | [NeedleTrails R1 HTML source](needle-trails-r1.html) |
| Did an automated check pass? | **Yes.** Source and four-size Chromium browser tests passed. | [Browser verification, 10 Nov 2026](https://github.com/CoCivium/CoCivium/actions/runs/42744256246) |
| Did the public-source data checks pass? | **Yes.** The existing census and R1 chart consistency gate passed on main. | [Main-branch verification](https://github.com/CoCivium/CoCivium/actions/runs/42750710011) |
| Does CoSpeedo automatically track all devices and projects? | **Not proven.** This page summarizes a *dated snapshot*, not continuously refreshed telemetry. | [Measurement contract](../../docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md) |
| Has independent 24-hour recovery worked? | **Not proven.** A GitHub CI job is not an independent external receiver. | [Receiver acceptance issue](https://github.com/CoCivium/CoCivium/issues/317) |
| How much effort did people save? | **Unknown.** No comparable receiver-side human outcome baseline has been established. | [Seven-day scorecard](../../docs/Metrics/COSPEEDO_7DAY_SCORECARD_R0_20261026.json) |

## The needle trail, without the jargon

The archived test ledger records **Pass**, **Held**, and **Fail** events. Those are engineering check outcomes, not numbers of people helped. A low Pass count could mean fewer tests ran, not that quality declined.

| Recorded day (UTC) | Passed checks | Held for evidence | Failed checks |
| --- | ---: | ---: | ---: |
| 2026-10-23 | 38 | 16 | 10 |
| 2026-10-24 | 40 | 26 | 3 |
| 2026-10-25 | 3 | 2 | 0 |
| 2026-10-26 | 3 | 3 | 1 |

**October 20–22 have no captured ledger rows.** That is **unknown coverage**, not proof that nothing happened. The four observed dates total 145 ledger rows. Source: [exact archived census](../../docs/Metrics/COSPEEDO_RECEIPT_CENSUS_R0_20261027.json).

## Three things to remember

**Source available:** You can read what was built.  
**Bounded test passed:** A reproducible check ran successfully.  
**Useful real-world outcome:** A person or independent receiver actually benefited, with measurable evidence.

The first two do **not** automatically establish the third. That distinction is the purpose of the gauge.

## Explore the evidence

The [R1 HTML prototype source](needle-trails-r1.html) includes a plotted historical needle trail, counter-needles and an optional technical explanation. GitHub's file view may show HTML *source*, not a hosted application. The [browser-QA run](https://github.com/CoCivium/CoCivium/actions/runs/42744256246) retains rendered screenshots and checks at 360, 390, 768 and 1440 pixels, subject to GitHub artifact retention. This Markdown page is the directly readable GitHub entry.

**Next proof:** An independently operated receiver must recover the exact source, a real reader must understand the result without coaching, and a later run must demonstrate durable recovery. Until then, the gauge stays honest rather than merely enthusiastic.

*Source snapshot: 10 November 2026. No automatic refresh, external tracking, background microphone/camera capture, service deployment, or independent receipt is claimed.*
