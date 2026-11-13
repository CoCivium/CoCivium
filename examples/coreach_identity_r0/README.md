# CoReach+ / CoRelationshipBraid+ Pre-Send Identity Gate R0

**State:** OFFLINE REVIEW-ONLY CANDIDATE; no interception of Gmail/WhatsApp, no mail transport, no installed runtime, no automatic sending authority.

## Scope

One intended message may involve **six different identities**, and none may be silently equated:

1. The authenticated transport account.
2. The selected From/Reply-To identity and verified send-as authority.
3. The human/AI who drafted the words.
4. The principal on whose behalf the words are offered.
5. The actual To/Cc/Bcc audience and verified person/organization bindings.
6. People mentioned, quoted or represented in the body who are **not necessarily recipients**.

Existing semantics are reused: `CoOrg+` owns identity/role claims; `CoRelationship+` persists across channels; `CoThread+` is the actual conversation; `CoReach+` tracks intended/sent/delivered/acked separately; `CoReceiver+` owns needs/preferences/consent. This is a **pure validator** of an explicitly assembled pre-send context envelope, not a new CRM, source of authority, or identity provider.

## Gate

`WHO-WROTE -> WHO-SIGNS -> ACTUAL FROM ACCOUNT -> WHO-IS-ADDRESSED -> WHO-IS-REFERENCED -> THREAD/REPLY-TO -> AUTHORITY/PRIVACY/SUPPRESSION -> HUMAN REVIEW -> SEPARATE ACTUAL SEND -> SEND-ID -> RECEIVER PROOF`

Fails closed on unknown From, sender alias, recipient, recipient route, group/membership state, Cc visibility, Bcc authority, mismatch between declared intended audience and actual header recipients, ambiguous relay/intermediary, stale identity proof, changed reply audience, quoted-speaker attribution, unapproved disclosure, opt-out/bounce/repeat and absent scoped approval. Every content statement and identity binding must be inspected outside this pure function; self-declared evidence is **not cryptographically verified** by it.

The gate never yields `SENT` or `SEND_ALLOWED`. Its highest state is `READY_FOR_HUMAN_REVIEW_ONLY`. Even successful manual review still requires the actual **separate, recipient-specific send authority** and a transport action with its own receipt.

## Run

Python 3.11+, standard library only.

```sh
python3 -m unittest -q test_coreach_identity_gate_r0.py
python3 CoReachIdentityGateR0.py < reviewed-preflight.json > receipt.json
```

The tool reads up to 128 KiB of explicit JSON stdin, examines at most 64 specified recipients, and writes one compact JSON review receipt to stdout. It does not enumerate or read mailbox content, resolve contacts, parse bodies, invoke models, touch the clipboard, write files, or start a process other than itself. Malformed data is refused without echoing it. The stdout receipt includes email-address hashes; **unsalted hashes are pseudonyms, not guaranteed anonymity**, so the receipt itself should remain scoped to its authorized audience.

## Requirements for the upstream reviewer

- Exact sender account comes from the connected transport, **not** from a signature or a subject saying "send from".
- A send-as alias needs independently observed provider permission; historical emails, Google Contacts entries, signatures and screenshot display names are not sufficient.
- To/Cc/Bcc identities require exact-route provenance, currentness and consent/permission review. A contact entry only establishes that an address was seen.
- When writing to an **intermediary** about a third person, the intermediary is the addressed person. Never record a direct send, reply, agreement, or endorsement by the referenced person.
- Reply-To and original participants should be inspected when continuing a thread; don't silently add a third party to inherited private context.
- Quotes and forwards have their own speakers; pasted content is not authored by the sender of the enclosing message.
- The human recipient and visible author/signer need to understand whether AI generated the draft and for whom the sender is writing.
- Every email with third-party information or sensitive claims needs a separate privacy/rights review.
- Do not equate `DRAFTED`, `SENT`, `DELIVERED`, `READ`, `ACK`, `AGREED` or `ADOPTED`.

## Test & privacy boundary

`test_coreach_identity_gate_r0.py` contains only fictional `example.test` address fixtures. **No private Gmail addresses, bodies, message IDs, contact names or relationship mapping belong in this public candidate**. Real draft audit findings are a separate restricted record. This module is not installed as an unavoidable Gmail send hook and cannot prevent someone using a different email client. It is a reusable component pending an explicitly authorized adapter and receiver acceptance.

Core non-equivalences:

`SPEAKER_NE_TRANSPORT_SENDER | SIGNATURE_NE_VERIFIED_FROM | MENTIONED_PERSON_NE_RECIPIENT | TO_INTERMEDIARY_NE_TO_THIRD_PARTY | CC_NE_PRIVATE | THREAD_NE_PERSON | CONTACT_NE_CONSENT | SENT_NE_DELIVERED | ACK_NE_ENDORSEMENT | CHECKER_PASS_NE_SEND_AUTHORITY`
