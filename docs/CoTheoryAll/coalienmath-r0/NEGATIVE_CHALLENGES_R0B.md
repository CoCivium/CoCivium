# CoAlienMath public R0B: finite false-green challenges

**State:** PUBLIC-SAFE, SYNTHETIC FIXTURES, REVIEW CANDIDATE.  Not canon, a new theorem, a receiver attestation, or a live CoCivium/X2 integration.

## Exact predecessor and scoped challenge

The November 7 public R0 model had Git blob `5deb3e3e9a6a0ccfe97ad0161a64697407b59b3c` and test blob `f4a78da8133f285b7e55ab60608be6248b90df94`, with 19 passing tests. The November 11 review preserved all 19 tests and reproduced two real software defects in the finite example:

1. `QualifiedObservation(..., value=None, null_kind="ALIEN_PASS")` was accepted despite `null_kind` requiring a declared `NullKind` enum. The Python dataclass annotation did not validate runtime input. Raw `"UNKNOWN"` was equally accepted but is not an enum instance.
2. `likelihood_evidence_bits(1.0, 1e-320)` returned positive infinity because it divided before taking logarithms. Both input probabilities are valid finite positive numbers; the log-likelihood ratio is large but finite.

A third malformed input, `QualifiedObservation(..., value=0j, null_kind=NullKind.OBSERVED_ZERO)`, previously passed because a complex zero compares numerically equal to `0`. The example's documented real-number model does not admit complex-valued observations.

## Bounded correction

- Reject unrecognized or untyped null enums rather than treating arbitrary strings as known states.
- Require **real, finite and nonboolean** values for `OBSERVED_ZERO`.
- Calculate evidence weight as `log2(p_e_given_h) - log2(p_e_given_not_h)`, avoiding intermediate ratio over/underflow for positive finite inputs.
- Add four negative/edge tests: unrecognized enum, raw enum string, complex-zero spoof and finite extreme likelihood symmetry.

## Measured local outcome

`python3 -m unittest discover -s ai/coalienmath -p 'test_*.py' -v` and the equivalent `python3 -O -m unittest` each reported **23/23 PASS** in an isolated local Python interpreter after the correction. The original 19 tests remain present. This is not hosted CI, independent receiver proof, physical truth, or a probability calibration study.

Source hashes for candidate review:

- `model_r0.py`: SHA-256 `002afa488139db230a30a8918c7f7f4c6f396c5b9208ad78480c0f01ec699e27`; proposed Git blob `d4c3285002bc252fbee8a1f368be28136619ffd0`.
- `test_model_r0.py`: SHA-256 `d23da7139c8035b0d13764a049ceccd56cb5d44756d0f60aa47289747429e03f`; proposed Git blob `7adab67997f6ee76de7e4d44411c19dc77b29c1b`.

## Proof boundaries and next verification

Verify exact PR-head Git blobs, run both Python versions under normal and optimized CI, and independently challenge any conversion into a trust or receiver-acceptance claim. The example still lacks temporal windows, calibration, provenance, independent witness evidence and resource scopes. **No finite passing fixture promotes a claim to real-world truth.**

`R0B_TEST_PASS_NE_HARDWARE_PROOF` | `NULL_ENUM_STRING_NE_QUALIFIED_STATE` | `EVIDENCE_BITS_NE_PROBABILITY_OF_TRUTH` | `PUBLIC_PR_NE_RELEASE`.
