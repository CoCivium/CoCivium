# CoMail+ R0 | Fixed invitation ↔ living resource

**State:** `PASS_BOUNDED_OFFLINE_DEMONSTRATION__NOT_SENT__NOT_AUTO_PUBLISHED__NOT_RECEIVER_ACK`. This is a synthetic, public-safe, portable design/test donor for **existing** CoFree+, CoLivingHighlight+, CoPublication Federation, CoRelationshipBraid+, CoSubscription Ecology and CoEvergreen+ concepts. It is **not** a new email standard, email account, social network, donation service, installed X2 app or externally hosted endpoint.

## Open in thirty seconds

Open `index.html` locally, or on a properly configured local static viewer. It contains one **synthetic unsent** historical invitation, an exact stable resource identifier, three immutable hash-bound versions, a predecessor/successor comparison, and a local unsent feedback export. Selecting `v0` or `v1` means inspect that version. `View latest` selects `v2`. The static `feed.atom` illustrates optional independent change discovery; it does not register subscribers or issue notifications. Original/older snapshots remain available rather than being rewritten away.

The page performs no HTTP request, send, sign-in, keylog, subscription, payment or tracking. The feedback export occurs only on an explicit click. A downloaded local proposal has `effect=NONE`, `delivery=NOT_SENT`, and the exact selected source SHA-256. It is a proposal **to someone who might later separately read it**, not a delivered contribution.

## Reproduce

```sh
python3 build.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
# Run this only on a clean CoCivium repository checkout; it validates donor git blob pins:
python3 build.py --check --check-donors
# Optional browser acceptance (requires Chromium / Playwright):
python3 tests/browser_qa.py
```

`build.py` deterministically reconstructs `index.html`, `feed.atom`, and `receipt.json` from `fixture.json` and `template.html`. It never modifies past versions during `--check`, and fails on mismatching output. `fixture.json` forbids recipients, outbound URLs, payment endpoints, live subscriptions and artificial claims of sending. Any version modification without its matching content hash fails validation; a new version must be separately reviewed. Source docs are pinned to exact GitHub blob identities. This is a source pin, not an adoption or recipient ACK.

Initial isolated Python 3.13: **75/75 tests PASS**, with **37 positive checks and 38 named fault controls** (test inventory is authoritative). Isolated headless Chromium: **50/50 desktop/mobile interactions PASS**, with **2 direct `file://` navigation holds** due to the test approach/sandbox. Earlier false-negative QA fixtures (substring test and direct-navigation race) are preserved as scoped FAIL historical notes; corrected fixtures passed without relaxing the production contract. Independent CI/source readback remains a separate gate until actually performed.

## Why the note cannot itself evolve

Ordinary email is delivered as a historical provider message. A later updated website does not rewrite that original provider message and cannot prove a recipient read the current link. Model the two separately:

```text
FIXED_EMAIL / HISTORICAL_MESSAGE_ID / SENDER / RECIPIENT / SENT_RECEIPT
                             |
                             | stable RESOURCE_REF (not permission)
                             v
LIVING_RESOURCE_ID -> IMMUTABLE V0 -> IMMUTABLE V1 -> IMMUTABLE V2
                             |                        |
                 PER-VERSION HASH / TIME / WHY         + CURRENT POINTER
                                                       |
                                                       + CHANGE FEED
                                                       + READ / CHALLENGE
                                                       + REVIEWED SUCCESSOR
```

The synthetic fixture deliberately has **no sender, recipient or provider send receipt**. For a real message: verify sender mailbox and intended recipient identity, exact content/version, consent and delivery route before sending; differentiate `PREPARED`/`SENT`/`DELIVERED`/`READ`/`ACK`/`USED`. Neither a stable URL nor opening a webpage proves acceptance or a relationship. For a corrected/retracted resource, show explicit correction or retraction in the current pointer while preserving archived snapshots where lawful and safe.

## Evolution and audience boundaries

- **Free access:** content accessible without purchasing or donating, where rights allow. Free **access** is not a claim every third-party work is openly licensed or that contributors owe free labour.
- **Support:** no active donation link. A future actual support route requires identity, recipient allocation, accounting, privacy and applicable legal/charitable qualification; never imply a registered charity or tax receipt without proof.
- **Recognition:** opt-in attribution, credited edits, independent replication and acknowledged challenges; donations/fame are not truth votes.
- **Community feedback:** opt-in corrections, disagreement, translations, accessible renditions and new experiments. Feedback remains its own event and does not silently overwrite the resource.
- **Many receivers:** prospective academic, maker, journalist, educator, public-interest and philosophical projections can differ in explanation, not in provenance or authority. A cohort of 1,000 proposed academics is a *candidate relationship index*, not 1,000 subscribers or permission to email them.
- **G_d / ET / CoTheoryAll:** spiritual/fictional/hypothesis lenses remain explicitly typed. Shared symbols or resonant diagrams are not empirical proof.
- **CoTurtle∞+:** recursive candidate review is bounded by actual verification, time, compute, attention and uncertainty. AutoEvo may run periodic qualified checks, never silently grant itself send, payment, private-data or website-update permission.
- **Provider independence:** one living resource may have Atom, RSS, webpage, offline bundle, downloadable JSON, CoMap and CoOrb views, but every *actual* destination has a distinct publication/currentness/cold-recovery gate.

### Existing source contracts, verified source identities at prototype creation

1. [CoFree+ Evolving Publication Commons](../../docs/Architecture/COFREE_EVOLVING_PUBLICATION_COMMONS_R0_20261026.md)
2. [CoPublication Federation + Receiver Interest](../../docs/Architecture/COPUBLICATION_FEDERATION_RECEIVER_INTEREST_R0_20261025.md)
3. [CoRelationshipBraid+](../../docs/Architecture/CORELATIONSHIP_BRAID_FABRIC_R0_20261026.md)

`fixture.json` contains exact 40-character git blob pins. Historical precedents, not claimed protocol implementations:
- [RFC 4287, Atom Syndication Format](https://www.rfc-editor.org/rfc/rfc4287.html) for optional source-controlled change feeds;
- [RFC 7089, Memento](https://www.rfc-editor.org/rfc/rfc7089.html) for historical resource versions and time-based resource access;
- [RFC 8058, List-Unsubscribe one-click](https://www.rfc-editor.org/rfc/rfc8058.html) as a requirement to qualify **only if** actual bulk mailing/list subscriptions are subsequently deployed. No actual RFC 8058 endpoint or DKIM-signed list message exists in this demo.

## Human-time acceptance

For the first legitimate sender/reader pilot, measure one real **opt-in** recipient following a historical note to the current resource, comparing a predecessor, identifying a real correction, and recovering after a broken or expired pointer. Use exact provider send identity, consent and independent receiver-side evidence. Require hosted link safety, public-domain front-door correctness, privacy scan, rights, accessibility and actual feedback route qualification before release. `SOURCE_CODE_NE_LIVE_WEBSITE`, `POINTER_NE_ACK`, `EMAIL_NE_CURRENT_RESOURCE`, `DEMO_FEEDBACK_NE_COMMUNITY_ADOPTION`.
