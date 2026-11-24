# W09 GUARDIAN — authority map R1 (candidate, not authority)

**R1 (2026-11-18T18:30:00Z) supersedes R0** (commit 2f20869c, sha256 48ab6728…5cd). R0 is retained in git history as SUPERSEDED_RETAINED.
- **Correction:** R0's PII-COCIVIUM row was falsified. `plans/MasterPlan.md` (blob 88d402f) names a personal webmail address as the GitHub account holding the CoSuite repositories. R0 missed it, and the W09-J2 gate linter found it. R1 records it, with the address redacted.
- **Falsification:** `falsify_map.py` checks every cited blob SHA against the pinned trees and checks 16 claims against the linter's output. R0 passes 28/29. R1 passes 30/30. Two negative controls (a corrupted SHA and a renamed path) were both detected.
- **Corroboration:** the InSeed scheduled-writer blob hashes match `docs/CoSites/INSEED_SOURCE_WRITER_GATE_20261118_R0.md` (blob a8632b2). That record says it was prompted by a Claude report, so it is a source-fact match, not an independent review.
- The gate linter, its fixtures and the three lint reports are on the separate candidate branch `claude/w09-guardian-gatetests-20261118`, under `docs/CoOps/w09/gatetests/`.

R0 text follows, still accurate except for the correction above.

`authority-map.json` lists 34 authority gates across InSeed, CoCivium and CoPolitic-site. Each row gives: action → resource → who can currently perform it → required authority → evidence → rollback.

**Who can currently perform each action is `unknown` in every row.** W09 had no authenticated GitHub, Cloudflare or registrar read access, and commit authorship is not proof of authority. W04's Cloudflare zone evidence was not on any readable branch, so the DNS, registrar and mail rows carry the gap explicitly.

## Sources (read-only)
- CoCivium/InSeed @ 1d09646 · CoCivium/CoCivium @ 090c532 · CoCivium/CoPolitic-site @ 0fb29d9 · base a07f154

## Highest-risk findings
1. **PAY-INSEED**: 16 public files carry a BTC and an ETH payment literal. The BTC string uses characters outside the bech32 set, so it cannot be a real address. The ETH address is valid, but nobody has proven who controls it. Money sent to it can't be recovered. Recommendation: HOLD and remove the literals until there is a signed ownership proof.
2. **WF-INSEED-SCHEDULED-WRITERS**: `coevo-forever.yml` appends to the production `index.html` every hour and pushes. It declares no `permissions:` block. No CoEvoBot commit exists on main, so these writers have never been seen landing anything. Recommendation: keep the workflow disabled.
3. **PII-INSEED / CRED-REGISTRAR-MAIL**: `scripts/CoNotifyReal.ps1` is public and contains two personal webmail addresses plus an `$AppPassword` variable. The value looks like a placeholder. The addresses stay in git history even after a revert.
4. **WF-INSEED-CI**: the probe loop never passes `$u` to curl, so it tests nothing.
5. **PAGES-COPOLITIC**: main has only a README, so it is not a deployable source.

## Change envelope
Every DNS, registrar and mail row, and the Cloudflare and registrar credential rows, requires the envelope listed in `change_envelope_schema`. That means a before-readback, the after-state, the TTL, evidence of the authorizing principal, an independent reviewer, a change window, a rollback record set and a post-change probe.

## Tests
The validator, `test_w09.py`, is not committed because the output scope allows only these two files. It is carried in the W09 receipt. It checks four things: all 9 actions are covered, no holder is named without evidence, every row has a rollback, and DNS/registrar/mail rows carry the envelope. A negative control with three injected faults failed as expected.

## Nonclaims
- No merge, deploy, DNS, Pages, comment, credential or payment action was taken.
- No claims are made about other workers.
