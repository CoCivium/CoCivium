#!/usr/bin/env python3
"""W07 reference harness for the CoLoop+ lease / idempotency / heartbeat design (R0).

Reference only: SQLite + local fake receiver, scratch files under a temp dir.
Installs nothing, schedules nothing, touches no network, performs no real external effect.
Timing is parameter-SCALED (L=3s, R=1s, H=0.5s) versus the design (L=90s, R=30s, H=30s);
bounds scale identically (takeover <= L+R, stale <= 4H, gap <= 2H).

usage: python3 -I w07_coloop_ref.py {lease|idem|hb|falsify|prod|all} --out results.json
"""
from __future__ import annotations
import argparse, hashlib, json, multiprocessing as mp, os, random, signal, sqlite3, sys, tempfile, time

L, R, H = (float(os.environ.get(k, d)) for k, d in (("W07_L", 3.0), ("W07_R", 1.0), ("W07_H", 0.5)))
SCHEMA = """
CREATE TABLE IF NOT EXISTS actuator_lease(name TEXT PRIMARY KEY, holder_id TEXT, epoch INTEGER NOT NULL,
  lease_until REAL NOT NULL, renewed_at REAL, holder_pid INTEGER, holder_start TEXT);
CREATE TABLE IF NOT EXISTS heartbeat(holder_id TEXT, epoch INTEGER, seq INTEGER, wall_ts REAL, phase TEXT,
  next_trigger REAL, PRIMARY KEY(holder_id, epoch, seq));
CREATE TABLE IF NOT EXISTS effect(idem_key TEXT PRIMARY KEY, work_id TEXT, epoch INTEGER,
  state TEXT CHECK(state IN ('INTENT','APPLIED','VERIFIED','FAILED')), receipt_sha256 TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS event(ts REAL, kind TEXT, detail TEXT);
"""
RECV = "CREATE TABLE IF NOT EXISTS delivery(idem_key TEXT, ts REAL, pid INTEGER);"


def connect(path, timeout=30.0):
    c = sqlite3.connect(path, timeout=timeout, isolation_level=None)
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=FULL")
    return c


def init(db, recv):
    c = connect(db); c.executescript(SCHEMA)
    c.execute("INSERT OR IGNORE INTO actuator_lease VALUES('coloop',NULL,0,0,NULL,NULL,NULL)"); c.close()
    r = connect(recv); r.executescript(RECV); r.close()


def proc_start(pid):
    """Process start time (clock ticks since boot, /proc/<pid>/stat field 22); None if gone. Guards against pid reuse."""
    try:
        return open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def acquire(c, holder, now, ttl=L):
    c.execute("BEGIN IMMEDIATE")
    cur = c.execute("""UPDATE actuator_lease SET holder_id=?,epoch=epoch+1,lease_until=?,renewed_at=?,holder_pid=?,holder_start=?
                       WHERE name='coloop' AND lease_until<=?""", (holder, now + ttl, now, os.getpid(), proc_start(os.getpid()), now))
    ep = c.execute("SELECT epoch FROM actuator_lease").fetchone()[0] if cur.rowcount == 1 else None
    c.execute("COMMIT"); return ep


def renew(c, holder, epoch, now, ttl=L):
    c.execute("BEGIN IMMEDIATE")
    row = c.execute("SELECT holder_id,epoch,lease_until,renewed_at FROM actuator_lease").fetchone()
    if row[3] is not None and now < row[3] - 5:          # backward wall-clock step > 5 s
        c.execute("INSERT INTO event VALUES(?,?,?)", (now, "CLOCK_STEP", f"{row[3]}->{now}"))
        c.execute("COMMIT"); return "CLOCK_STEP"
    cur = c.execute("""UPDATE actuator_lease SET lease_until=?,renewed_at=? WHERE holder_id=? AND epoch=?
                       AND lease_until>?""", (now + ttl, now, holder, epoch, now))
    c.execute("COMMIT"); return "OK" if cur.rowcount == 1 else "LEASE_LOST"


