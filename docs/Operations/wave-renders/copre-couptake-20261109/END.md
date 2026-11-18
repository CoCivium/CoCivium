# CoPre+ ↔ CoUptake+ | Wave render END

**WorkID:** `CoPre.Offshore.20261109`  **Wave:** `CoPreUptakeBridge.R0`  **Phase:** `END`
**Date:** 2026-11-09 UTC  **State at END authoring:** `SOURCE_LANDED_CI_PENDING`
**Destination:** CoCivium public draft PR #401, not main or a live system.

## What changed

- Separate [BEGIN](BEGIN.md) render records work intent before implementation.
- [CoPreUptakeBridgeR0.py](../../../../scripts/CoPreUptakeBridgeR0.py) connects two previously separate **existing** candidates: CoStatusOffload's WorkID structure and the exact CoUptake R0.2 standalone source-pin receiver from draft PR #360, held at commit `248d3f3bc4836bb2b42378152f087221494cf0bc` and Git blob `a3bbf5bf6b8ed9c1b54858346f67e8460ee958a5`. It copies the donor verifier into a temporary three-file receiver workspace and runs a separate isolated Python interpreter. The test packet/pin use synthetic public-safe data only.
- CI now proposes nine negative/positive cases covering correct source+work match, stale receiver generation, changed bytes, forged ACK, wrong policy pin, current-source mismatch, unauthorized inner checkpoint, lost STOP, and WorkID substitution.

## Proof boundaries

**Actual source effect:** draft-branch GitHub commits (including this END); source reads and CI receipts to be attached separately after verification. The END render is authored with CI pending and does not retroactively claim success.

**Not accomplished:** independently governed receiver pin, separate network/provider/host, externally reachable storage, real cross-session wake, model learning, authorized CoStead/X2 deployment, human receiver pickup, transaction, CoEx or canon. Even a successful isolated-process test is only a *source and integrity control*, not independent operational trust.

## CoPre+ NEXT

Elect one separately authorized independent receiver that retains a trust pin established **before** packet arrival. Compare the pinned checkpoint against a WorkID-only source pointer. Measure restoration correctness, STOP/authority retention, latency, false holds and human relay. HOLD until the receiver is available. Do not retry the previously declined storage write through another route.

**Inversion:** A simpler exact WorkID pointer and independently accessible source may beat a copied packet.

**Nonclaims:** `END_NE_CI_PASS | PIN_GENERATED_WITH_PACKET_NE_INDEPENDENT_TRUST | TWO_PROCESSES_NE_TWO_HOSTS | SOURCE_PIN_MATCH_NE_WORK_HEAD_CURRENT | VERIFIED_BYTES_NE_RECEIVER_ACCEPTANCE | DRAFT_LANDING_NE_COEX`.
