# CoOrbMembrane+ R0 | Evidence-driven projection canary

**State:** source candidate; read-only, synthetic fixture, no live CoOrb installation or independent receiver pickup.

This is a small pure JavaScript module in the existing CoMap/CoOrb/CoAhead architecture. It validates one typed work record and produces both an accessible SVG and a text projection from the **same immutable projected state**. It does not poll, approve, transmit, execute, mutate files or infer authority from a visual cue.

Run: `node --test examples/coorbmembrane_r0/membrane.test.mjs` (Node.js 22).

Contracts tested: verified receiver requires explicit authorization and readproof; expired receipt becomes STALE; forecast must carry horizon and confidence; contradictory and held edges retain different statuses; deterministic replay; SVG title/description; unsafe labels escaped; no placeholders or fake green liveness.

SVG is static and can be embedded inside a conventional HTML reader. All controls and native desktop interaction remain outside this module. It is not yet a completed accessibility or user comprehension test. Real proof needs a separately owned source/receiver, visual comparison, keyboard/screen-reader evaluation, and >24h interruption recovery.

Related: `docs/Architecture/COMAP_COORB_COAHEAD_TEMPORAL_R0A_20261023.md`, #178, #376, #386, #367.