def fenced(c, holder, epoch, sql, params, fence=True):
    """Single transaction: verify current lease, then mutate. Returns OK / FENCED / CONFLICT."""
    c.execute("BEGIN IMMEDIATE")
    if fence:
        row = c.execute("SELECT holder_id,epoch,lease_until FROM actuator_lease").fetchone()
        if not (row[0] == holder and row[1] == epoch and row[2] > time.time()):
            c.execute("ROLLBACK"); return "FENCED"
    try:
        c.execute(sql, params)
    except sqlite3.IntegrityError:
        c.execute("ROLLBACK"); return "CONFLICT"
    c.execute("COMMIT"); return "OK"


def idem_key(work_id, source_rev, payload_sha, action, target):
    return hashlib.sha256("|".join([work_id, source_rev, payload_sha, action, target]).encode()).hexdigest()


def deliver(recv, key):
    r = connect(recv); r.execute("INSERT INTO delivery VALUES(?,?,?)", (key, time.time(), os.getpid())); r.close()


def readback(recv, key):
    r = connect(recv); n = r.execute("SELECT count(*) FROM delivery WHERE idem_key=?", (key,)).fetchone()[0]; r.close()
    return n


def effect(c, recv, holder, epoch, key, work_id, crash_at=None, fence=True):
    def crash(point):
        if crash_at == point: os._exit(9)
    row = c.execute("SELECT state FROM effect WHERE idem_key=?", (key,)).fetchone()
    if row and row[0] == "VERIFIED":
        return "ALREADY_VERIFIED"
    if row is None:
        crash("before_intent")
        s = fenced(c, holder, epoch, "INSERT INTO effect VALUES(?,?,?,'INTENT',NULL,?)",
                   (key, work_id, epoch, time.time()), fence)
        if s != "OK": return s
        crash("after_intent")
        deliver(recv, key)
        crash("after_effect")
        fenced(c, holder, epoch, "UPDATE effect SET state='APPLIED' WHERE idem_key=?", (key,), fence)
        crash("after_applied")
        outcome = "APPLIED_NEW"
    else:                                   # INTENT or APPLIED left by a crash: readback before any retry
        if readback(recv, key) == 0:
            deliver(recv, key)
        fenced(c, holder, epoch, "UPDATE effect SET state='APPLIED' WHERE idem_key=?", (key,), fence)
        outcome = "RECOVERED"
    if readback(recv, key) >= 1:
        rc = hashlib.sha256(f"{key}|{epoch}".encode()).hexdigest()
        fenced(c, holder, epoch, "UPDATE effect SET state='VERIFIED',receipt_sha256=? WHERE idem_key=?", (rc, key), fence)
    return outcome


def hb(c, holder, epoch, seq, phase, next_trigger=None):
    return fenced(c, holder, epoch, "INSERT INTO heartbeat VALUES(?,?,?,?,?,?)",
                  (holder, epoch, seq, time.time(), phase, next_trigger))


def actuator(db, holder, sleep_every=0, sleep_s=0.0):
    """Long-running test actuator: acquire, then renew/heartbeat until lease lost (exit 3)."""
    c = connect(db)
    while (ep := acquire(c, holder, time.time())) is None:
        time.sleep(0.1)
    seq, last = 0, time.time()
    if hb(c, holder, ep, seq, "START") != "OK": os._exit(3)
    while True:
        now = time.time()
        if now - last >= R:
            if renew(c, holder, ep, now) != "OK": os._exit(3)
            last = now
        seq += 1
        if sleep_every and seq % sleep_every == 0:
            if renew(c, holder, ep, time.time()) != "OK": os._exit(3)
            last = time.time()
            if hb(c, holder, ep, seq, "SLEEP_UNTIL", time.time() + sleep_s) != "OK": os._exit(3)
            time.sleep(sleep_s); continue
        if hb(c, holder, ep, seq, "RUN") != "OK": os._exit(3)
        time.sleep(H)


def lease_state(db):
    c = connect(db); r = c.execute("SELECT holder_id,epoch,lease_until FROM actuator_lease").fetchone(); c.close(); return r


def fresh():
    d = tempfile.mkdtemp(prefix="w07-"); db, recv = os.path.join(d, "s.sqlite"), os.path.join(d, "r.sqlite")
    init(db, recv); return db, recv


def wait_for(pred, timeout, step=0.05):
    end = time.time() + timeout
    while time.time() < end:
        v = pred()
        if v: return v
        time.sleep(step)
    return None


