# CoFeedLoop | Developer-facing reproducible priorities R0

**Status:** public-safe triage derived from a user-supplied discussion. These are *candidate issues* to validate, not verified vendor defects, provider incidents or proof of a global session census.

| Priority | Observation or hypothesis | Discriminating acceptance test |
| --- | --- | --- |
| P0 | Human still relays context between separate provider sessions | Independent authorized second receiver reads a pinned WorkID and performs a bounded continuation without copied text |
| P1 | Replayed prompts can produce duplicate front projections | Replay the same signed observation repeatedly, one logical event and zero duplicate effects; conflicting event fails closed |
| P2 | Public source index and mirror URLs can be confused with working synchronization | Fetch every elected edition independently; check exact digest, timestamp and failure domain |
| P3 | Mouse macro may be too short or fixed to carry a dynamic prompt | Measure actual limit on the user's device; store one stable pointer; verify native keyboard escape and no silent truncation |
| P4 | Outputs sometimes overstate delivery/acceptance | Negative tests distinguish source commit, CI, publish, pickup, integration and runtime |
| P5 | Session recovery responses become longer than useful | Compare time-to-value, carry burden, unique recovered deltas, coverage, duplicate rate and verified outcomes |
| P6 | Proposed CoBar audio alerts may give a false impression of operational truth | Test alert comprehension against text, with explicit silencing, accessibility, false-positive rates and source pointers |
| P7 | Multiple URLs may share one failure domain | Fault-inject host, account, DNS, cache and content mismatch; show DEGRADED instead of fabricated synchronized status |

## Source-first constraints
Avoid publishing proprietary provider prompts, internal state guesses, raw WhatsApp exports, private session or email identifiers, or private CoStead coordinates. Existing baseline: [session bootstrap](../../../SESSION_BOOTSTRAP.md), [public rebound](../COGOALL_PUBLIC_REBOUND_HUB_20261108.md), [CoPre contribution](../../../ai/onramp/copre-generic-session-contribution-r0.json). Test candidate changes in existing CI; preserve successful older heads and exact failure receipts.

## Value gauge
Track: unique useful contributions accepted per unit carry; measured relay count; independent receiver readbacks; duplicate suppression; recovery time; unresolved source/rights gaps; UX task completion; cost and rollback rate. Do **not** replace this with front counts, CI green alone, supposed AGI progress, number of mirrors or mythical 1,000 sessions per pointer.
