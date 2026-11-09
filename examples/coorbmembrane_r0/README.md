# CoOrbMembrane+ R0 | Evidence-driven projection canary

**State:** public-safe synthetic projection candidate; zero device effects, not verified on X2, no independent receiver pickup. The R0 module deliberately refuses non-public strands and any input not explicitly labelled `SYNTHETIC_FIXTURE_ONLY`.

This is a small pure JavaScript module in the existing CoMap/CoOrb/CoAhead architecture. It validates one typed work record and produces both an accessible SVG and a text projection from the **same immutable projected state**. It does not poll, approve, transmit, execute, mutate files or infer authority from a visual cue.

Run: `node --test examples/coorbmembrane_r0/membrane.test.mjs` (Node.js 22).

Contracts tested: caller-claimed VERIFIED requires explicit authorization/readproof **but is only a synthetic fixture claim**, never an authenticated receiver ACK; expired receipt becomes STALE; forecast has horizon, finite confidence, falsifier and baseline; contradictory and held edges differ; public-only privacy scope; bounded fanout; exact source SHA shape; deterministic replay; accessible SVG description; escaped unsafe labels. Both SVG and text visibly say there is **NO LIVE RECEIVER ACK**.

SVG is static and can be embedded inside a conventional HTML reader. All controls and native desktop interaction remain outside this module. It is not yet a completed accessibility or user comprehension test. Real proof needs a separately owned source/receiver, visual comparison, keyboard/screen-reader evaluation, and >24h interruption recovery.

Related: `docs/Architecture/COMAP_COORB_COAHEAD_TEMPORAL_R0A_20261023.md`, #178, #376, #386, #367.
