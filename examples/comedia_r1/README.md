# CoMedia R1 | Great ReFact WIP production and proof gate

**Status:** DRAFT R0 candidate, offline-first, no publication/send rights.

This work **reuses** CoMedia Inspiration Corpus R0, CoBook Living Rich-Media System R0 and the existing CoCivium CoFireworks/CoReview lifecycle. It is a *small proof tool*, not a new media operating system or an additional AI publishing authority.

## Files

- `storyboard.md`: first 45-second Great ReFact short, six shots, truthful claims and accessible adaptation.
- `manifest.json`: exact source identity, six shots, rights and WIP status.
- `media_gate.py`: stdlib local read-only inspector; can optionally inspect one exact local video file using ffprobe/ffmpeg.
- `tests/test_media_gate.py`: synthetic negative tests plus real temporary FFmpeg media checks when installed; no account or network calls.
- `benchmark_evo.jsonl`: append-only scoped proof and separate release holds.

## Usage

```sh
python3 media_gate.py manifest.json
python3 -m unittest discover -s tests -v
python3 media_gate.py manifest.json --media /path/to/one/locally-authorized-clip.mp4
```

The tool **never uploads or publishes**. It does not read environment secrets, inspect a media folder recursively, use network access or act on other accounts. It accepts one explicitly named file and executes ffprobe/ffmpeg without a shell. The video is capped at 1 GiB, probe subprocess at 20 seconds and the first-60-second black-screen check at a 35-second process ceiling. SHA-256 is computed incrementally. Large or unsupported inputs return HOLD/FAIL; video content is not included in JSON receipts.

## WIP labels and reviewer authority

Statuses: CONCEPT, WIP_STORYBOARD, WIP_RENDER, REVIEW_CANDIDATE, RELEASE_CANDIDATE. **Neither source tests nor the `RELEASE_CANDIDATE` state mean the cut is approved.** This gate always reports `release_eligible=false`; a separate authorized publisher must verify editorial approval, rights, factual/symbolic/fictional status, captions and comprehension, then post only to an approved channel.

A public-safe WIP review may use a persistent visible slate, plain transcript and review-only link. Do **not** call a private, unlicensed or inaccurate video "WIP" and publish it anyway. WIP is not a liability shield.

Required real-world review includes: script pacing, story arc, visual originality, visual source rights, thumbnails, high-resolution/mobile typography, color contrast, subtitles, audio-description alternatives, music/voice rights, believable viewer understanding, AI-content disclosure, names/likeness consent, privacy, first-use destination and exact archive/rollback.

A simple technical 300 KB/720p/blackdetect pass is only a scoped decoder test, not proof of creative quality, ethical claims, engagement, impact, publication or subscriber delivery. FFmpeg `blackdetect` can flag intentional artistic black scenes; those should be manually reviewed rather than silently banned. Lack of audio may be deliberate but must also be reviewed.

## Platform adaptation

- YouTube Shorts: official YouTube Help says square or vertical uploads up to three minutes can be categorized as Shorts (subject to channel/category conditions). Produce a vertical, phone-readable master; never infer a public upload from a local MP4.
- YouTube's current AI use survey requires disclosure for realistic or materially altered synthetic events/people and has distinct exceptions for non-realistic or production assistance. The manifest has typed AI-use fields but cannot complete YouTube Studio disclosure.
- Substack/RickPublic: source-linked essay or serial with an explicitly chosen embedded media cut; don't silently auto-replace a chapter someone already read.
- "WeTube" is not assumed to be an authenticated distribution partner; verify actual service and account before creating any adapter.

Sources: https://support.google.com/youtube/answer/15424877 ; https://support.google.com/youtube/answer/14328491 ; https://ffmpeg.org/ffmpeg-filters.html ; https://support.google.com/youtube/answer/1722171

## Editorial regeneration rule

`SOURCE_CHANGES -> PIN_PRIOR_VERSION -> PROPOSE_SCRIPT/SHOT_DELTA -> RIGHTS/CLAIMS/A11Y CHECK -> TEST NEW CUT -> HUMAN / QUALIFIED PUBLISHER REVIEW -> PUBLISH IF AUTHORIZED -> INDEPENDENT READBACK -> RECEIVE VOLUNTARY CRITIQUE -> NEXT PROPOSAL`.

Only *proposals* and technical checks may be automated without external-effect authority. No silent overwrites, no thousand unsolicited emails, no covert spiritual persuasion, no fabricated feedback, no assumed editor approval, no generic claims of divine authority, and no infinite worker spawn. Material changes may trigger a new bounded review wave rather than a daily media rewrite.

`TECHNICALLY_VALID_NE_EDITORIALLY_GOOD | WIP_NE_RELEASE | SOURCE_LINK_NE_RECEIVER | VIEW_NE_COMPREHENSION | COMMUNITY_FEEDBACK_NE_AUTOMATIC_CONSENT | MANY_PROJECTIONS_NE_MANY_TRUTHS`.
