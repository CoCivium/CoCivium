# CoAsset+ minimal valency as reconstruction capacity | R0 candidate

**2026-11-07.**  **State:** SYNTHETIC_SOURCE_GRAPH_AND_RECOVERY_TEST__NOT_REAL_OFF_PROVIDER_CUSTODY_OR_RUNTIME.  Reuses CoSourceGraph+, CoIndex/GIBindex+, CoLex/CoMeaning+, CoPriorLeverageField+, CoResearchRecovery+ and existing CoResearch CI. It is a proof slice, not a new registry or daemon.

## Corrected interpretation of the earlier rule

The point of an asset's **bidirectional link to one or more other assets** is not merely navigation. It creates an addressable relational neighbourhood with potential for recovery from surviving overlap partners. Backlinks must be available as a derived **inverse query view**, not as an invented symmetric causal claim.

**Connectivity floor:** Every index-eligible asset should have >=1 qualified external partner or explicit `ORPHANED_UNRESOLVED`/isolation state. A fabricated link for quota compliance is worse than a visible orphan. Roots and privacy-isolated objects may require boundary-aware exceptions.

**Reconstruction floor:** Each asset should declare which kinds of loss it must survive and the *actual recoverability mechanism*: (a) semantic/relational reconstruction from versioned assertions, parents, negative knowledge and provenance; (b) exact-byte reconstruction from sufficient data, independently verified replicas, erasure/parity fragments, or deterministic build sources and dependencies; (c) receiver/workflow reconstruction from checkpoint, policy/authority, compatible capability and readback. A text label, URL, backpointer or SHA alone never implies exact-byte recovery.

**Recovery threshold is class-specific.** A two-of-three, 2 data + XOR parity example can restore one missing shard, provided the manifest, two valid shards and independent access survive. Real systems must separately prove genuine failure-domain diversity, restore rights and revocation, resilience to multiple simultaneous failures, privacy, currentness and receiver-bound execution. Greater valency may also improve error detection, interpretation, contradiction discovery, cross-lingual meaning, search, continuity and redundancy but does not guarantee these automatically.

## Bounded test design

The checked-in source-graph fixture is `ai/repo-field-projection-graph-r0.json`, a finite **repo-level** sample of 22 nodes and 21 directed relations. The new test derives outbound and reverse-navigation views from the **same** asserted edge. It detects orphan/dangling/self/duplicate errors. It does *not* enumerate every CoCivium asset or enforce a universal property.

The second part creates a synthetic binary payload, splits it into two padded halves, and stores their XOR parity as a third shard. It then discards the original for the reconstruction function and checks all three surviving pairs against its original SHA-256. Negative controls remove data bytes but leave pointer metadata, corrupt fragments, forge source hash/size, collapse declared failure domains and try too few surviving fragments. This only proves synthetic algorithm behaviour. All three fragments are created in one working process and the three failure-domain labels are **declared, not independently verified**.

## Self-contained embedded capsule, not a bare sidecar

The second tested candidate, `scripts/coasset_embedded_coshat_r0.py`, adds a **portable JSON capsule** for each of the three synthetic content fragments. Its envelope carries `coObject` identity/version, `coMeta` no-effect authority/privacy, `coMetaTrainable` frozen learning status, `coTime` fixture time, `coValence` two partner IDs and declared failure domain, `coSHAT` content/envelope SHA-256, and the fragment's actual base64 bytes. The canonical envelope digest excludes only its own `coSHAT.envelope_sha256` field, avoiding impossible self-hashing; it does not authenticate a writer without a separate trust/signature mechanism.

After deleting the original synthetic source file, **any two of three intact capsules** reconstruct its exact bytes; all three pairings, zero-length/odd-length cases, metadata tampering, false partner/domain claims, duplicate keys, source-version collision, unauthorized effect/trainability change, missing fragments and single-survivor failure are tested. This is a wrapper, **not proof that arbitrary PNG/DOCX/executable formats can acquire native metadata without changing their format or signature**. It is also not a real independent multi-provider backup: the three files were created inside one process and one CI failure domain, with independence represented only by synthetic labels.

A future asset-type policy can choose an inline, content-addressed, database-backed or externally stored reconstruction manifest according to format/rights/size/erasure requirements. Its *logical relation* should remain recoverable even if the physical metadata carrier moves. Neither a self-hash nor a successful CI test supplies semantic truth, custody landing, receiver ACK, a signature, or a 24-hour cold recovery.

## CoIndex / CI+ / CoOps+ relationships

- `CoIndex+` proposes `OVERLAPS_WITH`, `DERIVED_FROM`, `HAS_RECOVERY_FRAGMENT`, `REBUILDABLE_FROM`, `DISSENTS_WITH`, `SUPERCEDES`, `VERSION_OF` and `RECEIVED_BY` with source, class, time, confidentiality, direction and role. (Existing semantic relations remain authoritative for their scopes; these are examples, not an asserted new global ontology.)
- `CoLex/CoMeaning+` preserves variant/meaning/intent distinctions, semantic continuity and contradiction without asserting byte-perfect reconstruction.
- `CI+` validates referential integrity, reciprocal navigation **queries**, verifiable reconstruction fixtures, negative controls, explicit no-recovery cases and replay on source changes.
- `CoBoogie+` notices material loss, changed source/receiver, hash mismatch or disappeared overlap fragment; `CoRegroup+` elects recoverable alternatives and records why candidates are held.
- `CoOps+` may read/reconstruct in bounded authorized scope; it cannot infer file landing, receiver pickup, CoEx, canon, private-data movement or spending from the graph.
- `CoPriorLeverageField+` searches relevant historical overlaps and negative knowledge before rebuilding a supposedly missing idea. Index reach is not historical coverage.

**Next test that actually changes the resilience claim:** Place a rights-cleared source, manifest and independently useful recovery pieces with 3 genuinely distinct custodians or failure domains. Take the original offline, recover from the other two with an independent receiver, match bytes and version, then run a semantic teach-back. Retain null/blocked cases. No Rick relay is required if machine-owned authorized routes exist.

`POINTER_NE_PAYLOAD | BACKLINK_NE_REVERSE_FACT | GRAPH_CONNECTED_NE_RECONSTRUCTIBLE | HASH_NE_BYTES | OVERLAP_NE_SUFFICIENT_INFORMATION | DECLARED_DOMAIN_NE_INDEPENDENT_DOMAIN | LOCAL_REBUILD_NE_REMOTE_COLD_RESTORE | RECONSTRUCTED_BYTES_NE_ACCEPTED_MEANING | SOURCE_RECOVERY_NE_RECEIVER_ACK | SYNTHETIC_TEST_NE_CANON_RUNTIME_PUBLIC`.
