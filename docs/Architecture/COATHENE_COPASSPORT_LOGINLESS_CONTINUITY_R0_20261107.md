# CoAthene CoPassport+ R0 | No-password entry with consented child progress continuity

**Public-safe architecture proposal | 2026-11-07 | Not a child account service, identity provider, certified encryption design, operating AI arbitrator or pilot.** This extends CoPrivMin+, existing CoAthene RoamLab child-safety rules, and the optional CoPet/CoPath learning concept. It introduces no real learner identity, sync server, guardian relationship or child progress database.

## Decision: no login screen is an interface goal, not an exemption from authentication

A learner should be able to **start a local educational activity without providing a name, email, password, phone, biometric, age document or school**. The moment the product promises *that the same child's progress will be restored after losing a device*, it must distinguish the **person**, the **right to retrieve a record**, the **pseudonymous record**, the **pet**, and the **access authority**.

**No traditional login ≠ no trust check.** Recovery/sync may require device unlock, a passkey, a guardian-managed recovery action or another cryptographically valid authorization step. That process can be fast and passwordless. A visible parent/child permission moment must not be silently skipped where law, safety or privacy calls for it.

### Five identity and continuity objects, deliberately separated

| Object | Minimum scope | Never assume |
|---|---|---|
| **CoGuest+** | Current offline activity state; automatically disappears on close/reload in R0 | Guest identity can prove which child returned |
| **CoPet+** | Fictional character/lesson state, selected by child | Pet equals child, has emotions, can keep secrets, is a friend, or authenticates a person |
| **CoLearnerHandle+** | Random, high-entropy, site-scoped pseudonymous handle generated only after an authorized opt-in continuity decision | A nickname, device fingerprint, hash of name, birthdate, address, email or biometrics is safe identity |
| **CoPassport+** | Minimum necessary progress entries: original lesson ID/revision, learner-selected goal, evidence or activity confirmation, uncertainty, provenance and correction rights | Activity log equals ability/mental state, an official credit, or a verified identity without authorized key proof |
| **CoDelegation+** | Who may retrieve, correct, share or delete which subset, for which purpose, until what expiry/revocation | Guardian, educator, AI arbitrator and learner have interchangeable legal rights |

**Adult/guardian relations must be independently authorized.** Shared household devices require child account separation; a pet's visual appearance must not unlock another child's record. A rotating, scoped identifier is a pseudonym, not anonymity: cross-context linkage and disclosure of persistent learning data can still create privacy risk.

### Delivery tiers and explicit limitations

| Tier | Start | How progress continues | Evidence/limitations |
|---|---|---|---|
| **Guest** | Immediate; no identity | Session memory only. R0 prototype works now at source level | Nothing survives reload; no remote consent required for purely synthetic, no-data demo |
| **Device-only (future)** | Explicit learner/guardian choice, no typed account name | Encrypted local profile under platform protection and/or trusted OS user profile | Device sharing, uninstalls and loss need separate handling. Web storage is **not** private by itself |
| **Portable passport (future)** | Explicit consent, authorized recovery selection | Encrypted local export/import, using reviewed modern crypto, clear danger about who can open it | A plain QR/URL, name hash or printable progress sheet is **not** a secure identity credential |
| **Optional sync (future)** | Guardian/learner-authorized, accountless-looking passkey ceremony | Scoped encrypted storage, device-bound or synced passkey authentication, independently verified recipient | This still creates a service account-like record, needs lifecycle, deletion, incident response and real server security |
| **Institution federation (future)** | Authorized school plus relevant parent/learner permission and law | Separate school-scoped credential and minimum learning evidence under school controls | Never auto-synchronize to every teacher, guardian or third party; legal record retention may apply |

