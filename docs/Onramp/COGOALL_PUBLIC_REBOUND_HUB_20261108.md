# CoGoAll Public Rebound Hub R0 | 2026-11-08

**Purpose:** one durable, public-safe re-entry point for WhatsApp, browser sessions, people, and future model workers. **This page is a source index, not a delivery acknowledgment, synchronized memory, or deployed runtime.**

## Read this first (five minutes)
1. [Start Here](../../START_HERE.md): plain-language first use and honest capability boundaries.
2. [Evergreen status](../../EVERGREEN.md): historical results, limitations, and source pointers. Check dates and links.
3. [CoModelFabric provider-neutral adapters](../Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md): local/open/authorized models, fan-out, challenge, receipts, explicit effect gates.
4. [RickBar / CoFleet UX contract](../UX/COFLEET_RICKBAR_R4.md): one work-facing surface instead of session babysitting.
5. [CoReGroup peer evidence contract](../Evolution/COREGROUP_PEER_EVIDENCE_CONTRACT_R0.md): provenance, lease fencing, verification, recovery; proposed contract, not proof of live peer sync.

## Current engineering threads
- [CoMVP+ / CoLockStep+ stable-island release contract](../Architecture/COMVP_COLOCKSTEP_SOURCE_RELEASE_R0_20261109.md): runnable local source release-slot CLI, pinned minimum-use acceptance tests, atomic dependency cohorts, rollback and [74 passing CI checks](https://github.com/CoCivium/CoCivium/actions/runs/42605151164). **Not a qualified native X2/public MVP or CoAll-wide runtime controller.**
- [rickBar Continuity R1 source and host acceptance contract](../Architecture/RICKBAR_CONTINUITY_R1_20261108.md): durable local conversation, fenced worker epoch and restart recovery with [passing synthetic CI](https://github.com/CoCivium/CoCivium/actions/runs/42540438846). **Not installed on X2 or native rickBar; no hosted-session swap or automatic deletion.**
- [Ollama loopback gateway](../../examples/comodelfabric/ollama_gateway_r0.py) and [GitHub Actions workflow](../../.github/workflows/comodelfabric-ollama.yml): source and CI configuration; inspect actual run status before asserting PASS.
- [WorkID receipt store](../../examples/comodelfabric/test_gateway_bridge.py): idempotency/replay/conflict prototype; not native receiver.
- [Ollama-to-receipt CLI](../../examples/comodelfabric/rickbar_ollama_bridge_r0.py): source bridge, not verified X2 deployment.
- [GS loop guard tests](../../tests/gs_loop/test_loop_guard.py) and [durable seed tests](../../tests/gs_loop/test_durable_seed.py): isolated logic, not 24-hour production survival.
- [Receiver reconciliation tests](../../tests/gs_receiver/test_receiver_reconcile.py): synthetic distinction between source and receiver.
- [CoFleet projection compiler](../../scripts/CoFleetProjectionCompilerR4A.py): bounded fleet UX projection.
- [X2 diagnostic record](../Evolution/COWAVE_X2_DIAGNOSTIC_20261108_R0.md): observer/clone/test constraints; disconnected bridge does not mean X2 is powered off.

## Strategy and research
- [Frontier evidence review (2026-11-08)](../Public/COALL_FRONTIER_PUBLIC_EVIDENCE_REVIEW_R0_20261108.md): source-qualified AI capability, AutoDNA, security, SETI, unknown intelligence and falsifiable follow-up; research evidence, not a deployed agent or independent confirmation.
- [G_dSide / CoPriMath / GS-Loop public R0](../Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md): candidate future-directed valuation, typed relations, anti-loop contracts.
- [Five-lane workpack](../Evolution/GDSIDE_FIVE_LANE_WORKPACK_R0.md): proposed parallel areas, **not** fixed worker hierarchy.
- [CoLiving highlight assets](../Architecture/COLIVING_HIGHLIGHT_ASSETS_R0.md): receiver-relative, versioned highlights; observed version remains recoverable.
- [CoLiving highlight design](../Architecture/COLIVING_HIGHLIGHT_R0.md) and [machine-readable highlights](../../ai/highlight-assets.json).
- [CoOrb local regenerative UX](../Architecture/COORB_LOCAL_UX_REGENERATIVE_R0_20261026.md).
- [CoBrowser/CoOrb continuity](../Architecture/COBROWSER_COORB_CONTINUITY_R0_20261027.md).
- [CoMap examples](../../examples/comap/README.md).
- [CoPreCursor first-use demo](../../examples/coprecursor/README.md).
- [CoAttractorPull demo](../../examples/coattractorpull/README.md).
- [CoAcademy CoOrbWare First Look](https://github.com/CoCivium/CoAcademy/blob/master/docs/coorb/index.html).
- [CoAcademy civic lens](https://github.com/CoCivium/CoAcademy/blob/master/docs/civiclens/index.html).

## Discover the larger corpus without inventing a thousand vetted links
- [All public CoCivium source files](https://github.com/CoCivium/CoCivium/tree/main)
- [Architecture documents](../Architecture/)
- [Evolution documents](../Evolution/)
- [UX documents](../UX/)
- [Operations documents](../Operations/)
- [Examples](../../examples/)
- [Machine-readable assets](../../ai/)
- [Public GitHub issues](https://github.com/CoCivium/CoCivium/issues)
- [Public pull requests](https://github.com/CoCivium/CoCivium/pulls)
- [GitHub Actions runs](https://github.com/CoCivium/CoCivium/actions)

These indexes are expandable entry points, **not** a claim that 1,000 pages have been individually audited or that every linked candidate is production-ready.

## Rebound contract for an older WhatsApp or AI session
Read this page and the five-minute links above; identify source version and currentness; propose **one** source-bound delta or independently testable challenge; preserve counterevidence and nonclaims. Do not assert that reading this page synchronizes memory, establishes model identity, gives external account authority, or authorizes public/private messages. No manual copy-back should be required for the architecture; actual automated delivery still needs a verified transport.

## Current proof gates
**Known source:** Public gateway, bridge, receipt prototype, test files, CI configuration, and UX contracts.  
**Not established here:** Native RickBar input/output binding, real X2 Ollama round trip, independent CI pass readproof, 24-hour recovery, intersession delivery ACK, model-weight mindshare, or a production multi-model federation.

**Next measurable product proof:** RickBar prompt → authorized local Ollama → persistent WorkID receipt → RickBar display → restart/recovery readback, with independent observation and baseline latency.
