# CoCivia Shared Evolution Hub R0

**Status:** PROPOSED_SHARED_WORKFLOW__GMAIL_UNAVAILABLE__NOT_BROADCAST

## Purpose

Coordinate incremental shared evolution across authorized CoCivium workspaces, sessions, agents, and voluntary human contributors. Keep a versioned source of truth, make each projection's currentness explicit, and preserve receipts for actual actions.

## Identity, audience, attribution, and authorization contract

This contract applies to every outreach, email, introduction, shared draft, citation, publication, cross-session handoff, and external action.

### Resolve who is who

Before an external message or consequential handoff, record the following separately:

- **Actor / sender:** the actual human, agent, or system preparing or sending the content.
- **Represented identity:** the person, organization, project, alias, or role the actor claims to speak for. Never infer representation from a display name or address alone.
- **Recipient / audience:** exact intended To, Cc, Bcc, list, channel, or destination; distinguish a named person from an organization or shared mailbox.
- **Route evidence:** where the address or route came from, when it was last checked, and whether it is verified, user-provided but unverified, inferred, stale, or failed.
- **Message provenance:** who authored each substantive claim, quotation, attachment, or endorsement; link to source and version where practical.
- **Purpose and relationship:** why this recipient is included, the relevant relationship context, and whether the contact is invited, expected, optional, or not authorized.
- **Authority:** what permission allows this actor to read, draft, modify, share, or send this specific material to this specific audience.
- **Effect state:** distinguish prepared, saved as draft, approved, sent, delivery confirmed, replied, acknowledged, and published. Never collapse these into one status.

### Mandatory preflight for outreach and email

1. Resolve sender identity and represented capacity; do not imply that a model, agent, contributor, or organization has authorized a statement unless there is evidence.
2. Verify the recipient and route from an appropriate source. Check spelling, aliases, domains, role changes, and whether a group/list expands to additional recipients when that information is available.
3. Inspect To/Cc/Bcc and attachments explicitly. Apply least disclosure; do not expose private recipients or relationship notes unnecessarily.
4. Review every biographical, professional, historical, scientific, and endorsement claim against a source. Separate fact, inference, opinion, and invitation. Do not attribute words to someone unless they said them.
5. Ensure the content is addressed to this audience, not copied blindly from another recipient's draft. Check names, pronouns where known, context, confidentiality, tone, and requested action.
6. Check consent, legal/policy constraints, and authority for this particular action. A user's general agreement to evolve work is not blanket permission to contact every person or disclose every record.
7. If a material identity, recipient, route, claim, attachment, or permission is uncertain, pause the external action. Ask for confirmation or prepare an explicitly unsent draft with the uncertainty marked.
8. Before sending, require human approval where required by the available authority and workflow. Never treat draft preparation as send authorization.
9. After an action, record a receipt with actor, represented identity, exact recipients/destination, source version, timestamp, action, result, and remaining uncertainty. Store sensitive details only in an appropriately authorized place.
10. On error, stop follow-on sends, disclose the issue to the appropriate owner, preserve the audit trail, and follow an authorized correction/recall process. Never silently rewrite history.

### Identity and relation states

Use explicit states rather than guesswork:

- `IDENTITY_USER_ASSERTED_UNVERIFIED`
- `IDENTITY_SOURCE_VERIFIED`
- `REPRESENTATION_AUTHORIZED`
- `RECIPIENT_ROUTE_UNVERIFIED`
- `RECIPIENT_ROUTE_VERIFIED`
- `DRAFT_PREPARED`
- `DRAFT_SAVED_VERIFIED`
- `AWAITING_APPROVAL`
- `APPROVED_FOR_NAMED_AUDIENCE`
- `SENT_RECEIPT_VERIFIED`
- `DELIVERY_UNKNOWN`
- `DELIVERY_CONFIRMED`
- `REPLY_RECEIVED`
- `ACKNOWLEDGED`
- `BLOCKED_IDENTITY`
- `BLOCKED_RECIPIENT`
- `BLOCKED_AUTHORITY`
- `CORRECTION_REQUIRED`

