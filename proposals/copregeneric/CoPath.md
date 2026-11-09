# CoPath+ | Front-independent entry and recovery procedure

**Status:** Public proposal, not deployed coordination infrastructure.

## Route A: Discover

1. Retrieve `CoSeed.json` via this public repository's proposal branch.
2. Inspect `status`, `authority`, `source_branch` and explicit unverified gates.
3. Retrieve the technical proposal at the relative `technical_proposal` path.
4. Verify that the referenced content and version actually resolve. Record retrieval time and file/commit identity.
5. If a path fails, mark `HELD_UNRESOLVED_POINTER`. Do not repair by inventing a replacement URL.

## Route B: Contribute without overwrite

1. State the receiving front, source identity, access class and why the delta matters.
2. State the prior version/hash and relation type (`SUPPORTS`, `CONTRADICTS`, `SUPERSEDES`, `PREDICTS`, `FALSIFIES` or `REQUIRES_FOLLOWUP`).
3. Attach evidence and independent counterevidence; do not infer independent replication from copied inputs.
4. Submit a separate candidate change or reviewable branch; never overwrite canonical materials by assumption.
5. Record a receiver acknowledgment only when that receiver confirms the exact version and effect boundary.

## Route C: Retroactive CoEcho+ reconciliation

- **Backward:** current verified heads to accessible historical anchors.
- **Forward:** oldest accessible receipt to present claims and predicted outputs.
- **Sideways:** match deduplicated artifacts, dependencies and competing interpretations across fronts.
- **Gaps:** `INACCESSIBLE`, `UNVERIFIED_POINTER`, `PRIVATE_HOLD`, `POSSIBLY_MISSING`, `INTENTIONALLY_EXCLUDED`.
- **Recovery test:** prove at least one fresh reader can reconstruct source and status without the original chat.
- **Disposition:** `INTEGRATED`, `HELD_WITH_POINTER`, `SUPERSEDED_WITH_LINEAGE`, or `UNRESOLVED`.

## Route D: Human, machine and exploratory projections

Machine readers: use the typed JSON seed and versioned relations. Human readers: use the README, technical proposal and their source links. Future diagrams/audio/megascrollers must declare source IDs, translation loss and evidence boundaries. A projection is not an independent source.

## Route E: Promotion gates

This branch is not `CoTru+` canon, a live receiver or a verified website mirror. Promotion requires distinct authority, evidence, privacy and receipt checks. No automatic background operation follows from this document.

**Next actionable gate:** Have a real front retrieve and acknowledge this seed with its commit/ref and declare what, if anything, was integrated.