# ---------------- T-LEASE ----------------
def _l1_worker(db, holder, rounds, barrier, q):
    c = connect(db); wins = []
    for rnd in range(rounds):
        barrier.wait()
        now = 1_000_000 + rnd * (L + 1)      # logical clock: previous lease always expired at round start
        if acquire(c, holder, now) is not None: wins.append(rnd)
        barrier.wait()
    q.put((holder, wins))


def test_L1(rounds=1000, n=8):
    db, _ = fresh(); b = mp.Barrier(n); q = mp.Queue()
    ps = [mp.Process(target=_l1_worker, args=(db, f"p{i}", rounds, b, q)) for i in range(n)]
    [p.start() for p in ps]; res = [q.get() for _ in ps]; [p.join() for p in ps]
    per = [0] * rounds
    for _, w in res:
        for r in w: per[r] += 1
    epoch = lease_state(db)[1]
    ok = all(x == 1 for x in per) and epoch == rounds
    return dict(id="L1", rounds=rounds, contenders=n, rounds_with_exactly_one_winner=sum(x == 1 for x in per),
                max_winners_in_a_round=max(per), final_epoch=epoch, PASS=ok)


def _contender(db, q):
    c = connect(db)
    while (ep := acquire(c, "B", time.time())) is None: time.sleep(0.1)
    q.put((time.time(), ep))


def test_L2(trials=50):
    deltas, ep_ok = [], 0
    for _ in range(trials):
        db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start()
        wait_for(lambda: lease_state(db)[0] == "A", 5); ep0 = lease_state(db)[1]
        q = mp.Queue(); b = mp.Process(target=_contender, args=(db, q)); b.start()
        time.sleep(random.uniform(0, 2)); tk = time.time(); os.kill(a.pid, signal.SIGKILL); a.join()
        t_acq, ep = q.get(timeout=2 * L + R + 30); b.join()
        deltas.append(t_acq - tk); ep_ok += (ep == ep0 + 1)
    ok = max(deltas) <= L + R and ep_ok == trials
    return dict(id="L2", trials=trials, bound_s=L + R, max_takeover_s=round(max(deltas), 3),
                mean_takeover_s=round(sum(deltas) / trials, 3), epoch_plus_one=ep_ok, PASS=ok)


def test_L3(trials=20):
    exits, writes_after, blocked = [], 0, 0
    for _ in range(trials):
        db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start()
        wait_for(lambda: lease_state(db)[0] == "A", 5); epA = lease_state(db)[1]
        time.sleep(random.uniform(0.2, 1.5)); os.kill(a.pid, signal.SIGSTOP)
        b = mp.Process(target=actuator, args=(db, "B")); b.start()
        if not wait_for(lambda: lease_state(db)[0] == "B", 2 * L + 1):
            blocked += 1
        t_take = time.time()
        time.sleep(max(0.0, 2 * L - (time.time() - t_take)))
        os.kill(a.pid, signal.SIGCONT); a.join(10); exits.append(a.exitcode)
        c = connect(db)
        writes_after += c.execute("SELECT count(*) FROM heartbeat WHERE holder_id='A' AND epoch=? AND wall_ts>=?",
                                  (epA, t_take)).fetchone()[0]
        c.close(); b.kill(); b.join()
    ok = all(e == 3 for e in exits) and writes_after == 0 and blocked == 0
    return dict(id="L3", trials=trials, stale_holder_exit_LEASE_LOST=sum(e == 3 for e in exits),
                stale_writes_after_takeover=writes_after, takeover_blocked_by_stopped_txn=blocked, PASS=ok)


def test_L4():
    db, recv = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start()
    wait_for(lambda: lease_state(db)[0] == "A", 5)
    c = connect(db); before = c.execute("SELECT count(*) FROM effect").fetchone()[0]
    ep = lease_state(db)[1]
    r1 = fenced(c, "watcher", ep, "INSERT INTO effect VALUES('x','w',?, 'INTENT',NULL,0)", (ep,))
    r2 = fenced(c, "watcher", ep + 1, "INSERT INTO effect VALUES('x','w',?, 'INTENT',NULL,0)", (ep,))
    after = c.execute("SELECT count(*) FROM effect").fetchone()[0]; c.close(); a.kill(); a.join()
    return dict(id="L4", forged_same_epoch=r1, forged_future_epoch=r2, row_diff=after - before,
                PASS=(r1 == r2 == "FENCED" and after == before))


