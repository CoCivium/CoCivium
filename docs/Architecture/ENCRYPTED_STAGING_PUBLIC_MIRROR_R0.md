# Encrypted Staging / Public Mirror Policy R0

**State:** `PUBLIC_POLICY__NO_BULK_PAYLOAD_UPLOAD__NO_SECRET_MATERIAL`

## Lead decision

Do **not** use a public GitHub repository as the default storage destination for encrypted private or unknown-class payloads.

Encryption is a useful confidentiality layer. It does not convert a public repository into a private custody domain.

The preferred split is:

```
unknown/private Downloads payload
        |
        +--> encrypted private/offsite custody
        |      + exact hash/manifest
        |      + restore/readback proof
        |
        +--> public-safe redacted manifest/pointer, if useful
               + no secret values
               + no sensitive filenames/metadata unless deliberately public
```

Public-safe plaintext may be promoted to GitHub after classification.

## Why public encrypted blobs are not the default

A public encrypted blob can still expose:

- existence;
- timing;
- size;
- naming/path metadata;
- traffic and change patterns;
- repository relationships;
- who references it;
- a permanent target for future cryptanalysis or later key compromise.

Deleting it later is not equivalent to proving it was never copied or retained.

`ENCRYPTED_NE_PRIVATE_SURFACE`  
`DELETE_NE_UNPUBLISH_EVERY_COPY`  
`PUBLIC_CIPHERTEXT_NE_ZERO_DISCLOSURE`

## Unknown defaults private

Any Downloads object that has not been classified is treated as private/unknown until proven public-safe.

`UNKNOWN_NE_PUBLIC`

The fact that the project intends a broad future public release does not imply that historical private, operational, personal, third-party, credential-adjacent, or context-sensitive artifacts are safe to publish now.

`FUTURE_PUBLIC_INTENT_NE_PRESENT_PUBLIC_AUTHORITY`

## Downloads migration classes

Each candidate object should be classified into one of:

- `PUBLIC_SAFE_PLAINTEXT`
- `PUBLIC_SAFE_AFTER_REDACTION`
- `PRIVATE_PROJECT`
- `SENSITIVE_OR_GLUKEY_ADJACENT`
- `CREDENTIAL_OR_SECRET`
- `THIRD_PARTY_LICENSE_REVIEW`
- `UNKNOWN`

Routing:

- public-safe -> GitHub/public nodes;
- private project -> encrypted private node/offsite replica;
- sensitive/Glukey-adjacent -> private custody only;
- credential/secret -> secret manager/control plane only, never bulk archive;
- unknown -> private pending classification.

## Public manifest rule

For private/unknown payloads, a public manifest is optional and must be metadata-minimized.

Allowed examples:

- opaque object ID;
- ciphertext/content hash where safe;
- lifecycle state;
- public-safe relation class;
- currentness/wake condition;
- nonclaim.

Do not publish private filenames, paths, recipient identities, sizes, timestamps, or source descriptions unless individually classified public-safe.

## Encryption / backup relation

Candidate preferred tooling may include:

- age or equivalent public-key encryption;
- restic for encrypted backup/restore;
- rclone or another replaceable transport;
- independent offsite storage;
- periodic restore/readback proof.

Exact algorithms and tools remain replaceable.

`CRYPTO_TOOL_NE_ONTOLOGY`  
`BACKUP_NE_REAL_UNTIL_RESTORE_PROOF`

## GitHub role

GitHub is elected for:

- public-safe currentness;
- public source;
- collaboration;
- machine-readable twins;
- public-safe manifests and pointers;
- reviewable candidate work.

GitHub is **not** elected as the default raw private-archive store.

## Session rule

Sessions should not ask Rick to upload large private/unknown archives into provider context merely for classification when a machine-owned local/private route exists or can be restored.

`RICK_NE_FILE_FERRY`

When the X2/local capability route is unavailable, a bounded upload can be used as an exception, but it remains staging rather than the mature architecture.

## Nonclaims

This policy does not prove:

- current Downloads classification;
- current secret-free state;
- encrypted offsite backup;
- restore proof;
- X2-to-CoStead synchronization;
- private GitHub backup;
- public deletion guarantees.

## Rails

`ENCRYPTED_NE_PUBLIC_SAFE`  
`UNKNOWN_NE_PUBLIC`  
`PUBLIC_CIPHERTEXT_NE_ZERO_DISCLOSURE`  
`DELETE_NE_UNPUBLISH_EVERY_COPY`  
`FUTURE_PUBLIC_INTENT_NE_PRESENT_PUBLIC_AUTHORITY`  
`GITHUB_NE_PRIVATE_BACKUP_ROOT`  
`BACKUP_NE_REAL_UNTIL_RESTORE_PROOF`  
`RICK_NE_FILE_FERRY`
