# CoMeasure Outcome Crosswalk R0

**State:** PUBLIC REVIEW CANDIDATE.  Synthetic tests, not a production telemetry feed, a live CoBar/CoOrb gauge, a verified recipient acknowledgment, or an independent human acceptance result.

This is an additive, standard-library-only falsification experiment for [CoMeasureFabric+ issue #367](https://github.com/CoCivium/CoCivium/issues/367) and [draft PR #365](https://github.com/CoCivium/CoCivium/pull/365).  It does **not** replace the existing unit registry or its tests.

## Reproduce

From this directory in a Python 3.10+ checkout:

```bash
python -m unittest -v test_outcome_crosswalk.py
python -O -m unittest -v test_outcome_crosswalk.py
```

No network, credentials, mailbox/device access, provider token, third-party dependency, or external side effect is required. All sample work identifiers, SHA-like values and events are synthetic fixtures.

## Two intentionally different measurement families

1. **Physical-model family:** piecewise-constant power.  `100 W * 10 s + 40 W * 5 s = 1,200 J` over 15 s.  A fractional case additionally verifies exact rational arithmetic.  This validates only the declared calculation; there is no calibrated power instrument, observed energy or uncertainty estimate.  Both unit identity and model must be declared, and unsupported conversions fail closed.
2. **Receiver-event family:** three eligible synthetic work objects, one provider `SENT`, two simulated `RECEIVER_ACK_CLAIM` events.  The **claim count is 2/3**, not 3/3, but independently authenticated receiver outcomes are **UNKNOWN**.  Even exact matching IDs and hashes are insufficient to authenticate receipt or acceptance because the inputs and alleged ACKs could be fabricated in the same fixture.

**Important:** The two values are neither addable nor meaningfully convertible.  A computational model relating energy to useful outcomes would need defined acceptance and calibrated energy evidence.  No composite CoOomph score is implied.

## Negative controls

The tests reject non-positive duration, wrong/ambiguous unit codes, nonfinite or floating-point substitution, malformed fractions, missing coverage, conflicting ACK/non-delivery events, unexpected work IDs, duplicate event IDs, duplicate eligibility, and wrong source hashes.  A zero eligible-work denominator produces `NOT_APPLICABLE`, never a 0% success claim.  Provider `SENT` does not count as receiver ACK.  Switching to a production/live mode fails closed because the fixture offers no external attestation.

## Limitations and next proof

- This is local mathematical **and semantic fixture verification**, not a measured reliability, energy efficiency, audience response or X2 experience test.
- The model uses constant power within each segment and does not propagate power-meter calibration, sampling error or covariance.
- Receiver claims are purely synthetic.  Real attestation requires a separately authorized receiver, independently bound evidence, coverage and sender/receiver identity, and privacy-safe audit.
- Before runtime adoption, independently reproduce tests from a clean checkout, compare outputs across implementations, add uncertainty/clock provenance, and demonstrate one live, consented, useful receiver task.  Keep runtime and publication decisions separate.

**Rails:** ZERO_NE_NULL · PROVIDER_SENT_NE_RECEIVER_ACK · ACK_CLAIM_NE_INDEPENDENT_ATTESTATION · MODEL_NE_MEASUREMENT · TEST_PASS_NE_RECEIVER_ACCEPTANCE · PUBLIC_SOURCE_NE_PUBLIC_RUNTIME.
