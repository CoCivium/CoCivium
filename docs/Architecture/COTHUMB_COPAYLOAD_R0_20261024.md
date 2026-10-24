# CoThumb+ / CoPayload+ R0 — high-bandwidth contextual handoff

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NOT_NATIVE_RUNTIME__NOT_PHYSICAL_GESTURE_PROOF  
**Observed:** 2026-10-24

## Purpose

Evolve CoThumb+/CoCopy+ from a narrow text-copy gesture into a receiver-relative, high-bandwidth contextual handoff surface for text, files, images, video, audio, URLs, code, datasets, CoMap fragments and other typed work objects.

The thumb gesture is a **summon / bind / preview / choose** control, not implicit authority to send, publish, execute, overwrite or disclose.

## Core contract

```
gesture
-> bind foreground context
-> identify candidate object
-> fan out cheap read-only probes
-> classify / hash / provenance / privacy / authority
-> build preview + receiver candidates
-> fan in to a compact ranked action set
-> explicit user choice
-> bounded effect
-> receipt
```

Preparation may fan out in parallel. Consequential effects remain separately authorized and collision-safe.

## Payload modes

### SMALL_INLINE
Short text or compact structured data may travel inline with sentinels, byte count and SHA-256.

### FILE_BACKED
Larger or proof-critical payloads use an exact file-backed handoff with content hash, type, byte count and provenance.

### CONTENT_ADDRESSED
Rich media and large objects should normally travel as a content-addressed object plus manifest/preview rather than as megabytes of raw clipboard text.

Candidate manifest fields:

```
payload_id
payload_type
source_identity
sha256
byte_count
preview_ref
provenance
privacy
authority
currentness
receiver_candidates
transform_candidates
recovery_pointer
nonclaims
```

## Parallel interpretation lanes

A bounded gesture may prepare, where relevant:

- object/type identification;
- SHA-256 / byte-count integrity;
- metadata parse;
- thumbnail/preview generation;
- duplicate/prior lookup;
- CoOrg classification;
- CoMap relation candidates;
- privacy/authority classification;
- receiver compatibility;
- reversible transform candidates;
- historical/prior comparison.

These lanes do not grant effect authority.

## Rich-media example

For a video payload:

```
video file
-> exact file identity + SHA-256
-> byte count
-> ffprobe metadata
-> thumbnail
-> blackdetect gate where appropriate
-> optional transcript/summary candidate
-> related-prior search
-> receiver-safe preview
-> explicit attach/copy/reference choice
```

A preview or prepared attachment is not a send.

## Contextual gesture candidate

Default native mouse behavior remains unchanged unless the user explicitly enables a CoThumb binding.

Candidate semantics:

- short: summon context / top reversible actions;
- hold: expand relations and preview;
- double: capture/buffer current object;
- drag while held: ghost target preview;
- Ctrl+thumb: deep/forensic actions;
- Shift+thumb: compare/alternatives;
- Alt+thumb: priors/provenance/history.

Exact physical device mapping is not assumed. Middle button and XBUTTON1/2 are distinct Windows events.

## CoCopy / CoBuffer / CoOrg

CoCopy+ is treated as a provenance-aware transfer fabric, not a clipboard replacement.

```
CoCopy -> CoBuffer -> CoOrg/CoMap -> receiver preview -> explicit effect -> receipt
```

Native clipboard remains an adapter for small non-critical payloads only. File-backed or content-addressed handoff is preferred for long, rich, or proof-critical payloads.

## Million-session relation

High-bandwidth payload handling does not justify high active process count.

```
huge logical address space
-> bounded selector
-> small active frontier
-> parallel cheap probes
-> serialized consequential effects
-> receipts
-> sleep / wake / checkpoint
```

`LOGICAL_SESSION_NE_ACTIVE_PROCESS`
`MANY_PROBES_NE_MANY_EFFECTS`

## Test gates

### Architecture / source
- exact public source readback;
- schema fields present;
- no implicit effect authority;
- rich-media path distinguishes inline vs file-backed/content-addressed.

### Physical gesture
- actual X2 physical middle/thumb event observed;
- native fallback confirmed;
- panic-disable confirmed;
- no accidental double effect.

### Rich-media canary
For one non-sensitive media file:
- size > 300 KB;
- exact SHA-256 and byte count;
- thumbnail present and inspectable;
- ffprobe parses;
- blackdetect reports no disallowed black segment under the elected rule;
- preview is shown before external transmission;
- receiver action is explicit;
- receipt binds source and effect separately.

### Provider / receiver gates retained
- GitHub HTTP 200 <2s: scoped sample PASS only when named timed receipt exists;
- Gmail Primary <60s: HELD without recipient-side Primary timing;
- Pi compat <2s: HELD until real compatible endpoint/CLI receipt;
- Claude credential-presence <1s: HELD until safe presence-only receipt;
- local Llama/Ollama packet or response parse <3s: metadata-only PASS does not prove inference quality.

## Historical redo

Replays must preserve source, old assumptions, old failure evidence and comparison criteria. A newer model, richer payload or more parallelism is not automatically better.

## Rails

`COPY_NE_PASTE`  
`PASTE_NE_SEND`  
`BUFFER_NE_CUSTODY`  
`PREPARED_ATTACHMENT_NE_SENT`  
`PAYLOAD_POINTER_NE_PAYLOAD`  
`SCREEN_POSITION_NE_AUTHORITY`  
`PARALLEL_PREPARATION_NE_PARALLEL_EFFECTS`  
`RICH_MEDIA_NE_CLIPBOARD_BLOB`  
`LOGICAL_SESSION_NE_ACTIVE_PROCESS`  
`LOCAL_IS_NOT_LANDED`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

## Next bounded proof

On X2, observe one real physical thumb/middle gesture and one real non-sensitive rich-media file through:

`gesture -> identify -> hash -> preview -> explicit local receiver action -> receipt`

Stop before any external send unless separately authorized.
