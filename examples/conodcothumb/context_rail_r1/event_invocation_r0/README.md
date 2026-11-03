# CoB+ Event Invocation R0 + Durable Claim R1 | CoContextRail source-only donors

**State:** DRAFT / SYNTHETIC / NOT RUNTIME / NO DEVICE, ACCOUNT, NETWORK OR EXTERNAL RECEIVER EFFECTS.

## Two invocation routes, one operation

`CoEventInvocationR0.cjs` admits one local-only `REFRESH_LOCAL_STATUS` synthetic increment by either a BUTTON test entrypoint or a simulated CoB_EVENT test entrypoint. It fails closed for unallowlisted operations, privacy, stale/invalid packets, budget exhaustion and unavailable receivers. Its Map-based duplicate prevention **does not persist across process restart**.

## Added durability experiment

`CoBDurableClaimR1.cjs` is a separate Node test donor, **not a production replacement**. It accepts only public-synthetic, allowlisted packets and caller-supplied absolute fixture directories. A per-(work_id,operation) SHA-256 directory is claimed with exclusive creation; claim, synthetic effect marker and completion evidence are written in stages with file/directory fsync. Another process finding a completed and readable matching receipt returns DEDUPED. Any incomplete, unreadable or disputed claim returns HELD. No duplicate effect is attempted. Neither an event label nor a caller-supplied path establishes authentication or authority.

`test_durable_claim.cjs` exercises: replay in a fresh OS process, crash after claim, crash after synthetic marker, six competing OS processes, invalid packet denial, damaged completion, independent work IDs, and truthful no-receiver/no-authority receipts. `test_event_invocation.cjs` separately retains the eight in-memory synthetic-contract checks.

Both suites are wired into `.github/workflows/conod-cothumb-shadow-r0.yml`. **CI PASS must be verified against the exact PR head before citing it.** No preexisting local test result is substituted for CI.

## Essential limitations

- A crash after claim leaves the work **HELD**, requiring explicit evidence-based recovery. This is *at-most-once synthetic attempt*, **not guaranteed eventual completion**.
- A crash between the marker and completion also remains HELD; declaring DONE or retrying an irreversible effect is unsafe without independent receiver-origin readproof.
- The fixture has no authenticated actor, scoped live capability, cross-host lease, scheduler, provider event source, real button, remote effect, browser integration, X2/CoStead runtime or CoEx acceptance.
- Exclusive directory claims and fsync behavior here are tested in the GitHub Linux runner. No Windows or network-filesystem durability/locking guarantee is inferred.
- All receipts deliberately state `receiver_readproof: NOT_TESTED` and `authority: SYNTHETIC_POLICY_ONLY`; the harness cannot certify an independent receiver ACK.

**Next acceptance gate:** Independently qualify the current branch tests, prove evidence-based resolution of ambiguous claims, then connect a permitted, read-only operation to a distinct receiver that issues its own durable receipt. Keep draft until reviewed; no auto-merge, device hook, second scheduler or authority expansion.

Parent: [CoContextRail R1](../README.md). Existing coordination: [I/O Mesh #233](https://github.com/CoCivium/CoCivium/issues/233), [CoMiddle #246](https://github.com/CoCivium/CoCivium/issues/246).

`SOURCE_NE_RUNTIME | CLAIM_NE_COMPLETION | HELD_NE_SUCCESS | RECEIPT_NE_ACK | SYNTHETIC_NE_EXTERNAL_EFFECT`
