# CoMapCursor+ R0 | CoOrb trails + predictive caret, offline

**Status:** `PUBLIC_SAFE_DRAFT_CANARY__NO_PRODUCTION_RUNTIME_OR_LIVE_DATA`

This experiment extends, rather than supersedes, [RD1 CoMap/CoOrb draft PR #166](https://github.com/CoCivium/CoCivium/pull/166), [CoFleet/RickBar R4](../../docs/UX/COFLEET_RICKBAR_R4.md), [CoVirtualSession R0](../../docs/Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md), and [CoPulse currentness](../../docs/Architecture/COALL_PULSEFIELD_COTIME_R0.md).

## Try it

From repository root, run:

```sh
node --test experiments/comap-cursor-r0/core.test.mjs
python3 -m http.server 8787
```

Browse `http://localhost:8787/experiments/comap-cursor-r0/`. Python is only a local static file server. There are no package installs, CDN dependencies, telemetry, credentials or model-provider API calls.

## One source, multiple projections

`core.mjs` defines a small, explicitly synthetic graph with typed nodes and edges. The page derives CoMap, CoOrb, event trails, and an ambient-preview scene from **exactly the same in-memory seed**. Changing view or moving the synthetic temporal cursor does not mutate the source. Edges after the selected time cursor are omitted and counted, not declared nonexistent.

`CoQuanta+` here names typed relational units, **not physical quantum behavior**. Actual source data, uncertainty, authority, privacy and provenance must be bound before any real-work projection. In-between relations, predicted paths and conjectures are visible but not promoted to observations.

The ambient view is an in-page preview; it does not modify the desktop, wallpaper, Windows screensaver, or sensor permissions. A future authorized CoOrbWare adapter could render passive overlays, with explicit power, privacy and focus controls. A permanent heavy animation is not a better idle default.

## CoInput beyond the cursor

The page shows one of four deterministic **ghost suggestions** after the caret when the left-hand text matches a local prefix. The ghost never edits or sends text on its own. Only clicking **Accept suggestion into local text** inserts it at the cursor and emits a local-only event. Trailing user-authored text is preserved.

The checkpoint download preserves `source_id`, `source_version`, current view/time, draft and a bounded local edit-event log. It explicitly says `receiver_ack=UNPROVEN`, `submission=NONE` and `provider_session=NONE`. This is not an ACK-chain implementation, synchronization agent or account export tool. Do not treat `CoAckRAW` as proof of receiver acceptance.

## Resource and storage proposal, unbenchmarked

Candidate representation: immutable source objects + content-addressable identity + typed edges + temporal events + receiver-specific cursors + render recipes. The four views reuse the one source, but byte, latency, GPU/CPU, energy, index and rebuild savings are **not measured**. Compare against plain JSON + normalized tables before claiming a win. Track contradictions, omitted edges and missing provenance in the density score.

Maximize **recoverable meaning / (attention + storage + compute + bandwidth + loss)**, subject to privacy and correctness limits. This is an objective proposal, not a validated scalar metric.

## Logical virtual sessions and provider exit

A virtual session is a durable logical identity that can materialize through a local model, Claude, a deterministic worker, a paid provider, or no active process. Virtualization alone does not migrate old chats, preserve all histories, confer native session access, prove independent receivers, or cancel paid accounts. Provider exit needs tested substitutes, custody migration, recovery, billing audit, and explicitly authorized cancellation.

## Broadcast matrix, not a blast

| Route | State | Gate |
| --- | --- | --- |
| GitHub | Draft PR / review candidate | CI + merge separate |
| CoVIA / .nodes / sites / CoOrbWare | Candidate subscriber class | Exact receiver, confidentiality, opt-in |
| Private CoStead | Candidate custody/adoption | Receiver-specific source readproof |
| Gmail / named humans | NOT SENT | Known recipients, purpose, personal-data check, authorized send |
| Public web | NOT DEPLOYED | Safety classification + tested deployment |

All-to-all **discovery** is a graph relation. All-to-all **message sending** is neither authorized nor efficient. Filter updates through `MUST_KNOW`, `ROLE_FRONTIER`, `NEARBY_OPTIONALITY`, `DIGEST_ONLY`, and `SLEEP_UNTIL`.

## Acceptance and nonclaims

The automated tests exercise source integrity, typed epistemic classes, time-window omission, four-view source identity, predictive-caret explicit acceptance, checkpoint recovery, no fabricated ACK, no network API, and bounded event counts. Browser rendering, accessibility acceptance, production UX and storage performance remain separate gates.

`PROJECTION_NE_SOURCE`; `PREDICTION_NE_AUTHORED_INPUT`; `LOCAL_EDIT_NE_SUBMISSION`; `EXPORT_NE_RECEIVER_ACK`; `VIRTUAL_SESSION_NE_PROVIDER_TAB`; `RENDER_NE_PERSISTENCE`; `GITHUB_PR_NE_LIVE_DEPLOYMENT`; `BROADCAST_REQUEST_NE_SPAM_AUTHORITY`.
