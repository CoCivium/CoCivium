#!/usr/bin/env python3
"""W09 C2-J1: CoGuardian release-candidate gate sweep.

Full-tree lint of each target ref, with per-(blob,path) caching, and a
introduced/resolved delta against the merge-base with main. Reuses the pinned linter's rule
functions; never prints secret values or email addresses.
usage: sweep.py LINTER.py SRC_ROOT TARGETS.txt > report.json
TARGETS.txt lines: "<repo_dir_name> <ref> <short_sha>"
"""
import hashlib, importlib.util, json, sys

spec = importlib.util.spec_from_file_location("lint", sys.argv[1])
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
ROOT = sys.argv[2]
CACHE = {}

def lint_tree(repo, ref):
    full = L.git(repo, "rev-parse", ref + "^{commit}").decode().strip()
    ents = L.git(repo, "ls-tree", "-r", "-z", "--format=%(objectname) %(objectsize) %(path)", full).decode().split("\0")
    out = []; scanned = 0
    tree = {}
    for ent in filter(None, ents):
        oid, size, path = ent.split(" ", 2); tree[path] = (oid, size)
    def resolve(p):
        o = tree.get(p)
        if not o or o[1] == "-" or int(o[1]) > 2_000_000: return None
        return L.git(repo, "cat-file", "blob", o[0]).decode("utf-8", "replace")
    import inspect
    takes_resolver = "resolve" in inspect.signature(L.lint_workflow).parameters
    for ent in filter(None, ents):
        oid, size, path = ent.split(" ", 2)
        if size == "-" or int(size) > 2_000_000: continue
        is_wf = path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
        # workflow findings depend on called scripts in the same tree: key on full commit
        key = (repo, oid, path, full if (is_wf and takes_resolver) else None)
        if key not in CACHE:
            data = L.git(repo, "cat-file", "blob", oid)
            if b"\0" in data[:8000]: CACHE[key] = None; continue
            text = data.decode("utf-8", "replace"); f = []
            if is_wf:
                L.lint_workflow(path, text, f, resolve) if takes_resolver else L.lint_workflow(path, text, f)
            L.lint_text(path, text, f)
            if path in ("CNAME", "docs/CNAME"):
                f.append(dict(gate="G-DOMAIN-BIND", path=path, severity="REVIEW", domain=text.strip()[:80]))
            for x in f: x.setdefault("blob", oid)
            CACHE[key] = f
        if CACHE[key] is None: continue
        scanned += 1; out.extend(CACHE[key])
    return full, scanned, out

def fkey(f):
    # identity of a hazard independent of blob id, so an unchanged hazard in an edited file is not "new"
    d = {k: v for k, v in f.items() if k not in ("blob", "line")}
    return json.dumps(d, sort_keys=True)

def count(fs, sev=None):
    s = {}
    for f in fs:
        if sev and f["severity"] != sev: continue
        s[f["gate"]] = s.get(f["gate"], 0) + 1
    return dict(sorted(s.items()))

targets = [l.split() for l in open(sys.argv[3]) if l.strip()]
mains = {}
report = {"schema": "CoGuardian.ReleaseCandidateSweep.R1", "linter_sha256":
          hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest(), "mains": {}, "targets": []}
for repo in sorted({t[0] for t in targets}):
    full, n, fs = lint_tree(f"{ROOT}/{repo}", "origin/main")
    mains[repo] = fs
    report["mains"][repo] = dict(commit=full, files_scanned=n, holds=count(fs, "HOLD"), all=count(fs))
for repo, ref, _ in targets:
    full, n, fs = lint_tree(f"{ROOT}/{repo}", ref)
    # C2-J3 fix: delta vs merge-base, not main tip. Against the tip, a stale branch
    # appears to "resolve" every hazard main added after it forked.
    base = L.git(f"{ROOT}/{repo}", "merge-base", "origin/main", full).decode().strip()
    _, _, bfs = lint_tree(f"{ROOT}/{repo}", base)
    mk = {fkey(f) for f in bfs}; tk = {fkey(f) for f in fs}
    new = [f for f in fs if fkey(f) not in mk]
    resolved = [f for f in bfs if fkey(f) not in tk]
    behind = int(L.git(f"{ROOT}/{repo}", "rev-list", "--count", f"{full}..origin/main").decode())
    new_hold = [f for f in new if f["severity"] == "HOLD"]
    report["targets"].append(dict(
        repo=repo, ref=ref.replace("origin/", ""), commit=full, merge_base=base, behind_main=behind, files_scanned=n,
        holds_total=sum(f["severity"] == "HOLD" for f in fs),
        introduced=count(new), introduced_holds=count(new_hold), resolved=count(resolved),
        introduced_hold_findings=sorted(new_hold, key=fkey)[:25],
        verdict=("INTRODUCES_HOLD" if new_hold else "INHERITS_HOLD" if any(f["severity"] == "HOLD" for f in fs) else "CLEAR")))
report["targets"].sort(key=lambda t: (t["repo"], t["ref"]))
report["totals"] = {v: sum(t["verdict"] == v for t in report["targets"]) for v in ("INTRODUCES_HOLD", "INHERITS_HOLD", "CLEAR")}
print(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False))
