# CoEvidence Bundle Canary R0

**State:** `BOUNDED_PUBLIC_CORPUS_CANARY__NO_RUNTIME_ADOPTION`

## Question and decision

Can seven advisory roles share exact source bytes across their 31 input bindings while preserving provenance and declared relation-query results, and what does that cost?

The bounded experiment passes reconstruction and query checks. Sharing reduces duplication against the declared per-role-copy baseline, but **ordinary shared files are smaller than either content-addressed layout** on this corpus. The indexed bundle uses 6,022 more bytes than ordinary shared files (10.3% overhead), while using 70.4% fewer bytes than per-role copies. Use shared sources as the baseline; choose additional addressing and views for a demonstrated provenance/query need, not an assumed storage improvement.

Implementation: [CoEvidenceBundleCanaryR0.py](../../scripts/CoEvidenceBundleCanaryR0.py). Exact inputs and fixture: [specification](../../examples/co-evidence-bundle-r0.spec.json). Measured output, implementation hash, environment, timings, and probe outcomes: [2026-10-22 report](../Operations/fixtures/coevidence-bundle-r0-20261022.json).

This implements a limited experiment proposed in [CoRoleSpace Preview](COROLE_SPACE_PREVIEW_R0.md), using the boundaries of [CoSourceGraph](COSOURCE_GRAPH_R0.md), [CoLineageCompactor](COLINEAGE_COMPACTOR_R0.md), and [ReceiptGuard](COEVIDENCE_RECEIPT_GUARD_R0.md). It does not implement semantic lineage election or a live review-panel controller. The earlier design document remains unchanged as a historical source.

## Corpus and role bindings

