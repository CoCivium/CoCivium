# CoEvergreen Federation R0 | one first step, many optional paths

**Status:** Offline, static, public-safe research candidate. No Substack publication, social posting, subscription, account creation, active automation, external polling, inferred reader identity, or deployed server is represented by this package.

## First use

Open `FederationReader.html` locally. Select any of the six public-source paths. Finish the initial editorial sample or click **Check for sample update**, then **Compare editions** or **Open edition 2**. The older edition remains available. The links to GitHub require a deliberate click; the page makes no background requests.

The content is freshly written sample editorial text, **not a claim about actual live publications or verified user outcomes**. `routes.json` pins six source blobs read via the GitHub connector on 2026-10-25. File references link to current branch content and include the frozen blob identity separately; current links are not guaranteed immutable permalinks. A later public publisher should use release/commit-pinned URLs for true historical links.

## What this is solving

One *canonical editorial work object* can be represented as:

- a frozen versioned article / citation;
- a short task-specific first-use page;
- an opt-in topic newsletter or RSS feed;
- an accessible text- or graph-centered reading surface;
- a historical correction / challenge record;
- a reader-selected, not inferred, specialist view.

These are **views and delivery preferences**, not separate legal entities, domains, personas, users, paid accounts, or worker permissions. A fictional idea index can be very large with almost no active compute.

## One publication, several optional sections

Substack supports **Sections**: multiple newsletters within one publication, with selectable subscription preferences. For a controlled first test prefer one existing publication with **at most 2–3 narrowly defined, opt-in topics**, rather than many accounts or copied mailing lists. Do not check **Add new subscribers by default** or **Copy your email list** merely to inflate a topic audience. The actual section settings, owner credentials, editorial approval, subscriber consent and remote publication remain **NOT RUN**.

The existing CoCivium RickPublic queue (`docs/publishing/series/rickpublic_substack_seed_v1/queue.json`) was read from GitHub; all four items had `approved_to_publish: false`. Its browser poster is a stub. This kit **does not modify the queue or publish its articles**.

Candidate initial editorial sections, **not created**:

1. **Try One Thing**: one useful beginner action, nontechnical, weekly at most after consent.
2. **Prove or Disprove It**: reproducible results, counterexamples, limits and corrections, preferably periodic.
3. **Build or Fork It**: implementation, source, recovery and interoperability for opt-in builders.

More specialized subjects (civic, visual, game, scientific, accessibility, careers, education, open-model substrates, etc.) should remain topical tags or local reader-filtered views until sustained demand is independently observed.

## Two URLs, two contracts

- `latest`: a mutable **pointer** to an explicitly labeled current edition. May be updated only after a new release is verified.
- `editions/<version-or-hash>`: immutable snapshot with source identity, edition time and corrections. Never disappear simply because readers progressed.

An email is a **snapshot**. Do not pretend an already-delivered email can be silently updated everywhere. Append a correction notice and link to a permanent revised edition. If a publication is removed for privacy or legal reasons, show a truthful tombstone as permitted; do not promise perpetual storage when deletion is required.

**Version update rule:** retain the old text, show *new edition available*, let the reader compare, then require an explicit choice to switch. Do not create fake scarcity by expiring sources, countdowns, artificial broken links or unreadable historical pages. Real deadlines may be displayed when the underlying source supports them.

## The combinatorial explorer

`federation.py` defines **16 bounded descriptive axes** including route, audience, format, evidence, accessibility, time, versioning, privacy and feedback. Mixed-radix indexing gives exactly **8,427,641,241,600 logical configurations**.

`python3 federation.py` generates 1,000 seeded, unique candidate descriptions in `output/candidate_1000.jsonl`, plus their status distribution. Some combinations are incoherent, unsafe or require unavailable tools. They are marked `HOLD_*`; the rest are **ideas only**, not verified marketing campaigns, readers, delivered newsletters, or commercially meaningful leads. The heuristic score is a transparent convenience, **not a learned model**.

## Trust boundaries

`SOURCE_READ_NE_HOSTED_PRODUCT | LINK_NE_READ | EMAIL_SENT_NE_PRIMARY_ACK | REVISION_NE_DELETION | READER_CHOICE_NE_PROFILE_CONSENT | SCORE_NE_VALUE | LARGE_SPACE_NE_COMPUTE`

- No background tracking, telemetry, browser storage, subscription form, third-party script, server-side feed listener or account connector.
- No inferred personalization. Reader selects interest explicitly. No silent sharing of raw context between routes.
- No auto-publish, auto-send, payment, artificial referral rankings or message bombs.
- No detached worker fleet, million browser sessions or performance claim.
- Semantic and philosophical / G_d / CoSpirit lanes can be represented as hypotheses or metaphors but not promoted as measured mechanisms.
- A link to GitHub is evidence of a source **pointer**, not a receiver's visit or endorsement.

## Tests

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_reader.cjs
python3 federation.py
python3 build.py
python3 verify_evidence.py
```

Python tests prove arithmetic, deterministic sample generation, safe static structure and versioning requirements. Node V8 simulates a DOM, checks routing and edition interactions, but **does not replace a real browser test**. A headless Chromium attempt in this execution environment timed out at 15 seconds and is recorded as **FAIL / environment blocked**. An independent Windows/Mac/mobile first-use canary is required before claiming browser acceptance.

## One useful marketing funnel

`FOUND -> UNDERSTOOD -> TRIED -> GOT_VALUE -> TRUSTED -> VOLUNTARILY_RETURNED -> SHARED`

Measure each step separately with privacy-respecting, consented observations. “Published,” “indexed,” and “impressions” are not user success. Favor time to first useful outcome, task completion, correctness of evidence understanding, reader correction, accessibility, unsubscribe/exit quality and actual referrals. Preserve negative results. Ask an independent person to attempt the exact same task through the current `START_HERE.md` and the new reader, counterbalancing order, rather than comparing against a deliberately worse firehose.

## Prior work and editorial controls

- CoCivium `START_HERE.md` and `ai/onramp/specialist-entrypoints-r0.json` are the current public entry points.
- RickPublic queue: `docs/publishing/series/rickpublic_substack_seed_v1/queue.json`, approval required.
- CoRelay and CoPhoenix contain source-linked feed, public discovery and recoverability experiments; reuse them rather than creating another uncoordinated broadcaster.
- This artifact is a *reviewable implementation candidate*. It should not overwrite either original without a qualified review.

## License

Source for this new standalone prototype is licensed GPL-3.0-or-later; see `LICENSE`. The upstream resources are *linked*, not copied, and retain their own respective licenses and disclaimers. No publisher, collaborator, user or company is represented as endorsing this prototype.
