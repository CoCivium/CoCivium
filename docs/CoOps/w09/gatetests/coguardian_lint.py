#!/usr/bin/env python3
"""CoGuardian gate linter R2 (W09). Scans a git tree at an exact commit (not the
working tree) and emits gate findings. Never prints secret values, email
addresses or email hashes. R2 (C2-J2): closes the three R1 known misses
(obfuscated email, split literal, push in called script) and narrows three
false-positive classes found by the C2-J1 release-candidate sweep. Every
narrowing is a downgrade to REVIEW, never a silent drop.

usage: coguardian_lint.py <repo_dir> <commit> [--label NAME]  -> JSON on stdout
"""
import hashlib, json, math, re, subprocess, sys

# ---------------------------------------------------------------- keccak256
_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
       0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
       0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
       0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
       0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
M64 = (1 << 64) - 1
def _rol(x, n): return ((x << n) | (x >> (64 - n))) & M64 if n else x
def _f(A):
    for rc in _RC:
        C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
        D = [C[(x - 1) % 5] ^ _rol(C[(x + 1) % 5], 1) for x in range(5)]
        A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]
        B = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2 * x + 3 * y) % 5] = _rol(A[x][y], _ROT[x][y])
        A = [[B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
        A[0][0] ^= rc
    return A
def keccak256(data: bytes) -> bytes:
    rate = 136; p = bytearray(data) + b"\x01"
    while len(p) % rate: p += b"\x00"
    p[-1] |= 0x80
    A = [[0] * 5 for _ in range(5)]
    for off in range(0, len(p), rate):
        blk = p[off:off + rate]
        for i in range(rate // 8):
            A[i % 5][i // 5] ^= int.from_bytes(blk[8 * i:8 * i + 8], "little")
        A = _f(A)
    out = b"".join(A[i % 5][i // 5].to_bytes(8, "little") for i in range(4))
    return out
assert keccak256(b"").hex() == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"

# ---------------------------------------------------------------- address checks
B32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
def _polymod(v):
    g = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]; c = 1
    for x in v:
        b = c >> 25; c = (c & 0x1ffffff) << 5 ^ x
        for i in range(5): c ^= g[i] if (b >> i) & 1 else 0
    return c
def bech32_valid(addr):
    a = addr.lower(); hrp, _, data = a.rpartition("1")
    if hrp not in ("bc", "tb") or len(data) < 6 or any(ch not in B32 for ch in data): return False
    d = [B32.index(ch) for ch in data]
    pm = _polymod([ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp] + d)
    return pm in (1, 0x2bc830a3)  # bech32 / bech32m
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def base58check_valid(addr):
    try: n = 0
    except Exception: return False
    for ch in addr:
        if ch not in B58: return False
        n = n * 58 + B58.index(ch)
    raw = n.to_bytes(25, "big") if n.bit_length() <= 200 else None
    if raw is None: return False
    return hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4] == raw[-4:]
def eth_class(addr):
    h = addr[2:]
    if h == h.lower() or h == h.upper(): return "SYNTAX_VALID_NO_CHECKSUM"
    k = keccak256(h.lower().encode()).hex()
    ok = all((c.upper() if int(k[i], 16) >= 8 else c.lower()) == c for i, c in enumerate(h))
    return "EIP55_VALID" if ok else "EIP55_INVALID"

# ---------------------------------------------------------------- patterns
RE_BTC32 = re.compile(r"\b(?:bc|tb)1[0-9a-zA-Z]{20,90}\b")
RE_BTC58 = re.compile(r"\b[13][1-9A-HJ-NP-Za-km-z]{25,34}\b")
RE_ETH = re.compile(r"\b0x[0-9a-fA-F]{40}\b")
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})\b")
WEBMAIL = {"gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com",
           "icloud.com", "me.com", "proton.me", "protonmail.com", "aol.com", "gmx.com", "gmx.net", "yandex.com"}
BENIGN_EMAIL = re.compile(r"(noreply|no-reply)@|@users\.noreply\.github\.com$|@example\.(com|org|net)$|\.local$|\.invalid$|\.test$", re.I)
RE_CRED = re.compile(r"""(?ix)(?P<name>\$?[A-Za-z_]*(?:password|passwd|pwd|secret|token|api[_-]?key|apppassword)[A-Za-z_]*)
                         \s*[:=]\s*["'](?P<val>[^"'\n]{8,})["']""")
RE_TOKEN_PREFIX = re.compile(r"\b(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9]{32,})\b")
PLACEHOLDER = re.compile(r"(?i)your|here|xxx|changeme|example|placeholder|<|\$\{|\{\{|dummy|redacted|todo")
SELF_AUTH_KEYS = re.compile(r'"(blanketAuth|authorized|authority|approved|finalAuth|auth_granted)"\s*:\s*("([^"]{0,400})"|true)', re.I)
PUSH_ACTIONS = re.compile(r"(stefanzweifel/git-auto-commit-action|EndBug/add-and-commit|peter-evans/create-pull-request|ad-m/github-push-action|actions/deploy-pages|peaceiris/actions-gh-pages|JamesIves/github-pages-deploy-action)", re.I)
PUSH_RUN = re.compile(r"\bgit\s+push\b|\bgh\s+(pr\s+(create|merge)|release\s+create|api\s+.*-X\s*(PUT|POST|PATCH|DELETE))", re.I)
PROD_MUTATE = re.compile(r"(>>?\s*|sed\s+-i[^\n]*\s|tee\s+(-a\s+)?)(\./)?(index\.html|CNAME|404\.html)\b")

RE_EMAIL_OBF = re.compile(r"(?i)\b([A-Za-z0-9._%+-]{2,})\s*(\[at\]|\(at\)|\{at\}|\s+at\s+)\s*([A-Za-z0-9-]+)\s*(?:\[dot\]|\(dot\)|\{dot\}|\s+dot\s+|\.)\s*([A-Za-z]{2,})\b")
RE_CONCAT = re.compile(r"""(["'])([^"'\n]*)\1\s*\+\s*(["'])([^"'\n]*)\3""")
# exact generic name (+ up to 4 digits) only: "john.smith" must NOT match (C2-J2 self-falsification)
GENERIC_LOCAL = re.compile(r"(?i)^(alice|bob|carol|dave|eve|mallory|test|tester|user|someone|somebody|person|private|owner|foo|bar|demo|sample|fixture|nobody|example)\d{0,4}$")
TEST_PATH = re.compile(r"(^|/)(tests?|fixtures?|__tests__|spec)/|(^|/)test_[^/]*$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$", re.I)
REDACTION_CTX = re.compile(r"(?i)\bassert|\.Contains\(|\bnot\s+in\b|redact|reject|must[_ ]not|leak|scrub|\bFAIL\b")
HASH_NAME = re.compile(r"(?i)sha|hash|digest|checksum")
HASH_VAL = re.compile(r"(?:sha256:)?(?:[0-9a-f]{40}|[0-9a-f]{64})")
SCRIPT_CALL = re.compile(r"(?:^|[\s;&|(])(?:(?:bash|sh|zsh|pwsh|powershell(?:\.exe)?|python3?|node)\s+(?:-File\s+|-f\s+)?)?(?:\./)?((?:[\w.-]+/)*[\w.-]+\.(?:sh|bash|ps1|py|mjs|js))\b")
PY_PUSH = re.compile(r"""["']git["']\s*,\s*["']push["']|os\.system\(\s*["']git\s+push""")
DEFAULT_BRANCHES = {"main", "master", "gh-pages", "trunk", "production", "release"}

def push_targets(runs):
    """Explicit refs a run block pushes to; None if any push has no explicit target."""
    tg = []
    for m in re.finditer(r"\bgit\s+push\b([^\n;&|]*)", runs):
        args = [a for a in m.group(1).split() if not a.startswith("-")]
        if len(args) < 2: return None
        ref = args[-1].split(":")[-1]
        tg.append(ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref)
    return tg

def entropy(s):
    from collections import Counter
    c = Counter(s); n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())

def git(repo, *a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, check=True).stdout

def perms_state(p):
    """None -> undeclared; 'read' / 'write' / 'none'."""
    if p is None: return None
    if isinstance(p, str):
        return "write" if p.strip() == "write-all" else ("read" if p.strip() == "read-all" else "none")
    if isinstance(p, dict):
        if not p: return "none"
        if any(str(v).strip() == "write" for v in p.values()): return "write"
        return "read"
    return None

def lint_workflow(path, text, out, resolve=None):
    import yaml
    try: wf = yaml.safe_load(text) or {}
    except Exception as e:
        out.append(dict(gate="G-WF-PARSE", path=path, severity="REVIEW", detail=f"yaml error {type(e).__name__}")); return
    triggers = wf.get("on", wf.get(True, {}))
    trig = list(triggers) if isinstance(triggers, (dict, list)) else [triggers]
    unattended = any(t in ("schedule", "push", "workflow_run", "pull_request_target") for t in trig)
    top = perms_state(wf.get("permissions"))
    for jname, job in (wf.get("jobs") or {}).items():
        if not isinstance(job, dict): continue
        jp = perms_state(job.get("permissions")); eff = jp if jp is not None else top
        steps = job.get("steps") or []
        runs = "\n".join(str(s.get("run", "")) for s in steps if isinstance(s, dict))
        uses = "\n".join(str(s.get("uses", "")) for s in steps if isinstance(s, dict))
        writes = bool(PUSH_RUN.search(runs) or PUSH_ACTIONS.search(uses))
        via = []
        if resolve:  # R2: one level of called local scripts
            for sm in SCRIPT_CALL.finditer(runs):
                st = resolve(sm.group(1).lstrip("./"))
                if st and (PUSH_RUN.search(st) or PY_PUSH.search(st)):
                    via.append(sm.group(1)); writes = True
        base = dict(path=path, job=jname, triggers=[str(t) for t in trig])
        if via: base["via_script"] = sorted(set(via))
        sev = "HOLD" if unattended else "REVIEW"
        # R2: a push confined to explicit non-default branches, with the job guarded to
        # that same ref, cannot reach a served or default branch -> REVIEW, not HOLD.
        tg = None if (via or PUSH_ACTIONS.search(uses)) else push_targets(runs)
        guard = str(job.get("if", ""))
        if (sev == "HOLD" and tg and all(t not in DEFAULT_BRANCHES and f"refs/heads/{t}" in guard for t in tg)):
            sev = "REVIEW"; base["scope"] = "SELF_BRANCH_GUARDED"
        if writes:
            if eff is None:
                out.append(dict(gate="G-WF-PUSH-NOPERM", severity=sev,
                                detail="write step with no permissions block; effective scope = unknown repo default", **base))
            elif eff == "write":
                out.append(dict(gate="G-WF-PUSH-WRITE", severity=sev,
                                detail="write step with explicit write permission", **base))
            else:
                out.append(dict(gate="G-WF-PUSH-READONLY", severity="INFO",
                                detail="write step but token is read-only; push should fail", **base))
        if PROD_MUTATE.search(runs):
            out.append(dict(gate="G-WF-PROD-MUTATE", severity="HOLD" if unattended else "REVIEW",
                            detail="run step writes a served root file (index.html/CNAME/404.html)", **base))
        for m in re.finditer(r"for\s+(\w+)\s+in\s+([^;\n]+);\s*do(.*?)\bdone\b", runs, re.S):
            var, items, body = m.group(1), m.group(2), m.group(3)
            # R1: only URL/host lists are probes; numeric retry counters legitimately ignore $var
            if re.search(r"https?://", items) and not re.search(r"\$\{?" + var + r"\b", body):
                out.append(dict(gate="G-NOOP-PROBE", severity="REVIEW",
                                detail=f"loop variable ${var} unused in body: check gives false assurance", **base))
        secrets = sorted(set(re.findall(r"secrets\.([A-Za-z0-9_]+)", json.dumps(job))))
        if secrets:
            out.append(dict(gate="G-CRED-USE", severity="INFO", detail=f"secrets referenced: {secrets}", **base))

def lint_text(path, text, out):
    _lint_pay(path, text, out)
    # R2: wallet literal split by string concatenation ("0x618a" + "...")
    joined = text
    for _ in range(8):
        nj = RE_CONCAT.sub(lambda m: m.group(1) + m.group(2) + m.group(4) + m.group(1), joined)
        if nj == joined: break
        joined = nj
    if joined != text:
        seen = {(f["gate"], f.get("ref")) for f in out if f.get("path") == path}
        extra = []; _lint_pay(path, joined, extra)
        for f in extra:
            if (f["gate"], f.get("ref")) not in seen:
                f["split_literal"] = True; out.append(f); seen.add((f["gate"], f.get("ref")))
    lines = text.split("\n")
    def near_redaction(pos):
        ln = text.count("\n", 0, pos)
        return bool(REDACTION_CTX.search("\n".join(lines[max(0, ln - 6): ln + 7])))
    is_test = bool(TEST_PATH.search(path))
    _lint_rest(path, text, out, is_test, near_redaction)

def _lint_pay(path, text, out):
    for m in RE_BTC32.finditer(text):
        a = m.group(0); v = bech32_valid(a)
        out.append(dict(gate="G-PAY", path=path, severity="HOLD", kind="btc_bech32",
                        validity="CHECKSUM_VALID" if v else "INVALID_PLACEHOLDER", ref=a[:10] + "…"))
    for m in RE_BTC58.finditer(text):
        a = m.group(0)
        if base58check_valid(a):
            out.append(dict(gate="G-PAY", path=path, severity="HOLD", kind="btc_base58", validity="CHECKSUM_VALID", ref=a[:8] + "…"))
    for m in RE_ETH.finditer(text):
        a = m.group(0)
        out.append(dict(gate="G-PAY", path=path, severity="HOLD", kind="eth", validity=eth_class(a), ref=a[:6] + "…" + a[-4:]))

def _lint_rest(path, text, out, is_test, near_redaction):
    for m in RE_EMAIL.finditer(text):
        e = m.group(0); dom = m.group(1).lower()
        if BENIGN_EMAIL.search(e): continue
        cls = "personal_webmail" if dom in WEBMAIL else "other_domain"
        sev = "HOLD" if cls == "personal_webmail" else "REVIEW"
        f = dict(gate="G-PII-EMAIL", path=path, email_class=cls, line=text.count("\n", 0, m.start()) + 1)  # R1: no email hash
        # R2: only generic fixture names (alice@, test@) downgrade; a non-generic address in a
        # test file is still a published address, so it stays HOLD.
        if sev == "HOLD" and GENERIC_LOCAL.match(e.split("@")[0]): sev = "REVIEW"; f["fixture_like"] = True
        out.append(dict(f, severity=sev))
    for m in RE_EMAIL_OBF.finditer(text):  # R2: [at]/[dot] and "at"/"dot" forms
        dom = (m.group(3) + "." + m.group(4)).lower(); bracket = m.group(2).strip() != "at"
        if not bracket and dom not in WEBMAIL: continue  # plain-word "x at y dot z" only for webmail, avoids prose
        cls = "personal_webmail" if dom in WEBMAIL else "other_domain"
        out.append(dict(gate="G-PII-EMAIL", path=path, severity="HOLD" if cls == "personal_webmail" else "REVIEW",
                        email_class=cls, obfuscated=True, line=text.count("\n", 0, m.start()) + 1))
    for m in RE_CRED.finditer(text):
        v = m.group("val"); ph = bool(PLACEHOLDER.search(v))
        # R1: detection regex, not a secret. Require real regex constructs (char class,
        # quantifier or escape class) so a password with ( or * is not downgraded.
        pat = bool(re.search(r"\[[^\]]{2,}\]|\{\d+,?\d*\}|\\[dwsDWSb]", v))
        cls = ("PATTERN_LIKE" if pat else "PLACEHOLDER_LIKE" if ph else
               "HIGH_ENTROPY" if entropy(v) >= 3.5 and len(v) >= 16 else "LOW_ENTROPY_LITERAL")
        sev = "INFO" if pat else "REVIEW" if ph else "HOLD"
        extra = {}
        # R2: a pinned digest is not a secret, but only when the NAME says hash/sha/digest;
        # a 40-hex value named TOKEN (classic GitHub token shape) stays HOLD.
        if sev == "HOLD" and HASH_VAL.fullmatch(v) and HASH_NAME.search(m.group("name")):
            cls, sev = "HASH_DIGEST", "INFO"
        # R2: a literal beside a redaction assertion, or in a test path, is likely a fixture.
        # Downgrade to REVIEW only (still listed); a real secret wrapped in an assert stays visible.
        elif sev == "HOLD" and (is_test or near_redaction(m.start())):
            sev = "REVIEW"; extra["context"] = "TEST_OR_REDACTION_FIXTURE"
        out.append(dict(gate="G-CRED-LITERAL", path=path, severity=sev,
                        name=m.group("name"), value_class=cls, value_len=len(v), **extra))
    for m in RE_TOKEN_PREFIX.finditer(text):
        out.append(dict(gate="G-CRED-TOKEN-PREFIX", path=path, severity="HOLD", prefix=m.group(0)[:4]))
    for m in SELF_AUTH_KEYS.finditer(text):
        val = (m.group(3) or "").strip().upper()
        # R1: declarations of non-authority are the desired pattern, not a claim
        if m.group(2) != "true" and re.match(r"^(NONE|READ[_ -]?ONLY|NULL|FALSE|NO|UNKNOWN|HOLD|CANDIDATE|NOT[_ ]|PROPOSE)", val):
            continue
        out.append(dict(gate="G-SELF-AUTH", path=path, severity="REVIEW", key=m.group(1),
                        detail="self-asserted authority in content is not evidence of authority"))

def lint(repo, commit, label=None):
    full = git(repo, "rev-parse", commit + "^{commit}").decode().strip()
    files = git(repo, "ls-tree", "-r", "-z", "--format=%(objectname) %(objectsize) %(path)", full).decode().split("\0")
    out = []; scanned = 0
    tree = {}
    for ent in filter(None, files):
        oid, size, path = ent.split(" ", 2); tree[path] = (oid, size)
    def resolve(p):
        o = tree.get(p)
        if not o or o[1] == "-" or int(o[1]) > 2_000_000: return None
        return git(repo, "cat-file", "blob", o[0]).decode("utf-8", "replace")
    for ent in filter(None, files):
        oid, size, path = ent.split(" ", 2)
        if size == "-" or int(size) > 2_000_000: continue
        data = git(repo, "cat-file", "blob", oid)
        if b"\0" in data[:8000]: continue
        text = data.decode("utf-8", "replace"); scanned += 1
        n0 = len(out)
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            lint_workflow(path, text, out, resolve)
        lint_text(path, text, out)
        if path in ("CNAME", "docs/CNAME"):
            out.append(dict(gate="G-DOMAIN-BIND", path=path, severity="REVIEW", domain=text.strip()[:80],
                            detail="Pages custom-domain binding; DNS change envelope required to alter"))
        for f in out[n0:]: f.setdefault("blob", oid)
    out.sort(key=lambda f: (f["gate"], f["path"], json.dumps(f, sort_keys=True)))
    summary = {}
    for f in out: summary[f["gate"]] = summary.get(f["gate"], 0) + 1
    return dict(schema="CoGuardian.LintReport.R0", label=label, commit=full, files_scanned=scanned,
                summary=dict(sorted(summary.items())),
                hold_count=sum(f["severity"] == "HOLD" for f in out), findings=out)

if __name__ == "__main__":
    lbl = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else None
    print(json.dumps(lint(sys.argv[1], sys.argv[2], lbl), indent=1, sort_keys=True, ensure_ascii=False))
