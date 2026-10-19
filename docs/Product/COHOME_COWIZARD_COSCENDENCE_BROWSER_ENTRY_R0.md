# CoHome / CoWizard / CoScendence Browser Entry R0

**State:** PUBLIC CANDIDATE ONLY; no installation, runtime adoption, store listing, or CoAll authority grant.
**Related:** [CoVIA/CoOrb issue #181](https://github.com/CoCivium/CoCivium/issues/181), `COPLATFORM_HELPER_ECOLOGY_REPOZIPPER_R0`, `COVIRTUAL_SESSION_MORPHOLOGY_R0`, `COSESSION_SUBSCRIPTIONS_R0`, `COEVIDENCE_RECEIPT_GUARD_R0`.

## Product braid
`CoHome -> CoCatalogue -> CoWizard/CoWiz -> CoModule -> CoVIA -> CoOrb/CoPop/CoBar -> CoProof -> CoAckRewised`.

- **CoHome** is a participant-relative, private-by-default home for trusted links, capabilities, active tasks, custody pointers, and reversible preferences; not one machine or central authority.
- **CoCatalogue** is a searchable registry of *descriptions*, not a bulk installer. Each item has a stable ID, display name, CoTerm aliases, purpose, inputs/outputs, dependencies, provenance, exact version/compatibility, license and notices, privacy, required permissions, available embodiments, alternative implementation, health, evidence, authority ceiling, consent and uninstall/rollback instructions, and lifecycle status.
- **CoWizard** composes goal-directed steps from the catalogue. **CoWiz** is a reusable typed step, not an unconstrained AI agent. Every step states required inputs, reversible preview, human gate, receipt, next transition, and failure/undo path.
- **CoTermables** provides definitions, aliases, disambiguation, legacy translations, and source-linked usage. Do not mint duplicate concepts from naming variants.
- **CoHandle** resolves a typed portable reference to an object, capability or receiver, with expiry, privacy classification and source binding; possession of a handle never implies effect authority.
- **CoScendence** is an optional adoption bridge for current browsers; **CoBrowser** is a future optional embodiment, not a mandatory migration.

## Browser capability ladder
`DISCOVER -> EXPLAIN -> PREVIEW -> EXPLICIT_INSTALL -> PERMISSION_REQUEST -> ENABLE -> OBSERVE -> VERIFY -> OPTIONAL_EXPAND -> DISABLE/UNINSTALL`.

**R0 proposal:** Manifest V3 extension with only an action popup or side panel and local/static catalogue fixtures. No host permissions, content scripts, history, tabs, clipboard, camera, microphone, or network access by default. Never equate detected interest or visited pages with consent. The user chooses the browser-store installation and enables modules individually. Elevated site/host access may be requested only for a named feature in a user gesture, with plain explanation and a revoke path.

Optional native-message host is a separately installed, authenticated, least-privilege CoModule, explicitly approved and independently uninstallable. Browser messaging alone does not prove local runner authority. No silent sideload, forced store install, auto-enable, cross-site scraping, covert monitoring, or permission expansion. A future CoBrowser migration must be opt-in, preserve bookmarks and user data under explicit import scope, and offer independent rollback.

## Minimal catalogue and wizard record
```json
{
  "catalogue_entry_id": "cocivium.example.readonly-process-inventory",
  "version": "0.0.1-candidate",
  "status": "CANDIDATE",
  "audience": ["human", "agent"],
  "terms": ["console-window-diagnosis", "CoRunObserver"],
  "purpose": "Explain which managed process owns an interrupting console window",
  "capability": "read_only_inventory",
  "inputs": ["explicitly_selected_local_target"],
  "outputs": ["human_explanation", "receipt_pointer"],
  "embodiments": ["CoHome", "CoOrb", "browser_side_panel"],
  "permissions": ["local_inventory_after_separate_consent"],
  "authority_ceiling": "READ_ONLY",
  "dependencies": [{"name": "local-host-adapter", "state": "NOT_INSTALLED"}],
  "privacy": "LOCAL_FIRST_NO_BACKGROUND_PAGE_OBSERVATION",
  "proof": "NONE_YET",
  "rollback": "disable_or_uninstall",
  "consent_required": true
}
```

Wizard transition:
`GOAL -> DISCOVER -> QUALIFY -> EXPLAIN -> PREVIEW -> USER_COMMIT -> AUTH_CHECK -> BOUNDED_DEED -> EFFECT_RECEIPT -> HUMAN_FEEDBACK -> REVISION`.
A draft/hover/suggestion cannot become a commitment or install request.

## Progressive surfaces
One semantic object, distinct receiver projections: CoHome search, CoWizard step, CoOrb glance, CoPop exception, CoBar task indicator, mobile, desktop, voice and agent-readable JSON. Delivery, pickup, readback, comprehension, adoption and benefit are separate evidence states. UNKNOWN cannot be rendered as green.

## Priority candidate catalogue families
Onboarding; device setup; accessibility; process/no-popup diagnostics; backup/restore; home networking; source/repository migration; CoTerm disambiguation; permissions audit; privacy review; CoStead receiver readiness; source citation; contradiction detection; CoMap topology; temporal history; performance/energy; extensions and open-source donor qualification; software update rehearsal; agentic workflow design; CoOrb/CoVIA continuity; local AI onboarding; documentation translation; offline recovery; consent and revocation; education and shared commons.

Materialize specific wizard steps only for proven demand; do not generate one process or extension per catalogue entry.

## Bounded proof plan
1. Validate catalogue fixture schema and basic search/alias selection offline.
2. Render a static browser side-panel mockup with no privileged permissions or network calls.
3. Demonstrate one read-only `CoRunObserver` wizard using simulated inputs and explicit UNKNOWN markers.
4. Test keyboard access, screen readers, reduced motion, privacy, opt-in and immediate disable.
5. Independently inspect Manifest V3 browser compatibility, exact upstream licenses, package contents, store disclosure and permission prompts.
6. Only after an actual install decision: explicit scoped canary with rollback, receipts and named receiver.

## Nonclaims and rails
`CANDIDATE_NE_INSTALLED`; `DISCOVERY_NE_CONSENT`; `INTEREST_NE_INSTALL_AUTHORITY`; `EXTENSION_NE_BROWSER_CONTROL_PLANE`; `HANDLE_NE_PERMISSION`; `WIZARD_SUGGESTION_NE_DEED`; `STORE_LISTING_NE_USER_ACCEPTANCE`; `AUTOMATED_TEST_PASS_NE_RECEIVER_BENEFIT`; `COBROWSER_NE_REQUIRED_UPGRADE`.

No browser extension package, store submission, local-device integration, permissions grant, human acceptance or CoAll runtime adoption is asserted here.
