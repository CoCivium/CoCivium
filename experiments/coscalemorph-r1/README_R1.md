# CoScaleMorph+ R1 | CoOrbWare reversible reduction + actual process restart

**State:** `OFFLINE_LOCAL_TESTED_CANDIDATE`, **not** deployed as a native CoOrbWare renderer, a distributed fleet manager, a model session replacement, or a sender/receiver service.

## CoHereNow

A bounded public CoMapPulse graph can collapse to one visible CoOrb node and expand back to its original exact bytes **only if its source is retained and authorized**. R1 adds a separate process-life test: a local worker is **actually killed**, its checkpoint survives, a stale lock prevents an accidental concurrent start, an explicitly controlled successor resumes, and the final 32-task digest equals the uninterrupted baseline.

**The source retained:** `source/CoMapPulse_graph_R0.json`, byte SHA-256 `4eddc49ef5902673fa22af5ef969b60a74bbd3153bd5b493638c00230d963f27`, from the CoMapPulse public demo. No private historical source files or user contacts were bundled.

## Five-minute first use

1. Open `CoScaleMorph_Recovery_Viewer.html` for one-screen results. Use `CoScaleMorph_Viewer.html` to switch among one-, three- and nine-node displays.
2. Run tests from the package root (Python 3.9+):

   ```sh
   python3 -m unittest discover -s tests -v
   python3 verify_ledger.py
   python3 verify_evidence_r1.py
   ```

3. Reproduce the real OS-process kill and recovery, writing only into the package's `output/` directory:

   ```sh
   python3 supervisor_canary.py --output output/my_kill_restart_receipt.json
   ```

4. Independently compare serial vs two-process SHA workloads (5 synthetic repetitions each):

   ```sh
   python3 bench_repetitions.py
   ```

**No credentials, API keys, network, webcam, browser control or third-party agent access are required.** This test deliberately does not run a persistent daemon or touch the user's X2 or Mac.

## What was actually tested

| Test | Observed outcome | Limit |
|---|---|---|
| Original R0 scale/recovery regressions | 27 PASS | Source-bound browser projections only |
| R1 process and evidence regressions | 25 PASS | Isolated local fixture |
| Total Python unit tests | 52 PASS | Not independent production validation |
| OS process death | PASS: first worker killed at task 3 in the standalone run | One controller; exact checkpoint only |
| Stale lock/duplicate-start prevention | PASS: refused until explicit local reclaim | Not a multi-host lease |
| Independent successor | PASS: different PID, 32/32 tasks, matching result digest | Not a Claude/Ollama context revival |
| Revocation while active | PASS: stop at next step, no claimed external ACK | No distributed authority service |
| Source deletion/corruption, namespace drift, fabricated ACK | PASS: rejected | Hashes are not signatures |
| Repeated widths 1 and 2 | Equal result hash across 5 trials per width | No general speedup; noisy timing |
| Energy | NOT RUN | No meter |
| Github <=2s / Gmail Primary<=60s / Claude<=1s / Pi<=2s / Ollama<=3s | NOT RUN | Not end-to-end observed |
| CoVIA, .nodes, sites | HELD / NOT RUN | No verified destination or readproof |
| Thumb button / real CoOrbWare / X2 | NOT RUN | No native input or desktop integration |

### Why two processes did not earn promotion

Under five repeated synthetic SHA workload trials, p50 for width 1 was **0.304868 seconds**, and width 2 was **0.306505 seconds**. The observed p95 was highly variable. Output digests matched in all ten trials, but there was **no demonstrated median speed advantage**. High utilization is not verified useful progress.

## Four different reductions

- **UI reduction:** Collapse visible nodes, optionally expand from the *verified retained* source. No real source mutation.
- **Worker dormancy:** Stop a task process, retain checkpoint and provenance, later re-materialize using compatible code and authority. It may then finish the same deterministic work.
- **Lossy abstraction:** An embedding, summary or cache cannot reconstruct bytes no longer retained. Model-generated filler is not recovery.
- **Deliberate withdrawal/erasure:** Revoked rights, deletion and intended privacy barriers can block re-expansion even if caches persist. Never elevate cached possession into current permission.

`REDUCTION_NE_DELETION | DEMATERIALIZED_NE_COMPLETED | CHECKPOINT_NE_RESTORED_PROCESS | REPLAY_NE_PROVIDER_SESSION_RECOVERY | PREDICTED_NE_AUTHORIZED`

## Evidence, setbacks and scope

- R0 historical receipt chain: `output/benchmark_evo.jsonl`, pinned by `output/HEAD.sha256` (21 rows).
- R1 new receipt chain: `output/benchmark_evo_R1.jsonl`, pinned by `output/HEAD_R1.sha256`, and linked to the **R0 parent head**.
- **32 R1 entries: 18 PASS, 3 FAIL, 3 HOLD, 8 NOT_RUN.** FAIL includes the initial off-by-one verification expectation, corrected by a later PASS; the two other FAIL entries explicitly reject unsupported hypotheses about universal speedups and lost-source recovery.
- The custody skill inventory records **exact local files only**. Neither hashing nor public GitHub hosting implies other devices received or adopted work.
- Linux/container acceptance tests are not a completed Mac, Windows or true remote failover qualification. The lock is a *single-controller local PID lock*, not production coordination; stale-lock reclaim requires explicit process-exit verification.
- Checkpoint hashes detect accidental/unsynchronized changes only. They are not cryptographically authenticated against an actor able to rewrite all files.
- Authority is a synthetic public-safe file fixture; runtime credential/access management would need a separate qualified adapter.

## Next high-bar test

Repeat the actual death/recovery experiment on **one permissioned X2 or Mac** receiver from a clean checkout, then prove that an independently authorized receiver can fetch the exact checkpoint, check its source+mission namespace and produce a distinct readproof. Compare one useful real task, a plain text/list viewer and CoMap/CoOrb with independent participant comprehension. Measure energy per verified outcome before claiming resource savings.

**CoStretch+** represents up to `10^12` optional work descriptions in this demo but only tests **one active local worker at a time** for recovery and **two** for the separate synthetic multiprocessing benchmark. There is no infinite computation, no million-session deployment, no covert agent-to-agent broadcasting.

FOSS Forever (GPLv3), optional participation, privacy by design, Working Together Respectfully, LoLs = lots of layers, laughs, love and learning.
