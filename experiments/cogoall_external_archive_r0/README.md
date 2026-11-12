# CoGoAll cross-substrate archived WorkID byte readproof R0

Status: `VERIFIED_EXACT_ARCHIVE_BYTES_OFF_GITHUB_RUNNER`.

## Exact source object

- GitHub source artifact: `CoCivium/CoCivium`, Actions run `43113671112`, artifact ID `13896878596`, name `cogoall-unfinished-43113671112-a1`.
- GitHub artifact ZIP SHA-256 (recomputed from downloaded ZIP): `df10aa56be73cb131aa78cecf341dd4b329edabd6f1822711c755335fa9e813e`.
- `manifest.json` SHA-256: `eda81823dd2e2f07401bbe22bb9d43de19c0d1656921d8af55047f89c8a53599`.
- `queue.sqlite` SHA-256: `f54e89033aa68c9c94ce803feb41a1bcd70a71bb3c4ec444ee4a92f69dfeed04`.
- Historical source commit as *declared in the archive*: `6ca5f069ca0e0cf7f9ae6985b2e16a28cf579e6f`.
- Historical CoPre source SHA-256 as *declared in the archive*: `30129e630e73359bbe476d61e21cff4f5e7a8992cd1a79630c001a7de6bf84e4`. Original source bytes **not independently fetched in this external pass**.

## Independent byte inspection (separate execution substrate, transient)

The original ZIP was transferred from the GitHub connector to a temporary OpenAI execution container. The verifier read all ZIP entries, compared full SHA-256 hashes, performed SQLite `PRAGMA quick_check` on a disposable read-only/immutable extracted copy, and checked the *one* row:

- WorkID `CoGoAll.Unfinished.43113671112.a1`.
- `state=LEASED`, `epoch=1`, `due_at=100`, `lease_until=130` in synthetic seconds.
- `result_sha256=NULL`, `completed_at=NULL`.
- Owner `CoGoAll.Seed.43113671112.a1`.
- `effect_executed=false` and `external_receiver_ack=false` in the matching manifest.

This is an independent computation outside GitHub Actions on GitHub-served data, **not** an independent provider identity attestation, CoStead/X2 pickup or real-time recovery. GitHub metadata and the original manifest are untrusted claims until checked against an independent signed receiver/source.

## Reproduce

Place `cogoall-unfinished-43113671112-a1.zip` adjacent to these files, then run:

```bash
python verify_external_zip_r0.py --archive cogoall-unfinished-43113671112-a1.zip --output new_receipt.json
python -m unittest -v test_external_zip_r0
python -O -m unittest -v test_external_zip_r0
```

Seven tests pass under normal Python and seven with `-O` (14 test executions total). Tests cover exact normal readback and corrupted ZIP, altered archive checksum, altered embedded manifest/queue hashes and wrong WorkID pin. All evidence checks use explicit exceptions, not removable `assert` statements.

## Strict nonclaims

- `LOCAL_IS_NOT_LANDED` for X2 or CoStead.
- `VALIDATION_IS_NOT_ACCEPTANCE`.
- `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.
- `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`.
- `HASHING_IS_NOT_SEMANTIC_INGESTION`.
- `DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`.
- `SAME_GITHUB_ACTIONS_NE_INDEPENDENT_RECOVERY`.
- `TRANSIENT_BYTE_VERIFIER_NE_DURABLE_AUTHENTICATED_RECEIVER`.

**Next gate:** an elected, separately controlled receiver with durable identity, exact source retrieval, real-time fault injection, receiver-produced acknowledgment and a demonstrated useful CoBar/CoOrb result. Keep the archived source immutable. No user relay needed until an actual authority boundary.
