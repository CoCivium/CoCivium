# CoGbx UX Exemplar R0

**State:** public-safe static source exemplar. Not deployed to CoGbx.org.

Open `index.html` locally in a browser.

## What it demonstrates

- one durable work object projected as Orb/Map/Text/Ambient;
- optional 3D+ perspective without making 3D mandatory;
- responsive layout from narrow screens to X2-class desktops;
- explicit UNKNOWN/currentness state;
- redundancy / no-crown relation;
- local predictive shadow with explicit accept/reject;
- zero network, storage, credential, send or provider effects.

## What it does not prove

- deployed CoGbx.org;
- X2 runtime integration;
- XR/WebXR acceptance;
- screen-reader acceptance;
- provider substitution;
- distributed peer operation;
- receiver pickup;
- CoEx.

## Reproduce

```sh
node examples/cogbx_ux_exemplar_r0/smoke.cjs
```

## Source relations

- `docs/Architecture/COGBX_UNIVERSAL_UX_EXEMPLAR_R0_20261027.md`
- `docs/Architecture/COORB_LOCAL_UX_REGENERATIVE_R0_20261026.md`
- `docs/Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md`
- `docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md`
- `docs/Evolution/COSCALE_CONTINUUM_COORBWARE_R0_20261023.md`

## R0.1 status-truth and non-capture revision (2026-10-27)

The original R0 is a helpful **synthetic offline illustration**, but labels such as `recovery available`, `crown risk low`, and green-colored `PEER` paths could be mistaken for observed live device/federation state.

R0.1 adds a conspicuous **STATIC DEMONSTRATION · NOT LIVE** notice and changes the sample values to `synthetic fixture`, `not live-tested`, `not measured` and `candidate`. The forest-green notice indicates **explanation/context**, not proof of healthy status. The existing orbital, map, ambient, text, 3D+ and reversible local predictive controls remain.

This corrects presentation semantics only. It does **not** establish:
- that X2's current CoBar, Desktop Commander, browser or native agent is reachable;
- that PEER, WEB, MODEL and LOCAL are independently operable failover paths;
- that recovery can reconstruct real work after one device or provider disappears;
- that CoGbx.org is deployed, owned by the application, or an identity root;
- that any synthetic user interaction implies actual user consent.

**Next recommended test before native integration:** render the same **real, authorized, non-private** work-object packet on two independently implemented front ends and one text/headless projection; compare identity, source digest, freshness, unknown status and recovery bytes. Close one renderer, reconstruct from the portable packet, and confirm exact readback. The participant must be able to decline prediction, export/leave, and disable the UI. Report actual observed failure-domain diversity, not a count of logos.

**CI regression:** `smoke.cjs` rejects misleading green-status/failover strings. The optional Chromium acceptance test also exercises desktop and mobile view transitions, keyboard-focused controls, local accept/reject and zero outbound requests. These checks are separate from independent human accessibility and first-use tests.

## R0.1 CoSpeedo+ capacity context

The optional [throughput and qualified-resource contract](THROUGHPUT_BASELINE_R0.md) distinguishes **immutable historical high-watermark** from **repeatable sustainable baseline**, **verified useful results per human-time**, and **currently qualified spare capacity**. Each needs comparable workloads, correctness, receiver outcome, end-to-end timing, tail latency, resource/energy cost, currentness and recovery constraints.

The demo now shows all corresponding counters as **NOT MEASURED / UNQUALIFIED**. Its 60+ local Chromium checks are proof that an offline UI behaves within the test scope, *not* an X2 production workload benchmark, global inventory census or proof of independent peer/failover paths.

No resource discovery, private I/O access, telemetry capture, scheduled benchmark or device polling was added.

## CoPredictiveInput+ source-integrity reconciliation (2026-10-28)

The original static CoGbx PR #327 expected **Accept locally** to append a predicted suggestion directly to the editable `#draft` field while calling it "RAW preserved." That silently conflated the user's original input with a synthesized proposal. Parallel corrective [PR #326](https://github.com/CoCivium/CoCivium/pull/326) had already identified a safer rule: the original editable value remains untouched by an accepted, rejected or undone preview.

This candidate now reuses that rule without creating a new controller. `#proposal` is an accessible `role=status`, `aria-live=polite` preview distinct from raw `#draft`. **Preview accept** displays only a proposed next text; **Reject preview** declines it; **Undo preview** clears the proposal. Explicit user typing still edits raw text. No storage, network request, account effect, device input mapping, new task scheduler, real ACK or X2 runtime is introduced.

Source smoke rejects any JavaScript assignment to `draft.value`; desktop/mobile Chromium tests assert unchanged input after preview/reject/undo, user-initiated edits remain permitted, zero send/execution, no horizontal overflow and zero browser errors. The [verified GitHub CI run](https://github.com/CoCivium/CoCivium/actions/runs/40738116898) completed successfully on code head `4b8af1a02228dd3aac0b8bd8e8c0f39ad79248b4`: smoke PASS and **82/82** Chromium checks, zero failures.

**Overlap disposition:** #326 is a documented donor/collision candidate, not automatically closed, merged, superseded or approved by this source change. Reviewers must reconcile both branches before any merge. This is a proof-safe local UI change; the independent work-object -> receiver -> recovery gate, actual X2 keyboard/browser latency and live CoBar/CoOrb remain HELD.

`RAW_NE_PROPOSAL | PREVIEW_NE_EXECUTION | SOURCE_CI_PASS_NE_NATIVE_X2 | CROSS_PR_DUPLICATION_REQUIRES_EXPLICIT_REVIEW`
