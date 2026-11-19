# CoPre 9.2+ | CoWalkAway / CoBreakGlass / CoGuardian startup delta R0

**Status:** ADDITIVE PUBLIC-SAFE CANDIDATE, NOT GOVERNING OR RUNTIME. **Date:** 2026-11-19 UTC.

**Parent:** [CoWalkAway261118 recovery bootcard R0](COWALKAWAY261118_RECOVERY_BOOTCARD_R0.md). CoPre v8 continues to govern. This document neither replaces the bootcard nor elects another master, actuator, daemon, CoEx receiver or universal source of truth.

## Why this delta is material

A real post-update Windows reboot and a bounded, user-returned read-only PS7 snapshot showed that a registered task, a visible desktop surface, and a remote observer's connection status are **different kinds of evidence**. Earlier local child-process recovery tests do not prove host reboot recovery, successful post-boot execution, automatic new-work discovery, or restored human I/O. Visible stale/placeholder surfaces and overlapping launcher registrations add a separate UX and security risk.

The returned transcript is private operator evidence; no raw process command lines, startup target paths, user identity, provider tokens, credentials, sensitive metadata or screenshots are republished here.

## Additive CoPre 9.2 continuity rail

`CoPre9.2+|CoWalkAway<->CoBreakGlass|BreakGlass!=Routine|BridgeOffline!=HostOffline|TaskReady!=PostBootRun|ProcessPresent!=Healthy!=Useful|State>Chat|Recover>Restart|Event>BlindTimer|OneElectedActuator|OneOwnerPerStartupRole|SignedPinnedAllowlist>RemoteCommands|CoGuardian:Pub/Merge/Privacy/Delta|QuietUI>Popup|StopIsReal|Failure>FencedRecovery>Receipt|3indOrHOLD|Rick=0Routine|NoPhantomACK`

This **extends** but does not remove CoPre v8/v9.2 gates: one job/receipt, fan-in to the existing master, independent checks, replay safety, exact source lineage and honest custody.

## Operating distinctions

1. **CoWalkAway is the default, CoBreakGlass is the exception.** Eligible local work advances on a durable typed event under exactly one fenced actuator; exceptions freeze conflicting writers, preserve prior versions, and elect one bounded recovery route. Human keyboard relays must not become the heartbeat or long-term transport.
2. **Connection and computer health are distinct.** A remote bridge reporting offline means only that *observer route* is unavailable. It does not prove the host is powered off, work stopped, or an agent absent. Use an independently authenticated host observation when possible, else one audited local PS7 break-glass diagnostic.
3. **Startup evidence has separate stages.** `REGISTERED -> TRIGGERED -> PROCESS_OBSERVED -> HEALTH_PROVEN -> USEFUL_OUTPUT -> RECEIPTED -> RECOVERED_AFTER_INTERRUPT`. Never infer a later stage from an earlier one. The task's `Ready` state and last exit code do not prove it ran after the most recent boot. Compare source-bound task run, boot and receipt times, using independent readback.
4. **Startup ownership is role-based.** Inventory existing Startup-folder entries, registry Run keys, services, tasks, tray launchers and user-triggered terminals; reconcile against an explicitly approved desired-state manifest. One owner per effect/collision scope, with duplicate and obsolete launchers **held**, not automatically killed, enabled, deleted or replaced.
5. **No auto-elevation or cloud command shell.** Startup repairs require pinned executable identity, reviewed publisher/signature where available, SHA-256, ACL/least-privilege checks, authorized local policy, tested rollback and append-only receipt. Cloud may supply bounded analysis or signed proposals; it cannot confer authority or directly run arbitrary startup commands. Adversarial participation belongs in isolated consented test environments, not production.
6. **Recovery is observable and reversible.** Failed jobs keep leases/attempt history, recover only eligible successors, cap retry/backoff, quarantine crash loops, provide genuine Stop and restore prior behavior after validated recovery. Restarting the **child** does not prove recovery of the **parent**, scheduled task engine, operating system or network link.
7. **Quiet user-facing UX is the contract.** Background work should be headless. CoBar/CoDesktop must present useful input/output and age-qualified statuses; old dashboards and morning-brief recitals are on-demand rather than compulsory. No stale green percentages, unlabelled placeholders or surprise console windows claimed as success. Accessibility, revocation and consent remain first-class.
8. **CoGuardian failure gates are independent.** No automatic publication, public metadata remediation, merge, private-data transfer, finance, credential changes, destructive operation or governance promotion. Require explicit actor/scope and independent evidence at each high-risk boundary. Three independent roots or HOLD where the rail requires it.
9. **Break-glass closes itself.** One authorized intervention -> exact observation -> bounded reversible deed -> independent verification/receipt -> return to the pre-existing elected actuator. If that handoff cannot be proven, remain HOLD with the last-known-good control route. Never create a second permanent control plane.

