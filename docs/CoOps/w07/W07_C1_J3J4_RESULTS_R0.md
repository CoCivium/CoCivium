# W07 cycle C1 — falsification, fixes, production-timing spot runs, tick (J3 / J4 / C2-J1)

Raw: `W07_C1_J3J4_RESULTS_R0.json`. Host: Claude cloud sandbox (Linux). **Not the steward machine. T-REBOOT NOT_RUN.** Reviewer: none independent. All runs are W07's own.

## Defects found (falsification) and fixed
| ID | What failed | Evidence | Fix |
|---|---|---|---|
| D3 | **Design-level.** A holder frozen *inside* a write transaction holds the SQLite write lock, so a lease-only takeover can never happen. | `L5_baseline`: takeover attempt → `database is locked` after 6 s | Bounded busy timeout ≤ R. A contender declares `STALE_LOCK` when the lease has expired and the lock has been held ≥ L. Policy is then HOLD, or a single SIGKILL of the recorded `holder_pid`, which rolls back the holder's open transaction. |
| D1 | Harness: a fixed 30 s wait is shorter than L = 90 s at production timing. | prod L2 crashed with `queue.Empty` | Wait = 2L + R + 30 |
| D2 | Harness: a non-detection was recorded as a sentinel of 99 s. Against the 120 s production bound, a **non-detection counted as PASS.** | first prod H2 run: `max_detect_s: 99, PASS: true` | Sentinel = ∞, plus an explicit detected count. R0's scaled H2 result still stands, because at a 2 s bound the sentinel would have failed. |
| D4 | Tick: no lease release on clean exit, so every other tick was wasted. The crash test silently skipped one of its two crash points. | T1 exit codes `0,3,9,3,0,3…`; `after_effect` never fired | Release the lease on clean exit. Re-arm each crash until it fires. T2 now checks that active windows don't overlap. |

## Results after fixes (all PASS)
| Test | Measured | Bound |
|---|---|---|
| L5 hold policy ×10 | STALE_LOCK detected ≤ 4.323 s; no takeover | ≤ L+R+1 = 5 s |
| L5 break policy ×10 | takeover ≤ 4.419 s; epoch +1; 0 uncommitted stale rows visible | ≤ 5 s |
| Regression L1–L4, I1–I4, H1–H4 (scaled) | identical properties to R0 (e.g. L2 max 3.03 s, H2 max 1.387 s, 10/10 detected) | as R0 |
| **L2 production timing** ×5 (L=90, R=30) | takeover max 89.549 s, mean 89.254 s; epoch +1 in 5/5 | ≤ 120 s |
| **H2 production timing** ×3 (H=30) | stale detected max 88.951 s, 3/3 detected | ≤ 120 s |
| T1 tick catch-up with crashes | both crash points fired; 5 deliveries for 5 items, 0 duplicates, 0 overdue, 12-receipt chain verifies | exactly-once |
| T2 tick concurrency 20 rounds × 4 | 78 ticks ran, 2 held, 78 epochs, **0 window overlaps**, 1 delivery | 0 overlaps |

## Challenge (what could still be false)
- **Same host clock.** All lease timing uses one machine's wall clock. Skew between machines is irrelevant here, because the lease is local-only by design. A wall-clock jump forward could expire a live holder early; fencing then makes that holder fail safe, but this path is untested.
- **Windows.** No Windows run has happened. `coloop_tick.py` falls back to the PowerShell `LastBootUpTime` as its boot id, which is untested. The Task Scheduler XML is a well-formed template and has never been imported.
- **Power loss.** WAL with `synchronous=FULL` should survive power loss, but only the reboot ladder (§4.4 of the design) on real hardware can show it.
- **Break policy.** Killing `holder_pid` assumes the pid has not been reused. Production should check the process start time against the lease row before killing.
- **Independence.** Every check was written and run by W07 alone. They count as one lineage, not three independent checks.

## C2-J6 addendum (`W07_C2_J6_RESULTS_R0.json`)
| Test | Measured | Result |
|---|---|---|
| L6 pid-reuse guard ×5 | The recorded holder start time is forged. The break policy reports `STALE_LOCK_UNVERIFIED` and HOLDs; 0 kills; the frozen holder is left untouched. | PASS |
| L7 forward clock jump ×10 | A contender whose clock jumped forward took over early in 10/10 trials. That is the expected **liveness cost**. The live original holder was fenced every time: 0 writes after takeover, and it exited LEASE_LOST. | PASS |
| Regression L1–L5, I1–I4, H1–H4 after the schema change | 13/13, with the three groups run concurrently | PASS |

The pid guard reads `/proc/<pid>/stat`. On Windows it returns None, so the break policy safely degrades to HOLD and never kills. A Windows start-time source (WMI `CreationDate`) is successor C2-J7.

## C2-J7 addendum (`W07_C2_J7_RESULTS_R0.json`): Windows parity, **NOT run on Windows**
- `proc_start` on Windows uses `GetProcessTimes`, the creation FILETIME, through ctypes. `coloop_tick.boot_id` on Windows derives from `GetTickCount64`. The tick no longer spawns PowerShell on every run.
- New `w07_platform_selftest.py`, P1–P5: on Linux every check passes, the guard is in KILL_ALLOWED_WITH_GUARD mode, and the tick end-to-end produced 1 delivery with a valid chain. The regression after the change also passes: L5–L7 and T1–T2.
- **Gate:** someone must run the self-test on a Windows host. Until P1–P4 pass there, Windows runs in HOLD_ONLY mode, meaning the break policy never kills.
- Known limits: a process that genuinely exits with code 259 looks alive. The Windows boot id can flap if the clock is stepped near a 60 s boundary, so the reboot ladder uses the OS event log for boot confirmation.
