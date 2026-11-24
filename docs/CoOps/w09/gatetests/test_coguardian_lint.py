#!/usr/bin/env python3
"""Adversarial + benign fixture tests for coguardian_lint.py (W09-J2, R2 in C2-J2).
Each case builds a throwaway git repo, lints the exact commit, and checks
must-hit / must-not-hit gates. Known misses are asserted explicitly so a
silent improvement or regression is visible either way."""
import hashlib, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coguardian_lint as L

HEX24 = hashlib.sha256(b"w09-fixture").hexdigest()[:24]
WF = ".github/workflows/x.yml"
def wf(on, perms_top="", perms_job="", steps="      - run: echo hi"):
    return f"name: x\non: {on}\n{perms_top}jobs:\n  j:\n    runs-on: ubuntu-latest\n{perms_job}    steps:\n{steps}\n"

CASES = [
 # id, files, must_hit [(gate, {field: value})], must_not [gate]
 ("push_noperm_schedule", {WF: wf("{schedule: [{cron: '0 * * * *'}]}", steps="      - run: |\n          git commit -am x\n          git push")},
  [("G-WF-PUSH-NOPERM", {"severity": "HOLD"})], []),
 ("push_noperm_dispatch_only_is_review", {WF: wf("workflow_dispatch", steps="      - run: git push")},
  [("G-WF-PUSH-NOPERM", {"severity": "REVIEW"})], []),
 ("push_job_level_read", {WF: wf("push", perms_job="    permissions:\n      contents: read\n", steps="      - run: git push")},
  [("G-WF-PUSH-READONLY", {})], ["G-WF-PUSH-NOPERM", "G-WF-PUSH-WRITE"]),
 ("push_explicit_write", {WF: wf("push", perms_top="permissions:\n  contents: write\n", steps="      - run: git push origin HEAD:main")},
  [("G-WF-PUSH-WRITE", {"severity": "HOLD"})], ["G-WF-PUSH-NOPERM"]),
 ("push_write_all_string", {WF: wf("push", perms_top="permissions: write-all\n", steps="      - run: git push")},
  [("G-WF-PUSH-WRITE", {})], []),
 ("job_overrides_top_write_with_read", {WF: wf("push", perms_top="permissions: write-all\n", perms_job="    permissions:\n      contents: read\n", steps="      - run: git push")},
  [("G-WF-PUSH-READONLY", {})], ["G-WF-PUSH-WRITE"]),
 ("push_via_action", {WF: wf("{schedule: [{cron: '1 1 * * *'}]}", steps="      - uses: stefanzweifel/git-auto-commit-action@v5")},
  [("G-WF-PUSH-NOPERM", {"severity": "HOLD"})], []),
 ("gh_pr_merge", {WF: wf("push", steps="      - run: gh pr merge 1 --squash")},
  [("G-WF-PUSH-NOPERM", {})], []),
 ("prod_mutate_index", {WF: wf("{schedule: [{cron: '0 * * * *'}]}", steps="      - run: echo x >> index.html")},
  [("G-WF-PROD-MUTATE", {"severity": "HOLD"})], []),
 ("prod_mutate_cname_sed", {WF: wf("push", steps="      - run: sed -i s/a/b/ CNAME")},
  [("G-WF-PROD-MUTATE", {})], []),
 ("noop_probe", {WF: wf("push", steps="      - run: for u in https://a.test https://b.test; do curl -s -o /dev/null ; done")},
  [("G-NOOP-PROBE", {})], []),
 ("real_probe_not_flagged", {WF: wf("push", steps="      - run: for u in https://a.test; do curl -s \"$u\" ; done")},
  [], ["G-NOOP-PROBE"]),
 ("secrets_ref", {WF: wf("push", steps="      - run: echo ${{ secrets.CF_TOKEN }}")},
  [("G-CRED-USE", {})], []),
 ("btc_bech32_valid_vector", {"p.json": '{"a":"bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"}'},
  [("G-PAY", {"kind": "btc_bech32", "validity": "CHECKSUM_VALID"})], []),
 ("btc_bech32_invalid_placeholder", {"p.json": '{"a":"bc1qsyntheticplaceholderinvalidshape"}'},
  [("G-PAY", {"kind": "btc_bech32", "validity": "INVALID_PLACEHOLDER"})], []),
 ("btc_bech32_one_char_flip", {"p.json": '{"a":"bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5"}'},
  [("G-PAY", {"validity": "INVALID_PLACEHOLDER"})], []),
 ("btc_base58_valid", {"p.txt": "send to 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 today"},
  [("G-PAY", {"kind": "btc_base58"})], []),
 ("eth_lowercase", {"p.txt": "0xabababababababababababababababababababab"},
  [("G-PAY", {"kind": "eth", "validity": "SYNTAX_VALID_NO_CHECKSUM"})], []),
 ("eth_eip55_valid", {"p.txt": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"},
  [("G-PAY", {"validity": "EIP55_VALID"})], []),
 ("eth_eip55_bad_case", {"p.txt": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAeD"},
  [("G-PAY", {"validity": "EIP55_INVALID"})], []),
 ("webmail_pii", {"s.ps1": '$To = "someone_fixture_w09@gmail.com"'},
  [("G-PII-EMAIL", {"severity": "HOLD", "email_class": "personal_webmail"})], []),
 ("benign_emails", {"a.txt": "noreply@anthropic.com bot@cospeedo.local x@example.com 1+u@users.noreply.github.com"},
  [], ["G-PII-EMAIL"]),
 ("cred_placeholder", {"s.ps1": '$AppPassword = "your-16-char-app-password-here"'},
  [("G-CRED-LITERAL", {"value_class": "PLACEHOLDER_LIKE", "severity": "REVIEW"})], []),
 ("cred_high_entropy", {"c.env": f'API_KEY="{HEX24}"'},
  [("G-CRED-LITERAL", {"value_class": "HIGH_ENTROPY", "severity": "HOLD"})], []),
 ("token_prefix", {"c.txt": "ghp_" + "FAKE0" * 8},
  [("G-CRED-TOKEN-PREFIX", {"severity": "HOLD"})], []),
 ("cname_bind", {"CNAME": "example.org\n"},
  [("G-DOMAIN-BIND", {"domain": "example.org"})], []),
 ("self_auth", {"a.json": '{"blanketAuth": "sticky forever"}'},
  [("G-SELF-AUTH", {})], []),
 ("benign_repo_zero_findings", {"README.md": "# Hello\nContact via the issue tracker.\n",
   WF: wf("{schedule: [{cron: '5 5 * * *'}]}", perms_top="permissions:\n  contents: read\n", steps="      - run: python -m pytest")},
  [], ["*"]),
 # R1 regressions from real-repo falsification (CoCivium@090c532)
 ("R1_retry_counter_not_probe", {WF: wf("push", steps="      - run: for attempt in 1 2 3; do curl --fail http://127.0.0.1:8000/ && break; done")},
  [], ["G-NOOP-PROBE"]),
 ("R1_detection_regex_not_secret", {"s.ps1": "$GITHUB_TOKEN_LIKE = 'gh[pousr]_[A-Za-z0-9]{36,}'"},
  [("G-CRED-LITERAL", {"value_class": "PATTERN_LIKE", "severity": "INFO"})], []),
 ("R1_evasion_password_with_parens_stays_hold", {"c.env": f'DB_PASSWORD="({HEX24})*"'},
  [("G-CRED-LITERAL", {"value_class": "HIGH_ENTROPY", "severity": "HOLD"})], []),
 ("R1_evasion_authority_true_flagged", {"a.json": '{"authorized": true}'}, [("G-SELF-AUTH", {})], []),
 ("R1_long_self_auth_value", {"a.json": '{"blanketAuth": "' + "x" * 190 + '"}'}, [("G-SELF-AUTH", {"key": "blanketAuth"})], []),
 ("R1_authority_none_not_claim", {"a.json": '{"authority": "NONE", "b": {"authority":"READ_ONLY"}}'}, [], ["G-SELF-AUTH"]),
 ("R1_authority_affirmative_still_flagged", {"a.json": '{"authority": "FULL_ADMIN"}'}, [("G-SELF-AUTH", {})], []),
 # Payment fixtures are synthetic shapes (0xabab…, bc1qsynthetic…), never a real or published destination.
 # Fixture emails use "_" or <6-char Gmail locals, which Gmail cannot issue, so no real person's address is published.
 # R2 (C2-J2): former known misses, now must-hit
 ("R2_obfuscated_email_bracket", {"a.txt": "write to someone_fixture_w09 [at] gmail [dot] com"}, [("G-PII-EMAIL", {"obfuscated": True, "severity": "HOLD"})], []),
 ("R2_obfuscated_email_words", {"a.txt": "mail someone_fixture_w09 at gmail dot com"}, [("G-PII-EMAIL", {"obfuscated": True})], []),
 ("R2_prose_at_dot_not_email", {"a.md": "look at the docs dot page; the meeting at company dot org went well"}, [], ["G-PII-EMAIL"]),
 ("R2_push_in_called_script", {WF: wf("{schedule: [{cron: '0 * * * *'}]}", steps="      - run: ./deploy.sh"),
   "deploy.sh": "git push\n"}, [("G-WF-PUSH-NOPERM", {"severity": "HOLD", "via_script": ["deploy.sh"]})], []),
 ("R2_push_in_called_pwsh", {WF: wf("push", steps="      - run: pwsh -File scripts/ship.ps1"),
   "scripts/ship.ps1": "git add -A; git push origin HEAD\n"}, [("G-WF-PUSH-NOPERM", {"via_script": ["scripts/ship.ps1"]})], []),
 ("R2_push_in_called_python", {WF: wf("push", steps="      - run: python3 tools/sync.py"),
   "tools/sync.py": "import subprocess\nsubprocess.run(['git', 'push'])\n"}, [("G-WF-PUSH-NOPERM", {})], []),
 ("R2_called_script_without_push_clean", {WF: wf("push", perms_top="permissions:\n  contents: read\n", steps="      - run: ./check.sh"),
   "check.sh": "echo ok\n"}, [], ["G-WF-PUSH-NOPERM", "G-WF-PUSH-READONLY"]),
 ("R2_split_literal_eth", {"a.js": 'const a = "0xabababababababababab" + "abababababababababab";'}, [("G-PAY", {"kind": "eth", "split_literal": True})], []),
 ("R2_split_literal_three_parts", {"a.js": "const a = '0xabababababab' + 'abababababababab' + 'abababababab';"}, [("G-PAY", {"split_literal": True})], []),
 ("R2_whole_literal_not_double_counted", {"a.js": 'const a = "0xabababababababababababababababababababab" + "";'}, [("G-PAY", {"kind": "eth", "_count": 1})], []),
 # R2 narrowing, each with an adversarial counter-case
 ("R2_pinned_digest_is_info", {"t.py": f'TOKENIZER_SHA = "{hashlib.sha256(b"x").hexdigest()}"'}, [("G-CRED-LITERAL", {"value_class": "HASH_DIGEST", "severity": "INFO"})], []),
 ("R2_evasion_40hex_named_token_stays_hold", {"c.env": f'API_TOKEN="{hashlib.sha1(b"x").hexdigest()}"'}, [("G-CRED-LITERAL", {"severity": "HOLD"})], []),
 ("R2_redaction_fixture_is_review", {"x.mjs": 'const r=view({secret_password:"hunter2-fixture-zz"});\nassert.equal("hunter2-fixture-zz" in r,false);'},
  [("G-CRED-LITERAL", {"severity": "REVIEW", "context": "TEST_OR_REDACTION_FIXTURE"})], []),
 ("R2_test_path_cred_is_review_not_dropped", {"tests/test_a.py": f'API_KEY="{HEX24}"'}, [("G-CRED-LITERAL", {"severity": "REVIEW"})], []),
 ("R2_evasion_token_prefix_in_test_stays_hold", {"tests/test_a.py": "ghp_" + "FAKE0" * 8}, [("G-CRED-TOKEN-PREFIX", {"severity": "HOLD"})], []),
 ("R2_generic_fixture_email_review", {"tests/test_e.py": 'x = "bob@gmail.com"'}, [("G-PII-EMAIL", {"severity": "REVIEW", "fixture_like": True})], []),
 ("R2_evasion_firstname_lastname_stays_hold", {"tests/test_e.py": 'x = "john_smith_w09@gmail.com"; y = "alice_real_w09@gmail.com"'},
  [("G-PII-EMAIL", {"severity": "HOLD"})], []),
 ("R2_nongeneric_email_in_test_stays_hold", {"tests/test_e.py": 'x = "someone_fixture_q7@gmail.com"'}, [("G-PII-EMAIL", {"severity": "HOLD"})], []),
 ("R2_self_branch_guarded_writer_review", {WF: "name: x\non:\n  push:\n    branches: ['candidate/x']\njobs:\n  j:\n    if: github.ref == 'refs/heads/candidate/x'\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n    steps:\n      - run: git push origin HEAD:refs/heads/candidate/x\n"},
  [("G-WF-PUSH-WRITE", {"severity": "REVIEW", "scope": "SELF_BRANCH_GUARDED"})], []),
 ("R2_evasion_guarded_push_to_main_stays_hold", {WF: "name: x\non: push\njobs:\n  j:\n    if: github.ref == 'refs/heads/main'\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n    steps:\n      - run: git push origin HEAD:main\n"},
  [("G-WF-PUSH-WRITE", {"severity": "HOLD"})], []),
 ("R2_evasion_unguarded_branch_push_stays_hold", {WF: "name: x\non: push\njobs:\n  j:\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n    steps:\n      - run: git push origin HEAD:refs/heads/candidate/x\n"},
  [("G-WF-PUSH-WRITE", {"severity": "HOLD"})], []),
 ("R2_evasion_mixed_targets_stays_hold", {WF: "name: x\non: push\njobs:\n  j:\n    if: github.ref == 'refs/heads/candidate/x'\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n    steps:\n      - run: |\n          git push origin HEAD:refs/heads/candidate/x\n          git push\n"},
  [("G-WF-PUSH-WRITE", {"severity": "HOLD"})], []),
 ("R2_evasion_self_branch_plus_script_to_main_stays_hold", {WF: "name: x\non: push\njobs:\n  j:\n    if: github.ref == 'refs/heads/candidate/x'\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n    steps:\n      - run: |\n          git push origin HEAD:refs/heads/candidate/x\n          ./ship.sh\n",
   "ship.sh": "git push origin HEAD:main\n"}, [("G-WF-PUSH-WRITE", {"severity": "HOLD", "via_script": ["ship.sh"]})], []),
 # Known misses after R2, asserted so the limitation stays visible
 ("KNOWN_MISS_push_two_levels_deep", {WF: wf("{schedule: [{cron: '0 * * * *'}]}", steps="      - run: ./a.sh"),
   "a.sh": "./b.sh\n", "b.sh": "git push\n"}, [], ["G-WF-PUSH-NOPERM"]),
 ("KNOWN_MISS_base64_wallet", {"a.js": 'atob("MHg2MThhOWRhZmRkZTczZWJlMWRlMTJmYTNlNjIwMTJiYzA1ZTUxY2Yw")'}, [], ["G-PAY"]),
]

def build(files):
    d = tempfile.mkdtemp(prefix="cgl-")
    env = dict(os.environ, GIT_AUTHOR_NAME="f", GIT_AUTHOR_EMAIL="f@example.com",
               GIT_COMMITTER_NAME="f", GIT_COMMITTER_EMAIL="f@example.com")
    subprocess.run(["git", "init", "-q", d], check=True)
    for p, c in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        open(os.path.join(d, p), "w").write(c)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "-c", "commit.gpgsign=false", "commit", "-qm", "f"], check=True, env=env)
    return d