## Minimum next acceptance proof

- Confirm fresh host boot timestamp and **actual** task invocation/receipt timestamps after boot, with exact process identity, without exposing secrets.
- Submit one *new* eligible durable-work event via a real machine-owned producer, not a chat-triggered copy/paste; complete it under the original fenced ledger and observe output from an independently authenticated reader.
- Test a parent-process failure and a controlled fresh logon/OS restart; verify no duplicate elected actuator, no lost work, genuine Stop and rollback readback. A synthetic subprocess crash is **not** a substitute.
- Verify one useful, quiet CoBar/CoDesktop surface with nontechnical first-use acceptance; keep cosmetic previews and public releases separately gated.
- Preserve one source-linked, timestamped CoHereNow / ExState / receipt / HOLD+next job. Report any unobserved stage as UNKNOWN, not PASS.

**Current disposition (2026-11-19):** SOURCE CANDIDATE ONLY. The user-returned PS7 snapshot established a registered post-boot native task with the expected action, not a post-boot task-execution proof. No fresh independent X2 receiver acknowledgement, new-work autonomy, parent/reboot recovery, public deployment or CoEx claim is made here.

## Existing owners / source links

- [CoPre public entry](../../CoPre.md) and [CoPreGeneric bootstrap](../../SESSION_BOOTSTRAP.md).
- [CoWalkAway recovery bootcard](COWALKAWAY261118_RECOVERY_BOOTCARD_R0.md), [work queue](COCLAUDE_WORK_QUEUE_R0.json), [landing contract](COSESSIONMESH_COLANDING_CONTRACT_R0.md).
- [Read-only Windows startup inventory](../../scripts/CoRunnerStartupInventoryR0.ps1). Its generic/self-test output must not be represented as X2 proof.
- [CoDesktopPresence and CoRunner owner #181](https://github.com/CoCivium/CoCivium/issues/181), [CoBar/CoSpeedo acceptance owner #453](https://github.com/CoCivium/CoCivium/issues/453), [source-bound WorkID owner #450](https://github.com/CoCivium/CoCivium/issues/450).
- [Historical PS7 break-glass election](https://github.com/CoCivium/CoSteward/blob/main/docs/session_backchannel/provider_independence/CoProviderIndependence260924-V1_R0E_ps7_breakglass_election.json).

## Custody and nonclaims

`DISCOVERED != VERIFIED_LOCAL != LANDED != PICKED_UP != INTEGRATED != COEX`.

This **public GitHub candidate file**, if committed and read back, proves only public-source landing of its own sanitized text. It is not the private host forensic receipt, active runtime policy, elected owner ACK, merge approval or public website release.

`LOCAL_IS_NOT_LANDED; VALIDATION_IS_NOT_ACCEPTANCE; NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF; NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE; HASHING_IS_NOT_SEMANTIC_INGESTION; DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY; NO_PHANTOM_ACK`.
