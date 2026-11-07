# CoDemoWow+ | Truth Gate R0

**Status: PUBLIC EXAMPLE; WORKING OFFLINE CLAIM-CHECKING UI; NOT X2 SOFTWARE OR A PUBLIC RELEASE OF PRIVATE PR #296.**

[Open or save the standalone Truth Gate HTML](truth-gate-r0.html). GitHub source view may display the HTML markup instead of running it. Download the single file and open it in a browser.

This standalone example displays the source-bound CI result from the private CoSurface draft PR #296 (commit `ad6109a78808d089c6ed712d430a26f5c0503a5f`, run `42315581371`) with one orb, one evidence gauge, one action, and one observed timestamp. It shows the gap between **hosted CI accepted** and **X2 unknown/offline**. No network requests, telemetry, OS control or remote-agent installation.

## Try the actual interaction

1. **Run truth gate**: the four scoped evidence-consistency checks pass for the supplied observation.
2. **Test unsupported X2 claim**: an X2-live assertion is injected; the gate rejects it.
3. **Restore proven scope**: the baseline evidence returns. Expand the evidence packet to inspect/edit, validate malformed inputs, or export a local JSON receipt.

**Verification:** R0 was exercised in headless Chromium, including baseline acceptance (4/4), false-claim rejection (3/4), reset (4/4), malformed-JSON rejection, no JavaScript page errors, and mobile horizontal-overflow check. These tests establish the browser interaction only. Data supplied inside this page is an **observation record**, not live independent verification of CI or X2.

**Continuity:** An exact copy of the HTML is held in the separate CoCivium PublicationPackets Library, in addition to this source-controlled GitHub file. Complete independent-provider restore, X2 receiver pickup and >24-hour survivorship remain unproven.

Related: [CoCivium public start page](../../START_HERE.md) · [CoBook+ AGI reader](../../docs/Books/README.md) · [CoCivium repository](../../README.md).

**Next proof:** when an authorized X2 observer reconnects, collect a read-only live CoBar/CoOrb control receipt; do not confuse this fixture with the machine.
