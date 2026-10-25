# CoOmni+ / CoContextCompiler+ R0 | Public-only offline proof

**State:** local reproducible reference canary, NOT installed on X2, NOT merged or accepted by CoCivium receivers, NOT a security-complete context router.

This fills the first bounded proof specified by [`COOMNI_CONTEXT_RESOURCE_FABRIC_R0_20261024.md`](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COOMNI_CONTEXT_RESOURCE_FABRIC_R0_20261024.md). It illustrates how a durable work ID and exact source digests can be compiled to a **finite worker-specific packet**, while keeping one visible challenge, preserving references to full source content, and **withholding nonpublic material**. No accounts, microphone/camera, browser tabs, network, models, subprocesses, or mouse/keyboard hooks are used.

## Run

From any machine with Python 3.9+:

```sh
python3 -m unittest -v test_coomni_context_compiler
python3 CoOmniContextCompilerR0.py --input fixture_public_only.json --budget-bytes 1400
python3 bench_context.py
```

The CLI prints one context JSON packet to standard output. It reads **only the explicitly named input JSON file** and does not write anything. The optional benchmark script writes a local synthetic benchmark JSON in the package directory. Do not place sensitive text into its public-mode fixture.

## Proof scope

- Source `sha256` verifies the exact UTF-8 body represented by the input source record; it does **not** certify authorship, licence, truth, custody or remote identity.
- Source roles are `SOURCE`, `CHALLENGE`, `BASELINE`; epistemic states distinguish observation, inference, hypothesis and metaphor.
- Only visibility `PUBLIC` enters context. Unknown visibility, role, epistemic label or stale hash fails closed. A no-public-challenge or insufficient budget returns `HELD`.
- The context compiler requires one source and one challenge. Additional candidates compete for remaining packet bytes, with deterministic source ordering. Large sources become marked excerpts; exact local rehydration from the **same supplied snapshot** is separately tested.
- Private names and source text never appear in the public compiled packet. The `withheld_nonpublic` counter is only a demo; a real system may need to withhold aggregate counts too.
- `max_bytes` measures UTF-8 bytes in compact JSON, **not real tokenizer units**. Different models have different context windows. This is not a virtual unlimited token API.
- No external effects or standing scheduler. This prototype runs only on invocation; no physical device connection or autonomous evolution is claimed.

## Proposed real receiver adoption steps

1. Bind one authorized exact CoCivium public source set (without private/user messages).
2. Rebuild context with a named local worker's actual tokenizer and a measured context ceiling; verify precision and contradiction recall against a direct-source baseline.
3. Test recovery from an independently held immutable source bundle, including a forced source-tamper and unavailability case.
4. Compare human time saved and total cost to manual retrieval, while retaining a HELD state for outside first-use, X2 input integration and provider adapters.
5. Keep `CoTurtle+` challenges and inversions addressable with a bounded depth/round budget. No permanent recursive agent swarm.

`ADDRESSABLE_NE_RESIDENT` · `SHA_NE_TRUTH` · `PACKET_NE_RECEIVER_ACK` · `COMPILED_NE_AUTHORIZED_PROVIDER_SEND` · `INFINITY_NE_INFINITE_TOKENS` · `USER_NE_MAILMAN`.
