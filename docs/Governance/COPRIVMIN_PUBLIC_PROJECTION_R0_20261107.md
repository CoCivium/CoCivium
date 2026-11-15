# CoPrivMin+ R0 | Public by useful projection, private by justified exception

**Status:** PUBLIC GITHUB **CANDIDATE** (branch/PR only until merged) · 2026-11-07 · Not a live release service, a legal opinion, a privacy-policy replacement, or permission to disclose another person's information.

## Why this exists

When an R&D project lives in private repositories, participants may not know it exists, what is being worked on, or whether a claim is real. A private artefact can be valuable to the commons **without its entire private payload being public**. This proposal makes *useful public discoverability the default aim* while restricting only the **specific facts, fields, relationships and effects** that have a legitimate reason to remain protected.

**Two minimizations apply simultaneously:**
1. **Minimize unjustified secrecy:** publish the widest *authorized, accurate, helpful* public projection, with sources and honest progress labels.
2. **Minimize unnecessary disclosure/collection:** never make a third person's private data, a credential or an unsafe operational detail public merely because it appeared in a CoCivium conversation or repository.

This is **not** “move a private file into a public repository, redact it later.” Git history, search caches, forks and notifications can preserve unintended disclosures. The public-safe projection must be prepared and inspected **before the first public commit or PR**.

## Four principal reasons to withhold a specific part

| Hold family | Examples that stay protected | What may still be safely public |
|---|---|---|
| **People and consent** | Personal/health/child/family information, confidential communications, learner profiles, unpublished human reviews, sensitive identity relations | A generic design principle, anonymized or synthetic example, consent model |
| **Security and abuse risk** | API keys, passwords, private infrastructure endpoints, precise defensive weaknesses, exploitable runbooks, live access paths | General safety architecture, remediation classes, dependency-free synthetic demonstrations |
| **Rights and obligations** | Non-public customer/partner information, copyrighted assets without licence, contracted confidentiality, privileged material, unapproved third-party names/logos | Original summary, correctly attributed public references, rights and licence requirements |
| **Unqualified consequential claims or effects** | Unsupported delivery/ACK, accreditation, adoption, scientific authority, live deployment, finance/legal commitments, safety certification, mass outreach | Accurate candidate status, failed test or limitation, proposed experiment, clearly scoped source/CI result |

These are **review categories, not a claim that every datum belongs in exactly one category**. Legal duties, national/regional rules, safety and real participant preferences may require additional constraints. A false-green assertion is often safer to *correct publicly* than hide; withhold the protected operational detail while preserving the truthful limitation.

## Three-layer publication pattern

**A. Public topic card where even existence is safe.** Disclose *what question is being explored*, a plain-language explanation, independent public sources, current evidence class, known challenge, and what has not been established. A source can remain private while a **sanitized public hypothesis** can be independently criticized. No private source URL, name or hash is required merely to make a card.

**B. A qualified public artifact.** Publish original documentation, clean room demonstration or safely synthetic test data that passes field-level rights/privacy/safety review. Show version, date, source class and actual test receipt. Never imply a GitHub Actions job represents an independent child, educator, native-device or public adopter.

**C. Protected residual.** Keep only the fields and source bytes for which disclosure would violate an actual interest or obligation. The private source is retained for legitimate custodians with permission; the public projection need not reference its name, repository path, count, hash, timing or even existence when such a pointer would itself disclose protected facts.

**No global “everything in a private repo must be published” rule.** An inherited private classification triggers examination for a safe projection, not permission to publish.

## Field-by-field decision contract

For each candidate field or claim, record privately, when possible:

`object_id | field_or_claim_id | source_identity_and_currentness | owner/consent_scope | risk_and_rights | disclosure_decision | public_transform | retained_private_reason | review_class | effect_authority | release_version | publication_destination | reader_accessibility | expire_or_recheck_event | receipt`.

Possible field outcomes:

- `PUBLIC_EXACT`: genuinely public-origin content with rights and correct claims, eligible for an exact public projection.
- `PUBLIC_SUMMARY`: original paraphrase retaining meaningful idea, with source status and relevant uncertainties.
- `PUBLIC_SYNTHETIC`: demonstrate the concept with invented data, not traceable to protected people/operations.
- `WITHHELD_EXACT`: keep identifiable/confidential details inside an actually authorized private receiver.
- `EXISTENCE_HELD`: even revealing that a particular case, individual, vulnerability, negotiation or file exists is unsafe or unauthorized.
- `UNRESOLVED`: disputed ownership, unclear consent, unresolved rights, or conflicting safety/evidence checks. **HOLD**, qualify/recheck; do not turn “unknown” into “absent.”