# ---- L5 (J3 falsification): holder frozen INSIDE a write transaction ----
def _stuck_holder(db, forge_start=False):
    c = connect(db); ep = acquire(c, "A", time.time())
    if forge_start:                                    # simulate pid reuse: recorded start time no longer matches
        c.execute("UPDATE actuator_lease SET holder_start='forged'")
    for seq in range(3):
        hb(c, "A", ep, seq, "RUN"); time.sleep(H)
    c.execute("BEGIN IMMEDIATE")                       # holds the SQLite write lock
    c.execute("INSERT INTO heartbeat VALUES('A',?,99,?,'RUN',NULL)", (ep, time.time()))
    os.kill(os.getpid(), signal.SIGSTOP)               # frozen before COMMIT
    c.execute("COMMIT")


def acquire_or_break(db, holder, break_policy, q):
    """Contender with bounded busy timeout. STALE_LOCK = lease expired AND write lock held >= L.
    break_policy=True: SIGKILL the recorded holder_pid once (its open txn rolls back), then retry.
    break_policy=False: report STALE_LOCK and HOLD (no takeover)."""
    c = connect(db, timeout=min(R, 1.0)); first_lock = None; events = []; broke = False
    while True:
        now = time.time()
        try:
            ep = acquire(c, holder, now)
            if ep is not None:
                q.put(dict(t=time.time(), ep=ep, events=events)); return
            first_lock = None
        except sqlite3.OperationalError as e:
            if "locked" not in str(e): raise
            try: c.execute("ROLLBACK")
            except sqlite3.OperationalError: pass
            now = time.time(); first_lock = first_lock or now
            hid, _ep, lu, pid, pstart = c.execute(
                "SELECT holder_id,epoch,lease_until,holder_pid,holder_start FROM actuator_lease").fetchone()
            if lu <= now and now - first_lock >= L:
                if not events: events.append(dict(kind="STALE_LOCK", t=now, holder_pid=pid))
                if not break_policy:
                    q.put(dict(t=None, events=events)); return
                if not broke:
                    if pstart is None or proc_start(pid) != pstart:      # pid gone or reused: never kill
                        events.append(dict(kind="STALE_LOCK_UNVERIFIED", t=time.time(), pid=pid))
                        q.put(dict(t=None, events=events)); return
                    os.kill(pid, signal.SIGKILL); broke = True; events.append(dict(kind="BREAK_KILL", t=time.time(), pid=pid))
        time.sleep(0.1)


def _proc_state(pid):
    try:
        return open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[0]
    except OSError:
        return None


def test_L5(trials=10):
    bound = L + R + 1.0; out = {}
    for policy in (False, True):
        lat, ok_n, stale_rows = [], 0, 0
        for _ in range(trials):
            db, _ = fresh(); a = mp.Process(target=_stuck_holder, args=(db,)); a.start()
            wait_for(lambda: _proc_state(a.pid) == "T", 10, step=0.01); t_stop = time.time(); ep0 = lease_state(db)[1]
            q = mp.Queue(); b = mp.Process(target=acquire_or_break, args=(db, "B", policy, q)); b.start()
            res = q.get(timeout=4 * L + 20); b.join()
            if policy:
                d = res["t"] - t_stop; a.join(5)
                c = connect(db); stale_rows += c.execute("SELECT count(*) FROM heartbeat WHERE holder_id='A' AND seq=99").fetchone()[0]; c.close()
                ok = res["ep"] == ep0 + 1 and a.exitcode == -9 and d <= bound
            else:
                d = res["events"][0]["t"] - t_stop if res["events"] else float("inf")
                ok = res["t"] is None and lease_state(db)[0] == "A" and d <= bound
                os.kill(a.pid, signal.SIGKILL); a.join()
            lat.append(d); ok_n += ok
        key = "break_policy" if policy else "hold_policy"
        out[key] = dict(trials=trials, passed=ok_n, max_latency_s=round(max(lat), 3), bound_s=bound,
                        **({"uncommitted_stale_rows_visible": stale_rows} if policy else {}))
    out["finding"] = ("A holder frozen inside BEGIN IMMEDIATE blocks every writer indefinitely; the R0 harness's "
                      "30 s busy timeout + lease-only takeover cannot make progress. Fix: bounded busy timeout, "
                      "STALE_LOCK detection, then HOLD or a single kill of the recorded holder_pid.")
    ok = all(out[k]["passed"] == trials for k in ("hold_policy", "break_policy")) and out["break_policy"]["uncommitted_stale_rows_visible"] == 0
    return dict(id="L5", **out, PASS=ok)


