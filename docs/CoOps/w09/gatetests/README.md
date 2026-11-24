# W09 CoGuardian gate tests R2 (candidate, not authority)

This is a reusable linter that checks the flagship sites, and any constellation repo, for authority-gate hazards. It reads blobs at an exact commit with `git cat-file`, so a dirty working tree cannot change the result. It never executes repository content, never prints secret values, and never prints email addresses or email hashes.

```
python3 -I coguardian_lint.py <repo_dir> <commit> --label NAME > report.json
python3 -I test_coguardian_lint.py                 # 60 fixture cases
python3 -I mutate_r2.py                            # 12 R2 mutants, all must be killed
python3 -I falsify_map.py ../authority-map.json <src_root> .
python3 envelope.py verify <envelope.json> --files-root DIR
```

## Gates
| gate | trips on | severity |
|---|---|---|
| G-WF-PUSH-NOPERM | push, merge or deploy step with no `permissions:` at workflow or job level | HOLD if the trigger is schedule, push, workflow_run or pull_request_target; else REVIEW |
| G-WF-PUSH-WRITE | the same, with explicit `contents: write` or `write-all` | HOLD or REVIEW, as above |
| G-WF-PUSH-READONLY | a write step under a read-only token (the push should fail) | INFO |
| G-WF-PROD-MUTATE | a run step writing `index.html`, `CNAME` or `404.html` | HOLD if unattended |
| G-NOOP-PROBE | a loop over URLs whose body never uses the loop variable | REVIEW |
| G-PAY | a BTC bech32 or base58 address, or an ETH address. The checksum is verified, so placeholders and typos are distinguished from real addresses | HOLD |
| G-PII-EMAIL | an email address outside an allowlist (noreply, example.\*, .local and similar) | HOLD for personal webmail, else REVIEW |
| G-CRED-LITERAL | a credential-named variable assigned a literal, classified as PATTERN, PLACEHOLDER, HIGH_ENTROPY or LOW_ENTROPY | HOLD unless placeholder or pattern |
| G-CRED-TOKEN-PREFIX | `ghp_`, `github_pat_`, `AKIA`, `xox*-` or `sk-` | HOLD |
| G-CRED-USE | a `secrets.*` reference in a workflow | INFO |
| G-DOMAIN-BIND | a `CNAME` file (Pages custom domain) | REVIEW; changing it requires a DNS change envelope |
| G-SELF-AUTH | an affirmative authority value in content, such as `blanketAuth` or `authorized: true` | REVIEW; a self-asserted claim is not evidence of authority |

## Evidence of test strength
- **Fixtures:** 38 cases. They include adversarial evasions: job-level permissions overriding top-level ones, pushes done by an action, one-character bech32 flips, EIP-55 case errors, and passwords containing regex characters. There is also a zero-finding benign repo as a false-positive control.
- **Known misses (3), asserted so they stay visible:**
  - an obfuscated email (`[at]`/`[dot]`)
  - a push inside a script the workflow calls
  - a wallet literal split by string concatenation
- **Mutation testing:** of the mutants that applied, 14 were killed and 1 survived. The survivor is equivalent: the `true` guard in G-SELF-AUTH is redundant.
- **R1 fixes from real-repo falsification on CoCivium@090c532:**
  - numeric retry loops were wrongly flagged as probes
  - detection regexes were flagged as secrets
  - `"authority": "NONE"` was treated as a claim (self-auth hits fell from 122 to 32)
  - values longer than 40 characters were missed, a false negative (InSeed `blanketAuth` hits went from 1 to 8)
  - email hashes were removed from reports because they can confirm a guessed address

## R2 changes (C2-J2, 2026-11-19)
R1's three known misses are closed, and each is now a must-hit case:
- obfuscated emails (`[at]`, `(at)`, and the "at … dot" word form, the word form only for webmail domains so prose isn't flagged);
- wallet literals split by `+` concatenation;
- a push inside a called local script (one level deep: `.sh`, `.ps1`, `.py`, `.js`). The finding carries `via_script`.

Three narrowings, from false positives found by the C2-J1 sweep. Each is a downgrade, never a drop, and each has an adversarial counter-case:

| narrowing | trigger | counter-case that stays HOLD |
|---|---|---|
| pinned digest → INFO `HASH_DIGEST` | a 40- or 64-hex value **and** a variable named sha, hash, digest or checksum | 40 hex named `API_TOKEN` |
| credential in a test or redaction fixture → REVIEW | a test path, or a redaction assertion within 6 lines | a `ghp_` prefix in a test (G-CRED-TOKEN-PREFIX never downgrades) |
| generic fixture email → REVIEW | exactly a generic name (alice, test, …) plus at most 4 digits | a first-name-plus-surname webmail address, or any other non-generic address, even in tests |
| guarded self-branch writer → REVIEW `SELF_BRANCH_GUARDED` | every `git push` names a non-default ref **and** the job's `if:` pins that ref | a push to main, an unguarded push, a mixed or implicit target, or any push via a called script or action |

Self-falsification during C2-J2:
- The first generic-name regex allowed a suffix, so `john.smith@` would have been downgraded. That was caught by the R1 case and tightened.
- The first mutation run left 3 of 12 mutants alive. Three cases were added, and 12 of 12 are now killed.
- The fixture emails were changed to forms Gmail cannot issue (`_`, or fewer than 6 characters), so the tests don't publish anyone's real address.

Known misses after R2, asserted: a push two script levels deep, and a base64-encoded wallet.

On the three current mains, R2 output is **byte-identical** to R1 (`lint-*.R2.json` and `lint-*.json` have equal sha256). So R2 changes nothing on today's sources, and the extra strength has no yield there yet. Report files don't record which linter produced them; the C2 sweep report carries `linter_sha256` instead.

## Reports at pinned commits
| repo@commit | HOLD | summary |
|---|---|---|
| InSeed@1d09646 | 88 | 83 G-PAY in 16 files (BTC: every hit is an invalid placeholder; ETH: syntax valid, controller unproven); 2 PUSH-NOPERM; 1 PROD-MUTATE; 2 personal webmail; 8 SELF-AUTH |
| CoCivium@090c532 | 1 | 1 personal webmail in plans/MasterPlan.md; credential hit is PATTERN_LIKE; 0 write-capable workflows |
| CoPolitic-site@0fb29d9 | 0 | README only |

## Nonclaims
- No HOLD here has been acted on.
- No workflow, Pages, DNS or merge change was made.
- No independent review has been obtained. The reviewer for this candidate is UNKNOWN.
- R1 reports (`lint-*.json`) are kept unchanged as history. R2 reports are `lint-*.R2.json`.
