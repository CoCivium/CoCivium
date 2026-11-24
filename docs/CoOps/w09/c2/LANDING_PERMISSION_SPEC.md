# W09 C2-J3: the narrowest permission that would let candidate work land (candidate, not authority)

## Observed blocker (exact)
| check | result | class |
|---|---|---|
| `git push origin claude/w09-guardian-20261118` (2026-11-18) | git proxy 403: repo "not in this session's authorized repository set" | **authentication.** The session has no GitHub credential for the repo. This is not a refusal by the repo owner. |
| `add_repo CoCivium/CoCivium access=push` (2026-11-18 and 2026-11-19) | "link your GitHub account to let Claude access repositories" | **authentication.** No GitHub account is linked to the Claude session. |
| `GET origin` for `claude/*` branches on all three repos (2026-11-19) | 0 matches | This means unobserved, not "workers failed". Unpushed local work can't be seen on GitHub. |

There is no other transport that is both already authorized and independently verifiable. Downloads and chat paste-through are excluded by the CoPre rules, so this work is **LOCAL_ONLY / LANDING_HOLD**.

## Narrowest configuration that fixes the blocker
These are the requirements a configuration must meet. They are not a claim about how the Claude GitHub integration is implemented. Verify each one against what GitHub actually displays before relying on it.

1. **Link one GitHub identity to the Claude session** in claude.ai settings. Give the GitHub App access to **selected repositories only**: `CoCivium/CoCivium`. W09 writes nowhere else. Add InSeed or CoPolitic-site only for a worker whose assigned namespace is in those repos.
2. **App or token permissions:**
   - `Contents: write` and `Metadata: read`.
   - Do **not** grant `Workflows`, `Administration`, `Pages`, `Secrets`, `Actions: write`, `Environments` or `Deployments`.
   - Without `Workflows`, GitHub rejects any push that changes `.github/workflows/*`. That is a useful backstop against the G-WF-* hazards this map documents.
3. **Repository rulesets** do the narrowing, because `Contents: write` is repo-wide:
   - **Ruleset `protect-default`** on the default branch and `main`:
     - require a PR with 1 approving review from someone other than the last pusher, and code-owner review (this makes the existing `.github/CODEOWNERS` enforceable);
     - block force pushes and deletion;
     - the Claude identity is **not** on the bypass list.
   - **Ruleset `claude-candidates`** on `claude/**`:
     - block force pushes and deletion, so a landed receipt can't be rewritten silently; supersede it with a new branch instead;
     - optionally restrict file paths to `docs/CoOps/w*/**`, where rulesets support push path restrictions.
   - Optionally, **restrict branch creation** outside `claude/**` and the human-owned `candidate/**` prefixes for the Claude identity.
4. **No DNS, registrar, Cloudflare, mail-provider or payment credential** should be reachable from any worker session. None of the W09 jobs needs one.

## How to verify the configuration took effect, read-only
1. `add_repo` with `access=push` returns success for `CoCivium/CoCivium` only, and fails for a repo not in the list.
2. A push to `claude/w09-guardian-c2-20261119` succeeds. An independent reader can then fetch the exact commit and recompute the sha256 of each file from the manifest.
3. A test push touching `.github/workflows/` is rejected.
4. A test push to `main` is rejected.

Only check 2 changes the CoLanding state, from PREPARED to SOURCE_VISIBLE. HASH_VERIFIED needs a reader other than the pushing session.

## What this does not ask for
It does not ask for org-wide access, admin access, Pages or DNS control, the ability to merge, or a token in chat. Per CoPre v8.1 §6, it does not ask for unrestricted access to reduce interruptions.
