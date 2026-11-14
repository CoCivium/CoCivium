# CoPre recovery A/B | Wave render END

**WorkID:** `CoPre.Offshore.20261109` · **Wave:** `CoPreRecoveryAB.R0` · **Phase:** `END`  
**UTC date:** 2026-11-09 · **Destination:** public draft branch PR #401 only  
**State at END authoring:** `SOURCE_LANDED_CI_PENDING` · **CoEx:** `NOT_CERTIFIED`

## What changed

- Saved [BEGIN](BEGIN.md) as a separate Git source commit before this work.
- Added [CoPreRecoveryABR0.py](../../../../scripts/CoPreRecoveryABR0.py), a *read-only* A/B fixture that reuses the exact existing [CoPreUptakeBridgeR0.py](../../../../scripts/CoPreUptakeBridgeR0.py) and the CoStatusOffload checkpoint.
- Strategy A is a compact WorkID/source-revision/digest pointer requiring a separately accessible resolver. Strategy B is a complete portable packet checked against a synthetic receiver pin and validated for inner WorkID/authority/STOP.
- Twelve synthetic comparison cases evaluate normal restore, missing or unreadable source, modified source, valid but mismatched bytes, source-age divergence, identity substitution, expired receiver generation, full-packet corruption, pin mismatch and stale inner revision.

## What cannot be concluded

The full packet retains its embedded original bytes if the resolver disappears. The pointer is smaller when an exact current source is available. Neither guarantees independent availability, provider authenticity, remote pickup, or useful work after restoration. A packet containing old bytes can appear valid while its source has advanced; source currentness needs a separate authority.

At this END file's creation **CI results are pending**, not presumed green. Actual effects are GitHub draft-branch source writes only.

## CoPre | NEXT

Elect one actually authorized receiver holding a pin distributed *before* receiving the checkpoint. Compare full packet versus WorkID pointer with independent storage failure injection and observer-produced readproof, and measure human intervention, latency, currentness and task correctness.

**Inversion:** If the compact pointer plus reliable source gives lower overall recovery cost, retain it; use larger portable packets for cases that demonstrably benefit from offline bytes.

**STOP:** unauthorized receiver, stale head, unavailable independent source, or no useful new evidence.

**Nonclaims:** `END_NE_CI_PASS | TEST_FIXTURE_NE_REMOTE_STORAGE | TWO_PROCESSES_NE_TWO_FAILURE_DOMAINS | SOURCE_CHECKSUM_NE_AUTHENTICITY | PACKET_RESTORE_NE_RECEIVER_ACCEPTANCE | DRAFT_BRANCH_NE_COEX`.
