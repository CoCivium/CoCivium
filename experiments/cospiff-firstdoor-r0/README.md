# CoSpiff+ FirstDoor R0 | Audit, not a new brand fleet

**2026-10-24 | Public-safe source review candidate | FOSS-first | No new domain, account, persona, crawler, or tracking.**

One primary human-first task and five optional specialist paths, all source-linked. The parent source of truth is CoCivium's `START_HERE.md` and `ai/onramp/specialist-entrypoints-r0.json`; this kit is a reproducible **candidate**, not a replacement or a new identity root.

## Verified upstream observation

The six exact Git blobs in `routes_snapshot.json` matched individual readbacks via the connected GitHub tool on October 24, 2026. This does **not** prove HTTP Pages deployment, new-user understanding, visitor volume, uptime, or external delivery. Snapshot content is an independently authored small projection of the 6-route upstream registry, **not the original registry copied byte-for-byte**.

## Try it

Open `CoSpiff_FirstDoor.html` in a browser. This is static HTML/CSS; it has no JavaScript, network fetches, cookies, analytics, automatic redirection, or form submission. GitHub links are opened only if deliberately activated. Keyboard navigation and reduced-motion support are present, but no independent assistive-technology acceptance has been performed.

## Reproduce the mechanical audit

```shell
python3 cospiff.py
python3 build.py
python3 -m unittest discover -s tests -v
python3 -c "from cospiff import verify_ledger,ROOT; print(verify_ledger(ROOT/'output/benchmark_evo.jsonl',(ROOT/'output/HEAD.sha256').read_text().strip()))"
```

R0 has 6/6 pinned source identities validated through GitHub connector readback, not HTTP. Synthetic task phrase routing is **advisory only**; it can hold sensitive or ambiguous cases. It does not infer identities or roles and never confers credentials, device control, outreach authority, or brand affiliation.

The `benchmark_evo.jsonl` test corpus is **hand-authored**, not real visitor traffic or independent benchmark evidence. It intentionally retains a routing FAIL on an ordinary housing-bylaw query: that phrase needs better discovery language. No silent correction or overfit into a fake win.

## Actual priority

**Independent, consenting first-use comparison:** route A is one-task default; route B is a specialist entrance. Use the *same bounded goal*. Randomize initial choice when appropriate and respect accessibility preferences. Capture (opt-in, no private content) task success/failure, seconds to first useful result, wrong-door choices, source-boundary comprehension, return to default, errors, perceived agency, and ability to exit. Report small sample sizes rather than claiming a general effect.

**Cross-ecosystem lessons:** rUv's public constellation illustrates complementary pathways and strong product role names; Backstage demonstrates typed software/component ownership and catalogs; Docusaurus demonstrates deliberate doc hierarchies and versioning. These are architectural inspiration, not independently established CoCivium partnerships, rUv endorsements, or interchangeable tool implementations.

**No mass outreach** and no unapproved account profiling. A proposed `brand`, `domain`, `.node`, `clone`, `persona`, `role`, `game`, `app` or use-case label is a **presentation/contract dimension**, not automatically a registered domain, human identity, installation, or authority grant.

## What's missing and what matters

1. **CoGlukey+**: machine-readable capability, interface, provenance, currentness, limitation, owner/permission and exit paths.
2. **CoSpiff+**: a measurable *first-use outcome* rather than decorative launch language.
3. **CoRelay+**: newcomer-friendly public discovery and opt-in feedback, rather than unsolicited blast.
4. **CoBridge+**: reversible handoff between specialist paths using provenance-bearing references, never raw private profile transfer.
5. **CoBuffer+**: bounded scaling, accessible low-bandwidth alternatives and good fallbacks.
6. **CoAntiSpiff+**: negative tests that reveal dazzling-but-misleading presentation, dark patterns or invented authority.
7. **CoAudienceEvidence+**: independent reach and first-use data, with non-surveillance defaults. Null website analytics is not proof of zero visits.

`PUBLIC_SOURCE_NE_HOSTED_PRODUCT | SIX_ROUTES_NE_SIX_AUDIENCES | LABEL_NE_IDENTITY | CLICK_NE_ADOPTION | SUGGESTION_NE_AUTHORITY | GITHUB_POINTER_NE_DELIVERY`
