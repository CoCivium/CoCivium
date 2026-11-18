# W07 — LOCAL_LOOP inspection and CoLoop+ recovery test design (R0)

- worker_id: W07
- utc: 2026-11-18T17:36Z
- branch: `claude/w07-loop-20261118` from `a07f1544f83ccf13fad224328558fe77a176223b`
- contract under test: `CoCivium/CoCivium@a07f154:docs/CoOps/COCLAUDE_TEN_CONTEXT_DISPATCH_R0.md` § "CoLoop+ local-first recovery contract" (blob `41832275685fb1e90d2b2d4236c6304af6395024`, sha256 `ec169cffeba65e5d1bc5c4a84b3efd4d20ad03868d2e74898e7395fed33673e7`)
- status: **design only. NO_LOCAL_ACCESS.**

## 0. Nonclaims

- **NO_LOCAL_ACCESS.** W07 had no shell, bridge, or remote session on the steward's machine. No scheduled task, service, or running process on that machine was inspected. Every statement below about local machinery comes from repository source, not from a live machine.
- No process was started, stopped, or installed. No workflow was run, disabled, or edited. Only `docs/CoOps/w07/` was written.
- GitHub Actions run history for CoCivium/InSeed could not be read from this session (the API call was refused because the session has no repo credentials). Whether the InSeed workflows *ran* is therefore **unknown**. What is known is that none of their runs ever *landed a commit* (§1.2).
- This document claims **no unattended operation of any duration**. Under §4.5, the highest reboot rung passed so far is **none**.

## 1. What exists (evidence-pointed)

### 1.1 InSeed legacy local loops — `CoCivium/InSeed@1d0964637c68b49ef4274c5e48d034e148f1897a`

| File (blob) | Mechanism | Mutates | Lease / idempotency / heartbeat / reboot recovery |
|---|---|---|---|
| `auto-turns-waves.ps1` (`54930be5…`) | `while($true)` loop with 600 s sleep. Each turn runs `git fetch --all` and `git pull origin main --rebase`. Every 5 turns it appends to `heartbeat.log`. Every 20 turns it runs `git add heartbeat.log`, commits, and `git push origin main`. | Local working tree (rebase); `origin/main` (push) | None. Turn counters are held in memory and reset on restart. The "heartbeat" is a local file and has no reader. Nothing in the repo installs the loop, so it exists only while a console runs it. |
| `CoWatcher-filtered.ps1` (`a6bf6a01…`) | `FileSystemWatcher` on the hard-coded path `C:\Users\Owner\Desktop\InSeed\index.html`. On every `Changed` event it runs `git add index.html CoPingables.json CoVIA.json`, `git commit`, and `git push origin main`. | `origin/main` | None. `Register-ObjectEvent` subscriptions die with the PowerShell session. There is no debounce, so one save can fire several Changed events and push several times. |
| `forever-autoevo.ps1` (`d390651f…`) | `while($true)` loop with 3600 s sleep running `git fetch` and `git pull origin main --rebase`. It prints the log head. | Local working tree (rebase) | None. Display only, but it rebases unattended. |

Readback: `heartbeat.log` is **absent** at `1d09646` and in every commit reachable from the 6 remote refs. No commit message matches the loop's `wave N cycle N` or `auto cloudify` patterns. This shows that **neither PowerShell loop ever pushed to the remote**. It does not show whether either is running now (see §5).

### 1.2 InSeed scheduled workflows

| Workflow (blob) | Trigger | Action | `permissions:` |
|---|---|---|---|
| `.github/workflows/coevo-forever.yml` (`16fde065c20941d9fd16a7b33b0cc2175593a82f`) | `cron '0 * * * *'` (hourly) + dispatch | Appends to `evo.log` and **appends an HTML comment to `index.html`**, commits as `CoEvoBot <coevo@cospeedo.local>`, then `git push` | not declared |
| `.github/workflows/autoevo.yml` (`3e73d1886504ab3f4c37e2294ee1fd62d0e45953`) | `cron '30 10 * * *'` (daily) + dispatch | Appends to `evo.log`, commits as `CoEvoBot`, then `git push` | not declared |

