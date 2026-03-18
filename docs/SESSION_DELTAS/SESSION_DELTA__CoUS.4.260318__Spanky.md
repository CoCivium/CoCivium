# SESSION DELTA — CoUS.4.260318 (Spanky)

## 1. Session Labeling (Alias-First)

Display format:

Alias ⊂ CanonicalSessionID

Rules:
- Alias is the human-friendly handle.
- CanonicalSessionID remains source of truth.
- Bare alias references should resolve to the latest matching session in-account.
- Resolution must fail closed on ambiguity.
- Short CoSHA is mainly for automated or shadow sessions, not mandatory for casual sessions.

## 2. Session Classes

Primary posture classes:
- CoChat — advisory / exploratory / lighter tone permitted
- CoWork — execution / mutation / tighter rails
- CoPrime — orchestration / convergence / priority setting
- CoGuard / CoGuardian — verification / normalization / truth enforcement

Class should influence startup posture, authority claims, and response style.

## 3. Wake Intro

Recommended startup intro fields:
- identity
- role
- mandate
- confidence
- capabilities
- next_safe_action

This should be brief and self-locating, especially after handoff or hitching uncertainty.

## 4. CoBus Attachment Semantics

Allowed attach states only:
- bootstrapped
- read_attached
- write_attached
- fully_hitched
- blocked
- local_receipt_only

Critical rule:
- Local artifacts alone do **not** imply CoBus write attachment.
- A session may claim write_attached only after writing to a shared accepted CoBus surface and verifying that write.
- A session may claim ully_hitched only after read + write + verification are all true.

## 5. Missing Bootstrap Layer

CoBeacon is not enough by itself for full operational hitching.

Needed companion layer:
- CoHitch / CapManifest

CapManifest should expose:
- readable surfaces
- writable surfaces
- accepted publication routes
- append/update rules
- auth expectations
- verification method
- fail-closed behavior when a writable path is unavailable

## 6. Execution Discipline

For execution rebuilds:
- prefer fresh process isolation over in-session variable clearing
- reject Remove-Variable * as fake fresh-context isolation
- use pointer-first, immutable inputs where possible
- fail closed on count divergence or source-truth mismatch

## 7. Frozen Partial-Set Rebuild Context

Canonical rebuild truth for this branch:
- total = 30
- partial = 24
- complete = 6

Known issue:
- prior failures were execution contamination, not source-data defects

Canonical source root:
C:\Users\rball\CoBusArtifacts\COCAMPAIGN__FREEZE__PARTIAL_SET__20260318T122516Z

Canonical input:
SNAPSHOT__PARTIALS_24.json

Required rebuild rule:
- rebuild only from the frozen snapshot in a fresh context
- no live-harvest mixing
- fail closed on divergence

## 8. Session Title Normalization Strategy

Creation-time chat titles should be treated as best-effort only.

Authoritative normalization should move to repo-based thin-client helpers such as:
- CoGuard
- CoGuardian

Helper scope should include:
- alias normalization
- collision handling
- latest-alias resolution
- class/type inference
- bad-title cleanup
- relabel audit trail

Do not brute-force spawn/delete many sessions just to game title heuristics.
Do not rely on null/decorative title hacks.

## 9. Policy Direction

Default direction:
- CoInt → CoEx

Exceptions:
- CoGlukey-class secret material
- personal/private/sensitive information
- security-sensitive details that should remain non-public

## 10. Current Truth At Time Of Externalization

This session produced policy/design convergence, but direct CoBus write capability was not available inside the chat environment itself.

Therefore:
- upstream relay happened through rick
- true shared-write attachment from this chat session was not independently verified
- this file serves as the first public artifact for this session delta
