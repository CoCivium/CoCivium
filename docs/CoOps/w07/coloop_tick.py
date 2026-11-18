#!/usr/bin/env python3
"""coloop_tick R0 — one-shot CoLoop+ tick (W07 candidate; NOT installed, NOT scheduled by this file).

Each invocation: elect/renew the actuator lease (bounded busy timeout, STALE_LOCK -> HOLD), write START heartbeat,
run every due work item exactly once through the INTENT->APPLIED->VERIFIED effect protocol, append one
hash-chained receipt, write SLEEP_UNTIL heartbeat with next_trigger, release the lease, exit. A crashed tick
leaves its lease to expire after L.

Effects go only to a local file receiver (receiver/<idem_key>.done); no network, no external writes.

  python3 -I coloop_tick.py --state DIR enqueue WORK_ID PAYLOAD DUE_UNIX
  python3 -I coloop_tick.py --state DIR tick [--crash-at STEP]
  python3 -I coloop_tick.py --state DIR verify
Exit codes: 0 ok, 3 LEASE_LOST/held by other, 4 STALE_LOCK hold, 5 verify failed.
"""
import argparse, hashlib, json, os, socket, sqlite3, sys, time

L, R = float(os.environ.get("COLOOP_L", 90)), float(os.environ.get("COLOOP_R", 30))
SCHEMA = """
CREATE TABLE IF NOT EXISTS actuator_lease(name TEXT PRIMARY KEY, holder_id TEXT, epoch INTEGER NOT NULL,
  lease_until REAL NOT NULL, renewed_at REAL, holder_pid INTEGER, boot_id TEXT);
CREATE TABLE IF NOT EXISTS work(work_id TEXT PRIMARY KEY, payload_sha256 TEXT, due_at REAL, state TEXT DEFAULT 'PENDING');
CREATE TABLE IF NOT EXISTS effect(idem_key TEXT PRIMARY KEY, work_id TEXT, epoch INTEGER, state TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS heartbeat(holder_id TEXT, epoch INTEGER, seq INTEGER, wall_ts REAL, boot_id TEXT,
  phase TEXT, next_trigger REAL, PRIMARY KEY(holder_id, epoch, seq));
CREATE TABLE IF NOT EXISTS receipt(n INTEGER PRIMARY KEY, sha256 TEXT, prev_sha256 TEXT, body TEXT);
"""


def boot_id():
    try:
        return open("/proc/sys/kernel/random/boot_id").read().strip()
    except OSError:                                   # Windows: last boot time stands in for boot id
        try:
            import subprocess
            return subprocess.run(["powershell", "-NoProfile", "-Command",
                                   "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('o')"],
                                  capture_output=True, text=True, timeout=20).stdout.strip() or "unknown"
        except Exception:
            return "unknown"


def db(state):
    os.makedirs(os.path.join(state, "receiver"), exist_ok=True)
    c = sqlite3.connect(os.path.join(state, "state.sqlite"), timeout=min(R, 5.0), isolation_level=None)
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=FULL"); c.executescript(SCHEMA)
    c.execute("INSERT OR IGNORE INTO actuator_lease VALUES('coloop',NULL,0,0,NULL,NULL,NULL)")
    return c


def txn(c, fn):
    c.execute("BEGIN IMMEDIATE")
    try:
        r = fn(); c.execute("COMMIT"); return r
    except BaseException:
        c.execute("ROLLBACK"); raise


def elect(c, holder, boot):
    first = time.time()
    while True:
        now = time.time()
        try:
            def go():
                cur = c.execute("""UPDATE actuator_lease SET holder_id=?,epoch=epoch+1,lease_until=?,renewed_at=?,
                    holder_pid=?,boot_id=? WHERE name='coloop' AND lease_until<=?""",
                                (holder, now + L, now, os.getpid(), boot, now))
                return c.execute("SELECT epoch FROM actuator_lease").fetchone()[0] if cur.rowcount == 1 else None
            return txn(c, go), None
        except sqlite3.OperationalError as e:
            if "locked" not in str(e): raise
            lu = c.execute("SELECT lease_until FROM actuator_lease").fetchone()[0]
            if lu <= now and now - first >= L:
                return None, "STALE_LOCK"
            if now - first >= L + R:
                return None, "LOCK_TIMEOUT"
            time.sleep(0.2)


def fenced(c, holder, epoch, sql, params):
    def go():
        h, e, lu = c.execute("SELECT holder_id,epoch,lease_until FROM actuator_lease").fetchone()
        if not (h == holder and e == epoch and lu > time.time()):
            raise PermissionError("LEASE_LOST")
        return c.execute(sql, params)
    return txn(c, go)


def renew(c, holder, epoch):
    now = time.time()
    fenced(c, holder, epoch, "UPDATE actuator_lease SET lease_until=?,renewed_at=? WHERE name='coloop'", (now + L, now))


