# CoFeedLoop DevOps feedback | candidate public report
**Evidence boundary:** these are user-reported problems, source-derived risks and requested engineering priorities; absent reproducible external tests are explicitly labeled UNVERIFIED. This is not an automatically filed issue at platform vendors.

## Problems and reproduction gates
| Candidate | Current evidence | Discriminating test |
|---|---|---|
| Thumb prompt static, not source-resolved | Reported by user | Restart Logitech/host and compare output with current source revision |
| Logitech text truncates near 340 characters | User report in WhatsApp export | Record exact model, profile, bytes, codepoints, output and silent truncation |
| Repeated prompts generate redundant work | Reported behavior; CoPre synthetic dedupe tests exist | Repeat identical WorkID+revision and measure duplicate effects |
| AI sessions claim PASS without exact effect | Multiple narrative examples; not a census | Compare assistant claim to independent receiver readback |
| WhatsApp/ChatGPT do not share a universal session asset | Platform boundary described in source | Authorized receiver fetch and verifiable acknowledgement |
| Manual relay overload / historical orphan risk | User-reported CoCarry and bounded inventory gaps | Measure human interventions, recoverable historical object count, rehydration rate |
| Public mirrors split or unavailable | The three intended target URLs not qualified | Independent HTTP + bytes + SHA + effective URL + failover test |
| CoLUE draft and send confused | Existing lifecycle synthetic tests | Provider send/delivery/reply evidence at account-correct scope |

## Priority and ownership
P0: one authenticated durable receiver with exact WorkID readback and rollback.
P1: dedupe + collision fencing + append-only immutable lineage.
P2: public-safe canonical payload and machine-readable trust index.
P3: reversible CoMouse pointer-only command, startup qualification, keyboard fallback.
P4: actual historic discovery coverage and privacy-checked CoFront/CoEcho repair.
P5: CoOrb/CoNav visible navigation with truthful status and accessibility.
P6: independent mirror and restore receipts.
P7: opt-in CoBar sonification experiment, interpreted as status cues only, not whale language or divine congruence.

## Alternative paths
- Minimal native supervisor + durable queue versus cloud-centric fan-out; compare failures, cost and maintenance.
- One source graph, two different machine and human projections; measure semantic loss on translation.
- WorkID watcher election versus repeated live session spawning; benchmark novelty and false-green counts.
- Historical replay by chronology and relationship and critical risk, each with source references.
- Stop when expected additional verified benefit is lower than total operational burden.

## Public feedback hygiene
Every substantive issue should carry a repro, source/ref, build version, timestamp, actual vs expected, privacy scope, recovery steps, priority and review owner. This document is open for challenge but not evidence of platform-vendor receipt.
