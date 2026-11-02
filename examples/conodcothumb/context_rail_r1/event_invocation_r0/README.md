# CoB+ Event Invocation R0 | CoContextRail source-only donor

State: **DRAFT / SYNTHETIC / NO DEVICE OR EXTERNAL EFFECT / NOT RUNTIME**.

One allowed operation, `REFRESH_LOCAL_STATUS`, is invoked through two synthetic routes: a human-button entrypoint and an authorized-CoB-event *simulator* entrypoint. Neither route clicks another application nor gains implicit authority. The simulated operation increments only in-memory test state.

**Verification:** `node --test test_event_invocation.cjs` (8/8 local Node tests passed in isolated working container, 2026-11-02). Current GitHub source custody must be rechecked independently; no GitHub Actions result has been claimed. Tests cover route equivalence, cross-route dedupe, disallowed operations, privacy, undeclared fields, currentness/expiry, unavailable receiver, finite budget, zero external effects, and no fabricated receiver readproof.

**Limitations:** In-memory dedupe vanishes on restart; no authenticated actor, persistent work ledger, connected X2, real event source, native button, scheduled worker, file/OS/API action, independent receiver or CoEx acceptance is present. A `CoB_EVENT` entrypoint is not authentication. Real runtime must provide a verified actor/lease, authorized capability check, durable idempotency, event source and receiver-origin result receipts before a consequential operation.

Parent existing source: [CoContextRail R1](../README.md). Existing coordination: [I/O Mesh #233](https://github.com/CoCivium/CoCivium/issues/233), [CoMiddle #246](https://github.com/CoCivium/CoCivium/issues/246). Do not install a second mouse hook or auto-merge this candidate.

Next acceptance: independently run branch tests, then when X2 receiver is healthy test a safe read-only currentness query through the existing adapter and the accessible UI, with real source/receiver/rollback receipts.

`BUTTON_NE_AUTHORITY | EVENT_NE_AUTHENTICATION | SHADOW_NE_RUNTIME | DUPLICATE_NE_SECOND_EFFECT | RECEIPT_NE_ACK`
