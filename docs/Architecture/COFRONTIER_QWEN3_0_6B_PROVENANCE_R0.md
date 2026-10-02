# CoFrontierIntake+ Qwen3-0.6B provenance R0A

**State:** `REAL_PUBLIC_SOURCE_PROVENANCE_RECORDED__NO_MODEL_DOWNLOAD_NO_INFERENCE_NO_ROUTE_CHANGE`

## Purpose

Advance the frontier-intake membrane from synthetic model names to one real, pinned public candidate without downloading or running it.

Candidate:

`Qwen/Qwen3-0.6B`

Pinned Hugging Face revision:

`c1899de289a04d12100db370d81485cdf75e47ca`

Observed on 2026-10-02 from the public Hugging Face model API and pinned-revision file surfaces.

## Exact core anchors

The pinned source reports:

- `model.safetensors` SHA-256  
  `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`
- `tokenizer.json` SHA-256  
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`

The public API reports the repository's main revision as the same pinned SHA and identifies the model architecture as Qwen3ForCausalLM.

The source identifies the license as Apache-2.0, and the pinned LICENSE file identifies itself as Apache License Version 2.0, January 2004.

## What is verified

R0A records:

`PUBLICLY_AVAILABLE -> PROVENANCE_VERIFIED_FOR_PINNED_CORE_ARTIFACTS`

for the repository revision plus the exact weights/tokenizer hash metadata and license source identity.

This is deliberately narrower than a complete runnable-package proof.

## What remains open

The following runtime-package components are not independently hash-verified by this canary:

- config.json
- generation_config.json
- merges.txt
- tokenizer_config.json
- vocab.json
- README.md
- .gitattributes

The license source is identified, but no legal scope adjudication is claimed.

Therefore the candidate is **not yet eligible for isolated inference** under CoFrontierIntake+.

Next gate:

`COMPLETE_RUNTIME_PACKAGE_MANIFEST_AND_LICENSE_SCOPE_REVIEW_BEFORE_ISOLATED_CANARY`

## Why this candidate

The public source describes Qwen3-0.6B as a small causal language model, reports 751,632,384 parameters, and exposes a single safetensors weights file plus tokenizer/config assets.

That makes it a plausible bounded future canary for provider-independent reasoning without pretending that availability equals suitability.

## Effects

This R0A performs no:

- model download;
- model installation;
- inference;
- benchmark;
- runtime route change;
- account mutation;
- public effect.

## Rails

`CORE_ARTIFACT_HASH_METADATA_NE_FULL_PACKAGE_VERIFICATION`  
`LICENSE_SOURCE_VERIFIED_NE_LEGAL_SCOPE_ADJUDICATED`  
`PROVENANCE_VERIFIED_NE_MODEL_SAFE`  
`PROVENANCE_VERIFIED_NE_CAPABILITY_VALIDATED`  
`PUBLICLY_AVAILABLE_NE_OFFLINE_READY`  
`MODEL_AVAILABLE_NE_PROVIDER_EXIT_READY`  
`NO_MODEL_DOWNLOAD_NE_ISOLATED_CANARY`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
