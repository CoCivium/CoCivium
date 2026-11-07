# CoDemoWow+ | Truth Gate interactive editions

**Latest: [Truth Gate R1, time-bound evidence and currentness](truth-gate-r1.html)**  
**Preserved: [Truth Gate R0, original source-bound check](truth-gate-r0.html)**

**Status:** Public, self-contained browser demonstration; **NOT** live X2 software, a deployed CoBar/CoOrb controller, independent-host restore or a public release of private CoSurface PR #296. GitHub may display HTML source instead of executing it. Save the standalone HTML to open it in a browser.

## R1 improvement | Source freshness is not device freshness

R1 retains the original orb, gauge, source link, reversible fail-closed example and receipt export. It also:
- Displays the age of the *pinned historical CI observation*, calculated using the reader's own device clock. This is **not** a polling service or current X2 telemetry.
- Keeps X2 receiver currentness **UNVERIFIED** instead of promoting a historical CI success into a live machine claim.
- Rejects a locally edited source timestamp that falsely implies a newer independently observed event. The observed timestamp remains bound to the R0 pinned baseline.
- Preserves R0 as a byte-distinct predecessor for readers to compare or reproduce.

**Tested R1 in system Chromium with Playwright:** baseline **5/5**; unsupported X2 claim **FAIL CLOSED 4/5**; edited timestamp **FAIL CLOSED 4/5**; malformed JSON **FAIL CLOSED**; reset **5/5**; no JavaScript page errors; no browser HTTP requests; no horizontal overflow at 390-pixel viewport. Full reproducible browser-test log is a private scoped QA receipt, not an X2 runtime result.

## Try it

1. Open R1 offline and inspect the timestamp-derived **SOURCE SNAPSHOT** age.
2. Run the gate. Compare five checks against the **X2 HELD** indicator.
3. Inject an unsupported X2 claim and verify fail-closed, then restore.
4. Expand the evidence JSON, change `observed_utc`, and validate: the timestamp change is rejected.
5. Export a local receipt if you want to preserve the *demo's* outcome. Do not confuse a locally edited packet with an independently verified source.

Source CI: private [CoSurface draft PR #296](https://github.com/CoCivium/CoSteward/pull/296), head `ad6109a78808d089c6ed712d430a26f5c0503a5f`, run `42315581371`. The hosted job chain is evidence for that bounded code path, not X2. An exact R1 HTML snapshot and QA receipt are separately held in the private CoCivium PublicationPackets Library. GitHub-loss independent recovery remains untested.

[CoCivium first-use](../../START_HERE.md) · [CoCivia AGI reader](../../docs/Books/README.md) · [Main repository](../../README.md)
