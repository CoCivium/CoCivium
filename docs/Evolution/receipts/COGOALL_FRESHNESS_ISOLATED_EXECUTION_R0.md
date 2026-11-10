# CoGoAll isolated freshness verification receipt

Scope: local Python unittest execution, not GitHub Actions or X2.
Source: https://github.com/CoCivium/CoCivium/blob/main/tests/gs_receiver/test_freshness_projection.py
Method: source retrieved via connected GitHub fetch_file, reconstructed in isolated execution environment, then executed with Python unittest discovery.
Result: 5 tests run, 5 passed, 0 failed.
Source file SHA-256 (locally reconstructed): 2b16f29aca54f996ef95334667bc070df6078b349bbbf825798059e6afff1e2c

Tests:
- test_boolean_timestamp_is_not_valid_time: ok
- test_clock_skew_is_not_freshness: ok
- test_fresh_stale_boundary: ok
- test_no_evidence_is_not_success: ok
- test_self_asserted_verified_flag_cannot_bypass_verifier: ok

Limits: This proves only the isolated test cases execute successfully in the available environment. It does not establish production receipt verification, CI PASS, X2 runtime integration, or real-world outcome attestation. The direct git transport failed due to DNS resolution; the source was available via the GitHub connector.
