# CoOutreach Identity + Thread Binding R0

**State:** CANDIDATE_OUTREACH_SAFETY_CONTRACT__NOT_BULK_SEND_AUTHORITY
**Observed:** 2026-10-26

## Prime rule

`WHO_IS_WHO_BEFORE_WHAT_TO_SEND`

No external outreach should be sent until recipient identity, sender identity, channel, thread, and content scope are bound strongly enough for that action.

## Required bindings before send

### 1. Recipient identity
- exact person or organization;
- exact address / handle / account from an authoritative source;
- disambiguation against same-name contacts;
- relationship/source provenance;
- currentness.

### 2. Sender identity
- exact sending account;
- exact display/signature identity;
- authority to use that account;
- no silent substitution between personal, InSeed, CoCivium, AgentMail, Fastmail, or other identities.

### 3. Thread identity
- exact thread/message id where replying;
- exact subject/context;
- authoritative Reply-To when applicable;
- latest inbound message read before drafting;
- duplicate / newer-sent check.

### 4. Content identity
- what claim/request/invitation is being sent;
- intended receiver and why;
- evidence ceiling;
- privacy/sensitivity;
- whether attachments/links match the intended conversation;
- whether wording could be mistaken for endorsement, appointment, partnership, adoption, authority, or commitment.

### 5. Effect identity
- draft / sent / delivered / read / replied / accepted / adopted must remain distinct states;
- post-send receipt must bind sender, recipient, thread, message id, timestamp and exact content hash where feasible.

## Cross-channel rule

Names are not identities.

`SAME_NAME_NE_SAME_PERSON`
`SAME_PERSON_NE_SAME_CHANNEL_IDENTITY`
`CONTACT_CARD_NE_REPLY_TO`
`SCREENSHOT_NE_NATIVE_THREAD_BINDING`

Do not merge Gmail, InSeed, Fastmail, WhatsApp, LinkedIn, GitHub, AgentMail, or other identities solely because the display name matches.

## Reply rule

Before replying:

`READ_LATEST_THREAD -> VERIFY_SENDER -> VERIFY_RECIPIENT -> VERIFY_REPLY_TO -> CHECK_NEWER_SENT -> DRAFT_TO_CONTEXT -> CLAIM_CHECK -> SEND_ONCE -> RECEIPT`

If any identity link is uncertain:

`HOLD_IDENTITY`

Do not create a new thread from a different account merely because another address for the same-named person exists.

## New-thread rule

A new thread needs:
- verified recipient route;
- reason this route is appropriate;
- scoped invitation/request;
- duplicate-outreach check;
- no implied prior conversation unless source-bound;
- clear sender identity.

## Group / CC / BCC rule

Every visible recipient must be individually intended for the content.

Never infer that a relationship with one recipient authorizes copying others.

`CC_NE_CONSENT`
`KNOWN_CONTACT_NE_APPROPRIATE_RECIPIENT`
`CANDIDATE_POOL_NE_MAILING_LIST`

Use BCC only for legitimate privacy-preserving group mail where the group send itself is authorized; never to manufacture individualized outreach at scale.

## Who-said-what-to-whom ledger

Each outreach object should record:
- person_id;
- organization_id if relevant;
- channel_identity_id;
- sender_identity_id;
- thread_id;
- message_id;
- direction INBOUND / OUTBOUND;
- timestamp;
- subject / purpose;
- exact-source pointer;
- content hash or durable pointer;
- evidence class;
- state;
- commitments created;
- commitments satisfied;
- next safe action;
- supersession / correction.

## Commitment binding

A promise or ask in one thread must not be considered satisfied by an unrelated message to the same person.

`SAME_PERSON_NE_SAME_COMMITMENT`
`RELATED_TOPIC_NE_COMMITMENT_SATISFIED`

Commitments bind:
`PERSON + CHANNEL + THREAD + CONTENT_IDENTITY + TIME_WINDOW`

unless explicitly broadened.

## CoCopy / CoReach / CoOrb relation

CoCopy records chronological outreach events.
CoReach maintains source-relative relationship state.
CoOrb shows the current safe next action and identity confidence.

Suggested CoOrb card:

`WHO: Michael Murphy [THREAD-BOUND? NO]`
`FROM: rballard@inseed.com [CONNECTED? NO]`
`THREAD: Re: Apologies again [NATIVE READ? NO]`
`STATE: HOLD_WRONG_SENDER`
`NEXT: bind genuine InSeed thread before reply`

## Confidence

Use explicit confidence classes:
- IDENTITY_VERIFIED_NATIVE;
- IDENTITY_VERIFIED_SOURCE_BOUND;
- IDENTITY_PARTIAL;
- NAME_ONLY;
- CONFLICT;
- STALE;
- UNKNOWN.

Only appropriately verified classes may cross the send gate.

## Rails

`WHO_IS_WHO_BEFORE_WHAT_TO_SEND`
`SAME_NAME_NE_SAME_PERSON`
`SAME_PERSON_NE_SAME_CHANNEL_IDENTITY`
`CONTACT_CARD_NE_REPLY_TO`
`SCREENSHOT_NE_NATIVE_THREAD_BINDING`
`DRAFT_NE_SENT`
`SENT_NE_DELIVERED`
`DELIVERED_NE_READ`
`READ_NE_AGREED`
`REPLIED_NE_ADOPTED`
`SAME_PERSON_NE_SAME_COMMITMENT`
`CANDIDATE_POOL_NE_MAILING_LIST`

## First bounded proof

Audit the current outreach watchlist for every person with more than one possible channel or sender account. Flag ambiguous identity merges, wrong-sender risks, duplicate-thread risks, and commitments that may have been conflated. Make no sends during the audit.