A public version can say **“some underlying details cannot be shared”** only when even that generic fact is appropriate. Never leak the number or titles of protected records by an overzealous transparency dashboard.

**Hash warning:** A SHA-256 digest of a low-entropy secret, personal identifier or short confidential text can enable equality tests, guessing and correlation. Do not publish private-source hashes/IDs without risk review. For genuinely public, non-sensitive bytes, digest + reproducible output is a useful integrity receipt.

## CoBestFront+ and CoExPublic+ relationship

Present **one best supported, accessible public explanation per question** and keep safely shareable earlier versions under History/Compare. Give truthful status and next verification target; avoid stacking candidate versions as competing “live” experiences.

Keep these transitions separate:

`PRIVATE_SOURCE -> FIELD_REVIEW -> SAFE_PUBLIC_CANDIDATE -> EXACT_RELEASE_AUTHORIZATION -> PUBLIC_GIT_REF/URL_READBACK -> [INDEPENDENT_READER_ACK_IF_OBSERVED]`.

A public GitHub branch or draft PR is **already publicly visible source**. It is not a merge to `main`, app deployment, independent public readership, CoEx, formal canon or evidence that the public can run a product.

**Owner approval for the exact consequential public effect remains necessary.** Broad enthusiasm for openness does not permit disclosing private messages, third-party data, unreleased security info or unreviewed statutory commitments. Reversible private drafts are not interchangeable with immediately discoverable public PRs.

## Good default tempo, without an uncontrolled autopublisher

For a future authorized publication workflow:

`DISCOVER PUBLIC VALUE -> CLASSIFY FIELDS -> BUILD ORIGINAL SAFE PROJECTION -> CHALLENGE RIGHTS/CLAIMS -> TEST WITHOUT PUBLISHING -> APPROVE EXACT PUBLIC PAYLOAD -> COMMIT/PUBLISH -> READ BACK EXACT DESTINATION -> LOG DELTA -> RECHECK ON STALE/REVOCATION`.

Choose a regular review cadence (for example, daily for low-risk candidate discovery, weekly for publication quality) **only when an actual scheduler, actor and budget exist**. Candidate generation may automate; **publication authority may not be inferred from the clock**. Keep the review queue explicit and avoid repeatedly asking the original proposer to manually relay the same content.

A public index should show real, safely discussable projects rather than a fabricated dashboard of omniscient all-project status. If a private tool, session or repository is unreachable, say `NOT_VERIFIED`, not `NOTHING_EXISTS`. Recover reliable evidence before changing a public claim. If a protected project cannot be disclosed at all, no entry is created.

## Example: education without exposing an internal research thread

An openly useful projection can describe CoAthene as a **candidate inquiry-first learning approach**: begin with why education matters, teach questioning and responsible action *alongside* literacy, numeracy and deep subject expertise, provide optional social Houses/Clans, cite educators' prior work, and promise neither school accreditation nor verified outcomes. The private research debate, individual messages, unreviewed partner contacts and draft technical work need **not** be copied, named or linked.

See the separately authored public candidate [Why have schools at all?](../Public/COATHENE_WHY_HAVE_SCHOOLS_R0_20261107.md), the existing [CoAll GitHub Evolution Fabric](../Evolution/COALL_GITHUB_EVOLUTION_FABRIC_R0.md), [CoFree Publication Commons](../Architecture/COFREE_EVOLVING_PUBLICATION_COMMONS_R0_20261026.md), [CoReviewSpine](COREVIEW_SPINE_R0.md), [CoPublication Metabolism](../Architecture/COPUBLICATION_METABOLISM_R0_20261025.md), and [security reporting policy](../../SECURITY.md).

## Nonclaims

`OPEN_BY_INTENT_NE_AUTHORIZED_DISCLOSURE` · `PUBLIC_TOPIC_NE_PRIVATE_SOURCE_COPIED` · `PRIVATE_EXISTS_NE_EXISTENCE_SAFE_TO_REVEAL` · `SHA_NE_PRIVACY_PROOF` · `PUBLIC_PR_NE_PUBLIC_SITE_RUNTIME` · `UNKNOWN_NE_ABSENT` · `EXACT_PAYLOAD_AUTH_NE_UNLIMITED_AUTH` · `PUBLIC_GIT_REF_NE_INDEPENDENT_READERSHIP`.

This R0 is a proposal for a **better default**, not a blanket declassification power or an automatically deployed redactor.
