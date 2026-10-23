# CoEvoAll+ / CoStretch+ | R2 evidence broadcast (2026-10-23)

**Review gate:** DRAFT, NOT MERGED. No provider fleets, paid actions, external contacts, or public site deployments are claimed.

## Verified evidence
- Offline ReplayLab v0.3 tests: **70 main + 13 upstream = 83 PASS**, checked in a Linux Python 3.13.5 container.
- Archive passed ZIP integrity; its package verifier returned **68 content hashes verified**. SHA-256 of ZIP: `5fe57e0a991f405daf77b16857bb93710df9f3d956b835bb94a6f12ca36ed072`.
- Logical experiment-space capacity is **50,164,531,200,000 combinations**. That counts potential descriptions, **not experiments performed**.
- The [synthetic PASS/FAIL/HOLD ledger](./benchmark_evo.jsonl) is now on this review branch. [Verify the pinned 9-event ledger](./verify_public_ledger.py); head: `58df0b6c89b5b7b7db3ab2d3c96bd9fd5fcd9bf41138fab00acec0182f2984a7`.
- Run [provider-free index tests](./test_coturtle_index.py) with `python3 -m unittest discover -s experiments/costretch-r1 -p 'test*.py' -v`; they cover cardinality, boundaries, invalid inputs, and 1,000 deterministic index roundtrips.
- **Broker promotion gate FAILED:** calibrated synthetic stress 3 wins / 7 ties / 2 losses; adversarial 0 wins / 0 ties / 12 losses. Do **not** claim the broker is useful on real research workloads.

## NOT RUN, blockers, and nonclaims
- **Media video size >300KB, thumbnail validation, ffprobe blackdetect=0:** no video/thumbnail supplied. The 116KB research ZIP is not an eligible media file; don't pad it to pass a meaningless gate.
- **GitHub HTTP 200 <2s:** local sandbox curl failed with a DNS resolution error. GitHub connector file creation and fetch-back succeeded separately, but does not establish latency. No claim that GitHub is down.
- **Gmail Primary <60s and delivery ID/ACK:** not tested. A sent email is not proof of Primary classification or pickup.
- **Pi Mac compatibility <2s, Claude credentials <1s, Ollama/Llama packet parsing <3s:** not tested. Do not read credentials for a publicity benchmark.
- **CoVIA nodes/sites, receiver pickup and mass broadcast:** no validated endpoint/ACK; not claimed.
- **Million live AI sessions:** zero were spawned in the experiments. Logical slots are not living agents.

## Independent local follow-up
The companion downloadable CoStretch_Broadcast_R2 package adds a 28-event hash-linked combined ledger, Python and Node.js verifiers, and failure-preserving test reports. This GitHub branch holds the smaller 9-event public benchmark ledger and the standalone no-provider index and ledger witnesses. The unpublished combined receipt's head is `6560202a3b8d359f2a664bb8e851c1c41d3a234d8a42eaf1e6619bf69f469915`; this head alone does **not** prove possession of or delivery of that file.

Next promotion thresholds: independent Mac reproduction, consented Claude/Pi/local-model experiments, real historical-task adjudication, source-dependence detection, calibrated costs, and matched competent baselines. Keep challenge cases and negative results intact.

FOSS forever (observe repository GPLv3), respectful opt-in contribution, privacy by design, accessible display options, optional wearables, no implied financial holdings or authority.

`POINTER_NE_ACK | INDEXABLE_NE_EXECUTED | FAIL_IS_EVIDENCE | MODEL_OUTPUT_NE_TRUTH`
