# CoThumb+ / CoCopy+ R1 | Local rich-media intent capsule

**State (2026-10-24): PUBLIC SOURCE CANDIDATE; WINDOWS LIVE CANARY HELD.** The script and read-only Windows CI self-test source are on GitHub. No X2 hardware gesture, Windows GUI or CI execution result is claimed as PASS unless a fresh receipt proves it.

This is a successor to the existing CoThumb R0 local self-test, which reported `PASS_SELF_TEST__HELD_PHYSICAL_BUTTON`. It does not replace or modify `D:\CoCivium\CoFarm\CoThumbR0\CoThumbR0.ps1` or any Logitech Options+ setting.

## What it does now

The single PowerShell 7 script [CoThumbCoCopyR1.ps1](../../scripts/CoThumbCoCopyR1.ps1) is an **explicitly launched, visible Windows panel**. It has three user-initiated ways to supply actual file bytes or identities:

1. Choose up to four regular files with the native Windows file picker.
2. Select files in Windows Explorer and press Ctrl+C, then click **Use copied files**. The application reads only Windows' file-drop list after this explicit click, not plain-text clipboard contents.
3. Drag and drop files into the panel.

**Default** is `REFERENCE_ONLY`: hash each source with SHA-256 and create one private CoCopy+ capsule under CoFarm, without duplicating media bytes. Optional `STAGE_BYTES` requires a separate confirmation and caps total duplicate bytes at 2 GiB. The application leaves the source files unchanged.

It creates a unique, no-clobber run folder with `request.json`, `capsule.json`, `receipt.json`, and `benchmark_evo.jsonl`. It proposes typed derivative lanes, depending on the file: source integrity, provenance, relation mapping, ffprobe, blackdetect, thumbnails, captions, transcripts, document extraction, accessibility, rights/privacy checks and so on. The **derivative lanes remain proposals**. Maximum actual file-processing worker count in R1: **one**, bound to the visible panel's lifecycle. There is no outward send or autonomous publishing.

## Middle/thumb context: opt-in and no native remap

The physical observer is **OFF by default**. The user can arm a visible button and choose among:

- `Ctrl+Alt+Shift+F12`: preferred; assign an otherwise unused mouse control to this keystroke in Logitech Options+ manually, if desired.
- `XBUTTON2` or `XBUTTON1`: Windows standard side mouse inputs where not intercepted by Logitech or other utilities.
- `MBUTTON`: the physical wheel click, which may continue doing its native browser/scroll action.

The GUI polls only for the elected gesture while the preview is armed. One press merely activates the local panel and displays **foreground process class and coarse cursor region**. It does not read application content, selected text, window title, clipboard text, pixels, typed keys, credentials or web pages. Cursor coordinates and window titles are not saved. Region is a **weak hint**, not a reliable identifier of a selected file, source object or authority. File selection and creation require additional explicit action. Nothing hooks, intercepts, remaps, injects or automatically pastes a mouse action.

To disarm, click **Disarm preview** or close the panel. A running local file job cannot be silently abandoned; closing prompts first.

## Reproducible bounded self-test

On Windows PowerShell 7:

```powershell
pwsh -NoProfile -File .\scripts\CoThumbCoCopyR1.ps1 -Mode SelfTest
```

The run requires an existing `D:\CoCivium\CoFarm` or `C:\CoCivium\CoFarm` root. Hosted CI uses an explicitly declared disposable `-CoFarmRoot` instead. Success requires a new exact local SHA-256 source capture, readback of a source-bound capsule, a local receipt and **zero executed derivative lanes**. Self-test **does not test physical mouse events, actual Windows GUI behavior, file-drop integration or throughput on large real media**. The read-only CI workflow is [here](../../.github/workflows/cothumb-cocopy-r1.yml), with a short execution timeout.

To open the GUI:

```powershell
pwsh -STA -NoProfile -File .\scripts\CoThumbCoCopyR1.ps1 -Mode UI
```

## Promotion gates

1. Fresh self-test from the installed exact source digest on X2.
2. Physical gesture readback: one elected button/hotkey opens visible preview, and disarm stops observation; confirm original OS behavior is not unexpectedly disrupted.
3. One real, deliberately selected media file: stable source metadata, exact SHA, optional exact staged byte copy within budget, no private data exposure.
4. Independent first-use and accessibility canary, including keyboard support, recovery after cancel, and feedback on confusing behavior.
5. Measured idle cost, response latency, disk budget, file-stability failure and crash/stop behavior.
6. Only then consider an app-specific **CoCopy+/CoOrg+ transport adapter** that can deliver an exact capsule to an authorized local receiver with a receiver-origin readproof.

There is no CoBar/RickBar live runtime, always-on mouse agent, CoStead landing, independent receiver pickup, multi-provider session virtualization, large-file reliability proof, CoEx, canon or public release assertion here.

**Architecture:** one gesture → private capsule → multiple proposed typed tasks → bounded qualified workers → receiver-proofed handoff. A rich media payload travels by file/stream with hash and provenance; do not stuff video bytes or huge base64 blobs into chat text or clipboard.

`GESTURE_NE_AUTHORITY | CLIPBOARD_NE_UPLOAD | POINTER_NE_PAYLOAD | HASH_NE_TRUTH | PROPOSED_NE_EXECUTED | LOCAL_IS_NOT_LANDED | R1_SOURCE_NE_WINDOWS_RUNTIME_PASS`

FOSS Forever | CoGoAll | Working Together Respectfully | privacy-by-design | inclusive/voluntary | visible activity | wearable optional.