def tick(state, crash_at=None):
    c = db(state); holder = f"{socket.gethostname()}:{os.getpid()}:{time.time_ns()}"; boot = boot_id()
    epoch, why = elect(c, holder, boot)
    if epoch is None:
        print(json.dumps(dict(state=why or "HELD_BY_OTHER"))); return 4 if why else 3
    seq = [0]

    def hb(phase, nt=None):
        fenced(c, holder, epoch, "INSERT INTO heartbeat VALUES(?,?,?,?,?,?,?)",
               (holder, epoch, seq[0], time.time(), boot, phase, nt)); seq[0] += 1
    hb("START"); done = []; last_renew = time.time()
    due = c.execute("SELECT work_id,payload_sha256 FROM work WHERE state!='DONE' AND due_at<=? ORDER BY due_at",
                    (time.time(),)).fetchall()
    for work_id, payload in due:
        if time.time() - last_renew >= R: renew(c, holder, epoch); last_renew = time.time()
        key = hashlib.sha256(f"{work_id}|{payload}|local-file|receiver".encode()).hexdigest()
        mark = os.path.join(state, "receiver", key + ".done")
        row = c.execute("SELECT state FROM effect WHERE idem_key=?", (key,)).fetchone()
        if row is None:
            fenced(c, holder, epoch, "INSERT INTO effect VALUES(?,?,?,'INTENT',?)", (key, work_id, epoch, time.time()))
            if crash_at == "after_intent": os._exit(9)
        if not os.path.exists(mark):                  # readback before any (re)delivery
            with open(mark, "a") as f: f.write(f"{work_id} {holder} {time.time()}\n")
            if crash_at == "after_effect": os._exit(9)
        fenced(c, holder, epoch, "UPDATE effect SET state='VERIFIED',epoch=? WHERE idem_key=?", (epoch, key))
        fenced(c, holder, epoch, "UPDATE work SET state='DONE' WHERE work_id=?", (work_id,))
        done.append(dict(work_id=work_id, idem_key=key)); hb("RUN")
    nxt = c.execute("SELECT min(due_at) FROM work WHERE state!='DONE'").fetchone()[0]
    prev = (c.execute("SELECT sha256 FROM receipt ORDER BY n DESC LIMIT 1").fetchone() or [None])[0]
    body = json.dumps(dict(holder=holder, epoch=epoch, boot_id=boot, done=done, next_trigger=nxt, prev_sha256=prev,
                           utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), sort_keys=True, separators=(",", ":"))
    sha = hashlib.sha256(body.encode()).hexdigest()
    fenced(c, holder, epoch, "INSERT INTO receipt(sha256,prev_sha256,body) VALUES(?,?,?)", (sha, prev, body))
    hb("SLEEP_UNTIL", nxt)
    fenced(c, holder, epoch, "UPDATE actuator_lease SET lease_until=? WHERE name='coloop'", (time.time(),))  # clean release
    print(json.dumps(dict(state="OK", epoch=epoch, done=len(done), next_trigger=nxt, receipt=sha))); return 0


def verify(state):
    c = db(state); ok = True; prev = None
    for n, sha, p, body in c.execute("SELECT n,sha256,prev_sha256,body FROM receipt ORDER BY n"):
        ok &= hashlib.sha256(body.encode()).hexdigest() == sha and p == prev and json.loads(body)["prev_sha256"] == p
        prev = sha
    rec = {}
    for f in os.listdir(os.path.join(state, "receiver")):
        rec[f] = len(open(os.path.join(state, "receiver", f)).read().splitlines())
    dup = {k: v for k, v in rec.items() if v != 1}
    pending = c.execute("SELECT count(*) FROM work WHERE state!='DONE' AND due_at<=?", (time.time(),)).fetchone()[0]
    out = dict(receipts=c.execute("SELECT count(*) FROM receipt").fetchone()[0], chain_ok=bool(ok),
               deliveries=sum(rec.values()), duplicate_keys=len(dup), overdue_pending=pending)
    print(json.dumps(out)); return 0 if ok and not dup else 5


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--state", required=True); sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("enqueue"); e.add_argument("work_id"); e.add_argument("payload"); e.add_argument("due", type=float)
    t = sp.add_parser("tick"); t.add_argument("--crash-at", choices=["after_intent", "after_effect"])
    sp.add_parser("verify"); a = ap.parse_args()
    if a.cmd == "enqueue":
        c = db(a.state); txn(c, lambda: c.execute("INSERT OR IGNORE INTO work(work_id,payload_sha256,due_at) VALUES(?,?,?)",
                                                (a.work_id, hashlib.sha256(a.payload.encode()).hexdigest(), a.due))); sys.exit(0)
    sys.exit(tick(a.state, a.crash_at) if a.cmd == "tick" else verify(a.state))
