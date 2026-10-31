# CoBeacon+ | One Useful Door R0

**State:** CANDIDATE_BRANCH__SOURCE_VERIFIED_ONLY__NOT_DEPLOYED__NOT_RELEASE__NO_RECEIVER_ACK  
**Observed:** 2026-10-28  
**Bound:** A 12-entry sampled catalog, **not a complete inventory of CoCivium**.

## What is here

- `index.html`: a standalone, privacy-preserving task chooser (no account, network calls, cookies, local storage, telemetry, third-party scripts, automatic action or installer).
- `../../ai/beacon/experience-catalog-r0.json`: exact 12 public GitHub source paths, blob SHA-1 identities, editorial priority and strict presentation/receiver/installer states.
- `check.py`: Python standard-library validator for catalog schema, HTML parity, source URL constraints, accessibility structure and nine negative cases.
- Scoped `.github/workflows/cobeacon-useful-doors-r0.yml`: PR/push local checks, plus **weekly read-only GitHub Raw source-identity drift watch**. No automatic deployment, publication, source rewriting or outreach.

The front door intentionally embeds a copy of the catalog so it can open offline. This **embedded copy is checked for exact parity** against the separate JSON file in CI. No browser fetch is needed.

## Choose an experience, not a product name

Default: **Bring one thing you want to improve**. Optional choices: **Try**, **Explore**, **Learn**, **Build**, plus a search field. Every card links to source, not a supposed installed or live service. External links are outside this page's no-tracking claim.

## Prioritization, with qualitative gates before scores

1. **P0: Trust and arrival.** Fix the publicly observed custom-domain routing and privacy/currentness mismatch, with real external TLS/HTTP and rollback checks. Use existing GitHub Start Here fallback meanwhile. No fake "working site" claim.
2. **P1: One useful action.** CoCivia first-use guide and the CoPreCursor reversible demo; require actual first-use outcome and comprehension.
3. **P2: Show the work.** CoLens+ Map/Orb/Text, CoOrb First Look, visual source cards and one **fully reviewed, captioned short film**. Reuse genuine CoMedia masters; do not present private narrated prototypes as public releases.
4. **P3: Reproducible builders.** CoStretch/CoTurtle benchmark, CoAttractor resource finder and machine-readable index. Require exact reproducibility and plain-language promise.
5. **P4: Education and research.** CivicLens, CoPlay, lessons, correction routes and inspectable dissent. Keep fictional and scientific states separate.
6. **P5: Qualified federation.** YouTube and Shorts, RickPublic/Substack, owned website, RSS/Atom, educational partners, optional PeerTube/owned-player, media/print/audio and emerging WeTube adapters. Each needs real destination, rights, accessibility, consent, platform compatibility and an exact effect/receiver receipt.
7. **P6: Installer/executable. HELD.** No claimed public CoCivium Windows installer or device runtime. The promotion requires signed/reproducible build, version, hash, anti-malware/security review, permissions, install/uninstall, rollback, accessibility, telemetry/privacy declarations and independent device acceptance.

This order is **editorial**, not a measured ranking or conversion forecast. Do not multiply weak signals by a million social surfaces.

## One content identity → many honest projections

`SOURCE_ID + RIGHTS + CLAIMS + VERIFICATION -> (TEXT | VISUAL | AUDIO | VIDEO | INTERACTIVE | DEMO | EDUCATION | SOURCE | MACHINE_TWIN) -> CHANNEL_ADAPTER -> RECEIVER_EVENT -> CHALLENGE -> VERSIONED_SUCCESSOR`

- **Find:** source-bound capability registry and prior-art search
- **Qualify:** rights, privacy, source-identity, effect ceiling and receiver utility
- **Select:** first-use value, evidence, reversibility, low friction, accessibility, media fit and cost. Use existing `CoExperimentSelector+` Pareto/reserved lanes for later evidence-based selection, not arbitrary pseudoscientific marketing scores
- **Produce:** a master with captions, readable screenshots, original/sourced audio, alternate text and a clear ending. Share accessible versions, not a random spray of derivatives
- **Beacon:** one current pointer per concept, with immutable historical editions, clearly labeled WIP and optional redirects, rich results where supported
- **Receive:** measure actual voluntary first-use success, time to useful result, comprehension, accessibility, source-check ability and willingness to return
- **Evolve:** cite receipt, track exact predecessor, propose a scoped PR after a material improvement; do not silently rewrite source meaning.

### Suggested source-backed exposure surfaces