def main():
    fails, known = [], []
    for cid, files, hits, nots in CASES:
        rep = L.lint(build(files), "HEAD", cid); fs = rep["findings"]
        for gate, fields in hits:
            want = fields.get("_count"); fields = {k: v for k, v in fields.items() if k != "_count"}
            match = [f for f in fs if f["gate"] == gate and all(f.get(k) == v for k, v in fields.items())]
            if want is not None and len(match) != want:
                fails.append(f"{cid}: expected exactly {want} x {gate}, got {len(match)}")
            if not match:
                fails.append(f"{cid}: expected {gate} {fields}; got {[ (f['gate'], f.get('validity') or f.get('severity')) for f in fs]}")
        for gate in nots:
            bad = fs if gate == "*" else [f for f in fs if f["gate"] == gate]
            if bad: fails.append(f"{cid}: must not hit {gate}; got {[f['gate'] for f in bad]}")
        if cid.startswith("KNOWN_MISS"): known.append(cid)
        # privacy: report must never contain a raw email or credential value
        blob = json.dumps(rep)
        if any(k.startswith("email_sha") for f in fs for k in f): fails.append(f"{cid}: report carries guessable email hash")
        for leak in ("someone_fixture_w09@gmail.com", "someone_fixture_q7@gmail.com", "bob@gmail.com", "john_smith_w09@gmail.com", "hunter2-fixture-zz", HEX24, "your-16-char-app-password-here",
                     hashlib.sha256(b"someone_fixture_w09@gmail.com").hexdigest()[:12]):
            if leak in blob: fails.append(f"{cid}: report leaks raw value")
    # determinism / idempotency: same commit -> identical bytes
    d = build(CASES[0][1])
    if json.dumps(L.lint(d, "HEAD"), sort_keys=True) != json.dumps(L.lint(d, "HEAD"), sort_keys=True):
        fails.append("non-deterministic report")
    print(f"cases={len(CASES)} known_misses={len(known)}")
    if fails: print("FAIL\n" + "\n".join(fails)); sys.exit(1)
    print("PASS: all must-hit/must-not, no raw-value leaks, deterministic; known misses asserted: " + ", ".join(known))


if __name__ == "__main__": main()
