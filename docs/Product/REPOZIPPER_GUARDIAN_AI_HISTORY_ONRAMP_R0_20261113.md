# RepoZipper+ / CoGuardian+ AI-history intake R0

**Date:** 2026-11-13  
**Status:** OFFLINE SOURCE PROTOTYPE, SYNTHETIC TESTS; NOT ACCOUNT DATA INGESTION, DEPLOYED UX, COMPLETE RESTORE, PUBLIC WEB SERVICE, CANON, OR ACCOUNT DELETION.

## Why this exists
Many people have years of work in one or more legacy AI providers. CoCivium should offer a **portable, optional, local-first onramp**, not demand users move providers, upload sensitive histories, create an account, or trust a new custody service before receiving value.

This extends [RepoZipper / CoPlatformHelper R0](COPLATFORM_HELPER_ECOLOGY_REPOZIPPER_R0.md) (the earlier merged product-family contract) and [CoGuardian StateTruth v0](../COBUS_LITE/guardian/CoGuardian_StateTruth_v0.md). It reuses existing [CoEvidenceReceiptGuard R0](../Architecture/COEVIDENCE_RECEIPT_GUARD_R0.md), [CoCivia First Use](../Onramp/COCIVIA_FIRST_USE_R0.md), [CoSessionAutocycle](../Architecture/COSESSION_AUTOCYCLE_R0.md), and CoLUE+ maintenance/portability rails. Prior exact RepoZipper program/source lineage is still not fully recovered; do not treat this adapter as the original source project's successor without reconciliation.

## Product packaging / optionality

**One core adapter, multiple replaceable projections:**
- CoModule: pure local ZIP inspection and provider-specific parser adapters.
- Standalone productlet: no-account, no-cloud, self-contained private tool usable without CoAll.
- CoBar / RickBar: one calm import / count / inspect / recover / exit card, only when native UI and first-use behavior are verified.
- Optional local web UI: localhost, explicit bind and access controls, no account.
- Hosted service: **not authorized for private export upload** until encryption, retention, consent, breach response, deletion and independent security review are qualified.
- CoGuardian: protect raw bytes, verify recovery across independent failure domains and lifecycle; **file existing != backup proven**.
- CoSession: source-preserving WorkID and obligation reconstruction, not recreation of model hidden state.

## Actual R0 interface

`examples/repozipper/ai_history_intake_r0.py` takes `--zip <LOCAL_ZIP> --out <NEW_PRIVATE_DIRECTORY> --mode inspect|census`.

- `inspect`: SHA-256 of exact input ZIP, bounded ZIP member metadata, identify a single `conversations.json` candidate. No extraction.
- `census`: stream top-level JSON conversation objects one at a time, require string IDs, preserve only keyed HMAC identifiers, timestamps and per-conversation message-node counts in a **private** SQLite file. Output a numeric and provenance receipt with unknown-account coverage explicit.
- No credentials, cookies, browser tab access, outbound network, account export request, provider session deletion, or public private-content upload.
- Unknown format, missing/duplicated records, suspicious ZIP traversal, ambiguous source candidates, and duplicate outputs must **HOLD**, not be reported as zero or repaired silently.
- File paths and raw conversation text must never appear in routine stdout/release artifacts. **Never commit a real export, secret key, local SQLite DB, or private receipt to GitHub.**
- Results are structural evidence of export contents only: **not** full provider account census, semantic ingestion, independent backup, receiver ACK, or delete-safe.

## Uncertainties / next qualification

1. Actual OpenAI/ChatGPT export schema, huge ZIP size and all attachments unknown. R0 is tested on synthetic `conversations.json` arrays; another export format requires a separately qualified adapter.
2. Large single conversations above a 64-million-character bound fail explicitly, not silently dropped. Memory and decompression resource tests with sparse/large synthetic exports remain necessary.
3. The HMAC index deliberately does not include conversation titles or raw text. Search and semantic CoWork reconstruction need a new **private, consent-scoped** derivative layer, not an automatic GitHub upload.
4. An original export saved on X2 is local working custody. Independent durable copy must be separately hashed and cold-restored before CoGuardian calls it a backup.
5. Local SQLite is **not encrypted at rest by this code**. Use device/full-disk encryption, permission-scoped output directories and controlled private storage; do not assume a Windows ACL from POSIX mode 0600.
6. Real provider export arrival, account-level count, attachment completeness, explicit per-conversation delete approval, and X2 CoBar UX acceptance remain **UNPROVEN**.
7. When available, inspect original ZIP read-only, verify exact receipt and scope, run supported census, compare metadata against the existing CoSession shadow ledger, then independently rehydrate **one consented, non-sensitive** WorkID.
8. A ZIP parser is not a security boundary against a compromised host. Full review (ZIP bombs, symlinks, encodings, race conditions, filesystem ACLs and long-running resource ceilings) is required before broad release.
9. Benchmark using a corpus with 0, 1, 1,001 and 100,000 synthetic conversations, duplicated IDs, uncommon Unicode, long nested mapping graphs, malformed exports, and memory/RAM monitoring; CI green on tiny fixtures cannot replace this.

## Session failure survival / collaboration

**Public successor entry:** this repository's RepoZipper R0 branch and draft PR. Fresh sessions/workers can fetch *source*, check exact Git head/CI, reuse source-bound notes and collaborate through bounded PR reviews. **No claim that another ChatGPT conversation automatically wakes, has read this, or acknowledges delivery.**

**Work object:** `RepoZipper.AIHistoryPortability.R0`.
**Next elected safe deed:** observe CI, fix any deterministic regression, then locally run synthetic large-input tests before touching any actual account export.
**RickAction:** when the provider's export email arrives, download **original ZIP** to X2 Downloads; don't paste transcript contents. This may not be feasible for every workspace/export channel.

**Qualifying user journey:** `Select local ZIP -> see covered conversation count + incomplete/unknown warnings -> choose one safe recoverable project -> verify independent cold restore -> optionally stay with original provider, move to CoBar, or export to third party`.

**Stop/recursive invariant:** source-bound useful gain > new upkeep. Otherwise quiesce. One elected mutator per shared source, many read-only verifiers. Privacy and provider deletion gates remain human-controlled.

`EXPORT_NE_ACCOUNT_COMPLETENESS | ZIP_NE_BACKUP | HASH_NE_SEMANTIC_RECOVERY | PROVIDER_SESSION_NE_WORKID | DRAFT_NE_RELEASE | ACK_NE_ACCEPTANCE | FREE_EXIT_NE_FORCED_ONBOARDING`