def test_L6(trials=5):
    """C2-J6: break policy must refuse to kill when the recorded holder start time does not match (pid reuse)."""
    ok_n, kills = 0, 0
    for _ in range(trials):
        db, _ = fresh(); a = mp.Process(target=_stuck_holder, args=(db, True)); a.start()
        wait_for(lambda: _proc_state(a.pid) == "T", 10, step=0.01)
        q = mp.Queue(); b = mp.Process(target=acquire_or_break, args=(db, "B", True, q)); b.start()
        res = q.get(timeout=4 * L + 20); b.join()
        kinds = [e["kind"] for e in res["events"]]; alive = _proc_state(a.pid) == "T"
        kills += "BREAK_KILL" in kinds
        ok_n += res["t"] is None and "STALE_LOCK_UNVERIFIED" in kinds and "BREAK_KILL" not in kinds and alive
        os.kill(a.pid, signal.SIGKILL); a.join()
    return dict(id="L6_pid_reuse_guard", trials=trials, passed=ok_n, kills=kills, PASS=ok_n == trials and kills == 0)


def _jumped_contender(db, q):
    c = connect(db); now = time.time() + L + 1          # this process's clock jumped forward past the lease
    q.put((time.time(), acquire(c, "B", now)))


def test_L7(trials=10):
    """C2-J6: a forward wall-clock jump in a contender causes premature takeover. Safety requirement: the live
    original holder is fenced (0 writes after takeover, exits LEASE_LOST)."""
    ok_n, stale_writes, premature = 0, 0, 0
    for _ in range(trials):
        db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start()
        wait_for(lambda: lease_state(db)[0] == "A", 5); epA = lease_state(db)[1]; time.sleep(random.uniform(0.2, 1.0))
        q = mp.Queue(); b = mp.Process(target=_jumped_contender, args=(db, q)); b.start(); t_take, epB = q.get(timeout=30); b.join()
        premature += epB is not None
        a.join(R + H + 5); code = a.exitcode
        if code is None: a.kill(); a.join()
        c = connect(db)
        n = c.execute("SELECT count(*) FROM heartbeat WHERE holder_id='A' AND epoch=? AND wall_ts>?", (epA, t_take)).fetchone()[0]; c.close()
        stale_writes += n; ok_n += epB == epA + 1 and code == 3 and n == 0
    return dict(id="L7_forward_clock_jump", trials=trials, premature_takeovers=premature, stale_writes_after_takeover=stale_writes,
                passed=ok_n, note="liveness cost: a forward jump forces an early takeover; safety (fencing) must hold",
                PASS=ok_n == trials and stale_writes == 0)


def test_L5_baseline():
    """Falsifier: R0 behavior (plain acquire, 30 s busy timeout) against a holder frozen in-transaction."""
    db, _ = fresh(); a = mp.Process(target=_stuck_holder, args=(db,)); a.start()
    wait_for(lambda: _proc_state(a.pid) == "T", 10, step=0.01); t0 = time.time()
    c = connect(db, timeout=2 * L)
    try:
        r = acquire(c, "B", time.time()); outcome = f"acquired epoch {r}" if r else "not acquired"
    except sqlite3.OperationalError as e:
        outcome = f"OperationalError: {e}"
    waited = time.time() - t0; os.kill(a.pid, signal.SIGKILL); a.join()
    blocked = outcome.startswith("OperationalError")
    return dict(id="L5_baseline", expectation="R0 takeover blocked (falsifies R0 liveness)", waited_s=round(waited, 3),
                outcome=outcome, r0_liveness_falsified=blocked, PASS=blocked)


# ---------------- T-IDEM ----------------
def _hold(db):
    c = connect(db); ep = acquire(c, "A", time.time(), ttl=3600); return c, ep


