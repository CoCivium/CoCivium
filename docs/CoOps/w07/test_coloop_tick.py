#!/usr/bin/env python3
"""Process-restart tests for coloop_tick.py (W07-C2-J1). Not an OS-reboot test; T-REBOOT stays NOT_RUN.

python3 -I test_coloop_tick.py --out results.json
"""
import argparse, json, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__)); TICK = os.path.join(HERE, "coloop_tick.py")
ENV = dict(os.environ, COLOOP_L="2", COLOOP_R="1")


def run(state, *args):
    p = subprocess.run([sys.executable, "-I", TICK, "--state", state, *args], capture_output=True, text=True, env=ENV, timeout=60)
    return p.returncode, p.stdout.strip()


def verify(state):
    return json.loads(run(state, "verify")[1])


def test_catchup_with_crashes():
    """5 items due across ~6 s; ticks every 1 s; each crash type is re-armed until it actually fires once."""
    s = tempfile.mkdtemp(prefix="tick-"); t0 = time.time()
    for i, d in enumerate([-1, -1, 2, 4, 6]):
        run(s, "enqueue", f"W{i}", f"payload-{i}", str(t0 + d))
    pending = ["after_intent", "after_effect"]; fired = []; codes = []
    for k in range(16):
        args = ["tick"] + (["--crash-at", pending[0]] if pending else [])
        rc = run(s, *args)[0]; codes.append(rc)
        if rc == 9: fired.append(pending.pop(0))
        time.sleep(1)
    v = verify(s)
    ok = (v["chain_ok"] and v["deliveries"] == 5 and v["duplicate_keys"] == 0 and v["overdue_pending"] == 0
          and fired == ["after_intent", "after_effect"])
    return dict(id="T1_catchup_crash", exit_codes=codes, crashes_fired=fired, verify=v, PASS=ok)


def test_concurrent_ticks(rounds=20, n=4):
    """n ticks launched together per round. PASS: active windows (first..last heartbeat per epoch) never overlap,
    epochs unique, exactly one delivery overall."""
    import sqlite3
    s = tempfile.mkdtemp(prefix="tick-"); run(s, "enqueue", "W0", "p0", str(time.time() - 1)); rcs = []
    for _ in range(rounds):
        ps = [subprocess.Popen([sys.executable, "-I", TICK, "--state", s, "tick"], stdout=subprocess.PIPE, text=True, env=ENV)
              for _ in range(n)]
        rcs += [p.wait(60) for p in ps]
    c = sqlite3.connect(os.path.join(s, "state.sqlite"))
    win = c.execute("SELECT epoch,min(wall_ts),max(wall_ts) FROM heartbeat GROUP BY epoch ORDER BY 2").fetchall(); c.close()
    overlaps = sum(1 for a_, b_ in zip(win, win[1:]) if b_[1] < a_[2])
    v = verify(s)
    ok = overlaps == 0 and len({w[0] for w in win}) == len(win) and v["deliveries"] == 1 and v["duplicate_keys"] == 0 and v["chain_ok"]
    return dict(id="T2_concurrent_ticks", rounds=rounds, ticks_per_round=n, ticks_ok=rcs.count(0), ticks_held=rcs.count(3),
                epochs=len(win), window_overlaps=overlaps, verify=v, PASS=ok)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    res = [test_catchup_with_crashes(), test_concurrent_ticks()]
    for r in res: print(json.dumps(r))
    json.dump(dict(params=dict(COLOOP_L=2, COLOOP_R=1, scaled=True), results=res, all_pass=all(r["PASS"] for r in res),
                   utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), open(a.out, "w"), indent=2, sort_keys=True)
