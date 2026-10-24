# CoPayload Handoff R1 | file-backed, preview-only CoQuanta

**State:** offline experimental reference implementation; **not** a mouse mapping, clipboard manager, desktop/CoOrbWare runtime, persistent object store, durable custody receiver, or external broadcast.

In CoCivium's existing [`CoThumb+/CoPayload+ R0` architecture](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COTHUMB_COPAYLOAD_R0_20261024.md), a contextual thumb gesture can *summon* a preview of source-linked text, images, video, audio and other typed work. This small tool implements only the safe **file-backed content-hash and byte-readback** part. It adds no independent ontology or device ownership.

## What it does

- Operates only on **one file explicitly selected** by its caller; no screen hooks, clipboard snooping, directory discovery or shell effects.
- Streams SHA-256 over the file and makes at most **32 exact hashed content chunks**. By default it accepts files up to 1 GiB; memory consumption is bounded to a 1 MiB read block.
- Writes a **new local JSON manifest** using exclusive creation. Holds instead of overwriting an existing file or following a source symlink. Source bytes are never rewritten or copied.
- Keeps the source path, filename and content *out of the manifest*. MIME is an extension-based guess only, not `ffprobe` or playback verification.
- Separately verifies exact bytes of an explicitly selected local file against that manifest. This is a **byte match**, not independent receiver ACK or semantic acceptance.
- Includes `nonclaims`, privacy class, actual external effects zero, authorization ceiling `NONE`, and physical gesture `HELD_NOT_OBSERVED`.

**Privacy:** A SHA-256 and byte length can disclose sensitive facts if published. A private manifest is **not automatically safe to publish**. The tool sends nothing, but the operator must elect a private destination and actual receiver authority before sharing.

## Try with a disposable local file

With Python 3.9+ (no third-party packages), from this directory:

```sh
python3 copayload.py prepare --file /path/to/harmless-sample.mp4 --out /path/to/new/manifest.json --privacy PRIVATE
python3 copayload.py verify --file /path/to/harmless-sample.mp4 --manifest /path/to/new/manifest.json
python3 -m unittest -v test_copayload.py
```

On X2 PowerShell 7, use `python` instead of `python3` if that is the installed launcher; do **not** run as administrator. The destination directory must already exist. Only test non-sensitive disposable material initially. Nothing is mapped to MX Master 4 or any other input device by this source.

## Integration gates

1. X2 Desktop Commander or another authorized local receiver reports online after cold start; inspect actual mouse/Logitech settings **read-only**.
2. Observe the actual physical event in a foreground user session, with cancel/rollback and no interception of native input.
3. Bind the event to a **visible** CoThumb R1 preview through Logitech's supported per-app mapping or Action Ring. Preserve native fallback and keyboard equivalence.
4. Preview a *harmless* file or other selected object. Invoke this byte manifest helper only by explicit user action. Show source type, size, SHA and privacy, with no raw path in public projection.
5. Elect one local receiver and have it independently supply/check the exact bytes, produce its own receipt, and record whether the user understood the preview. A source-side byte match alone does not qualify receiver pickup.
6. Then measure chunk-selective cross-provider context retrieval on real bounded tasks: accuracy, latency, cost, consent, and user effort. A model cannot access arbitrary media or infinite tokens merely because a manifest exists.

## High-bandwidth without false infinities

`ONE_WAVE_ID -> VERIFIED_OBJECT_MANIFEST -> SMALL_CONTEXT_PACKET -> ROLE_FILTERED_RETRIEVAL -> BOUNDED_AGENTS -> SCOPED_OUTPUT -> EXACT_RECEIPT`.

Large media should live in appropriate private custody (file/object store) and be referenced by small typed manifests. Processing and model-context windows remain finite. Agent processes do not inherit credentials, user permissions, or durable currentness simply from a shared packet.

**Nonclaims:** `BUFFER_NE_CUSTODY` · `PREVIEW_NE_EXECUTE` · `FILE_BACKED_NE_SENT` · `HASH_NE_TRUTH` · `MANY_LOGICAL_SESSIONS_NE_MANY_WORKERS` · `SCREEN_POSITION_NE_AUTHORITY` · `ACTUAL_COTHUMB_EVENT_HELD` · `LOCAL_IS_NOT_LANDED` · `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.
