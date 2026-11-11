# CoBar / CoPre local I/O R4b | public research candidate

**Status:** PUBLIC SOURCE PROPOSAL / SYNTHETIC BROWSER-LOCAL FIRST-USE CANARY.  
**Not:** public application release, deployed CoBar, independent receiver ACK, native CoStead service, human UX acceptance, durable cross-host session synchronization, canon or CoEx.

## Purpose

Preserve and independently review an exact X2-tested CoBar first-use candidate. It provides one small, functional input-to-result loop on top of the existing R3c recovery surface. It is not another command framework or new background watcher.

- **Fixed synthetic WorkID:** `CO-SESSION-RECOVERY::LOCAL-SYNTHETIC-R0`.
- **Inputs:** `recovery status` and `why held` only. Unsupported input holds.
- **Effect:** after explicit synthetic-only consent, store exactly one browser-local record and render a deterministic answer. This does **not** send a message, start a device process, mutate the NAS, or grant cleanup authority.
- **Retry:** same WorkID and command is suppressed as a duplicate; a conflicting command is held.
- **Cold browser reload:** same browser-profile `localStorage` record read back. This is **not** off-host recovery.
- **Stop:** local WorkID changes to `REVOKED`. Subsequent reload and retry stay held.
- **Corruption:** malformed stored record fails closed without overwrite.
- **Evidence:** source-anchored frozen historical snapshot, not live telemetry.

## Exact source and proof

| Object | SHA-256 from authorized X2 observation |
| --- | --- |
| Exact R4b HTML candidate (`copre_local_io_r4b.html`) | `D56DF449DF491EC38F0D9B963B1B3D93DBC04FAEB7E1B3C8679462E3B39A2B72` |
| Exact R4b first-use receipt (`receipts/cobar_r4b_first_use_20261111.json`) | `76C38FFB45C26C81ABA1B773AA6086331B15E007BAEA9FC1218D2EF2D5BAC900` |
| Prior local R4a predecessor | `FFFADD8CFC199C749925ACA74396B76CA33EA80B197CC38F030AB2771DA4694A` |
| Original R3c qualified read-only source | `BB1483149B30A336617805CDF3AF02483EA3A46A8347C8220602E1DCB7AE0B6A` |

The source is an exact research preservation of the locally tested file, **not** an app deployment. Its historical receipt hashes are references, not proof of a currently running NAS receiver.

The first headless Edge trial of R4 failed at 1280px because a fixed bottom rail covered `Run locally`; a click targeted the rail instead. R4a moved the control clear on desktop but left the 390px consent checkbox under the rail. These failed receipts are preserved outside this public proposal; do not silently replace failure history with the R4b PASS.

**R4b browser proof:** isolated headless Microsoft Edge runs at **320, 390 and 1280 pixels** (850px tall) passed **11 checks each, 33/33 total**, with no external requests or page errors. Checks include explicit consent, browser-local commit/readback, duplicate suppression, cold tab reload, conflicting WorkID hold, revocation and revocation replay hold, corrupt-storage hold, and unobstructed Run/Stop/consent hit targets. [Public source-bound acceptance note](https://github.com/CoCivium/CoCivium/issues/453#issuecomment-6805571881).

## How to inspect

Review `copre_local_io_r4b.html` as source. Open the static HTML in an isolated browser profile for a synthetic demo. Select explicit test consent, enter one of the two supported commands, click `Run locally`, retry, reload, then click `Stop and revoke`. Do not use actual personal, private or operational data.

Browser `localStorage` is **not** durable shared custody. Once revoked, this synthetic WorkID must not be silently reset in the same profile merely to re-run a green demo.

## Additional control challenges (X2 process stdout only)

A separate, bounded X2 headless Edge challenge confirmed that the Run/consent/Stop sequence remained clickable and functional at five lower-height sizes: **320×568, 375×667, 390×667, 1280×600 and 1280×720**, with zero external requests or local artifact writes. This extends the prior browser receipt but does **not** alter its original 33/33 claim or create an additional receiver ACK.

**Important negative control:** A deliberately fabricated, internally schema-consistent `localStorage` record was accepted on reload as `RECOVERED_LOCAL_ONLY`, without a new checkbox interaction. That is an expected limitation of a client-controlled browser store. The field validator rejects malformed records but **cannot authenticate who wrote a well-formed record, prove genuine consent, or establish remote receiver identity**. Never promote the status label, nonce-like fields, local timestamp or self-declared receipt into authorization or a third-party ACK. A real receiver requires a separate trusted origin, consent validation, and exact readproof.

`LOCAL_STORAGE_SCHEMA_VALID_NE_AUTHENTICATED_CONSENT`  `BROWSER_RELOAD_NE_INDEPENDENT_RECEIVER`

## Required next proof

The existing [CoSpeedo/CoBar acceptance issue #453](https://github.com/CoCivium/CoCivium/issues/453) remains the product owner; [browser-to-SQLite bridge issue #450](https://github.com/CoCivium/CoCivium/issues/450) remains the receiver-contract gap, and [cross-surface recovery issue #317](https://github.com/CoCivium/CoCivium/issues/317) remains the external-origin ACK and custody gap.

The next independent gate is a **real human first-use** and, separately, an **authorized cross-failure-domain receiver** producing its own exact-object readproof. Neither is established by 33 synthetic browser tests or publication of a GitHub branch.

**Rails:** `LOCAL_IS_NOT_LANDED`; `VALIDATION_IS_NOT_ACCEPTANCE`; `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`; `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`; `HOLD_NO_DELETE`.

No local predecessors were deleted or authorized for retirement by publication.