def test_I1():
    db, recv = fresh(); c, ep = _hold(db)
    k = idem_key("W1", "rev1", "p1", "post", "fake://recv")
    outs = [effect(c, recv, "A", ep, k, "W1") for _ in range(10)]
    st = c.execute("SELECT state FROM effect WHERE idem_key=?", (k,)).fetchone()[0]
    return dict(id="I1", runs=10, deliveries=readback(recv, k), final_state=st, outcomes=sorted(set(outs)),
                PASS=readback(recv, k) == 1 and st == "VERIFIED")


def _crash_run(db, recv, k, point):
    c, ep = _hold(db); effect(c, recv, "A", ep, k, "W1", crash_at=point)


def test_I2(trials=20):
    points = ["before_intent", "after_intent", "after_effect", "after_applied"]; bad = []; total = 0
    for pt in points:
        for _ in range(trials):
            db, recv = fresh(); k = idem_key("W1", "rev1", "p1", "post", "fake://recv")
            p = mp.Process(target=_crash_run, args=(db, recv, k, pt)); p.start(); p.join()
            crashed_count = readback(recv, k)
            c = connect(db)
            c.execute("UPDATE actuator_lease SET lease_until=0")           # crashed holder's lease expires
            ep = acquire(c, "A2", time.time(), ttl=3600)
            effect(c, recv, "A2", ep, k, "W1")
            n = readback(recv, k); st = c.execute("SELECT state FROM effect WHERE idem_key=?", (k,)).fetchone()
            total += 1
            if p.exitcode != 9 or n != 1 or (st is None or st[0] != "VERIFIED"):
                bad.append(dict(point=pt, exit=p.exitcode, at_crash=crashed_count, final=n, state=st))
            c.close()
    return dict(id="I2", trials=total, failures=len(bad), failure_detail=bad[:5],
                note="kill injected via os._exit(9) at each protocol step, then recovery tick by new holder",
                PASS=not bad)


def test_I3():
    db, recv = fresh(); c, ep = _hold(db)
    k1 = idem_key("W1", "rev1", "p1", "post", "fake://recv"); k2 = idem_key("W1", "rev1", "p2", "post", "fake://recv")
    effect(c, recv, "A", ep, k1, "W1"); effect(c, recv, "A", ep, k2, "W1")
    return dict(id="I3", keys_distinct=k1 != k2, deliveries_k1=readback(recv, k1), deliveries_k2=readback(recv, k2),
                PASS=k1 != k2 and readback(recv, k1) == 1 and readback(recv, k2) == 1)


def _race(db, recv, k, barrier, q):
    c = connect(db); barrier.wait(); q.put(effect(c, recv, "X", 0, k, "W1", fence=False))


def test_I4(trials=50):
    worst, conflicts = 0, 0
    for _ in range(trials):
        db, recv = fresh(); k = idem_key("W1", "rev1", "p1", "post", "fake://recv")
        b = mp.Barrier(2); q = mp.Queue()
        ps = [mp.Process(target=_race, args=(db, recv, k, b, q)) for _ in range(2)]
        [p.start() for p in ps]; outs = [q.get() for _ in ps]; [p.join() for p in ps]
        worst = max(worst, readback(recv, k)); conflicts += outs.count("CONFLICT") + outs.count("ALREADY_VERIFIED")
    return dict(id="I4", trials=trials, max_deliveries_per_key=worst, loser_conflict_or_already=conflicts,
                note="lease bypassed (fence=False); INTENT primary key is the only guard",
                PASS=worst <= 1 and conflicts == trials)


# ---------------- T-HB ----------------
def stale(db, now):
    c = connect(db)
    row = c.execute("SELECT wall_ts,phase,next_trigger FROM heartbeat ORDER BY wall_ts DESC LIMIT 1").fetchone(); c.close()
    if row is None: return False
    ts, phase, nt = row
    if phase == "SLEEP_UNTIL" and nt is not None and now <= nt + 3 * H: return False
    return now - ts > 3 * H


