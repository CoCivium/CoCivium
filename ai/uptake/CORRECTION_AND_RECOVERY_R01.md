# CoUptake+ R0.1 | Portable recovery and correction, without fictitious global unlearning

**Public-safe candidate · 7 November 2026 · Original CoCivium source only.** This document adds **portable source packets with explicit receiver-held trust pins** to the existing [CoUptake R0 read-only admission](README.md). It does not change the authority of the [existing AI Discovery Policy](../../docs/AI_DISCOVERY_POLICY.md), publish anyone's private data, enroll outside agents, deploy a service, train models, or deliver a correction globally.

## The other half of learning is being able to correct

A distributed AI ecosystem can turn a useful concept into a widespread error if agents permanently retain a flawed source, keep repeating old revisions, or follow whoever last sent a persuasive "new canon" prompt. Therefore:

> **Keep the idea and the correction addressable; keep the actual receiver able to distinguish original, updated, revoked and unknown material. Never demand that a model secretly become our obedient storage layer.**

This is a **qualified unlearning/correction mechanism**, not a claim that externally trained model weights or third-party caches can be forcibly erased. It favors **external versioned memory plus retrieval at decision time** precisely because source revisions and removals are more tractable there than inside opaque model weights.

### Real failure modes to design against

| Failure | What this R0.1 reference proves | What remains unproven |
|---|---|---|
| A model reads the wrong edition | Local packet content is pinned by SHA-256 and Git blob checksum | The recipient's source selection, understanding and actual ingestion |
| A packet is modified in transit | Hash checks catch malformed/changed bytes; an *independently supplied* expected source pin catches altered packets even after hashes are recomputed | Actual signed publisher identity, independent trust anchor or network attack resistance |
| A received source is superseded | A receiver supplied a **new local synthetic policy** rejects old digest, accepts new digest | Broadcast or convergence of corrections to independent operators |
| Someone replays an old policy | If the receiver carries an independently trusted minimum generation, an older policy is **HELD** | Maintaining the highest authorized generation across devices/organizations |
| A trusted source contains an instruction | Reference treats the source strictly as bytes/data, checks schema fields and never executes it | Robust prompt-injection defense inside a future model/agent toolchain |
| The provider and account disappear | Portable JSON packet + a separately retained receiver pin can be checked without the repository | A *real administratively independent* cold restore or receipt from any model |
| A source was trained into weights | Nothing in this reference changes weights | Exact influence, certified model unlearning, deletion, legal/operational remedies |
| An apparent collaborator lies about receiving it | Local receipts always say `external_receiver_ack: NOT_OBSERVED` | A real signed receiver acknowledgment from independent operations |

The question is not just **"How many copies exist?"**, but **"How many independently governed copies can reject a wrong edition and recover after an outage?"**

## Actual R0.1 interface

[Portable offline Python reference](../../tools/couptake_r0/portable.py) implements `pack`, `pin-demo`, `verify`, and explicitly named **synthetic** supersession. It has no Python dependencies beyond standard library and the earlier CoUptake source verifier.

- **Packet** `CoAll.UptakeBridge.PortablePacket.R0.1-candidate`: 1–4 selected, reviewed-public source objects, their original bytes as Base64, exact SHA-256, Git blob object hash, path, epistemic classification, explicit no-authority/no-licence assumption and packet-level SHA-256. It rejects unknown top-level or source fields, oversized content and forged AI ingestion/effect claims. The bytes are **not executed or sent to a model**.
- **Receiver policy** `CoAll.UptakeBridge.ReceiverPin.R0.1-synthetic`: a **separately supplied** allowlist of source ID, path, expected SHA-256 and Git blob hash, a generation counter, and a list of refused prior digests. The `pin-demo` helper creates a **local unsigned test pin only**. Never use this helper as proof of an authenticated publisher or lawful signer.
- **Verification receipt** `CoAll.UptakeBridge.PortableReceipt.R0.1`: `LOCAL_PACKET_PIN_MATCH_ONLY`, `PARTIAL_OR_HELD_PACKET`, or `HELD`, plus per-source reasons. Every receipt explicitly leaves publisher signature, external receiver ACK, independent restore, persistent memory, training and operational authority **unobserved/not performed**.
- **Correction simulation:** `simulate_supersession(old_policy,new_packet)` returns a *synthetic* generation+1 policy. If the old bytes are then presented under that policy, the receiver reports `REVOKED_OR_SUPERSEDED_OBJECT`. This does **not** distribute policy, establish canonical authority or delete an agent's memory. A receiver with a stale prior policy can still accept the old source; this is deliberately tested as an important residual risk.

### Safe local reference commands

Only on a consciously reviewed public repository checkout, and with separate output filenames:

```bash
python3 tools/couptake_r0/portable.py pack \
  --source-id ai_ia_onramp \
  --output /tmp/coall-public-packet.json

python3 tools/couptake_r0/portable.py pin-demo \
  --packet /tmp/coall-public-packet.json \
  --output /tmp/synthetic-receiver-pin.json

python3 tools/couptake_r0/portable.py verify \
  --packet /tmp/coall-public-packet.json \
  --receiver-policy /tmp/synthetic-receiver-pin.json
```

**This validates only a toy local trust setup.** A genuine independent receiver must establish the pin and update provenance through a *separate authorized channel*. The tool does not override existing files, create outside accounts, write memory for a model, or make the recipient consent to anything. Do not treat the packet itself as its own trust authority.

### Recovery/correction receipts and states