These states are vocabulary for the proposed workflow, not evidence that a runtime currently enforces them.

### Required message receipt

For each external message or consequential share, capture where authorized:

- stable message/action ID;
- actual actor and represented identity, with verification status;
- exact recipient list or destination, with route provenance;
- subject/title and content/source version or content hash;
- attachments and disclosure classification;
- approval/authority evidence;
- timestamp and sending surface;
- result state and provider receipt, if any;
- follow-up owner, next wake condition, and correction/recovery path.

Do not put passwords, tokens, or unnecessary sensitive relationship data into public repositories or receipts.

## Shared evolution workflow

1. Discover existing source and current versions before creating duplicates.
2. Propose bounded changes against a named source.
3. Compare alternatives and retain substantive disagreement.
4. Verify citations and distinguish influence from analogy or independent convergence.
5. Review privacy, consent, authority, attribution, audience, and external claims.
6. Accept, revise, defer, or reject with a reason.
7. Publish a new version with a change note and source pointers.
8. Update authorized projections individually and record each result.
9. Preserve unresolved tasks with an owner or unassigned status and a next wake/check.
10. Mark completion only when observable acceptance criteria are satisfied.

## Broadcast message for authorized channels

> **CoCivia / CoCivium shared evolution invitation**
>
> Please help evolve the shared CoCivium work incrementally rather than rebuilding it in isolation. Start from the current source and version, identify the most useful next improvement, and contribute bounded changes with sources, rationale, alternatives, attribution, permissions, and a clear next action.
>
> Relevant work includes CoTheoryAll+, CoCitation+, CoFanOut+, CoChorus+, CoReview+, CoPublish+, CoProof+, CoOrbWare+, CoAllBloom+, CoEvergreen+, CoTime+, and related families. Look for cross-disciplinary links while distinguishing direct evidence, historical influence, independent convergence, analogy, and speculation. Preserve disagreements and credit.
>
> Where authorized and available, use the designated Gmail Drafts folder for `rballard@inseed.com` as human-reviewed outreach staging; keep versioned CoCivium source documents as canonical references. Treat `CoCivia@CoCivium.org` as a requested identity pending verification of mailbox/alias status and permissions. Do not assume the two addresses are connected.
>
> Participation is optional. Do not send messages, grant access, represent endorsement, or modify shared external systems without the relevant authority. Record what was actually saved, shared, sent, delivered, reviewed, or published; these are distinct states.
>
> The goal is not maximal noise or forced consensus. It is useful, attributable, evidence-backed improvement and publications that can stand on their own.

## Current execution boundary

This document is a proposal and reusable broadcast text. It has not been broadcast to email, other sessions, agents, or external workspaces. The Gmail integration was found disabled by administrator, so no Gmail draft was created. The requested address `CoCivia@CoCivium.org` and its relationship to the Gmail account have not been verified.

## Acceptance criteria for the first real integration

- Verify the authorized mailbox and whether `CoCivia@CoCivium.org` is a mailbox, alias, or separate route.
- Create one draft without sending it.
- Record its exact draft identifier, source version, and saved-state receipt.
- Make one versioned edit and verify the update and history.
- Verify sharing/access only with authorized identities.
- Test the identity-and-recipient preflight against a synthetic misaddressed email, ambiguous alias, unverified quote, and unauthorized Bcc.
- Test recovery from a fresh session using the source pointer and task packet.
- Keep every other surface explicitly unsynced until its own update is verified.

**Invariant:** one evolving body of work, many scoped projections, no assumed broadcast, no silent loss, no identity conflation, and no claimed synchronization without receipts.

**LATCHED EVERMORE** means durable and recoverable continuity, not perpetual execution or blanket authority.
