# CoTouchEvo+ R0A | source-bound impact and rights/retraction guard

**State:** \`DRAFT_PR_READ_ONLY_SOURCE_GUARD__NO_LIVE_CHANGE_EVENT__NO_DEVICE_OR_PROVIDER_EFFECT\`

This **adds to** the existing CoTouchEvo R0 impact selector; it is not another
scheduler, bus, agent fleet, rights engine or filesystem watcher. The guard
reads exactly one known public donor in the checked-out repository:

- \`examples/colensmedia/manifest.json\`
- pinned Git blob SHA-1: \`b5a87427f2a6bf3c5e4928b7aa2c64e3a46deb01\`
- the guard recomputes Git blob SHA-1 and SHA-256 on actual local checkout bytes
- source remains unchanged, and no network, device or remote receiver is called

## Discriminating cases

1. **Current matches previous:** \`NO_CONTENT_DELTA\` and **zero proposals**,
   despite a preexisting synthetic fixture whose event title says "changed."
   A recorded sentence is not a changed file.
2. **Different caller-provided previous blob:** proposals may be shown only as
   \`SIMULATED_CONTENT_DELTA_SHADOW_ONLY\`. The supposed earlier blob and
   event origin remain *explicitly unauthenticated*. This is a counterfactual
   canary, not evidence of a real GitHub change.
3. **RIGHTS_CHANGE or RETRACTION:** can occur without file-byte change. Return
   \`HELD_RIGHTS_EVENT_AND_RECEIVER_AUTHORIZATION\` with **no target names or
   shadow proposals** until actual policy-event and recipient authorization
   proof exists. It never attempts automatic deletion or public broadcast.
4. **RELATION_EDIT / RULE_EDIT:** explicitly typed but **HELD** until a
   qualified relation/rule source event exists. No assumed edge direction or
   automatic inheritance from another experimental engine.
5. **Unpinned or modified source:** fail closed; source-identity verification
   is not the same as source-authorship or semantic correctness.
6. **Two receiver outcomes in the synthetic fixture:** the existing R0
   selector previews requests for interested CoUX/CoProof/CoPrivate aliases,
   while the unconnected CoPublic alias stays dormant. All are fictional
   receiver identifiers, not live subscriptions or legitimate delivery ACKs.

## Scope and acceptance

\`\`\`sh
python3 -m unittest discover -s examples/cotouchevo_r0 -p 'test_*.py' -v
\`\`\`

No code in this extension calls GitHub, providers, external networks, X2,
mouse hooks, schedulers, or actual user accounts. Nothing modifies the donor
or a consent/rights record. It uses a hard-coded public donor and a
256 KiB read ceiling. This is *not* a hostile-filesystem sandbox.

**Next real gate:** authenticated previous and current source bytes with
origin timestamps, explicit source/rightsholder evidence, two real receiver
subscriptions with their own authorization, and independent read-only
receiver acceptance. Only then measure false wakes and actual human time.

\`TOUCHED_NE_CHANGED | RIGHTS_CHANGE_NE_BYTE_CHANGE | RETRACTION_NE_ERASURE |
UNVERIFIED_PRIOR_NE_HISTORY | RELATION_DIRECTION_NE_UNIVERSAL |
SOURCE_HASH_NE_EVENT_AUTHORITY | PREVIEW_NE_EXECUTION | TOKEN_POOL_NE_FREE_COMPUTE |
RECEIPT_NE_ACK | RICK_NE_MAILMAN\`