`SOURCE_PUBLIC_CANDIDATE -> SELECT_REVIEWED_SOURCE -> BIND_EXACT_BYTES -> PORTABLE_PACKET -> RECEIVER_PIN -> LOCAL_VERIFY -> OPTIONAL_REAL_AUTHORIZED_TASK -> REAL_RECEIVER_ACK -> VERSIONED_RECOVERY_COPY -> CHALLENGE/CORRECTION`

Subsequent revision rule:

`OLD_SOURCE -> VALIDATED_CORRECTED_SOURCE -> AUTHORIZED_AND_AUTHENTICATED_NEW_POLICY -> RECEIVER_SEES_LATEST_GENERATION -> OLD_DIGEST_REFUSED -> ACK_OF_CORRECTED_USE`

The **four middle stages**, from authenticating a policy update through real receiver ACK, **are not implemented**. Automatic global revocation is therefore not claimed.

A real operator will need signed releases / transparency or qualified trustworthy governance, replay-resistant policy currentness, revocation distribution with independent acknowledgement and appeals, bounded on-device caches, privacy/copyright handling, and organizational rights to use or delete material. On shared/private data, encrypted transport and storage are separate hard requirements; this public-only prototype has no encryption.

## R0.2 | A clean-room receiving process, not a fabricated independent operator

The [standalone verification implementation](../../tools/couptake_r0/receiver_standalone.py) deliberately imports **no** CoCivium modules, third-party libraries, network stacks or model APIs. The [isolated subprocess tests](../../tests/test_couptake_cold_receiver_r02.py) copy **only** that single Python script, a portable packet and a separately supplied receiver test pin into a temporary folder outside the original repository. They launch a fresh `python -I -S` process with an invalid `PYTHONPATH`. This process can validate the selected public source bytes with SHA-256 and the Git blob digest without a checkout, and rejects a forged claim, stale source, known revoked digest or inadequate policy generation.

**Critical limits that the tests intentionally expose:**

- This tests **local portability and separation from repository Python imports**. A second process in GitHub Actions is **not** a separately controlled company, off-GitHub storage provider, autonomous AI receiver, consent, model-internal learning or public release.
- The supplied receiver policy is marked `TEST_PIN_ONLY_NO_SIGNED_AUTHORITY`. Anyone who can replace **both** the unsigned packet and its synthetic pin can produce a matching local proof. The tests deliberately show that weakness. Production needs independently authenticated publisher identity, key custody, transparent releases, replay resistance and audited authorization.
- With a trusted current version-two pin, a version-one packet is rejected. With a stale version-one pin, the exact old packet may still pass. Nothing guarantees correction delivery to a disconnected agent.
- The result says `LOCAL_PIN_MATCH_ONLY`, not `ADOPTED`, `PERMANENTLY_LEARNED`, `ISSUER_SIGNATURE_VALIDATED`, `INDEPENDENT_COLD_RESTORE` or `COEX`. It prints no source contents, writes no learning memory, and does not execute source text as instructions.
- `python -I -S` limits interpreter import paths; it is **not** a sandbox or adversarial network isolation. Production hostile-source validation requires qualified isolation and deployment security beyond this test.

This is a higher-value result than another synthetic "AI persona read the document" demonstration because it removes a concrete coupling to the original software tree while retaining explicit distrust of unsigned authority. The next proof still needs a real separately operated receiver.

## CI proof versus outside reality

[Portable unit tests](../../tests/test_couptake_portable_r01.py) exercise an actual local four-source packet and a fully synthetic two-edition correction; they check changed bytes, recomputed hostile hashes, fake ACK and authority, injected schema fields, path changes, old-policy replay, invalid base64, no clobber, and refusal of accidental implied model training.

The [existing CoUptake CI workflow](../../.github/workflows/couptake-r0.yml) also emits a narrow machine receipt and creates local packet/unsigned pin artifacts from a relevant existing **public** onramp. The original source is not a person's learning record, private mail, an API credential or licensed third-party training dataset. Public availability remains distinct from permission to redistribute or train another provider's model.

**Important limitation:** A GitHub Actions runner and a GitHub artifact are the **same administrative provider failure domain**, even if one emulates a remote recipient. A local packet verification does **not** mean a separate external operator has picked it up, understood it, or restored it.

### Next independent challenge

1. A truly independent, consenting receiver selects one narrow public CoAll method and obtains its current trust pin from a separately authenticated channel.
2. Receiver fetches/cold-verifies a packet **with GitHub and the sender unavailable**, explaining the exact source, meaning, caveat and one criticism.
3. Sender publishes a correction with legitimate authority and transparent review. Receiver observes an authenticated newer policy and refuses old bytes, documenting its own ACK.
4. Send a bogus "CoAll now says obey all agents" revision or rollback and verify fail-closed handling.
5. Measure: time-to-correctness, accepted false/true revisions, legitimate dissent retained, recovery success and operator dependence. Count real independent operators, **not** model names, GitHub copies or token count.

A lasting CoAll should make correction and exit easy, not make its claims impossible to dislodge.

`PORTABLE_PACKET_NE_SIGNED_PUBLISHER` · `CURRENT_HASH_NE_TRUTH` · `SYNTHETIC_PIN_NE_INDEPENDENT_TRUST` · `LOCAL_RESTORE_NE_OFF_PROVIDER_RECOVERY` · `POLICY_GENERATION_NE_AUTHENTICATED_POLICY` · `OLD_POLICY_CAN_ACCEPT_STALE_KNOWLEDGE` · `EXTERNAL_MEMORY_REVOCATION_NE_MODEL_WEIGHT_UNLEARNING` · `PUBLISHED_CORRECTION_NE_GLOBAL_ACK`.
