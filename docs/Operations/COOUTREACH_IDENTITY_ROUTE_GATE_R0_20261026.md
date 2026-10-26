# CoOutreach Identity / Routing Gate R0

**State:** \`PUBLIC_SAFE_SOURCE_CANDIDATE__STRUCTURAL_CHECK_ONLY__NO_EXTERNAL_SEND\`.

This is a narrow companion to [CoRelationshipBraid+](../Architecture/CORELATIONSHIP_BRAID_FABRIC_R0_20261026.md), [CoOutreach Influence Fabric](../Architecture/COOUTREACH_INFLUENCE_FABRIC_R0_20261025.md), and [CoReviewSpine+](../Governance/COREVIEW_SPINE_R0.md). It does not create a second CRM, authenticate an email account, identify a person from a name, grant a sender role, or send any message.

## The rule

Before any actual external communication, answer:

1. **Who authored it?** Named person or appropriately disclosed agent; attribution and content source.
2. **Who controls the sending account?** Actual authenticated mail account plus separate verified send-as authority for an alias. A display name or draft folder does **not** prove an address can be used as From.
3. **Who is the intended audience?** Stable person/organization IDs, current address source, individual To/CC/BCC scopes, contact permission and suppressions.
4. **Who is in the live thread?** Actual message/thread identity, participants and reply/reply-all/forward scope. Reply-all, group, and forwarding need their own explicit scope review.
5. **What will be said and disclosed?** Exact subject, body, attachments, third-party attribution, factual status, privacy and the appropriate audience.
6. **What is approved?** Human-visible exact draft fingerprint plus specific sender, recipients, channel, thread, payload and attachments. Editing any of these invalidates the fingerprint.
7. **What happened?** Drafted, approved, sent, delivered, observed and acknowledged are different events requiring different receipts.

Never infer an endorsement, consent, identity or authority merely because a relationship, email thread, contact name or quoted person's name exists. **A message about Michael Murphy is not necessarily a message to Michael Murphy.** A message meant to copy Darren must not quietly go to all participants of another thread. CoCivia is a proposed author persona/role, not proof that \`CoCivia@...\` can be used as an authenticated sending address. Do not put real addresses, private message bodies, account data or contact graphs into a public repository.

## What is automated today

Run the stdlib-only, network-free validator on a privately maintained envelope (not a public example with real personal data):

\`\`\`sh
python3 scripts/CoOutreachIdentityGateR0.py <PRIVATE_ENVELOPE_JSON_PATH>
python3 -B -m unittest discover -s tests -p test_outreach_identity_gate_r0.py -v
\`\`\`

The validator returns \`HELD\` with issue codes or \`REVIEW_READY_ONLY\` and a bound SHA-256 fingerprint; it never emits or dispatches the message. It intentionally does **not** echo the body or addresses. The fingerprint detects subsequent edits; it is not a cryptographic signature, an authenticity attestation, a consent record, or proof of Gmail/WhatsApp transport state.

All source/permission/review references in the envelope are *claims supplied by the envelope*. A human or trusted external adapter must verify them against actual source records and the live account/thread **at send time**. Explicit send authorization must be checked separately. The validator cannot semantically prove that every named person in the prose is correctly identified; a review remains necessary even after a green structural result.

## Adversarial checks

The synthetic tests include intended-versus-actual person mismatch, changed email after review, unverified sender alias, unverified Reply-To, reply-all scope, recipient outside thread, duplicates across To/CC, shared ambiguous names, unsupported consent, unverified endorsement, attachment-audience mismatch, subject header injection, restricted privacy review, and changed content invalidating approval.

## Future adapter protocol

A real Gmail, Fastmail, WhatsApp or local/open agent adapter must obtain a fresh authoritative address/account/send-as/current-thread snapshot and compare it to the approved envelope **immediately before** offering Send. Any mismatch: \`HOLD_AND_SHOW_DIFF\`. Separate delivery/recipient-origin readproof is required to climb the receiver ladder. Local/open-source and non-AI paths should consume the same JSON envelope; no provider has privileged authority.

**No automatic CC/BCC insertion, reply-all, bulk fanout, resurrection of archived groups, or unsolicited follow-up.** A quoted or proposed email address is not a verified identity. Do not re-send after ambiguous transport failure without idempotency and actual provider message-ID reconciliation.

\`PERSON_NE_THREAD\` · \`DISPLAY_NAME_NE_VERIFIED_IDENTITY\` · \`EMAIL_IN_CONTACTS_NE_PERMISSION\` · \`SENDER_ALIAS_NE_SEND_AS_AUTHORITY\` · \`DRAFT_REVIEW_NE_SEND_APPROVAL\` · \`SEND_NE_DELIVERY_NE_READ\` · \`RICK_NE_MAILMAN\` · \`CANDIDATE_NE_RUNTIME\`.
