# CoDOM+ R0 | Structural mining across browser and non-browser surfaces

**State:** `OFFLINE_PUBLIC_SYNTHETIC_CANDIDATE__NO_BROWSER_OR_WINDOWS_CAPTURE__NO_RUNTIME`  
**Observed:** 2026-11-03  
**Continuity root:** existing CoBrowser/CoOrb R0 architecture and CoQuanta/CoMap projection grammar.

## Purpose

DOM mining is useful when it means extracting **authorized, useful relations** from document and interface structure without turning a visible page or application window into a source-of-truth or a blanket data-harvesting license.

*Browser:* DOM, accessibility tree, selected metadata and change observations, only for a user-authorized surface. A DOM is a structure of a page, not what the viewer understood, whether the page is true, whether the backend is healthy, or whether an action actually completed. JS-rendered state, shadow roots, cross-origin frames, dynamic controls and accessible names require real browser APIs and distinct permissions. This R0 intentionally implements none of those captures.

*Beyond browser:* Windows UI Automation, mobile accessibility/view hierarchies, structured PDF trees, code ASTs, scene graphs and typed native application objects. Those are separate adapters, not literally DOMs. They can normalize to a common **CoQuanta structural packet** while preserving their origin, evidence class, uncertainty, authority, currentness and missingness.

## First bounded test

`python3 -m unittest discover -s examples/codom_structure_r0 -p 'test_*.py' -v`

`python3 examples/codom_structure_r0/CoDOMStructureR0.py --fixture examples/codom_structure_r0/fixture.json`

Synthetic HTML fixture A and synthetic HTML fixture B share one `work_id` and `source_id`; the button changes from `Inspect evidence` to `Challenge evidence`. Native-accessibility fixture C represents the same selected four semantic objects as B. R0:

- extracts only an explicit identifier, approved role, and bounded label;
- ignores password/hidden controls and strips URLs and value properties;
- rejects wrong privacy/authority, oversized input, unexpected schema and duplicate semantic identities;
- reports A→B as a one-object change, B↔C as matching semantic fingerprints;
- marks currentness `UNKNOWN`, acknowledgement `UNPROVEN` and effects zero;
- records missing-in-after as `not_observed`, not proven nonexistence.

**21/21 local Python tests passed** in the authoring environment (Python 3.13.2, isolated Linux container). These check structural policy on synthetic inputs only. They do not establish end-to-end X2, Edge, Chromium, Firefox, WebView2, Windows UI Automation, provider/API, accessibility, OCR or independent user behavior. Equivalent synthetic labels do not prove all DOM and accessibility trees carry equivalent real-world information.

## Integration contract

`CONSENTED_SOURCE -> ADAPTER_DOM_OR_NATIVE -> STRUCTURAL_QUANTA -> SOURCE_BIND -> TYPED_COTRAIL -> DELTA -> COBROWSER/COORB_VIEW -> OPTIONAL_CHALLENGE`.

Candidate structural packet:

`work_object_id | source_id/hash | adapter_kind | observer/capture_scope | observed_at | privacy_ring | authority_ceiling | role | semantic_id | accessible_label_or_whitelisted_name | evidence_class | currentness | relation_digest | delta_from | omitted_classes | missingness | recovery_pointer | next_permitted_action`.

The prototype does not capture `input.value`, passwords, auth tokens, content of private frames, cross-origin material, unsent drafts, private email/message content, cookies, localStorage or unknown personal data. No hidden monitoring or general web crawler. Browser automation and cross-origin data access require separate authorization and source-specific policies.

## Useful future canaries

1. One opt-in, expendable local HTML page served in a disposable test origin. Compare actual browser DOM vs accessible roles, test language/contrast/keyboard, no private user text. Capture only allowlisted public structural labels. A real browser observation must document its permissions and declared omission/losses.
2. One local Windows UIA window under user/elected observation. Normalize *public synthetic* labels; test privacy, currentness, foreground interference and unavailable-API fallback. No X2 claim until observer is actually connected and independent readproof exists.
3. One source delta -> selectively invalidate only dependent relations -> one hot receiver plus one async pending receiver -> replay and compare independently acknowledged source hashes. If unavailable, mark unknown rather than green.

## Existing sources

- [`docs/Architecture/COBROWSER_COORB_CONTINUITY_R0_20261027.md`](../../docs/Architecture/COBROWSER_COORB_CONTINUITY_R0_20261027.md)
- [`docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md`](../../docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md)
- [`docs/Architecture/COBROWSER_RENDERER_SUBSTITUTION_R0_20261027.md`](../../docs/Architecture/COBROWSER_RENDERER_SUBSTITUTION_R0_20261027.md)
- [`examples/conotspace/README.md`](../conotspace/README.md)

**Rails:** `DOM_NE_WHOLE_UI` · `NATIVE_TREE_NE_BROWSER_DOM` · `STRUCTURE_NE_TRUTH` · `VISIBLE_NE_CURRENT` · `READ_NE_SEND_AUTHORITY` · `SCREENSHOT_NE_DOM` · `UNKNOWN_NE_ABSENT` · `USER_CONSENT_NE_GLOBAL_SCRAPING` · `LOCAL_TEST_NE_X2` · `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.
