# Downloads Custody Reconciliation R1

State: PUBLIC_SCRIPT__LOCAL_READONLY_CUSTODY_COMPARISON__APPEND_ONLY_OUTPUT

R0 produced an exact top-level Downloads census. R1 compares those exact SHA-256 hashes against the elected local durable roots D:\CoCivium\CoFarm and D:\CoCivium\CoStead.

R1 does not infer receiver pickup, integration, CoEx, supersession, public safety, or delete eligibility from a matching hash.

Input contract: exact R0 run root plus exact SHA-256 of R0 99_RECEIPT.json.

Efficiency: each durable root is enumerated once, filtered by target file sizes, and only size-compatible candidates are hashed. If bounded scan limits or hash errors create gaps, negative no-match claims are downgraded.

Output is append-only under D:\CoCivium\CoFarm\CoDownloadsCustodyReconcileR1\<UTC>.

No source deletion, movement, rename, upload, publication, or network request.

Rails:
HASH_MATCH_NE_RECEIVER_PICKUP
HASH_MATCH_NE_DELETE_SAFE
NO_MATCH_NE_ORPHAN_WITHOUT_BOUND_COVERAGE_AND_RECEIVER_EXPECTATION
