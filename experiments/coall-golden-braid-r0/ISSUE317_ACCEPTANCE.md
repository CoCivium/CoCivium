# CoAll Golden Braid R0 | Issue #317 acceptance mapping

Scope: **offline, synthetic, local two-receiver conformance**. This proves no outside recipient uptake, production synchronization, cross-device recovery, deployed CoGbx.org page, or current X2 runtime. It is an independent reproducible candidate to review alongside existing CoPulse R0B/R0C, **not** a replacement coordination bus.

| Acceptance requirement | Evidence | Disposition |
| --- | --- | --- |
| Inventory authorized surfaces | `SURFACE_INVENTORY.json`; two local subprocess receiver destinations; all external and device routes held | PASS_BOUNDED |
| Canonical task packet | `fixture/task_packet.json`; `task.json` hash, `pointer.json`, scoped authority, epistemic state and provenance | PASS_LOCAL |
| One input, two destinations | `output/demo/demo_work/receivers/{alpha,beta}/delivery.json`, separately originated receiver processes | PASS_LOCAL |
| Separate receipt and ACK | Separate `ack.json` per receiver, bound to task and exact delivery hashes; `coall_braid.verify_receiver()` | PASS_LOCAL |
| Failure and no duplicate retry | `run_demo.py` injects one beta failure, retains alpha ACK, retries beta, and then skips both | PASS_LOCAL |
| Fresh-process reconciliation | `verify_output.py` and fresh subprocess check against pinned task + journal head | PASS_LOCAL |
| Concurrent dispatcher held | `tests/test_braid.py::test_supervisor_lock_blocks_concurrent_dispatcher` | PASS_LOCAL_ONLY |
| Worker dies after writing delivery, before ACK | `tests/test_braid.py::test_crash_between_delivery_and_ack_recovers_without_rewrite` | PASS_SYNTHETIC_FAULT |
| Source/ACK tamper rejection | Negative tests for altered task, journal, receiver ACK, missing proof, changed partial delivery | PASS_LOCAL_ONLY |
| Stop and authority limits | `stop` marker blocks worker/dispatch; permission scope allows synthetic local only | PASS_LOCAL_ONLY |
| Real independent receivers | Both processes share a host/filesystem; no independent operator or trust domain | HOLD |
| Global/cross-provider sessions and X2 | No installed adapter or current remote X2 readproof | NOT_RUN |
| CoGbx.org landing | Local HTML candidate only; no DNS/TLS/hosting validation or deployment | NOT_RUN |
| Human first-use and useful outcomes | No uncoached user task, comprehension or accessibility audit on a device | NOT_RUN |

Source and evidence: immutable sample task, pinned journal, test logs and separate receiver files inside the package. A GitHub commit or this package is a publication/discovery surface, **not receiver acceptance**. Successful test status must not be conflated with independent beneficiary value.

## Remaining work to close issue #317

1. Have a receiver under another administrator/failure domain read the exact, consented packet and return independently generated proof bound to a known identity/key and source hash.
2. Disconnect the origin and recover the same task from the receiver's stored copy in a fresh session.
3. Validate no double effects across a real interruption, actual scoped authorization, persistent revocation and stale-lease handling.
4. Make the current state visible from a separate observer, distinguish local ACK from external pickup, and observe a real user completing a useful task.

`POINTER_NE_ACK | TWO_PROCESSES_NE_TWO_FAILURE_DOMAINS | MODEL_SUGGESTION_NE_TRUTH | SYNTHETIC_NE_GLOBAL_SYNC`
