# CoLocalModelWorker R3 | Transport hardening candidate R0

State: CANDIDATE_SOURCE_ONLY; no X2 deployment, scheduler, CoStead ACK, live Ollama model inference or public-site effect.

Objective: harden the existing `scripts/CoLocalModelWorkerR3.py` rather than create a replacement worker or new controller. Its predecessor source on CoCivium main and the existing `candidate/copre-cof2b-release-rail-20261118` branch had Git blob SHA `95217286632662bf8bc5e1a3fb197e252615c62f` at this review.

Changes relative to predecessor:
- Require canonical, explicit-port HTTP loopback origin with no path, query, fragment or credentials; preserve documented 127/8, ::1 and localhost eligibility.
- Disable ambient HTTP/HTTPS proxy routing for model prompts.
- Reject redirects from the local endpoint, including same-host and external redirects.
- Bound model response to one megabyte and timeouts to <=300 seconds.
- Preserve R3 public-only, LOGICAL_ONLY, advisory/no effects, no-clobber output, JSON format and existing CLI contract.

Local model-workspace tests: 12/12 PASS, Python standard-library-only. Test suite creates two ephemeral loopback HTTP endpoints, with no actual Ollama or external provider calls.

To test in an isolated checkout:

    python -B -m unittest -v tests/test_colocal_worker_transport_r0.py
    python -B scripts/CoLocalModelWorkerR3.py --selftest

If reviewing this staged standalone bundle, execute from this directory:

    python -B -m unittest -v test_colocal_worker_transport_r0.py
    python -B CoLocalModelWorkerR3.py --selftest

No production activation until a qualified X2/CoStead local observer verifies process health, actual model output, exact WorkID, receiver readproof, restart/Stop and quiet foreground behavior. Do not silently reenable the disabled tasks or create an additional scheduler.

Existing primary design: https://github.com/CoCivium/CoCivium/blob/main/docs/Operations/COLOCAL_MODEL_WORKER_R3.md
Existing local gateway: https://github.com/CoCivium/CoCivium/blob/main/examples/comodelfabric/ollama_gateway_r0.py

Rails: LOCAL_NE_TRUSTED; MODEL_OUTPUT_NE_EFFECT_PERMISSION; CANDIDATE_OUTPUT_NE_RECEIVER_PICKUP; LOCAL_IS_NOT_LANDED; VALIDATION_IS_NOT_ACCEPTANCE; NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF; NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE.
