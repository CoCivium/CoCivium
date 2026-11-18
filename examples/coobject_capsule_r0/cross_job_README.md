# CoObject+ cross-job capsule recovery R0

**State:** `DRAFT_SOURCE_ONLY_CI_CROSS_JOB_SYNTHETIC__NOT_COEX_NOT_DEPLOYED_NOT_X2_RECEIVER`.

This is a bounded increment to [CoObject+ / CoSeren+ Offline Capsule R0](../README.md) and [CoObject/OVP draft PR #446](https://github.com/CoCivium/CoCivium/pull/446), not a new scheduler, model, authority source or standalone public product.

## Question

Can one GitHub CI job create a self-describing public-synthetic CoObject capsule, hand it across GitHub's artifact boundary, and can a **different runner job** verify and reconstruct the exact content after deleting one local replica? The expected content is a committed fixed literal, so the second job checks against something other than a producer-authored manifest.

## Evidence chain

1. **Producer job:** compile one public-synthetic literal into `capsule/manifest.json`, `capsule/payload.bin`, `capsule/recovery.bin`, plus a strict `handoff.json`; remove original source and upload only the capsule and envelope. No user content or secret material.
2. **Artifact transfer:** GitHub Actions `upload-artifact@v4` then `download-artifact@v4` across a job dependency boundary. The transfer uses GitHub infrastructure, not a CoAll/CoStead bridge and not a peer-to-peer verification.
3. **Receiver job:** checkout source again; reject any unexpected files, symlink, authority or fabricated evidence field; compare manifest and exact bytes to the source-pinned literal, not just the producer's self-attested digest; destroy *one* verified local replica; verify degraded state and exact restoration; emit a typed readback artifact.
4. **Source CI:** existing OVP tests run independently; the new 13 adversarial tests exercise missing/corrupt copies, forged ACK, source mutation, unexpected files and no-clobber. The real cross-job result requires a specific successful GitHub Actions run, not just these local tests.

The receiver's local test result is `CROSS_JOB_SYNTHETIC_RECONSTRUCTION_PASS` only if the full chain passes. This is **a cross-job artifact transfer with separate job filesystem environments**, not a tested independent organization, distinct durable storage provider, long-term resilience, real device, external reader or authenticated end-user benefit.

## Run locally (not a substitute for CI cross-job proof)

```sh
python3 -m unittest -v test_cross_job_handoff_r0.py
mkdir -p /tmp/coobject-local-receiver
python3 cross_job_handoff_r0.py produce /tmp/coobject-local-producer
python3 cross_job_handoff_r0.py consume /tmp/coobject-local-producer --receipt /tmp/coobject-local-receiver/receipt.json
```

Do not run these using a nonempty existing output path. Python 3.11+ standard library only, `coobject_capsule_r0.py` remains the owner of the pack/verify/restore implementation.

## Strong simple baseline and open gate

A GitHub Action artifact containing one source file plus its SHA-256, or a repository checkout of an immutable commit, is a serious alternative. The capsule must eventually demonstrate a better or complementary ability at comparable cost, complexity and safety. This cross-job canary can establish an exact file transfer/reconstruction at CI scope, not that it is better than those simpler methods. An actual user- or device-receiver acceptance gate remains unproven.

## Rails

`JOB_HANDOFF_NE_INDEPENDENT_TRUST_ROOT` · `TWO_JOB_FILESYSTEMS_NE_DISTINCT_DURABLE_STORAGE` · `HASH_MATCH_NE_ORIGIN_AUTHENTICATION` · `CI_SOURCE_READBACK_NE_END_USER_ACK` · `TEST_CODE_NE_RUNNING_X2` · `QUESTION_NE_EFFECT_AUTHORITY` · `ONE_USEFUL_FILE_NE_ALL_OF_COALL`.