- GitHub source, README and machine index: **source readback available**.
- Owned custom domain: **hold public discovery campaigns** until verified externally and corrected.
- CoAcademy browser/Pages: source exists, but **independent served-URL/browser acceptance is not established by the catalog**.
- YouTube: 2026-10-26 screenshot observed one public video in one Studio view. Not channel-wide analytics or a new upload. One reviewed film and a real receiver playback before any broad video series.
- WeTube: **candidate only**. Do not assume an operating federated platform. An owned player or standards-based PeerTube adapter may be evaluated with consent and preservation contracts.
- RickPublic/Substack: **existing publisher surface**; use approved publishing queue and actual post URL verification, not presumed API automation.
- RSS/Atom, translations, accessibility packs, podcasts, education and approved partner embeds: adapters proposed, not all deployed.
- Local executable: **HELD** until signed release evidence.

## CoAwards+ recognition relation

[Proposed awards criteria](../../ai/beacon/awards-criteria-r0.json) adds twelve **candidate recognition categories**, not twelve issued awards. They span reproducible proof, repairs, useful dissent, accessibility, education, media craft, commons, bridges, continuity, generosity, resource-wise design and non-obvious better alternatives.

The role of awards in beaconing is to **help others find evidence-backed contributions and learn from them**, not manufacture status or reward clicks. Each future award would reference an immutable source/version, contextual evidence, accountable review, limitations and an accessible media/text twin.

Stages: `SUGGESTED -> NOMINATED -> QUALIFIED -> REVIEWED -> CONSENTED -> ISSUED -> REVISED_OR_WITHDRAWN`. No active nomination endpoint, issuer, recipient, prize, or award issuance is represented by this R0 draft. Recipients may decline or request correction. Financial contribution, popularity or social reach cannot buy an award. A prize has no governance, scientific, professional or operating authority.

Run the opt-in recognition policy check:

```sh
python -B examples/cobeacon_useful_doors_r0/check_awards.py
```

The checker rejects synthetic award issuance, fake availability, missing consent, purchased rankings, auto-publication and missing nonclaims. It does not substitute for human or independent receiver acceptance.

## CI and currentness

Run from repository root:

```sh
python -B examples/cobeacon_useful_doors_r0/check.py
python -B examples/cobeacon_useful_doors_r0/check.py --remote
```

The second command makes at most 12 bounded read-only HTTPS GET requests to `raw.githubusercontent.com`, computes Git blob SHA-1 from source bytes and compares with the catalog. It uses no credentials and performs no writes. If a blob changes, the scheduled check **fails closed**. A failure does not authorize auto-updating the catalog, changing semantic pointers, sending notifications, launching agents or promoting a newer file to truth.

This check cannot establish reader comprehension, public-domain TLS health, app accessibility, YouTube publication, off-provider durability or first-person acceptance. A PASS means only scoped source/structure checks passed.

## Provenance and relation

Reuses:
- [CoCivium Start Here](../../START_HERE.md)
- [Six specialist routes](../../ai/onramp/specialist-entrypoints-r0.json)
- [CoFireworks readiness](../../docs/Launch/COFIREWORKS_READINESS_R0_20261024.json)
- [CoLivingHighlight+](../../docs/Architecture/COLIVING_HIGHLIGHT_R0.md)
- [CoPublication Federation](../../docs/Architecture/COPUBLICATION_FEDERATION_RECEIVER_INTEREST_R0_20261025.md)
- [CoFree+ publication commons](../../docs/Architecture/COFREE_EVOLVING_PUBLICATION_COMMONS_R0_20261026.md)
- [CoReviewSpine+](../../docs/Governance/COREVIEW_SPINE_R0.md)
- [Existing CoGoAll Evergreen CI](../../.github/workflows/cogoall-evergreen-blast.yml)

**No new global supervisor**. CoBeacon is a discoverable projection over existing evidence and publication machinery, not CoAll canon, a permanent worker or new external contact authority.

## Acceptance to promote

1. Current custom-domain or owned-subdomain **external readproof and privacy/security review**, distinct from GitHub.
2. One consenting unfamiliar reader independently follows a card, finishes a genuinely useful action and reports a source/version-bound result. A screenshot or click is not completion.
3. One offline self-contained HTML page is opened, read and safely exited on a real representative phone/desktop browser; keyboard and assistive-technology review.
4. One public-safe, rights-qualified film can play with captions and text alternative, with actual published destination and playback receipt if authorized.
5. A separate independent failure-domain owner restores an edition using its immutable content manifest, not a GitHub Raw/Pages alias.

## Rails

`ONE_VALUE_BEFORE_TWELVE_DOORS` · `SOURCE_NE_HOSTED_PRODUCT` · `PUBLIC_NE_ADOPTION` · `MACHINE_INDEX_NE_ENDORSEMENT` · `DOWNLOAD_NE_INSTALLER` · `SIGNED_NE_SAFE_WITHOUT_REVIEW` · `VIEW_NE_COMPREHENSION` · `VIDEO_NE_BROADCAST` · `WE_TUBE_NAME_NE_DEPLOYED_SERVICE` · `MASSIVE_PREPARATION_NE_MASSIVE_SENDS` · `LOCAL_IS_NOT_LANDED` · `VALIDATION_IS_NOT_ACCEPTANCE` · `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.
