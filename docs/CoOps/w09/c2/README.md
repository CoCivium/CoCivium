# W09 GUARDIAN cycle C2: release-candidate gate sweep (candidate, not authority)

Session `w09-db64050f00b94d81`, cycle `C2-20261119`. All inputs are read-only public clones, fetched 2026-11-19. The mains are unchanged since C1: InSeed `1d09646`, CoCivium `090c532`, CoPolitic-site `0fb29d9`.

## J1: what would each release candidate publish?
`sweep.py` lints the full tree of **191 refs**: every `candidate/`, `review/`, `canary/`, `preview` and `policy*` branch of the three sites (`targets.txt` pins each SHA). Each branch is diffed against its **merge-base** with main, which splits hazards into those the branch *introduces*, those it *inherits*, and those it *resolves*.

Results with the R2 linter (`release-candidate-sweep.linterR2.json`): **CLEAR 6 · INHERITS_HOLD 184 · INTRODUCES_HOLD 1**.

| site | finding |
|---|---|
| **InSeed** (5 candidates) | **No candidate removes any of the 83 G-PAY HOLDs.** The payment literals ship with every candidate. `cosites261118-inseed-workflow-safe-r0` and `inseed-human-first-site-r0` resolve the 3 workflow HOLDs (85 HOLDs left). `inseed-trust-first-use-r0` and `inseed-trustworthy-first-use-20261117-r1` point at main's commit itself, so they contain no changes. |
| **CoPolitic** (6 refs) | All CLEAR, with no hazard of any gate class. |
| **CoCivium** (180 branches) | 179 branches inherit HOLDs (the 184 total = 179 CoCivium + 5 InSeed). Every CoCivium branch has 1 HOLD except cosurface, which has 8. Main's single HOLD is a personal webmail address in `plans/MasterPlan.md`. `human-first-public-profile-20261111` resolves one inherited PII HOLD but still carries 1 HOLD. The one INTRODUCES_HOLD is `cosurface-stitched-orb-nav-r0-20261108`, with 7 personal-webmail hits on two non-generic addresses used as test fixtures. Those addresses are not reproduced here and don't match the InSeed or main addresses. The median branch is 879 commits behind main, and 137 are more than 500 behind. |

**Implications for the release gate:**
- The InSeed payment-literal removal (map row PAY-INSEED) is not in any candidate. It is the open gate.
- No CoCivium candidate is HOLD-free.

## J3: falsifying J1, and what changed because of it
1. **The delta was wrong in its first form.** Comparing against main's *tip* made stale branches appear to "resolve" hazards that main added after they forked. For example, `coallbloom` appeared to resolve 6 PII and 26 self-auth hits. The sweep now uses the merge-base (`merge_base`, `behind_main` per target).
2. **I hand-checked the 9 R1 INTRODUCES_HOLD branches**, with literals masked:
   - 7 were false positives: redaction-test fixtures, plus a pinned SHA-256 named `TOKENIZER_SHA`;
   - 1 was over-severe: a writer guarded by its ref and paths that pushes only to its own candidate branch;
   - 1 was a likely true positive (cosurface).
   - This drove linter R2 (see `../gatetests/README.md`).
3. **Re-sweeping with R2** moves exactly those 8 false positives to INHERITS and keeps the true positive. Main-branch HOLD counts are identical under R1 and R2, and no new rule hits any main.

Residual risks:
- A real secret placed next to an `assert` is downgraded to REVIEW. It is still listed, never dropped.
- The sweep can't see anything that isn't on GitHub, including every worker's unpushed work.

## J3: landing
See `LANDING_PERMISSION_SPEC.md`. The blocker is authentication: no GitHub account is linked to the session. The spec gives the narrowest configuration that fixes it: selected-repo access, `Contents: write` without `Workflows`, and rulesets on `main` and `claude/**`.

## Reproduce
```
python3 -I sweep.py ../gatetests/coguardian_lint.py <dir with clones> targets.txt > out.json
```
Fetch first. The output is deterministic for fixed refs and linter bytes, and `linter_sha256` is recorded in the report.

## Nonclaims
- No HOLD here was acted on.
- No branch was changed except this worker's own.
- Nothing is claimed about other workers.
- No independent reviewer exists. The reviewer is UNKNOWN.