Readback (`git log --all`, 6 remote refs):
- **0** commits by `CoEvoBot`, `coevo@`, `github-actions` or `[bot]`.
- `origin/main` HEAD is still `1d09646` (2026-10-13T11:35:43-04:00). If the hourly schedule had pushed successfully since the workflows were added (`8dc2551`/`73468e5`, 2026-10-13), there would be on the order of 800 bot commits. There are none.
- `evo.log` has been touched only once, by human commit `73468e5`.

Conclusion: **no evidence that either workflow has ever mutated the repo.** The cause is unknown. Candidates include a read-only default `GITHUB_TOKEN`, Actions being disabled, or runs failing; telling these apart needs Actions run history (§6 next_gate).

**Latent hazard (finding, no action taken):** the workflows still exist on `main` and do not declare `permissions:`. If the repo's or org's default workflow token were ever switched to read/write, `coevo-forever.yml` would start pushing a mutation of the public `index.html` every hour with no review. Before then, the steward should declare `permissions: {}` or delete both files.

### 1.3 CoCivium machinery at `a07f154` (closest existing parts)

| Part (blob) | What it gives | What it does not give |
|---|---|---|
| `examples/cotalkitout/due_work_catchup_r0.py` (`a143e683…`), class `DueWorkQueue` | SQLite `work` table with states `PENDING/LEASED/DONE`. Leases are **per WorkID** and bounded (1–86400 s), with an `epoch` counter. `complete()` is a conditional UPDATE that returns `FENCED` for a stale claim. `next_wake()` computes the next due time. | No **actuator** (singleton) election, no heartbeat, no receipt chain, no OS wake. `next_wake()` has no consumer. |
| `examples/cotalkitout/local_source_work_cycle_r0.py` (`034adb73…`) | One-shot WorkID `CoPre:source-integrity:R0`. A replay returns `LOCAL_REPLAY_OR_LEASED`, a working per-WorkID idempotency check. | Its docstring says *"no scheduler … An OS/service wake can invoke this later, but is deliberately not installed here."* |
| `.github/workflows/cogoall-unattended-proof-pulse.yml` (`0a6f1660…`) | Hourly `:17` cron on GitHub-hosted runners with `permissions: contents: read`, a `concurrency` group, and a replay-equals-DONE assertion. | Runs on ephemeral cloud runners and keeps its DB in `$RUNNER_TEMP`. It is **not local** and does not survive a reboot. It proves CI replay logic, not a local loop. |
| `.github/workflows/coloops-safety.yml` (`e5076be1…`) | Push/PR-triggered regressions in `tests/gs_loop`, `tests/gs_receiver` | Not scheduled; not a runtime. |

**Gap against the contract.** Of its required items (elected lease, job state, heartbeat, receipt, retry/idempotency key, next trigger, recovery after reboot), the repos contain only *job state* and *per-WorkID idempotency/fencing*. They contain no elected actuator lease, no heartbeat with a reader, no persisted next trigger that anything consumes, no installed wake, and no reboot evidence.

## 2. Design principles

1. **Tick, not forever loop.** The OS scheduler starts a short-lived `coloop tick` that does bounded work and then exits. A `while($true)` loop does not survive reboot, logoff, or a crash, and leaves nothing for an auditor to check.
2. **One actuator, many watchers.** Only the holder of the current-epoch actuator lease may mutate. Watchers read the DB and never write work, effect, or lease rows.
3. **Every mutation is fenced by epoch.** A stale holder that wakes from sleep or SIGSTOP cannot write.
4. **Every external effect is keyed.** It happens at most once per idempotency key, and only a readback-verified receipt marks it done.
5. **Claims follow evidence.** A duration of unattended operation may be stated only up to a test rung that has passed (§4.5).

