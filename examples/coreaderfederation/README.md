# CoReaderFederation+ R0: the trillion-option router (bounded reference)

**State:** `PUBLIC_SAFE_DRAFT_CANDIDATE__NO_LIVE_SUBSTACK_OR_READER_TRACKING__NO_AUTOMATED_PUBLICATION`

## What this adds to existing CoBook+, CoLivingHighlightAsset+ and CoInterestField+

This is a thin deterministic **reader-choice projection**, not a new publication database or second source of truth. Source documents, Git provenance, historical versions and currentness remain owned by existing CoBook / CoSourceGraph / highlight systems. Surfaces (Substack, sites, CoAcademy, media, agent-readable cards) would **project** published source objects with explicit status, not become separate canons. A current GitHub `main` link is a pointer, and the captured git blob SHA is a source identity, not a promise of immutable one-click historic retrieval.

- User explicitly selects interests, audience, output format and update mode. Zero inferred identity, cookie, read tracking or newsletter enrollment.
- Five existing public GitHub documents form a bounded sample. **None is claimed to be a live Substack article.**
- Ranking uses an inspectable deterministic formula: `10 × shared topics + 3 × matching audience + 2 × matching format`; ties break by ID.
- Each output retains source identity and nonclaims. No runtime fact-checking, crawl, push notification or live diff is performed.
- The chosen reader session never silently rewrites its observed article. A newer version would appear as an available successor with preserved prior version and a source-bound visible diff.

## Does this create one trillion pages?

No. `12` possible personalization/representation axes with `10` hypothetical values each give **`10^12 = 1,000,000,000,000` raw configuration tuples**. The real current catalog has **five** source entries. Most theoretical combinations are redundant, incompatible, unhelpful or not permitted. The catalog records the `10^12` count as **illustrative capacity only**, not deployed pages, generated roles, agents, checked combinations, human readers or observed demand.

Only calculate the small set needed at the moment of a consenting reader's request. Cache by public source version, explicit selections and projection recipe, within source privacy boundaries. Recompute only when a relevant verified source changes. The actual number of *useful* projections must be measured.

## How fading, freshness and scarcity should work

| Feature | Correct behavior | Forbidden shortcut |
|---|---|---|
| Article correction | New source version, visible diff, last-seen version recoverable | Silent rewrite while reader is reading |
| Superseded article | Permanent historical reference and successor pointer | Erase the past or deliberately break links |
| Real limited-time offer | Verified start/end, evidence, explicit CTA, archive still accessible | Invent a countdown or pretend ordinary facts expire |
| Temporary live event | Event time, timezone, enrollment capacity, actual closure | False scarcity |
| Reader engagement | Consent-based topic choices, anonymous aggregate where feasible | Fingerprinting, hidden behavioral scoring or automatic lists |
| Cross-channel fanout | Publish only after approval, receipt and destination-specific permissions | Broadcast to every subscriber/node/account |
| Reader feedback | Separately triaged challenge, evidence and editor-controlled revision | Reading itself automatically changes the source |

Marketing urgency is earned by *actual* deadlines, new findings, useful events and genuine community participation. **Virality cannot be assured.** Optimize for first-use completion, comprehension, voluntary returns, sharing with attribution and substantive challenges, not outrage or disappearing sources.

## Run it without any model or account

```sh
python3 examples/coreaderfederation/route.py --interest publishing --audience curious --format brief --mode SNAPSHOT --as-of 2026-10-25T00:00:00Z
python3 examples/coreaderfederation/route.py --interest evidence --audience researcher --format technical --mode DIFF_AVAILABLE --as-of 2026-10-25T00:00:00Z
python3 -B -m unittest discover -s examples/coreaderfederation -p test_route.py -v
```

Outputs are JSON route previews. They create no subscriber account, article post, e-mail, AI call, server state, analytics event or agent session. An optional genuine time-limited offer must declare timezone-aware start/end, evidence URL and archival URL; an expired offer disables **only its CTA**, not the underlying article.

## Near-term receiver experiments

1. **Journalist:** 60-second verified thesis → source and counterclaims → current status → challenge route.
2. **Developer:** usable tool or code example → tests → issue / contribution route → model-neutral instructions.
3. **Educator:** plain-language projection → accessible alternate format → reproducible classroom challenge.
4. **Researcher:** precise claims → citations → falsifiers → immutable predecessor / successor.
5. **AI reader:** structured source references and claim ceilings, not permission to scrape private context.

