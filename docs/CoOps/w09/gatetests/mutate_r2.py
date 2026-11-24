#!/usr/bin/env python3
"""C2-J2 mutation test: each mutant disables one R2 rule; the fixture suite must fail."""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "coguardian_lint.py")).read()
M = [("hash name check removed", 'HASH_VAL.fullmatch(v) and HASH_NAME.search(m.group("name"))', 'HASH_VAL.fullmatch(v)'),
     ("fixture -> INFO", 'sev = "REVIEW"; extra["context"]', 'sev = "INFO"; extra["context"]'),
     ("guard check removed", 'and f"refs/heads/{t}" in guard', ''),
     ("default-branch check removed", 't not in DEFAULT_BRANCHES and ', ''),
     ("script resolver off", '        if resolve:  # R2', '        if False:  # R2'),
     ("split join off", '    if joined != text:', '    if False:'),
     ("plain-word webmail filter off", 'if not bracket and dom not in WEBMAIL: continue', 'pass'),
     ("generic regex loosened", '\\d{0,4}$")', '[._+-]?\\w{0,12}$")'),
     ("obf email off", '    for m in RE_EMAIL_OBF.finditer(text):', '    for m in []:'),
     ("split dedupe off", 'if (f["gate"], f.get("ref")) not in seen:', 'if True:'),
     ("mixed-target None off", '        if len(args) < 2: return None', '        if len(args) < 2: continue'),
     ("via-script disables self-branch off", 'tg = None if (via or PUSH_ACTIONS.search(uses)) else push_targets(runs)', 'tg = push_targets(runs)')]
killed = 0
for name, a, b in M:
    assert src.count(a) == 1, name
    d = tempfile.mkdtemp(); shutil.copy(os.path.join(HERE, "test_coguardian_lint.py"), d)
    open(os.path.join(d, "coguardian_lint.py"), "w").write(src.replace(a, b))
    ok = subprocess.run([sys.executable, "-I", os.path.join(d, "test_coguardian_lint.py")], capture_output=True).returncode != 0
    killed += ok; print(("KILLED  " if ok else "SURVIVED"), name)
print(f"{killed}/{len(M)} killed"); sys.exit(0 if killed == len(M) else 1)