## 3. Components (to be built and installed later; not installed here)

State store: a single SQLite file in WAL mode with `synchronous=FULL`, located at `%LOCALAPPDATA%\CoLoop\state.sqlite` on Windows or `$XDG_STATE_HOME/coloop/state.sqlite` on Linux. Every write runs inside `BEGIN IMMEDIATE`.

```sql
CREATE TABLE actuator_lease (           -- exactly one row, name='coloop'
  name TEXT PRIMARY KEY, holder_id TEXT, epoch INTEGER NOT NULL,
  lease_until INTEGER NOT NULL, renewed_at INTEGER, boot_id TEXT);
CREATE TABLE heartbeat (
  holder_id TEXT, epoch INTEGER, seq INTEGER, wall_ts INTEGER, mono_ns INTEGER,
  boot_id TEXT, phase TEXT, last_work_id TEXT, next_trigger INTEGER,
  PRIMARY KEY (holder_id, epoch, seq));
CREATE TABLE effect (                   -- one row per idempotency key, ever
  idem_key TEXT PRIMARY KEY, work_id TEXT, epoch INTEGER,
  state TEXT CHECK (state IN ('INTENT','APPLIED','VERIFIED','FAILED')),
  receipt_sha256 TEXT, prev_receipt_sha256 TEXT, ts INTEGER);
-- work: reuse DueWorkQueue.work unchanged (per-WorkID lease + epoch fence).
```

- **holder_id** = `hostname:pid:start_ns`. **boot_id** = the Windows last-boot time (`Win32_OperatingSystem.LastBootUpTime`) or `/proc/sys/kernel/random/boot_id` on Linux.
- **Lease:** TTL `L = 90 s`, renewed every `R = 30 s`. To acquire: `UPDATE actuator_lease SET holder_id=?, epoch=epoch+1, lease_until=now+L WHERE name='coloop' AND (lease_until<=now OR holder_id=?)`, and succeed only if exactly one row changed. A renewal is the same statement guarded by `epoch=?`. Before any mutation the holder re-reads `epoch` and `lease_until > now` in the same transaction. If a renewal fails, the process exits without mutating.
- **Idempotency key:** `idem_key = sha256(work_id | source_revision | payload_sha256 | action_kind | target_uri)`. The effect protocol has four steps: (1) insert an `INTENT` row, where a PK conflict means the key was already seen and nothing is done; (2) perform the effect, passing `idem_key` to the receiver if it accepts one; (3) set `APPLIED`; (4) read back from the receiver, then set `VERIFIED` with `receipt_sha256`. On recovery, an `INTENT` or `APPLIED` row triggers a **readback before any retry**, never a blind re-send.
- **Heartbeat:** the actuator appends one row every `H = 30 s` while ticking, plus one row at tick start and one at tick exit (`phase = START|RUN|SLEEP_UNTIL`). The exit row carries `next_trigger`. A watcher reports `STALE` when `now − max(wall_ts) > 3H` and no `SLEEP_UNTIL` row covers the gap.
- **Wake (installation is a separate gated step, not done here):** on Windows, a Task Scheduler task with triggers *AtStartup*, *AtLogOn*, *every 5 min*, and *on resume*, plus "run whether user is logged on or not", "start when available", and "do not start a new instance". On Linux, a systemd `--user` timer with `Persistent=true`, `OnBootSec=1min`, and `OnUnitActiveSec=5min`. A tick runs only due work, so extra triggers cost nothing.
- **Receipts:** one JSON per tick in `receipts/`, hash-chained through `prev_receipt_sha256` and listing the lease epoch, boot_id, heartbeat seq range, and the effects VERIFIED.

## 4. Tests and pass criteria

All tests run against a scratch DB and a **local fake receiver** (an HTTP or file sink that counts deliveries per `idem_key`). No real external effect is involved. A test PASSes only if every listed criterion holds. Raw logs, the DB export, and their sha256 are kept for both PASS and FAIL runs, and FAILs are never deleted.

