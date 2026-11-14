# CoObject Cross-Job Witness R0 | exact bytes, not self-certified success

**State:** `PUBLIC_SAFE_DRAFT_SOURCE_ONLY__THIRD_JOB_RECEIPT_CHECK__NOT_REAL_USER_OR_X2_PROOF`.

**Question:** Can a third isolated GitHub CI job inspect both the producer capsule and the receiver's readback, compare them with a literal independently pinned in its own source, and reject false proof/authority claims?  The same checker also reads GitHub's exact downloaded ZIP artifacts outside the Actions runtime.

This strengthens the existing `examples/coobject_capsule_r0/` work and draft [PR #446](https://github.com/CoCivium/CoCivium/pull/446). It does not duplicate the CoObject capsule implementation, the CoMVP release controller, or a global watchdog.

## Two boundaries, two distinct claims

1. **Independent data inspection (demonstrated here):** GitHub Actions run [42752754688](https://github.com/CoCivium/CoCivium/actions/runs/42752754688) completed a source test, producer and receiver job. Its artifacts were independently retrieved via the GitHub connector and inspected in a separate local container. Both the producer's exact 109-byte payload copies and the receiver's digest claims match the expected source literal SHA-256 `ea65c2bac2f4f3900ef69100d3a1d85a99e7c34083f43800b58bbb1a52b5c293`. An author-supplied digest alone was not used as the sole reference.
2. **Third CI witness (this candidate):** An extra job downloads producer and receiver artifacts separately, uses independent read-only checks and emits its own scoped receipt. The job must actually run and pass on a named commit before counting this step as verified. In all cases the data come from the *same repository's CI* and remain untrusted as a third-party user result.

Source artifact ID `13734620489`, ZIP digest `0c26ba9555e46fbd9163d1380ae0c917169936eedd1584ac252722de6953fd42`.
Receiver artifact ID `13733334240`, ZIP digest `f90a1c72afa30a3e63a31f03d03c5e0a0f410723521380ba5145e2a3ce0e53ae`.

**IMPORTANT:** GitHub's downloadable artifacts expire. Stable source/receipt identity and hashes stay in this note; an expired ZIP does *not* constitute durable off-provider storage. The third job can independently check that the producer artifact still contains the literal and that the receiver's report is internally coherent, but **cannot independently observe the receiver's deleted/restored file** when the readback artifact contains only the JSON receipt. Do not upgrade to genuine end-user ACK or recovery on that basis.

## Reproduce locally (no network)

```sh
python3 -m unittest discover -s examples/coobject_capsule_r0 -p 'test_cross_job_witness_r0.py' -v
python3 examples/coobject_capsule_r0/cross_job_witness_r0.py producer.zip receiver.zip --report witness.json
```

The CLI accepts extracted artifact directories or the original ZIPs. It allows only the exact synthetic filenames; rejects symlinks, unexpected/duplicate files, over-budget data, wrong exact source, false evidence, incorrect copy roles, malformed JSON and writing over an existing receipt. It never executes capsule bytes or follows source-provided instructions. The 19 adversarial tests are local, not an independent institutional audit.

## Actual product and comparative gates still outstanding

- X2 Remote Desktop Commander remained **offline** when checked on 2026-11-10, a statement about connector reachability, not whether X2 power is on.
- No authorized RickBar -> real local Ollama -> visible output -> durable WorkID -> restart -> user acceptance was observed by this witness.
- A plain immutable Git checkout, one exact file plus SHA, or a conventional archive might outperform the richer capsule in cost and operational simplicity. Compare with those before selecting it as a product.
- Cross-job production and verification are not independent trust roots: a compromised source revision could alter producer, receiver and witness. Real independence needs separately controlled validator identity and provenance, signed or equivalent independently trustworthy origin, retention and receiver-side observation.
- **No new effect authority:** all data and operations here are public synthetic; no network outreach, account operation, publication, spending, consent assumption, or X2 mutation is enabled.

**Rail:** `THREE_JOBS_NE_THREE_TRUST_ROOTS` · `HASH_MATCH_NE_SOURCE_AUTHENTICITY` · `RECEIPT_COHERENCE_NE_RECEIVER_EFFECT` · `ARTIFACT_EXPIRY_NE_DURABILITY` · `SOURCE_CI_NE_MVP`.