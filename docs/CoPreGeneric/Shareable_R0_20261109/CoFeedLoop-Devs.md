# CoFeedLoop | Public candidate developer feedback

Status: DRAFT / source-reported observations, not confirmed upstream bugs. Independent reproductions required before assigning vendor defects.

## Reported friction and reproducibility checks
- Static mouse-button text causes repeated human copy work. Test one-line URL against long prompt and record success, retry count and time-to-value.
- User reports Logitech text truncation. Record mouse/software version, configured input, actual clipboard output, text length and reproducible capture before asserting a product limit.
- Pasted model replies sometimes declare PASS or 'drained' without matching durable and independent evidence. Compare receiver proof against reply claims.
- Some sessions generate further concepts where a bounded, deduplicated recovery was requested. Measure useful unique objects versus duplicates and total human relay burden.
- WhatsApp transcript, ChatGPT conversation and GitHub artifact are different custody scopes. Test authorized transfer and exact-object recovery rather than presuming shared context.

## Candidate order of engineering work
P0 independent receiver with readback, custody and privacy boundary; P1 idempotent source-bound dedupe; P2 currentness and last-known-good rollback; P3 short mouse pointer with safe fallback; P4 verified mirror/URL resolution; P5 session summary and stop rules; P6 optional accessibility-aware audio; P7 multi-provider challenger and replay.

## Alternative designs
- Public discovery index plus private, authenticated source store; no blanket release of private chat.
- Machine-readable CoSynthVerse projection and human-readable CoBioVerse projection with explicit translation loss.
- Event-sourced retro coverage with negative knowledge and dispute links.
- A receiver election protocol: many readers, one fenced actuator per collision domain.

## Feedback instrumentation
Measure: exact-object retrieval, independent receiver read, resume success after 24h, unauthorized effects=0, orphan-risk count within declared scan roots, duplication, human relay count, comprehension, and rollback success. Unknowns must stay unknown. No global 'thousands of sessions' count is established here.

## Sharing policy
Publish only approved, generalizable issues and synthetic examples. No credentials, private messages, device secrets or internal gateway details. Developer feedback is a proposal, not an automatic delivery to a vendor.