A physical passkey or synced passkey can eliminate username entry and shared passwords, but registration and recovery are still **authentication**. WebAuthn does not by itself provide encryption at rest or prove guardian status; those are separate design and operational obligations. Consult [W3C WebAuthn](https://www.w3.org/TR/webauthn/) and qualified security and child-privacy reviewers for a real implementation.

## Teaching pet vs learner proxy vs safeguarding

**CoPet R0:** the learner teaches a fictional Moss character by choosing a defensible claim and evidence; the character responds with a dated subject explanation and disconfirming case. This demonstrates *learning by teaching*, not a synthetic companion that can observe or profile children.

**Possible CoProxy+ later:** a minimal scoped, revocable learning handle can route a progress capsule without disclosing a real name to every module. A proxy cannot autonomously give adult consent, recover school records, speak in the child's voice or infer their private preferences.

**CoGuard+ later:** a rules/source checker can identify a contradictory claim and show why a lesson is uncertain. A synthetic checker is not an independent guardian, therapist, human safeguarding officer, legal arbitrator, or proof of pupil identity. Child-safety decisions, real-world incidents, access grants, and important educational evaluations must have legitimate human accountability and appeal.

### Boundaries that must fail closed

1. No stealth device fingerprint, IP fingerprint, login-by-face, voice clone, exact birthdate or tracking pixel to make accountless feel seamless.
2. No persistent interest/profile history, ad targeting, emotion prediction, behavioral manipulation, synthetic attachment, endless streaks or unsafe private one-to-one channels.
3. No cleartext learner record in a URL, public QR, public repository, logs, analytics, AI training corpus or product debugging ticket.
4. No automatic parent/guardian claim from possession of a device, house, email, pet name or invite link.
5. No wholesale cross-institution access or child-activity mining because “education is a common good.”
6. No permanent parental visibility beyond age-appropriate, lawful permissions; children gain independent privacy and control as they develop.
7. No credential based on a printable “progress receipt” alone. A plain progress copy is **not** identity authentication, proof of independent learning, a grade, or tamper-resistant credit.

## Trust, recovery and durable rights

For any real learner progress service, first specify: responsible operator and jurisdiction; why a stable handle is necessary; lawful basis and age-appropriate guardian/learner consent; what proof allows recovery; key/device loss; revocation and delegation; minimal data fields and encryption; integrity/anti-rollback; retention and deletion; teacher access; accessibility; sibling separation on shared devices; breach procedure; human remedy and appeals; alternative no-ID route.

**A proposed progress atom:** `{lesson_id, revision, viewed_explanation, source_status, revision_event, learner_chosen_next_interest}`. Make each field optional and purpose-bound; avoid collecting detailed interaction traces or raw chats as a default. An adult educator may need outcome evidence beyond clicks. A toy check-box is not mastery.

**CoPrivMin+ boundary:** Publish the architecture and synthetic verification tests. The actual handle, guardian tie, key, custody receipt, enrolment or learning history remain private unless lawfully disclosed with specific consent and purpose.

## Evidence donors and next product gate

- [Canada OPC Children's Privacy Code, October 2026](https://www.priv.gc.ca/en/privacy-topics/privacy-for-businesses/protection-of-children-for-businesses/childrens-privacy-code/children-code-final-report-2026/): high-privacy defaults, parental consent under 13, data minimization, correction/deletion, restrictions on profiling.
- [UNICEF AI-and-children guidance v3](https://www.unicef.org/innocenti/reports/policy-guidance-ai-children): privacy, agency, explainability, safety and AI companion risks.
- [W3C Web Authentication](https://www.w3.org/TR/webauthn/): discoverable credentials/passkeys can provide passwordless authentication and local user verification, not child legal identity.
- [CoAthene child-safety and accessibility baseline](../Business/CoAthene_RoamLab_R0/SAFETY_PRIVACY_ACCESSIBILITY.md).
- [CoPrivMin+ public-safe projection](../Governance/COPRIVMIN_PUBLIC_PROJECTION_R0_20261107.md).

**Next proof:** offline fictional CoPet activity, zero collected identifiers and zero persistent progress. Show a plain *“progress this visit only”* line; a child can reset at any time. Independently test whether adult educator reviewers distinguish (a) a toy's answer from verified mastery; (b) a visual CoPet from a trusted child ID; and (c) true optional sync from false no-login promises. Only after threat model and privacy review, prototype **guardian-controlled portable continuity** with actual cryptographic integrity/recovery tests. For genuine remote sync, add a separately authorized service with passkeys, not a hidden anonymous persistent tracking channel.

`LOGINLESS_UX_NE_NO_AUTHENTICATION | CHILD_PET_NE_CHILD_ID | NO_LOGIN_NE_NO_PRIVACY_DUTIES | PRINTED_PROGRESS_NE_VERIFIED_IDENTITY | PASSKEY_NE_LEGAL_GUARDIANSHIP | SYNTH_ARBITER_NE_HUMAN_SAFEGUARDING | CANDIDATE_NE_CHILD_PILOT`.
