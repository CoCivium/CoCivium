# CoArtifactPublication+ / CoPublicStem+ R1 | Public-safe default, canonical filenames

**2026-11-12. State:** PUBLIC SOURCE CANDIDATE, not a CoAll runtime, system-wide session policy, or authorization to upload private content.

## CoDecision

For CoCivium work, default to **publicly discoverable artifacts when content is safe and approved for public release**. That is distinct from making every session's raw outputs public. A small private conversation export, local hardware log, credential, unpublished partner draft, or child/guardian record must not become public merely because a prompt said "all".

**One logical artifact has one canonical versioned stem.** Reuse that stem for the native XLSX, interoperable CSV, README, and manifest; do not assume filename equality means byte equality. Compare SHA-256 and Git blob, keep the predecessor immutable, and require explicit supersession if there is a collision.

The reference implementation this cycle is **[CoTalkItOut R1 public workbook](https://github.com/CoCivium/CoCivium/blob/main/docs/CoLocal/CoTalkItOut_Headless_Screenless_Autonomy_R1_20261112.xlsx)**, with [CSV](https://github.com/CoCivium/CoCivium/blob/main/docs/CoLocal/CoTalkItOut_Headless_Screenless_Autonomy_R1_20261112.csv), [manifest](https://github.com/CoCivium/CoCivium/blob/main/docs/CoLocal/CoTalkItOut_Headless_Screenless_Autonomy_R1_20261112_MANIFEST.json), and [exact publication receipt](../../ai/currentness/cotalkitout-publication-r1-20261112.json).

## CoGlyphRail+

1. Classify content and rights. **UNKNOWN / PRIVATE / RESTRICTED → hold private**.
2. Redact only by authorized, auditable transformation, retaining a private predecessor pointer.
3. Bind WorkID, canonical versioned stem, source hash, provenance, audience and intended receiver.
4. Elect one public landing path, perform a no-clobber collision and current branch-head preflight.
5. Write with an expected-head lease. Retrieve and independently compare committed blob identities.
6. Index the public path for future authorized readers. **Discovery does not notify active sessions**.
7. Require receiver-origin exact-object readproof for `PICKED_UP` and separate product acceptance for `INTEGRATED` or `COEX`.
8. Preserve permissions, rollback, source lineage, and uncertainty across supersession.

## CoGlyphList+ / inversions

- Public-safe original vs private source, redacted derivative and withheld provenance.
- Same filename vs different bytes; same bytes vs different semantic context.
- Many writing sessions vs one elected public object owner.
- Last-writer-wins vs explicit collision, provenance comparison and successor election.
- Public repository file vs usable user-facing product.
- Published pointer vs actively notified, independently reading receiver.
- Recursive publication validators vs bounded cycle-stopped review.

## Currentness

Machine-readable [policy](../../ai/publication-contract-r1.json) is a candidate adoption target. Its presence does not prove that 30 active chats read it, that every public artifact is synchronized, or that a private CoStead receiver has accepted it.

**Next safe proof:** One authorized subsequent session must resolve this public artifact by canonical name, compare the SHA and report a bounded receiving result, without manual copying of source content.
