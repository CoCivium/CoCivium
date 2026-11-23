# GroupBuild Idea Commons | First-use comparison protocol R1

**Status:** REVIEW_PROTOCOL_ONLY. No actual participants recruited, sampled, measured or attributed. Do not conflate same-host browser automation with independent receiver usefulness.

## Source scope and question

Two UI variants now exist in one source-bound GroupBuild draft: `simple_baseline.html` (plain text) and `index.html` (rich Float / Sketch / Circle, with the idea first and previews optional). Both are local-file prototypes, without service login, outbound submission, commercial rights grant or active community federation.

**Discriminating question:** Does the extra visual inspiration help a first-time person leave one useful idea **without** making them feel recruited, tracked, compelled to do development work, or confused about where the idea went?

## Safety preflight

- Voluntary adults may test either interface using a fictional suggestion. A separate guardian-approved, age-appropriate test design would be required for minors; **do not recruit children under this R1 protocol**.
- No real names, email addresses, affiliations, private histories, religion, health information, location, recordings or screen capture of user-entered text.
- Use an offline device with no website submission endpoint. Before each session clear both origins' relevant local drafts. Use made-up examples exclusively.
- Explain that stopping anytime requires no explanation; test results, if ever collected, are separately consented and may be declined.
- Neither variant should pretend to receive ideas. Keep is a browser-local action, Export requests a private file, and Clear aims to remove the local copy.

## Matched first-use tasks

1. **Notice:** Without coaching, ask the participant what this experience is for and whether it creates an account.
2. **Contribute:** Ask them to enter a fictional improvement about an invented application. Record task completion and help requests, not the raw idea text.
3. **Keep:** Ask them to preserve it locally and say where they think it went.
4. **Export:** Ask them to request a file they can carry away. Distinguish click from completed browser download, and download from receiver delivery.
5. **Clear:** Ask them to remove the local draft, then reload and check if the fictional text returns.
6. **Walk away:** Ask whether they believe they have joined a group, assigned themselves a task, or surrendered the idea to a service. Record comprehension, not compliance.
7. **Visual option:** Ask whether Float, Sketch or Circle helped, distracted or confused them. In the plain version, ask whether anything was missing.

## Counterbalancing

For a small exploratory comparison, assign alternating or randomized order AB / BA; keep the same fictional task intent, identical device type and assistance rules. Prefer a short rest between versions. Do not infer statistical superiority from a tiny convenience sample. Record accessibility needs only at a privacy-safe functional level if voluntarily disclosed and actually necessary.

## Measurement vector, not a gimmick score

| Dimension | Recorded output |
| --- | --- |
| Task completion | Completed/partial/failed for each of the seven tasks |
| Unassisted first action | Whether they locate the suggestion field without prompting |
| Time to first contribution | Seconds, observed with consent and without text capture |
| Permission comprehension | Separately explain local Keep, Export requested, sent, received, joining, and rights |
| Walk-away confidence | Self-reported 1–5 or unscored qualitative dissent, optional |
| Perceived burden | Self-reported 1–5, optional; distinguish entertaining visuals from work assignment pressure |
| Accessibility | Keyboard-only and assistive interaction issues, with no diagnostic/profile capture |
| Preference | Simple / Rich / Neither / Both for different purposes, with reason |
| Source/privacy errors | Any misleading state claim, failed clear, unsolicited prompt, network effect or unapproved retention |

## Acceptance and fail-fast rules

Stop, fail and preserve a private correction receipt if the page silently sends data; assigns participation; changes a source-term's permission meaning; stores a draft before an explicit Keep; cannot clearly distinguish Export from received submission; or makes a false claim of browser persistence. Positive UX evidence is separate from security, governance, rights, operational availability and actual deployment.

## Automated comparator evidence (not a human test)

Same-host Puppeteer comparison on X2 used the same five-click synthetic path in both variants: sample, Keep, reload, Clear, sample, Export. At 390px, the text-input top appeared at 425px in the simple baseline; in the rich preview original it appeared at 1,332px, after adding a jump link at 1,423px, and after source reorder at **702px**. The final reordering reduced the original difference from 907px to 277px and removed 630px of rich-page lead-in; its extra visual controls remain available after the contribution section.

The final comparator reported two scripted PASS cases, zero detected external requests, zero JS errors and no horizontal overflow at 390, 768 and 1440px. The original 30 source checks and 22 browser QA checks were rerun against the reordered rich page and passed. These numbers are **not** independent participant comprehension, real task times, source review or recipient ACK.

## Lifecycle and next qualified action

`SOURCE_PINNED -> LOCAL_COMPARATOR -> INDEPENDENT_VOLUNTARY_FIRST_USE -> REVIEW_DISSENT -> VERSIONED_CORRECTION -> EXPLICIT_RELEASE_REVIEW -> INDEPENDENT_RECEIVER_PROOF`

**Pending:** The first independently consenting adult must actually use both local prototypes, with exact documented observation and a right to retract their own feedback. No participant exists in this source fixture and no invitation has been sent.

**Rails:** `VISUAL_ENJOYMENT_NE_ADOPTION | CLICK_NE_CONSENT | LOCAL_KEEP_NE_COMMONS_SUBMISSION | EXPORT_NE_RECEIVED | NO_JOB_PROMISE_NE_PROVEN_COMPASSION | SOURCE_QA_NE_HUMAN_ACCEPTANCE | BASELINE_WIN_NE_TOTAL_PRODUCT_FAILURE`.
