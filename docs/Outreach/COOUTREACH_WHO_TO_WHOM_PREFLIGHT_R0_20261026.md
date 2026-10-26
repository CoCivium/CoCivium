# CoOutreach Who-to-Whom Preflight R0

**State:** PUBLIC-SAFE REVIEW CANDIDATE; NOT A LIVE CONTROLLER, CONFIRMED IDENTITY, OR SEND AUTHORIZATION.
**Observed:** 2026-10-26

## Scope

Before sending a message, resolve **who is communicating, who drafted and approved it, which authenticated account will send it, exactly who will receive it, what the exact message asserts or requests, and which delivery/receiver states are actually proven**.

This is an outgoing acceptance gate for existing [CoRelationshipBraid+](../Architecture/CORELATIONSHIP_BRAID_FABRIC_R0_20261026.md), [CoOutreach+](../Architecture/COOUTREACH_INFLUENCE_FABRIC_R0_20261025.md), [CoReach/CoOrg](../Architecture/CORELATION_CLOUD_CLUSTER_ORG_BRAID_R0_20261026.md), and [CoCivia front identity](../Identity/COFRONT_COCIVIA_GITHUB_R0.md). It is **not** a new CRM, broadcaster, sender, identity root or authority fabric.

## Distinguish the actors

- **Principal:** human/organization responsible for the communication.
- **Drafter:** human, model, agent or disclosed composite front that prepared a particular version.
- **Front:** projected voice/persona. CoCivia is not automatically a legal principal or a Gmail mailbox.
- **Seat:** the actually authenticated account, verified From identity, authorized aliases and Reply-To route.
- **Approver:** actor whose scoped permission is bound to exact content, audience, sender and expiry.
- **Recipient:** actual individual/organization with identity and delivery route independently matched. Namesakes must remain distinct.
- **CC/BCC audience:** all additional recipients; check privacy and authorization for each.
- **Referenced party:** a person/organization described in the content; not automatically its recipient, author or endorser.
- **Receiver:** independent destination whose response, acknowledgment or adoption requires separate evidence.

`PERSON_NE_ACCOUNT | FRONT_NE_PRINCIPAL | DRAFTER_NE_SENDER | CONTACT_NAME_NE_IDENTITY | CITED_NE_ENDORSED`

## Exact pre-send gate

Bind a stable work ID, revision, SHA-256 of the *exact private message*, permitted audience, current channel, and a private message-body pointer. Never commit unpublished correspondence or real private contact routes to a public repository.

Check: (1) principal/front/drafter/approver separation; (2) authenticated sender and alias; (3) To/CC/BCC + Reply-To; (4) actual recipient identity, route, relationship and opt-out state; (5) whether this is an introductory email or a verified reply thread; (6) subject, factual claims and citations, speculative framing, potential implied endorsement, attachments and ask; (7) privacy and effect ceiling; (8) human approval for **this exact hash, account and audience**; (9) send-state evidence.

If content, account, audience, recipient identity, thread context, claim or attachment changes, requalify the approval. Do not silently overwrite an earlier revision.

## Provenance and status

`PROPOSED -> DRAFTED -> REVIEWED -> AUTHORIZED -> SENT -> DELIVERY_OBSERVED -> RECEIVER_ACKED -> UNDERSTOOD/USED(IF_PROVEN)`

A sender mailbox open in a browser is not connector API access. A Gmail draft is not sent. Draft CC is not delivery. A sent provider message ID is not an independent recipient ACK. Silence is not rejection.

`BROWSER_VISIBLE_NE_CONNECTOR_ACCESS | DRAFT_NE_SENT | SENT_NE_DELIVERED | DELIVERED_NE_READ | READ_NE_ENDORSEMENT`

## Specific collision cases to test

- A contact happens to share a public figure's name: **hold biographical personalization** until sourced identity match.
- A draft exists in a different Gmail account from the intended sender: **hold account-specific send** even when the browser shows the intended account.
- A human-approved text changes after approval: **hold** and require reapproval of exact content hash.
- Sender alias, Reply-To or CC/BCC changes: **hold**.
- No-contact or uncertain consent/preferences: **hold**.
- A tool result reports draft or sent state but no receiver readproof: **do not claim receiver pickup, adoption or endorsement**.

## Test and authority limits

A dependency-free local structural checker and 23 synthetic-only tests were exercised alongside this proposal. They detect missing fields and false state transitions; they do **not** authenticate accounts, verify the recipient's identity, infer meaning from text, authorize sends or read delivery from a provider. The attached draft code must be separately reviewed and connected to actual sources before operational use.

Next eligible proof: a **read-only**, account-scoped examination of one real intended sender mailbox, one exact existing draft and its actual recipient identity; then a human-visible preflight. No send, mass fanout, private GitHub disclosure or deployment is part of R0.

`STRUCTURE_PASS_NE_SEND_AUTHORITY | PUBLIC_SOURCE_NE_RUNTIME | PROVIDER_MESSAGE_ID_NE_RECEIVER_ACK | HUMAN_REVIEW_REMAINS_REQUIRED`
