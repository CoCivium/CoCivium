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

## R0.1 | Lost device, no child biometric vault (2026-11-07)

**User challenge:** kids lose passports, cards, keys and devices; biometrics seem harder to misplace. That is true for the **physical trait**, not for a lost device or the right to retrieve encrypted data. The distinction matters more than a clever login-free illustration.

### The stronger design: CoRecoveryMesh+ as an *optional* scoped identity recovery method

| Situation | Proposed authorized continuation | Protection or failure state |
|---|---|---|
| **No saved profile** | Guest CoPet works immediately with fictional content and in-memory progress | No real identity or progress to recover; no child account |
| **Same trusted device** | A platform-protected, user-selected local progress vault (future) may unlock using device PIN or local biometric | **Not built**. Require sibling-safe OS separation and an alternative unlock method. Browser storage alone is not an encrypted private vault |
| **A second pre-authorized device or guardian** | Another bound passkey or approved device can authenticate a narrow retrieval of the learner's encrypted capsule | Register in advance with consent. Revoke the lost device, rotate keys if exposed, record lawful access and avoid exposing the child's real name |
| **Device lost; guardian still has access** | Guardian verifies their own independent authorization, then helps the child recover a **scoped** record on a new device | A guardian relationship must have been validated and remain lawful; holding a phone, sharing a surname or knowing pet name is not proof |
| **Both devices/keys missing** | If configured, use a separately protected recovery key or appropriately vetted multiple-trustee recovery, with rate limiting, review, revocation and appeal | If nobody can prove authority and no recovery path exists, **HOLD / data may be unrecoverable**. Do not silently bypass encryption, demand child biometric enrollment or reveal family relationships |
| **Child growing older / guardianship changes** | Age-appropriate transfer of access, consent renewal and revocation of prior delegated powers | Not perpetual parent surveillance, school ownership or indefinite behavioural archive |
| **No biometrics available, inaccessible or refused** | PIN/platform verification, approved security key or other appropriate non-biometric credential | Equivalent opportunity to learn; no biometric participation requirement |

**Biometrics belong at the *edge*, if used at all.** Device-local face or fingerprint recognition can activate a cryptographic passkey. In standard WebAuthn, the relying service receives a signed assertion, **not the biometric sample**. A server-side biometric registry is not a backup for an absent or lost physical authenticator. A child's biometric features can change; sensors fail; fingerprints and facial images are not revocable secrets; false matches/non-matches exist and access can be coerced. **No central biometric template, emotion-recognition identifier, gait/voice fingerprint, latent cross-site device fingerprint or child face database is part of this proposal.** [NIST SP 800-63B (2025)](https://pages.nist.gov/800-63-4/sp800-63b.html) limits biometrics to multifactor use with a physical authenticator and requires a non-biometric alternative. [WebAuthn](https://www.w3.org/TR/webauthn/) defines authenticator-local verification, not a legal guardianship certification.

### CoRecoveryMesh+ capability/permission model, not an assumed implementation

1. Random **site-scoped** learner handle, separated from real-world identity. Handle alone **never** grants access.
2. One or more independent **cryptographic authenticators** bound to appropriate access scopes; guardian rights are separately documented, time-bound and revisable. A synced passkey may be convenient, but a single synced-provider account creates shared-provider recovery risks.
3. Optional **end-to-end encrypted** minimal progress capsules and optional backed-up/recoverable data keys. Authentication of access and encryption of *data* are separate components; loss of every unlocking key is a real failure, not something a pet avatar can repair.
4. Existing trusted device or approved guardian can initiate new-device binding; verify intent through a safe authenticated channel; log only minimal authorized receipt; **do not transfer raw biometrics**.
5. Revocation, rollback detection, lost-device response, guardian dispute, sibling separation and child age transition must be tested before production. Multi-trustee recovery, if ever used, requires professional design and must not become a covert permanent parental watch service.
6. If rights, recovery trust or provenance cannot be established, **stop and explain why**. Do not grant access merely to avoid UX friction.

**What “loginless” may honestly mean:** no routine typed username or password and no account to enter a guest demo. A persistent, cross-device, child-specific record still needs explicit registration, key use, and lawful consent at appropriate moments. A hidden background identifier is **not** a safer substitute.

### Disconfirming recovery drills before any real learner

- A child chooses Moss on a family tablet; verify a sibling cannot read the first child's progress via the same pet selection.
- A device is reported lost; test that its credential is invalidated and a correctly authorized second device can retrieve only the intended minimum capsule.
- Both recovery methods are unavailable; system reports **UNRECOVERABLE_OR_HELD** instead of opening a backdoor.
- Biometric access is refused or unavailable; a non-biometric method works with equivalent learning access.
- Guardian authority expires or is contested; future access refuses unauthorized historical browsing.
- A public recovery link/QR/screenshot is leaked; it cannot alone authenticate, authorize access, or reveal identifiable learning records.
- A child requests correction/deletion; the responsible operator demonstrates appropriate effective control, including lawful limits.
- A hostile participant knows the pet, surname, school and birthdate; still cannot authenticate.
- A passkey is available but the record-decryption key is gone; the design must not promise data decryption merely because login succeeded.

**Release boundary:** **This is a design and test plan, not a secure implementation**. CoPet R0 remains in-memory only. No child ID, biometric, encrypted profile, real guardian, sync, contact, credential or permanent progress has been created.

`BIO_TRAIT_NE_SECRET` · `LOCAL_BIOMETRIC_NE_GLOBAL_CHILD_ID` · `PASSKEY_NE_DATA_DECRYPTION_KEY` · `AUTHENTICATION_NE_GUARDIAN_AUTHORITY` · `LOST_ALL_KEYS_NE_SILENT_BACKDOOR` · `NO_LOGIN_UI_NE_NO_AUTHENTICATION` · `CHILD_RIGHTS_SURVIVE_RECOVERY`.

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
