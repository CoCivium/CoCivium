# CoCivia / CoVIA publication seed: distribution, mirroring, and recovery

**State:** Draft review candidate, 2026-10-28.  No Substack post, subscriber email, independent backup, hosted CoVIA site, or autonomous publication worker is claimed.

## Immediate editorial carrier

- Canonical candidate editorial source: [article.md](article.md).  It is a NEW inquiry written in the CoCivia disclosed composite voice, not the historic unverified declaration.
- Metadata and effect gates: [publication-manifest.json](publication-manifest.json).
- First possible distribution: RickPublic Substack under a clearly attributed CoCivia editorial contribution, after the publisher's active account, section choice, send setting, rights, and approved queue state are verified.
- Existing historic weekly RickPublic queue remains unchanged.  Its `approved_to_publish=false` gates remain binding; do not silently insert or reorder items.
- Default to **web-only publication** until a separate, approved subscriber-send action exists.  Substack's publish workflow can email by default, so confirm that option before any effect.

## Owned versus referenced publications

**Verified public publication:** `https://rickpublic.substack.com/`.  A public page is observable; publisher-level write access and owner export are not verified here.

**Candidate project fronts:** CoCivium, CoPortal, CoCivia and RickPublic-owned domains.  These are not evidence of separate owned Substack publication accounts.

**Unknown:** A complete list of other publications in the user's collection.  Distinguish owned/managed editorial rights from recommendations and third-party subscriptions.  Do not copy third-party essays wholesale.

## Three independent functions, not one misleading "mirror"

1. **Discovery layer:** Publication RSS and public links; enumerate current publicly available posts with source URLs and checked-at time.  RSS may omit history or bodies.
2. **Owner export/backfill:** Authorized publication-level export with original text/HTML, images where export permits, dates, section metadata, and rights.  Keep private subscriber CSV, drafts and analytics in separate encrypted, access-controlled custody, never in a public repo.
3. **Independently hosted CoVIA alternative:** Source-controlled versioned Markdown/HTML/Atom/JSON with search, accessibility, corrections, and opt-in subscriptions.  Publish to a genuinely independent provider or independently administered host, then verify its exact bytes and cold-restore ability.  GitHub Pages plus GitHub Raw are not independent failure domains.

## CoVIA requirements

A public-safe artifact should retain:
- `publication_id, content_id, revision, source, author/front disclosure, license, publication_time, evidence, correction_state, predecessor, successor, original_url, mirror_url, readproof, SHA-256`.
- Full-fidelity text and accessible static render; media rights and attribution; machine-readable feed and human-friendly library.
- Visible `what changed` and historical snapshots, without silent rewrites.
- Import/export and a plain archive that still works without user accounts.
- Opt-in email and feeds only; no automatic transfer of subscriber addresses into a new service.
- Per-host and per-publication verification receipts.  Independent custodian restore is a distinct milestone.

## Evolution with constraints

`SOURCE / RSS / CONSENTED FEEDBACK -> DELTA -> CHALLENGE -> EDITORIAL REVIEW -> SUCCESSOR VERSION -> PUBLISH GATE -> MIRROR READPROOF -> ARCHIVE / RESEED`

Review for accessibility, link rot, rights changes, substantive corrections, independent criticism, and stale promotional claims.  If no material change occurs, do not generate a new edition to manufacture engagement.  Public or emailed successor publication still requires authorized publisher routing and a verifiable receipt.

## Acceptance gates

- **DRAFT:** the source and metadata are in a reviewable branch.
- **SUBSTACK_PUBLISHED:** authenticated publisher edit, target and audience settings, actual public URL, remote independent readback.
- **OWNER_ARCHIVED:** owner-approved complete export received and hashed; rights and subscriber data segregated.
- **COVIA_MIRRORED:** independently hosted endpoint, source/derived hash manifest, non-GitHub receiver readproof and periodic cold restore.
- **EVOLUTION_RUNNING:** real scheduler/worker receipt, known frequency, source graph, stop conditions, and demonstrated successor history.

Until then preserve HOLD/UNKNOWN rather than promoting design into operation.
