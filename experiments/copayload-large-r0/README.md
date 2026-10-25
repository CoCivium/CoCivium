# CoPayload LargePath R0: bounded rich-payload + CoEvo cycle canary

**State:** offline implementation and local canary, **not** a native middle/thumb button, full CoOrbWare, real 16 GiB transfer, or background daemon.

This builds **on** [CoThumbCoCopyR1.ps1](https://github.com/CoCivium/CoCivium/blob/main/scripts/CoThumbCoCopyR1.ps1) and [CoThumb / CoPayload R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COTHUMB_COPAYLOAD_R0_20261024.md). It does not replace them or claim to execute the Windows GUI. The existing R1 limits are **up to four source files, 16 GiB aggregate reference/hash ceiling, and 2 GiB aggregate explicit staged-copy ceiling**. R0 models their admission boundary using declared sizes without touching giant real files.

## Reproduce without credentials or network

Python 3.10+, standard library only, no OS privilege required:

```sh
python3 -B -m unittest discover -s experiments/copayload-large-r0 -p 'test_copayload_large_r0.py' -v
mkdir -p /tmp/copy_canary
python3 experiments/copayload-large-r0/copayload_large_r0.py --cycles 3 --output /tmp/copy_canary/evo.jsonl --summary /tmp/copy_canary/summary.json
```

Run outputs are **exclusive-create**: supply new destinations for each run. Optional `--sample-file /path/to/explicit-nonsensitive.file` computes streaming SHA-256 (4 MiB reads), after refusing symlinks and checking file identity, size, and modification time. The summary contains only byte count, chunk count, hash, and nonclaims, not the local source path. It does not stage/copy/send the bytes.

## What is actually covered

Eight descriptor cases per cycle: tiny inline candidate, >300 KiB file-backed reference, exactly 2 GiB staging, 2 GiB+1 rejection, exactly 16 GiB reference, 16 GiB+1 rejection, over-budget aggregate rejection, and four-file admission. Three deterministic cycles produce 24 check events with chained event SHA-256 and identical normalized case results. There is **no forever loop** and **zero provider sessions, daemons, physical button remaps or external writes**.

Real streaming read test: explicit local file only, plus regression for symlink rejection and path-free summary. Local unit regressions check fail-closed validation, exact limits, recursion/cycle ceilings, output no-clobber, zero receiver authority and no fake file-read claims. These tests do not validate Windows `pwsh` semantics of the predecessor; CI only validates this portable candidate.

The descriptor fields `actual_file_sha256=null`, `actual_bytes_read=0`, `file_existed_or_was_staged=false` deliberately distinguish planning a 16 GiB object from transferring one. A small actual file's streaming digest proves only that exact local file's read. Neither result proves media visual acceptance, human review, receiver behavior or throughput on large material.

## Honest continuing gates

- **Physical middle/thumb:** HELD until an observed local device action with panic-disable and original button behavior preserved.
- **Video:** HELD for a selected real file until preview, ffprobe, blackdetect, visual clipping and rights checks run together on *the same* source hash.
- **Other providers:** Claude/Pi/Anthropic and Ollama compatibility are explicit, permissioned adapters. Credential presence is not proof of access; metadata parse is not inference correctness. Nothing in this canary tests them.
- **Gmail:** search time is not recipient Primary delivery time. No mail is sent.
- **GitHub public HTTP:** the repository page must be independently timed for an observed sample; a CI pass is not an SLA.
- **Real auto-cycling:** a finite, foreground 1-3-cycle rehearsal only. Durable scheduling, receiver ACK, queue pressure control, energy use and resource budgets remain separate to prove.
- **Million sessions:** only logical address spaces; no bogus human accounts, provider-limit avoidance or unsanctioned fleet.

## Follow-on

When X2 is online, run predecessor `pwsh` SelfTest and one user-consented, *non-sensitive* small and rich-media case in UI. Record `PASS/FAIL/HELD` for file identity, visual preview, exact receiver paste/attachment **without sending**, cancellation, and key fallback. Then elect a 4 MiB -> 256 MiB -> 2 GiB -> 16 GiB **reference-only** scale ladder with actual time, peak memory, read throughput and error metrics; stop if latency, privacy or pressure gates regress. Do not force large file creation just to meet a marketing number.

**Acceptance boundary:** `PLANNER_NE_TRANSFER | LARGE_DESCRIPTOR_NE_LARGE_FILE_PROOF | COPY_NE_SEND | AUTO_CYCLE_NE_DAEMON | FILE_HASH_NE_SEMANTIC_PROOF | NO_RECEIVER_ACK_WITHOUT_EXACT_READPROOF`.
