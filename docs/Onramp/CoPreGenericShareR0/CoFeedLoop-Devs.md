# CoFeedLoop | Developers, open source and operators | PUBLIC CANDIDATE
Observed 2026-11-09. These are user-reported symptoms, candidate priorities and test requirements, not all verified vendor defects.

## Candidate bugs and failure modes
- Static thumb does not discover the current Seed on its own; duplicate pastes can multiply workload. Test two identical sends to same WorkID.
- User-relayed Logi mouse text truncation around 340 characters. Verify device/profile/version and whether a warning appears.
- False PASS or DRAINED from source-only artifacts without runtime or receiver readback.
- Session-drain requests generating new plans instead of deduped work.
- Private or historical artifacts missing stable provenance, exposure controls and recovery paths.
- WhatsApp export mistaken for ChatGPT session inventory.
- Repeated all-session relays exceeding human CoCarry tolerance.
- Public URLs conflated with DNS control, mirror equality, delivery or independent pickup.

## Ranked delivery opportunities
P0: independently verifiable durable receiver and exact-object readproof with effect fencing.
P1: source+WorkID+effect dedupe and held/missing/conflict negative tests.
P2: safe public machine/human twins and independent recovery, with real HTTP and hash checks.
P3: mouse pointer, native fallback and reversible user-controlled bindings.
P4: root-by-root historical CoEcho against current descendants, with unknown coverage explicit.
P5: public-facing CoMap/CoNav and first-use CoOrb task completion.
P6: optional sound/CoBar experimental sonification with source-linked warning mapping and accessible text.
P7: provider-failure cold restore and CoStead/Gateway acceptance.

## Strategies and optionality
Reuse [PR #415](https://github.com/CoCivium/CoCivium/pull/415), [PR #420](https://github.com/CoCivium/CoCivium/pull/420), [PR #422](https://github.com/CoCivium/CoCivium/pull/422), [PR #426](https://github.com/CoCivium/CoCivium/pull/426). No newest-wins. Protect last-good MVP and source evidence. Publish only public-safe records; never expose credentials, private correspondence, home network specifics or child data.

## Falsifiable outcome
An authorized new receiver fetches one exact WorkID, provides independent source-hash readproof, recovers a last-good state after an injected interruption, and needs no user paste. Compare against current manual relay time.