### 4.1 T-LEASE (elected lease)

| ID | Procedure | PASS iff |
|---|---|---|
| L1 contention | 8 processes call `acquire` simultaneously, for 1000 rounds | In every round exactly 1 acquire succeeds. Across all rounds, **0** instants have two rows with `lease_until > now` for different holders (checked from the acquire log). Epoch strictly increases by 1 per successful takeover. |
| L2 holder death | SIGKILL / `Stop-Process -Force` on the holder, 50 trials | A new holder acquires within `L + R = 120 s` of the kill in 50/50 trials, with epoch = old + 1. |
| L3 stale-holder fence | SIGSTOP the holder for `2L`, let another take over, then SIGCONT | The resumed process performs **0** writes to `work`, `effect`, or `heartbeat` under the old epoch (row diff = 0) and exits with code `LEASE_LOST`. |
| L4 watcher cannot actuate | Run the watcher binary with a forged mutation call | The mutation is rejected and the DB row diff is 0. |

### 4.2 T-IDEM (idempotency key)

| ID | Procedure | PASS iff |
|---|---|---|
| I1 replay | Run the same WorkID tick 10× | The fake receiver counts exactly **1** delivery per `idem_key`, and `effect` has 1 row in `VERIFIED`. |
| I2 crash points | Kill the actuator at each of the 4 protocol steps (before INTENT, after INTENT, after effect but before APPLIED, after APPLIED but before VERIFIED), 20 trials each, then restart | For every trial the receiver count is exactly 1 per key (or 0 if the kill came before the effect) and the final state is `VERIFIED` (or no row). **0** duplicate deliveries in 80 trials. |
| I3 key separation | Same `work_id`, changed `payload_sha256` | A distinct `idem_key` and exactly one new delivery. |
| I4 fence + key together | Bypass the lease and force two actuators onto one key | ≤ 1 delivery, and the loser records `FENCED` or a PK conflict. |

### 4.3 T-HB (heartbeat)

| ID | Procedure | PASS iff |
|---|---|---|
| H1 cadence | 60 min continuous ticking | Gap between consecutive heartbeat rows ≤ `2H = 60 s` (except gaps covered by a `SLEEP_UNTIL` row). `seq` is strictly monotone with 0 gaps within an epoch. |
| H2 staleness detection | SIGSTOP the holder with no `SLEEP_UNTIL` row | The watcher emits `STALE` within `3H + 30 s = 120 s`, 10/10 trials. |
| H3 no false STALE | 60 min run that includes declared sleeps | **0** `STALE` events. |
| H4 clock honesty | Compare `wall_ts` with an independent observer process's timestamps | Absolute skew ≤ 5 s. A backward wall-clock jump of more than 5 s is logged as `CLOCK_STEP`, and no lease is extended because of it. |

### 4.4 T-REBOOT (recovery after reboot, escalating idle)

Rungs (idle interval during which the machine is left alone with work scheduled to come due inside the interval): **R1 15 min → R2 1 h → R3 4 h → R4 12 h → R5 24 h → R6 72 h → R7 7 d.**

Each rung runs four variants: (a) clean reboot, (b) forced reset or power loss, (c) sleep/hibernate then resume, (d) reboot with no user logon. Before the idle starts, seed `N = 5` items whose `due_at` values are spread across the interval, one of them due during the downtime.

