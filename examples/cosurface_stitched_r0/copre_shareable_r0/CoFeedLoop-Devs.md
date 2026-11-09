# CoFeedLoop | Public engineering feedback R0
**PUBLIC CANDIDATE / NOT A VERIFIED VENDOR BUG REPORT.** 2026-11-09.
The items below are user-reported observations, model-output hazards and engineering hypotheses. Do not represent every report as reproducibly confirmed.

## Observed and reported pain
| Issue | Status | Reproduction / evidence needed |
| --- | --- | --- |
| Thumb button pastes static instructions, not a live source | User report | Capture exact host adapter configuration and bounded paste test |
| Logitech text reportedly truncated near 340 characters | User report, **not independently measured** | Record device/software version, max exact bytes, pasted text hash and screenshot |
| Repeated paste creates duplicate front work | Risk supported by prompt pattern | Run same WorkID/revision twice, compare durable event keys |
| AI outputs may call a draft PASS/DRAINED without receiver readback | Verified design hazard, no provider-wide prevalence claim | Compare written claim to receiver-side exact-object readproof |
| WhatsApp export does not include other ChatGPT sessions | Source boundary | Independently enumerate authorized source scopes, respecting privacy |
| CoCarry exhaustion from manual session relay | User report | Count required human actions and cumulative elapsed time |
| Three proposed public routes may be unavailable or divergent | Unverified routes | HTTP fetch, content hash, failure domain and rollback test |

## Proposed priority order
**P0** Authenticated independent receiver and durable queue.
**P1** Stable WorkID+revision dedupe, replay and explicit hold.
**P2** Versioned release manifest, exact hash, public-safe change feed.
**P3** Stable mouse pointer with Stop/keyboard fallback and a real startup test.
**P4** Independent mirror readback and restore drill across failure domains.
**P5** Privacy-safe 7-field source-intake and synth/human views.
**P6** CoBar/CoWhale and alternate sensory renderings as optional audification experiments, not animal language translation.

## Engineering alternatives
- Start with one durable public source and an independent read-only receiver before multiplying websites.
- Keep append-only deltas; resolve contradictions via independent challenge instead of overwriting priors.
- Compare front-selection strategies by verified gain, diversity, missed fronts and recovery cost.
- Package public artifacts for open-source reproduction without private prompts, credentials or local infrastructure maps.

## Measurement
Per experiment record WorkID, source revision, fixture hash, test version, adapter, time, cost, outcome PASS/FAIL/UNKNOWN, specific evidence refs and a human intervention counter. Do not treat CI green as runtime or acceptance.

## Publication
This document is an issue/feature feedback candidate only. No claim of delivery to OpenAI, Meta, Logitech, external developers or open-source maintainers.
