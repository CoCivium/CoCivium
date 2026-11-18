#!/usr/bin/env python3
"""W07 reference harness for the CoLoop+ lease / idempotency / heartbeat design (R0).

Reference only: SQLite + local fake receiver, scratch files under a temp dir.
Installs nothing, schedules nothing, touches no network, performs no real external effect.
Timing is parameter-SCALED (L=3s, R=1s, H=0.5s) versus the design (L=90s, R=30s, H=30s);
bounds scale identically (takeover <= L+R, stale <= 4H, gap <= 2H).

usage: python3 -I w07_coloop_ref.py {lease|idem|hb|all} --out results.json
"""
from __future__ import annotations
import argparse, hashlib, json, multiprocessing as mp, os, random, signal, sqlite3, sys, tempfile, time

L, R, H = 3.0, 1.0, 0.5
SCHEMA = """
CREATE TABLE IF NOT EXISTS actuator_lease(name TEXT PRIMARY KEY, holder_id TEXT, epoch INTEGER NOT NULL,
  lease_until REAL NOT NULL, renewed_at REAL);
CREATE TABLE IF NOT EXISTS heartbeat(holder_id TEXT, epoch INTEGER, seq INTEGER, wall_ts REAL, phase TEXT,
  next_trigger REAL, PRIMARY KEY(holder_id, epoch, seq));
CREATE TABLE IF NOT EXISTS effect(idem_key TEXT PRIMARY KEY, work_id TEXT, epoch INTEGER,
  state TEXT CHECK(state IN ('INTENT','APPLIED','VERIFIED','FAILED')), receipt_sha256 TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS event(ts REAL, kind TEXT, detail TEXT);
"""
RECV = "CREATE TABLE IF NOT EXISTS delivery(idem_key TEXT, ts REAL, pid INTEGER);"


def connect(path):
    c = sqlite3.connect(path, timeout=30, isolation_level=None)
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=FULL")
    return c


def init(db, recv):
    c = connect(db); c.executescript(SCHEMA)
    c.execute("INSERT OR IGNORE INTO actuator_lease VALUES('coloop',NULL,0,0,NULL)"); c.close()
    r = connect(recv); r.executescript(RECV); r.close()


def acquire(c, holder, now, ttl=L):
    c.execute("BEGIN IMMEDIATE")
    cur = c.execute("""UPDATE actuator_lease SET holder_id=?,epoch=epoch+1,lease_until=?,renewed_at=?
                       WHERE name='coloop' AND lease_until<=?""", (holder, now + ttl, now, now))
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
        t_acq, ep = q.get(timeout=30); b.join()
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
        t = wait_for(lambda: time.time() if stale(db, time.time()) else None, 10, step=0.02)
        lat.append((t - ts) if t else 99); os.kill(a.pid, signal.SIGKILL); a.join()
    return dict(id="H2", trials=trials, bound_s=4 * H, max_detect_s=round(max(lat), 3), PASS=max(lat) <= 4 * H)


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


GROUPS = {"lease": [test_L1, test_L2, test_L3, test_L4], "idem": [test_I1, test_I2, test_I3, test_I4],
          "hb": [test_H1, test_H2, test_H3, test_H4]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("group", choices=[*GROUPS, "all"]); ap.add_argument("--out", required=True)
    a = ap.parse_args(); mp.set_start_method("fork")
    tests = [t for g in (GROUPS if a.group == "all" else [a.group]) for t in GROUPS[g]]
    out = dict(params=dict(L=L, R=R, H=H, scaled=True), python=sys.version.split()[0], started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), results=[])
    for t in tests:
        r = t(); out["results"].append(r); print(json.dumps(r), flush=True)
    out["all_pass"] = all(r["PASS"] for r in out["results"])
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(a.out, "w") as f: json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