def test_H1(seconds=60):
    db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start(); time.sleep(seconds); a.kill(); a.join()
    c = connect(db); rows = c.execute("SELECT seq,wall_ts FROM heartbeat ORDER BY seq").fetchall(); c.close()
    gaps = [b[1] - a_[1] for a_, b in zip(rows, rows[1:])]; seqs = [r[0] for r in rows]
    ok = max(gaps) <= 2 * H and seqs == list(range(len(seqs)))
    return dict(id="H1", seconds=seconds, heartbeats=len(rows), max_gap_s=round(max(gaps), 3), bound_s=2 * H,
                seq_contiguous=seqs == list(range(len(seqs))), PASS=ok)


def test_H2(trials=10):
    lat = []
    for _ in range(trials):
        db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start()
        wait_for(lambda: lease_state(db)[0] == "A", 5); time.sleep(random.uniform(0.5, 2))
        os.kill(a.pid, signal.SIGSTOP); ts = time.time()
        t = wait_for(lambda: time.time() if stale(db, time.time()) else None, 4 * H + 30, step=0.02)
        lat.append((t - ts) if t else float("inf")); os.kill(a.pid, signal.SIGKILL); a.join()
    return dict(id="H2", trials=trials, bound_s=4 * H, max_detect_s=(round(max(lat), 3) if max(lat) != float("inf") else "NOT_DETECTED"), detected=sum(x != float("inf") for x in lat), PASS=all(x <= 4 * H for x in lat))


def test_H3(seconds=30):
    db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A", 5, 2.0)); a.start()
    wait_for(lambda: lease_state(db)[0] == "A", 5); end = time.time() + seconds; false = 0; polls = 0
    while time.time() < end:
        false += stale(db, time.time()); polls += 1; time.sleep(0.05)
    a.kill(); a.join()
    c = connect(db); sleeps = c.execute("SELECT count(*) FROM heartbeat WHERE phase='SLEEP_UNTIL'").fetchone()[0]; c.close()
    return dict(id="H3", seconds=seconds, declared_sleeps=sleeps, polls=polls, false_stale=false,
                PASS=false == 0 and sleeps >= 3)


def test_H4():
    db, _ = fresh(); a = mp.Process(target=actuator, args=(db, "A")); a.start()
    wait_for(lambda: lease_state(db)[0] == "A", 5); skews = []; seen = -1; end = time.time() + 10
    while time.time() < end:
        c = connect(db); r = c.execute("SELECT seq,wall_ts FROM heartbeat ORDER BY seq DESC LIMIT 1").fetchone(); c.close()
        if r and r[0] != seen: seen = r[0]; skews.append(abs(time.time() - r[1]))
        time.sleep(0.02)
    a.kill(); a.join()
    db2, _ = fresh(); c = connect(db2); t0 = time.time(); ep = acquire(c, "A", t0)
    renew(c, "A", ep, t0 + 1); lu_before = lease_state(db2)[2]
    step = renew(c, "A", ep, t0 - 10); lu_after = lease_state(db2)[2]
    ev = c.execute("SELECT count(*) FROM event WHERE kind='CLOCK_STEP'").fetchone()[0]; c.close()
    ok = max(skews) <= 5 and step == "CLOCK_STEP" and lu_after == lu_before and ev == 1
    return dict(id="H4", samples=len(skews), max_skew_s=round(max(skews), 3),
                note="observer shares the host clock, so skew bound is weak here; clock-step path is the real check",
                clock_step_result=step, lease_extended_on_step=lu_after != lu_before, PASS=ok)


GROUPS = {"lease": [test_L1, test_L2, test_L3, test_L4, test_L5],
          "falsify": [test_L5_baseline, test_L5, test_L6, test_L7],
          "prod": [test_L2, test_H2], "idem": [test_I1, test_I2, test_I3, test_I4],
          "hb": [test_H1, test_H2, test_H3, test_H4]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("group", choices=[*GROUPS, "all"]); ap.add_argument("--out", required=True)
    a = ap.parse_args(); mp.set_start_method("fork")
    tests = [t for g in ([g for g in GROUPS if g not in ("falsify", "prod")] if a.group == "all" else [a.group]) for t in GROUPS[g]]
    out = dict(params=dict(L=L, R=R, H=H, scaled=True), python=sys.version.split()[0], started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), results=[])
    for t in tests:
        r = t(); out["results"].append(r); print(json.dumps(r), flush=True)
    out["all_pass"] = all(r["PASS"] for r in out["results"])
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(a.out, "w") as f: json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