Run a **five-person consenting first-use** test on one accessible front door, measure time to first useful action and independent ability to recover a previous version. Do not claim adoption, engagement lift, click-through or ROI before observations.

## Integration boundary

The prototype fits the existing:
- `docs/Architecture/COBOOK_LIVING_RICH_MEDIA_SYSTEM_R0_20261025.md`
- `docs/Architecture/COLIVING_HIGHLIGHT_ASSETS_R0.md`
- `docs/Architecture/COSUBSCRIPTION_ECOLOGY_R0.md`
- `docs/Strategy/COFIREWORKS_FRONTDOOR_CULTURESUBSTRATE_R0_20261024.md`
- `docs/publishing/series/rickpublic_substack_seed_v1/AUTOMATION_WORKFLOW.md`

Do not edit their authority, change Substack approval states or auto-deploy sites based on this draft. The broader eventually federated environment may add Claude, local FOSS models, accessibility renderers and alternate substrates, but these are independently qualified adapters, not limitless shared context or universal ongoing execution.

`PROJECTION_NE_SOURCE` | `READER_INTEREST_NE_CONSENT` | `SCARCITY_NE_MANUFACTURED_PRESSURE` | `EXPIRED_CTA_NE_EXPIRED_HISTORY` | `PUBLISHING_NE_VIRALITY` | `DRAFT_NE_RELEASE`


## CoMail+ R0 | Historical message, living referenced work

**Dependent donor for CoReaderFederation PR #271; synthetic-only.** [mail_envelope.py](mail_envelope.py) composes a source-labelled read-only projection from a **fixed message hash** plus a small, explicitly elected **living source version graph**. It is not an SMTP/IMAP adapter, web host, native desktop program, mailing service, newsletter, subscriber tracker, autonomous correction sender, or new source-of-truth store.

The [public synthetic fixture](mail_fixture.json) intentionally has:
- one fixed **SYNTHETIC_NOT_SENT** message, source version v1;
- a reviewed successor v2 and corrected successor v3;
- an alternative fork v2b, **not** silently promoted to the current pointer;
- a declared current pointer v3 with **no fetched independent HTTP/currentness proof**;
- zero real addressees, provider receipts, messages, source mutations or notifications.

Explicit reader projections:
- **PIN:** preserve the historically offered v1 identity and metadata. A real historical content fetch is separate, subject to continued rights and exact-byte proof.
- **FOLLOW:** propose the elected v3 resource pointer. This does not send notifications or change the original message bytes.
- **COMPARE:** show declared differences along the v1 to v3 lineage, with *verified_diff=false* until independently checked.
- **CORRECT / RETRACT:** a correction warning is visible even in pinned mode. A retracted current resource yields a tombstone, not a fake recall of the original email. Material safety/legal corrections may still require separately authorized recipient notification; a link alone does not prove notice.
- **FORK:** preserve v2b as an alternative, not the recipient's implied endorsement or the current elected successor.

Run locally with Python standard library only:

    python3 examples/coreaderfederation/mail_envelope.py
    python3 -B -m unittest discover -s examples/coreaderfederation -p 'test_*.py' -v

The output is **synthetic local JSON**. The fixture's 64-character source hashes are test values, not real Git blob checksums, and its allowlisted public source link is a pointer, not an independently verified snapshot. For a real correspondence edge, validate the **actual From/To/Cc/Bcc/body and source versions** under the separate privacy-protected [CoWHO↔WHOM gate](https://github.com/CoCivium/CoSteward/pull/290), then require an actual effect permission, delivery receipt and independent recipient-side read when relevant. Do not publish recipient identities in this public fixture.

The sent message cannot be changed retroactively. The living target may change, but historical version meaning and reader agency survive it.

**CI acceptance:** preserve the existing 17 route tests; add 35 CoMail negative/evolution checks in the existing reader-federation CI. Source and CI PASS never establish a sent message or subscriber uptake.

\`STATIC_MESSAGE_NE_LIVING_SOURCE | POINTER_NE_RECEIVER_ACK | FOLLOW_NE_AUTO_OPTIN | CORRECTION_NE_NOTICE_DELIVERED | RETRACTION_NE_RECALL | FORK_NE_CANON | PUBLIC_DECLARATION_NE_RIGHTS_VERIFIED\`.