PASS for a variant iff **all** hold:
1. **Wake.** The first post-boot (or post-resume) heartbeat row appears ≤ 10 min after the OS boot or resume time. Boot time comes from Windows System log Event ID 12 (Kernel-General) or 6005, or from `journalctl --list-boots`. Resume time comes from Event ID 1 (Power-Troubleshooter) or the systemd sleep log.
2. **Lease.** Exactly 1 holder after recovery, with `boot_id` ≠ the pre-reboot `boot_id` and epoch > the pre-reboot epoch.
3. **Exactly-once catch-up.** All N items are `DONE`; the receiver count equals N, with 0 duplicates; no item ran before its `due_at`.
4. **Next trigger.** The last tick's exit heartbeat carries a `next_trigger` ≥ now, or null with the queue empty.
5. **Receipt chain.** The first post-boot receipt's `prev_receipt_sha256` equals the sha256 of the last pre-boot receipt. The chain verifies end to end.

**Rung progression.** A rung is PASSED after **3 consecutive** runs in which all four variants pass. Only then can the next rung start. Any failure resets that rung's count to 0 and keeps the FAIL bundle.

### 4.5 Claim rule

"Unattended for X" may be stated only if X ≤ the idle interval of the highest PASSED rung, and must cite the evidence bundle by path and sha256 (DB export, heartbeat CSV, receiver count log, OS boot/resume event export, receipt chain). **Current highest PASSED rung: none → no unattended-operation claim is permitted.**

### 4.6 Self-check of this document (required by W07 job)

- lease → §4.1 L1–L4, numeric PASS/FAIL ✔
- heartbeat → §4.3 H1–H4, numeric PASS/FAIL ✔
- reboot → §4.4 criteria 1–5 + rung rule ✔
- idempotency → §4.2 I1–I4, numeric PASS/FAIL ✔
- No claim of unattended operation without an evidence pointer: §0 and §4.5 assert none; §1 statements cite blob hashes and git readback ✔

## 5. Read-only inspection protocol (for a worker that does have a shell on the steward machine)

Run read-only and hash every output (`Get-FileHash` / `sha256sum`). Do not stop, disable, or start anything.

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -match '^Co|evo|loop|watch' -or ($_.Actions.Execute + $_.Actions.Arguments) -match 'Co[A-Z]|InSeed|forever|autoevo|waves' } |
  Select TaskName,TaskPath,State,@{n='Exec';e={$_.Actions.Execute + ' ' + $_.Actions.Arguments}}
Get-Service | Where-Object { $_.Name -match '^Co' -or $_.DisplayName -match '^Co' }
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'Co[A-Z]\w*\.ps1|forever-autoevo|auto-turns-waves|CoWatcher|coloop' } |
  Select ProcessId,ParentProcessId,CreationDate,CommandLine
Get-CimInstance Win32_StartupCommand | Select Name,Command,Location
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run','HKLM:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Select-String -Path $PROFILE.AllUsersAllHosts,$PROFILE.CurrentUserAllHosts,$PROFILE -Pattern 'Co[A-Z]|forever|watcher' -ErrorAction SilentlyContinue
Test-Path 'C:\Users\Owner\Desktop\InSeed\heartbeat.log'   # existence only => auto-turns-waves has run locally
```

Linux/macOS equivalents: `systemctl list-timers --all`, `systemctl --user list-timers --all`, `crontab -l`, `ls /etc/cron.*`, `launchctl list | grep -i co`, `ps -eo pid,lstart,args | grep -Ei 'co[A-Z]|forever|autoevo|coloop'`.

An inspection PASSes when every Co*-matching task, service, process, and startup entry is listed with its path, command line, creation time, and output hash, **or** the inspection states `NONE_FOUND` with the hashed command outputs attached.

## 6. Next gate

1. **Steward-local read-only inspection (§5)** by a worker with a shell on that machine. This replaces NO_LOCAL_ACCESS.
2. Authenticated read of InSeed Actions run history for `coevo-forever.yml` and `autoevo.yml`, to settle §1.2 (ran-and-failed vs. never-ran).
3. A steward decision on the §1.2 latent hazard (`permissions: {}` or removal). That change is outside W07's scope.
4. Build `coloop tick` on top of `DueWorkQueue`, then run §4.1–4.3 in CI. §4.4 needs the real machine and a separate install authority.
