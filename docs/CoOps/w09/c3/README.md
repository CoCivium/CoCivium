# W09 GUARDIAN C3-J1: InSeed payment-destination withhold patch (candidate, not authority)

**What it fixes.** InSeed `main` (`6b27d24` as of 2026-11-24; the publish commit was `d4f63d0` on 2026-11-21) now carries the new human-first front door. The same root still contains 16 legacy `board/`, `api/` and `board.html` files holding an **unproven ETH payment address** and an invalid BTC placeholder (83 occurrences). It also contains `scripts/CoNotifyReal.ps1`, which has two personal webmail addresses, an app-password variable and a third party's first name in a "claim allocation" mail template. With `CNAME` = inseed.com, those files are part of what Pages publishes (map rows PAY-INSEED and PII-INSEED). Every InSeed branch, including main, still has them as of 2026-11-24.

**The patch** is one commit, `135d51665b14caac8c366acb5619e350b61160da`, on parent `6b27d24` (current main):
- **Payment literals:** all 83 are replaced by a visible marker, `[withheld: no verified payment destination]`, and every JSON file stays valid. To restore an address, list it in `payment-destinations.verified.json` with a `proof_uri` (a signed-ownership proof) and an `approver_ref`.
- **`CoNotifyReal.ps1`:**
  - the recipient, sender and SMTP password now come from environment variables only;
  - the script exits with an error unless all three are set and `-Send` is passed;
  - the person's name is now a `$Name` parameter.
- **New guard:** `tests/test_inseed_no_unverified_payment_r0.py` checks the whole tree and fails closed, with 5 tests including negative controls. Those controls are synthetic shapes, so this file, which Pages also serves, neither holds nor reconstructs any real address. It is wired into the existing read-only `inseed-first-use-r0.yml` CI with `if: always()`, so it still runs when an earlier step fails.
- **`.gitignore`:** `__pycache__/`.

**Evidence** (all from W09's own lineage, so it counts as one validator, not three):
| check | result |
|---|---|
| New guard tests | 5/5 OK |
| main's own 16 first-use tests | 14/16 on main **and** on the patch. The 2 failures exist on unpatched `6b27d24` too: its tests went stale after the owner's 2026-11-23 homepage edits (Cloudflare-analytics wording; a `cocivium.github.io` link). This patch doesn't touch them. |
| W09 linter R2: main `6b27d24` → patch `135d516` | HOLD 85 → **0** (G-PAY 83 → 0; personal webmail and credential HOLDs → 0) |
| The new guard on unpatched main | fails: 16 BTC-shape files, 16 ETH, 1 webmail, 1 credential |
| Raw-byte scan of every pack entry in the bundle, deltas included | 33 entries, 0 carry the address, the webmail or the name |
| Restore from a fresh public InSeed clone plus the bundle | exact `a400783e`, tests OK |

**Apply** (owner or elected InSeed writer):
```
git fetch <path>/inseed-w09-c3r2-pay-withhold-on-6b27d24.bundle w09-c3r2-inseed-pay-withhold:claude/w09-inseed-pay-withhold-r2-20261124
```
The bundle requires `6b27d24`. Then open a PR. Rollback is `git revert 135d516`.

**What this does NOT do:**
- **It doesn't unpublish history.** The values stay in earlier commits and in any forks. Purging them would need an owner decision on rewriting history.
- **It isn't proof of the live state.** I couldn't fetch inseed.com from this session (not allowlisted), so what visitors see is UNVERIFIED.
- **It doesn't touch the other legacy board claims.** Strings such as "FINAL AUTH ALL" and "200 OK" (G-SELF-AUTH, 8 REVIEW) are left alone. Deciding whether to retire `board/` is the owner's call.
- **It makes no decision about whether `CoNotifyReal.ps1` should exist.** The script is a solicitation-style template, so that decision is a HOLD for the owner.

**Superseded, not landed:** r0 `cd14679` (on `d732424`) and r1 `a400783` (on `d4f63d0`) both went stale because main moved. They're kept only in the W09 local archive.

**Why a bundle, not a `.patch`:** a text diff would print the old values on its `-` lines and republish them inside public CoCivium. The bundle carries only the new objects and their deltas, which the raw-byte scan confirms.
