# W07 — reference harness results (R0)

- Harness: `docs/CoOps/w07/w07_coloop_ref.py`, sha256 `e8d826ca26db6999790056f595fd41c5a04b4d3000194b8b806594722ed34562`
- Raw results: `docs/CoOps/w07/W07_REF_RESULTS_R0.json`, sha256 `7792155984a6e15ae27381fc1cc231162b05e68fc63f5221a4290365b2c8517c`
- Host: Claude cloud sandbox (Linux 6.18, Python 3). This is **not the steward machine**.
- Timing was parameter-scaled from the design (L=90 s, R=30 s, H=30 s) to **L=3 s, R=1 s, H=0.5 s**. Each bound was scaled the same way: takeover ≤ L+R = 4 s, heartbeat gap ≤ 2H = 1 s, stale detection ≤ 4H = 2 s.
- Reproduce: `python3 -I w07_coloop_ref.py {lease|idem|hb} --out <file>.json`. The harness uses scratch temp dirs and a local fake receiver. It needs no network and installs nothing.

| Test | Measured | Bound | Result |
|---|---|---|---|
| L1 contention, 8 × 1000 rounds | 1000/1000 rounds had exactly 1 winner; final epoch 1000 | exactly 1 per round | PASS |
| L2 SIGKILL takeover, 50 trials | max 3.053 s, mean 2.589 s; epoch +1 in 50/50 | ≤ 4 s | PASS |
| L3 SIGSTOP stale holder, 20 trials | 20/20 exited LEASE_LOST; 0 stale writes; 0 blocked takeovers | 0 writes | PASS |
| L4 forged watcher mutation | FENCED (same and future epoch); row diff 0 | rejected, diff 0 | PASS |
| I1 replay ×10 | 1 delivery, state VERIFIED | exactly 1 | PASS |
| I2 crash at 4 steps × 20 trials | 0 failures in 80 trials | 0 duplicates | PASS |
| I3 key separation | distinct keys, 1 delivery each | distinct, 1 each | PASS |
| I4 forced race, lease bypassed, 50 trials | max 1 delivery per key; loser got CONFLICT/ALREADY in 50/50 | ≤ 1 | PASS |
| H1 cadence, 60 s | 121 heartbeats, max gap 0.505 s, seq contiguous | ≤ 1 s | PASS |
| H2 stale detection, 10 trials | max 1.495 s | ≤ 2 s | PASS |
| H3 declared sleeps, 30 s | 7 sleeps, 592 polls, 0 false STALE | 0 | PASS |
| H4 clock | max skew 0.048 s; a 10 s backward step returned CLOCK_STEP and did not extend the lease | ≤ 5 s; no extension | PASS |

## Limits (nonclaims)

- These results show the **design logic** at scaled timing on one Linux host. They prove nothing about Windows Task Scheduler, the steward machine, or the production parameters.
- **T-REBOOT (§4.4) was not run.** No rung has passed, so no unattended-operation claim is allowed.
- H4's skew check is weak because the observer and the actuator share one clock. Only the clock-step path is a real check.
- Residual risk seen in code review but not in the 20 L3 trials: a holder frozen *inside* a `BEGIN IMMEDIATE` transaction holds the SQLite write lock, which delays takeover by up to the busy timeout (30 s). A production tick must keep transactions short and treat a lock wait longer than L as STALE_LOCK. L3 should get a targeted trial that stops the holder mid-transaction.
- The fake receiver counts deliveries locally. The protocol relies on a real receiver either accepting the idempotency key or supporting readback; each real receiver needs its own test.
- Reviewer: none independent. These are self-run by W07.
