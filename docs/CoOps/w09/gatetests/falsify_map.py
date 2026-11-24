#!/usr/bin/env python3
"""W09-J3: try to falsify authority-map.json against source and lint reports.
usage: falsify_map.py <authority-map.json> <src_root> <lint_dir>"""
import json, re, subprocess, sys
amap, src, lintdir = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(amap))
REPO = {"InSeed": ("InSeed", "1d09646"), "CoCivium": ("CoCivium", "090c532"), "CoPolitic-site": ("CoPolitic-site", "0fb29d9")}
def rev(repo, spec):
    r = subprocess.run(["git", "-C", f"{src}/{repo}", "rev-parse", "-q", "--verify", spec], capture_output=True, text=True)
    return r.stdout.strip() or None
checks, fails = [], []
# 1. every 40-hex sha cited in evidence must be a blob in a pinned tree at a path the evidence names
trees = {}
for k, (repo, c) in REPO.items():
    out = subprocess.run(["git", "-C", f"{src}/{repo}", "ls-tree", "-r", c], capture_output=True, text=True).stdout
    for line in out.splitlines():
        meta, path = line.split("\t", 1); sha = meta.split()[2]
        trees.setdefault(sha, []).append((k, path))
seen = set()
for r in d["rows"]:
    for ev in r["evidence"]:
        for sha in re.findall(r"\b[0-9a-f]{40}\b", ev):
            if (r["id"], sha) in seen: continue
            seen.add((r["id"], sha))
            hits = [(k, p) for k, p in trees.get(sha, []) if p in ev]
            checks.append(("blob_pointer", sha[:12], bool(hits)))
            if not hits:
                fails.append(f"{r['id']}: sha {sha[:12]} not a blob at any path named in its evidence (pinned trees)")
# 2. claims vs independent mechanical lint
L = {k: json.load(open(f"{lintdir}/lint-{k}-{v}.json")) for k, v in
     [("InSeed", "1d09646"), ("CoCivium", "090c532"), ("CoPolitic", "0fb29d9")]}
def files(rep, gate, **kw):
    return {f["path"] for f in rep["findings"] if f["gate"] == gate and all(f.get(k) == v for k, v in kw.items())}
claims = [
 ("PAY-INSEED: 16 files carry wallet literals", len(files(L["InSeed"], "G-PAY")) == 16),
 ("PAY-INSEED: BTC literal invalid", files(L["InSeed"], "G-PAY", kind="btc_bech32") == files(L["InSeed"], "G-PAY", kind="btc_bech32", validity="INVALID_PLACEHOLDER")),
 ("PAY-INSEED: ETH syntactically valid, checksum unproven", bool(files(L["InSeed"], "G-PAY", kind="eth", validity="SYNTAX_VALID_NO_CHECKSUM"))),
 ("PAY-COCIVIUM/COPOLITIC: 0 destinations", not files(L["CoCivium"], "G-PAY") and not files(L["CoPolitic"], "G-PAY")),
 ("WF-INSEED: both scheduled writers push with no perms", files(L["InSeed"], "G-WF-PUSH-NOPERM", severity="HOLD") == {".github/workflows/autoevo.yml", ".github/workflows/coevo-forever.yml"}),
 ("WF-INSEED: coevo-forever mutates served index", files(L["InSeed"], "G-WF-PROD-MUTATE") == {".github/workflows/coevo-forever.yml"}),
 ("WF-INSEED-CI: no-op probe", files(L["InSeed"], "G-NOOP-PROBE") == {".github/workflows/ci.yml"}),
 ("WF-COCIVIUM: no write-capable workflows", not any(f["gate"].startswith("G-WF-PUSH") for f in L["CoCivium"]["findings"])),
 ("CRED: CoCivium/CoPolitic workflows reference 0 secrets", not files(L["CoCivium"], "G-CRED-USE") and not files(L["CoPolitic"], "G-CRED-USE")),
 ("PII-INSEED: personal webmail in CoNotifyReal.ps1", files(L["InSeed"], "G-PII-EMAIL", email_class="personal_webmail") == {"scripts/CoNotifyReal.ps1"}),
 ("CRED-REGISTRAR-MAIL: AppPassword placeholder-like", files(L["InSeed"], "G-CRED-LITERAL", value_class="PLACEHOLDER_LIKE") == {"scripts/CoNotifyReal.ps1"}),
 ("PAGES-INSEED: CNAME inseed.com", any(f.get("domain") == "inseed.com" for f in L["InSeed"]["findings"])),
 ("PAGES-COCIVIUM/COPOLITIC: no CNAME", not files(L["CoCivium"], "G-DOMAIN-BIND") and not files(L["CoPolitic"], "G-DOMAIN-BIND")),
 ("PII-COCIVIUM: map records every personal-webmail file the linter finds",
  all(any(path in e and "personal webmail" in e for e in next(r for r in d["rows"] if r["id"] == "PII-COCIVIUM")["evidence"])
      for path in files(L["CoCivium"], "G-PII-EMAIL", email_class="personal_webmail"))),
 ("PII-INSEED: map records every personal-webmail file the linter finds",
  all(any(path in e and "personal webmail" in e for e in next(r for r in d["rows"] if r["id"] == "PII-INSEED")["evidence"])
      for path in files(L["InSeed"], "G-PII-EMAIL", email_class="personal_webmail"))),
 ("No unredacted email in map", not re.search(r"[A-Za-z0-9._%+-]+@(gmail|outlook|hotmail|yahoo|icloud|proton)", json.dumps(d))),
 ("Every holder unknown", all(r["current_performer"] == "unknown" for r in d["rows"])),
]
for name, ok in claims:
    checks.append(("claim", name, ok))
    if not ok: fails.append(f"FALSIFIED: {name}")
print(json.dumps({"schema": "CoGuardian.Falsification.R0", "map": amap, "checks": len(checks),
                  "passed": sum(c[2] for c in checks), "blob_pointers": len(seen),
                  "falsified": fails}, indent=1))
sys.exit(1 if fails else 0)
