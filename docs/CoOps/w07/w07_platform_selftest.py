#!/usr/bin/env python3
"""W07 C2-J7 platform self-test: is the pid-reuse guard and boot id sound on THIS OS?

Run from docs/CoOps/w07:  python -I w07_platform_selftest.py --out selftest.json
Uses only the standard library and a temp dir. Starts short-lived child processes of its own; installs nothing.
Checks:
  P1 proc_start(self) is non-None and stable across calls
  P2 a child has a token different from ours; after the child exits, its token is None (or differs)
  P3 boot_id is not 'unknown' and is stable across 3 calls 2 s apart
  P4 coloop_tick enqueue -> tick -> verify end to end: 1 delivery, chain ok, exit codes 0
  P5 break policy degrades safely: if P1 fails, report HOLD_ONLY (never kill) rather than FAIL
"""
import argparse, importlib.util, json, os, platform, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    ref, tick = load("w07_coloop_ref"), load("coloop_tick"); res = []
    me = [ref.proc_start(os.getpid()) for _ in range(3)]
    p1 = me[0] is not None and len(set(me)) == 1
    res.append(dict(id="P1_self_token", token_present=me[0] is not None, stable=len(set(me)) == 1, PASS=p1))

    child = subprocess.Popen([sys.executable, "-I", "-c", "import time; time.sleep(3)"])
    time.sleep(0.5); live = ref.proc_start(child.pid); child.wait(); time.sleep(0.5); dead = ref.proc_start(child.pid)
    p2 = live is not None and live != me[0] and dead != live
    res.append(dict(id="P2_child_token", live_present=live is not None, differs_from_self=live != me[0],
                    gone_after_exit=dead is None, changed_after_exit=dead != live, PASS=p2))

    b = []
    for _ in range(3):
        b.append(tick.boot_id()); time.sleep(2)
    p3 = b[0] != "unknown" and len(set(b)) == 1
    res.append(dict(id="P3_boot_id", known=b[0] != "unknown", stable=len(set(b)) == 1, PASS=p3))

    st = tempfile.mkdtemp(prefix="w07-selftest-"); env = dict(os.environ, COLOOP_L="2", COLOOP_R="1")
    run = lambda *x: subprocess.run([sys.executable, "-I", os.path.join(HERE, "coloop_tick.py"), "--state", st, *x],
                                    capture_output=True, text=True, env=env, timeout=120)
    codes = [run("enqueue", "W0", "p0", str(time.time() - 1)).returncode, run("tick").returncode]
    v = run("verify"); codes.append(v.returncode)
    try:
        vj = json.loads(v.stdout)
    except ValueError:
        vj = dict(raw=v.stdout[-500:], err=v.stderr[-500:])
    p4 = codes == [0, 0, 0] and vj.get("deliveries") == 1 and vj.get("chain_ok") is True
    res.append(dict(id="P4_tick_end_to_end", exit_codes=codes, verify=vj, PASS=p4))

    res.append(dict(id="P5_break_policy_mode", mode="KILL_ALLOWED_WITH_GUARD" if p1 and p2 else "HOLD_ONLY", PASS=True))
    out = dict(platform=platform.platform(), python=sys.version.split()[0], os_name=os.name, results=res,
               all_pass=all(r["PASS"] for r in res), utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    json.dump(out, open(a.out, "w"), indent=2, sort_keys=True)
    for r in res: print(json.dumps(r))
    sys.exit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
