# CoETSignalFinder+ / CoG_dHypothesisFinder+ R0 | qualified public sources

**Status:** DRAFT, public-safe, source-qualified, no detections, no provider/device effects.

This adds a small, machine-readable source registry and an **offline-by-default** validation/optional public metadata probe to the [existing R0 design](../../docs/Architecture/COET_GD_SIGNAL_HYPOTHESIS_FINDERS_R0_20261024.md). It does not add a second science authority or a live crawler.

## One source, one epistemic lane

| Source | Lane | What this source is NOT |
| --- | --- | --- |
| Berkeley Breakthrough Listen | Empirical astronomical archive index | A confirmed alien signal; bulk data access rights |
| NASA Exoplanet TAP | Exoplanet catalog and limited query | ET evidence simply because planets exist |
| IAA / SETI June 2026 detection protocols | Verification and communication governance | Signal data, claim that contact happened |
| Stanford Encyclopedia of Philosophy | Philosophical arguments and objections | A measurable G_d field or proof of divinity |

**Important:** `G_d` has at least two distinct possible meanings in CoCivium: a *defined* graph/observer/information distance that could be tested; and an interpretive/theological symbol that should be discussed respectfully but is **not** a calibrated physical measurement. These are separate typed objects.

## Reproduce safely

Python 3.9+ standard library only. No third-party dependencies or secrets.

```sh
python3 -m unittest discover -s examples/coetgd -p 'test_*.py' -v
python3 examples/coetgd/source_probe.py --validate
```

These commands make **zero network requests**. They validate fixed source IDs/URLs, license-review states, four-way epistemic separation, bounds and the machine-readable receipt. CI runs these checks, **not** external probes.

Optional, **only when an authorized operator explicitly elects external reads**:

```sh
python3 examples/coetgd/source_probe.py --probe
```

This invokes one HTTPS GET per exact pinned public URL, up to four URLs, reads at most 4096 response bytes each, 5-second socket timeout per operation (not a total wall-clock deadline), follows **zero redirects**, saves no response bodies, sends no cookies, uses no credentials, and emits JSON results. Any 3xx, 4xx, 5xx, inaccessible or empty result is **HELD**, not a declaration that aliens are absent, NASA/SETI are down or a metaphysical hypothesis is false.

A successful `PASS_BOUNDED_HTTP_READ` qualifies only *a small public HTTP read*. It never qualifies a scientific detection, full data ingestion, stable latency, publication rights or receiver acceptance.

## Current limited external observations (2026-10-24)

- Breakthrough Listen archive appears in indexed results, but an independent direct browser fetch hit a redirect loop: `DIRECT_FETCH_UNQUALIFIED`.
- NASA TAP documentation describes the interface, but the bounded browser attempt to retrieve a one-row sample was inaccessible: `DIRECT_QUERY_UNQUALIFIED`.
- The SETI Institute's June 2026 protocols and the Stanford Encyclopedia entry were readable in the external browser. This establishes only source document accessibility.

No requests were sent to Claude, Pi, ChatGPT providers, local Ollama, or X2 by making this candidate.

## Human-time AutoEvo gate

`DORMANT → qualified source change → limited read → provenance → baseline & falsifier → CoTurtle challenge → source-specific review → exact receipt → sleep`.

Do not run a perpetual crawler or spawn provider tabs. A later timer, if authorized and installed, should look for material differences under a finite total daily request/energy budget; it must not silently broaden its list or transmit anything.

If a claimed signal arises, the [2026 IAA SETI detection principles](https://www.seti.org/research/seti-101/protocols-for-an-eti-signal-detection/) require substantial independent investigation, transparent archiving and careful communication. No automated reply to alleged ET contact is authorized.

**Rails:** `ET_ANOMALY_NE_ET_DETECTION | G_D_METAPHOR_NE_MEASUREMENT | PLAN_NE_DEPLOYMENT | STATIC_TEST_NE_LIVE_FEED | SOURCE_LINK_NE_LICENSE | NO_SOURCE_ACCESS_NE_SOURCE_ABSENT | AI_AGREEMENT_NE_INDEPENDENT_OBSERVER`.