Seven explicit public paths were read at commit [`778d6fad4ca42c4a1aee58b3cc94126bd87cf007`](https://github.com/CoCivium/CoCivium/tree/778d6fad4ca42c4a1aee58b3cc94126bd87cf007), observed `2026-10-22T20:44:17Z`. Returned UTF-8 bytes matched the reported Git blobs and pinned tree. The specification retains original locators, Git blob identifiers, SHA-256 digests, lengths, observation time, and custody scope.

| Source ID | Public artifact | Bytes |
|---|---|---:|
| `role_preview` | `COROLE_SPACE_PREVIEW_R0.md` | 9,427 |
| `source_graph` | `COSOURCE_GRAPH_R0.md` | 6,234 |
| `lineage_compactor` | `COLINEAGE_COMPACTOR_R0.md` | 5,903 |
| `receipt_guard` | `COEVIDENCE_RECEIPT_GUARD_R0.md` | 4,580 |
| `session_morphology` | `COVIRTUAL_SESSION_MORPHOLOGY_R0.md` | 12,963 |
| `source_schema` | `cosource-record-v0.1.schema.json` | 3,149 |
| `spawn_schema` | `cospawn-contract-v0.1.schema.json` | 3,034 |
| **Total, seven distinct payloads** | | **45,290** |

The fixture assigns 7 sources to Proposal, 4 to Formal, 3 to Empirical, 4 to Challenge, 2 to Perspective, 4 to Provenance, and 7 to Synthesis: **31 role–source bindings**. The exact mapping is in the specification. These are input-binding fixtures, not executed reviews or independent evidence channels. The Perspective seat accommodates ethical, experiential, spiritual, and other interpretations without establishing physical effects or treating role labels as participants.

Source identity remains separate from byte identity. Content-addressed paths include a digest of custody scope and confidentiality as well as the payload digest; identical bytes do not authorize crossing those boundaries. The experiment accepts declared `PUBLIC` sources and verifies their bytes. Declaration validation is not a general privacy classifier or authorization system.

## Four measured layouts

Every layout stores the specification, role bindings, payloads, and a complete file inventory. The indexed layout additionally stores its materialized views. Metadata includes the inventory itself. Totals count logical file contents, not filesystem allocation, RAM, network transfer, executable code, or this report.

| Layout | Payload | Metadata | Views | Total bytes | tar.gz bytes |
|---|---:|---:|---:|---:|---:|
| Per-role copies | 202,165 | 15,902 | 0 | 218,067 | 53,942 |
| Ordinary shared paths | 45,290 | 13,184 | 0 | **58,474** | **19,879** |
| Content-addressed, no views | 45,290 | 16,424 | 0 | 61,714 | 19,884 |
| Content-addressed, with views | 45,290 | 16,535 | 2,671 | 64,496 | 20,387 |

Per-role copies are a declared duplication scenario, not the minimum necessary storage of existing systems. Ordinary shared paths already remove that duplication. Content addressing adds longer bindings and inventory entries; materialized views add further stored data.

The supplemental archive comparison compresses the whole stream: sorted USTAR file members, fixed modes and zero timestamps, followed by gzip level 9 with zero modification time. It includes metadata and inventories. Archive sizes are reproducible within the recorded implementation/runtime conditions; they are distinct from uncompressed totals and do not establish universal compression superiority.

## Query contract and checks

All six fixture claims, relation assertions, and candidate-validity intervals are `TEST_ONLY`. The synthetic query cutoff is `2026-10-22T00:00:00Z`; it is unrelated to live freshness and does not assert that these files were observed at that earlier time.

| Query | Declared behavior |
|---|---|
| Sources behind a claim | Union source IDs along explicit `derived_from` and `projection_of` paths; terminate cycles. |
| Unresolved contradictions | Return explicit unresolved `contradicts` records, preserving direction, identity, and ambiguity. |
| Receiver candidates | Select the named receiver's `CANDIDATE` claims with `valid_from <= cutoff < expires_at`, or no expiry. |

The reference implementation uses depth-first traversal and parsed timestamps. Materialization uses fixed-point set closure and canonical UTC-string comparisons. Their normalized results must agree. The fixture includes a derivation cycle, reverse contradiction edges, an already-resolved edge, an expiry boundary, a future candidate, and a historical claim. These test declared graph behavior; they are not detected contradictions or elected successors in the actual documents.

Each view binds its transformation version, complete specification digest, exact source bindings, and cutoff. Verification checks the external expected inventory digest, file membership and hashes, stored specification, role/source membership, and byte-for-byte reconstruction of all 31 bindings. Indexed results must equal the reference results. Missing or altered payloads, altered views, changed source versions, and changed cutoffs must hold rather than report success.

## Timing and refresh

The report records three build/validation samples and 31 warm query samples by default, including medians and ranges. Build timing includes serialization, applicable view construction, writes, and inventory reads after inputs are loaded. Full validation measures disk reads/hashing, metadata checks, reconstruction, and query comparison separately. Warm-query timing includes result JSON encoding and excludes loading, hashing, and validation; it cannot establish end-to-end latency or scalable throughput.

Refresh appends one newline to one in-memory source, explicitly labels the result a synthetic derivative, preserves its original source record, and fully rebuilds and verifies every layout. It does not observe a new remote Git version or implement incremental refresh. Changed storage includes derivative provenance metadata as well as the additional payload byte. Both old and new layouts are verified; restored originals and source files are read again before success. Temporary layouts are removed when the run ends; the CLI emits the report to stdout.

## Trust and limits

The expected inventory digest is supplied from outside the layout under verification. That trusted value must survive independently: replacing both an artifact and its expected digest defeats this integrity boundary. Hashes provide no cryptographic authenticity, source truth, availability guarantee, receiver acknowledgement, or semantic ingestion proof. This is a canary-specific format, with no claim of full `CoSourceRecord` or `CoSpawn` conformance.

The result establishes this corpus's reconstruction, declared queries, measured sizes, and tested failure handling. It does not establish live session synchronization, independent scientific replication, panel quality, unfamiliar physical substrates, or deployment on any receiver.

## Reproduce

Run the current implementation against a separate immutable corpus checkout:

```sh
git worktree add --detach ../coevidence-pinned-corpus 778d6fad4ca42c4a1aee58b3cc94126bd87cf007
python scripts/CoEvidenceBundleCanaryR0.py \
  --spec examples/co-evidence-bundle-r0.spec.json \
  --source-root ../coevidence-pinned-corpus \
  --as-of 2026-10-22T00:00:00Z \
  --repetitions 31 --build-repetitions 3 > /tmp/coevidence-canary-report.json
```

CI separately checks out the candidate implementation and the pinned corpus into `pinned-corpus`, then passes that path through `--source-root`. Failures return a nonzero status and `HELD`; timings and observation times will vary. A next integration gate needs a real consumer, its retrieval/custody requirements, and measured end-to-end behavior before choosing a more complex storage layout.
