# CoStretch+ R4 | finite multiprocessing over a huge logical frontier

**State:** `PASS_LOCAL_SYNTHETIC_MULTIPROCESS`. One bounded X2 canary on 2026-10-23, not a CoOrbWare runtime or an always-on worker fleet.

## Why this experiment exists
A potentially enormous/open-ended CoTurtles+ search space must not mean a corresponding number of live workers. Reuse existing CoExperimentSpace+, CoVirtualSession+, CoSessionAutocycle+, CoPulse+ and CoStretch+ contracts. This R4 tests a narrower transition:

`logical recipe -> bounded selected horizon -> short-lived processes -> exact local checkpoint -> recover and finish -> evidence-bound CoMap/CoOrbWare data views`.

## Executed evidence
- Declared logical population: `1,000,000,000,000`. This is a count in the source manifest, **not** a trillion materialized jobs or validated opportunities.
- Selected: 8 deterministic, distinct synthetic tasks across four investigation lanes.
- Active ceiling: 2 local processes. In each of two epochs, 2 distinct process IDs reported overlapping work.
- Epoch A completed 4 and wrote a checkpoint. A separate second invocation verified that checkpoint's manifest and event hashes, then executed the remaining 4. No candidate was executed twice in the recovered ledger.
- Local policy/continuity result: **20/20 PASS**. Three negative admission cases (WRITE authority, unqualified private payload, and parent-budget exceedance) rejected.
- Source-backed CoMap and CoOrbWare **JSON projections** agree on work ID, source SHA-256, authority, proof status, receiver ACK=false and active-now=0.
- X2 end-of-run process inspection found all four reported worker PIDs absent.
- Runner SHA-256 on X2: `b90c3e44d577f85c7b5ec2ead7bb9dede4c828ed22b4285d3a5455b17cdb0215`.
- Local result SHA-256: `5b9f0b7e16162e10169295f91e2123e8c478f6b121bfd8b57cb16a6afbc500b5`.
- Local benchmark event SHA-256: `bfdb559c17d89c3d306256acdf5921e06dd4605870838c270ee17ffd2248abcc`.

[Source code](CoStretch_Horizon_R4.py) | [One-event benchmark ledger](benchmark_evo_R4.jsonl)

## Reproduce safely
Requires Python 3.9+ with the standard library. No external credentials, network service or provider account. The worker function hashes synthetic payloads and sleeps briefly to make overlap inspectable.

```shell
python CoStretch_Horizon_R4.py begin
python CoStretch_Horizon_R4.py resume "<RUN_PATH_PRINTED_BY_BEGIN>"
```

Each invocation is finite. Each output file is exclusive-create, so rerunning against the same completed run refuses to overwrite the checkpoint. A new run uses a new directory. Do not interpret a permissive source-level concurrency ceiling as authority to run a real workload.

## CoOrbWare relation
CoOrbWare should *render* eligible CoPulse/CoQuanta projections; it does not own work identity or action authority. This canary writes two data projections, **not** a native desktop orb, wallpaper integration, receiver acknowledgment or browser view.

Proposed first-view sentence: **8 sampled tasks proved, 0 live workers, no recipient readproof; inspect evidence or wake a qualified next step.** Drill-down exposes candidate identity, original manifest hash, event receipts, error/unknown labels, and rollback/recovery options. Desktop bystander privacy remains independent of technical success.

## High-bar and unknowns
Actual Windows processes and checkpoint/recovery were exercised on synthetic local inputs. The test did **not** independently measure scheduler fairness under overload, true AI inference, meaningful receiver work, verified energy usage, pricing, correctness on real tasks, thermal envelopes, multi-host failure domains or continuous background operation. A simple source-level no-network assumption is not network-traffic attestation. Two overlapping PID reports are not an authenticated remote-receiver binding.

No CoStead landing, CoMx pickup, CoEx, canon, live CoOrbWare, external outreach, provider-session spawn, mouse remap or account retirement is claimed.

The next meaningful promotion is an **independent receiver** reading the same exact R4 projection in the existing CoPreCursor+/CoOrb view, confirming readable source history, privacy, freshness, authority and recovery after a fresh start.

**Rules:** `DESCRIPTOR_NE_EXECUTION | SESSION_NE_PROCESS | PROCESS_NE_RECEIVER | OBSERVATION_NE_RECEIVER_ACK | FINITE_PREFIX_NE_INFINITE_RUNTIME | PROJECTION_NE_RUNTIME | VALIDATION_NE_ACCEPTANCE`

FOSS Forever | CoGoAll | Working Together Respectfully | privacy-by-design | optional participation.
