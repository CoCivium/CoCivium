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
