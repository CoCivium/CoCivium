# CoCopy+ Rich Payload Palette R0 | One deliberate gesture, multiple useful formats

**2026-10-24 | CANDIDATE_SOURCE_IN_CHAT | NO_X2_INSTALLATION | NO_MOUSE_BINDING | NO_AUTOMATED_RECEIVER**

This is a bounded, visible **CoNod+/CoThumb+ successor candidate**, not a second installed framework. Its source and ZIP are delivered in the originating ChatGPT conversation as `CoCopyRichPaletteR0.ps1` and `CoCopyRichPaletteR0.zip`. GitHub currently contains **the manifest and this public design only**, **not the executable source**; the full Windows implementation is therefore not reproducible from this repository alone.

[Machine-readable source hashes, limits and nonclaims](../../ai/payloads/cocopy-rich-palette-r0.json) · [Existing CoNod+ 22-test shadow policy](../../examples/conodcothumb/README.md) · [CoCopy+/CoThumb+ earlier attractor concept](CORESOURCE_ATTRACTOR_R0.md).

## Reframe: parallel representations, not parallel side effects

A single explicit user-selected payload can be represented as multiple *typed, destination-negotiated clipboard formats*. Examples:

- `FILEDROP`: up to **24 existing file references** (e.g., videos, PDFs, images, archives), without duplicating the files' bytes into RAM; accompanied by a **UnicodeText** fallback listing only file basenames.
- `UNICODE_TEXT`: up to **65,536** user-entered characters with no automatic source-app text capture.
- `BITMAP`: one explicitly selected PNG/JPEG/BMP/GIF converted to pixels after file-size **32 MiB** and decoded **16-million-pixel** checks.
- `CONTEXT`: the active process **name** and horizontal pointer region help propose a default visible tab. The script does not read title, text, browser contents, current clipboard contents, webcam, mic or screen pixels.

The user then manually chooses the receiving application's paste/upload action. Browser file pickers, creative tools, messaging apps and Windows Explorer may accept different formats. **FileDrop references do not transfer media bytes to another machine by themselves.** Actual paste happens only when the target app accepts them.

A future **CoOrg+** can treat a group as one typed source object with media references, checksum receipts, MIME types, permissions, dimensions and temporal relations. Preview/format negotiation can run *logically* in parallel, but active CPU, API, memory, privacy and receiver counts remain bounded.

## The current X2 path

1. Download the ZIP attached in the original conversation into X2's Downloads folder.
2. Use the single PowerShell 7 copy/paste verifier and launcher supplied alongside it. It checks exact ZIP SHA-256 `9eed927fc6a6797feb8793106e51129dc929eea347a2c132bca9a815f43e1b18` and PS source SHA-256 `e7d6d4446e74e35bb7a649ab21b73e2bc0379e891b32c5e44956aa32e1a7ae5f`, refuses to clobber a changed installed script, runs `-SelfTest` in STA, then opens a foreground palette.
3. For first acceptance, use **only non-sensitive test media**. Stage one public file, verify the intended clipboard mode, paste manually into one consenting target application, and cancel safely. Record actual app support and exact test outcome.
4. If preflight and real clipboard behaviour pass, the device owner may elect an explicit **reversible gesture-to-open-palette mapping** after identifying the actual mouse and its existing middle/thumb assignments. Keep the normal click/scroll semantics or a keyboard fallback; **never bind gesture directly to paste/send, nor silently install an OS-wide mouse hook**.
5. Only after that can a native CoOrbWare overlay be considered. CoCopy+ should not steal focus, hide sensitive data, intercept bystanders, or draw unverified content on wallpaper.

## Source and proof

The generated script/package were checked against **26/26 static source predicates**, and the ZIP passed extraction-integrity testing. These tests validate source structure and policy language only. The executable PowerShell parser and Windows Forms GUI were **not run** in the Linux container, and X2's Desktop Commander was **offline** in the current wave.

A Windows `-SelfTest` exists and checks seven in-memory integration prerequisites; **its PASS is not yet observed**. The physical middle/thumb gesture is not mapped; no OS action, file upload, Gmail send, CoVIA relay, CoStead landing, media `ffprobe` rerun or user task completion has been claimed.

### Risk and recovery

The Windows clipboard is shared among applications and may be synchronized or retained by clipboard history/managers; it is **not a privacy vault**. FileDrop carries real absolute file paths to a target when deliberately pasted. Stage only safe data; closing the UI does not automatically erase clipboard history. The script creates no shortcut, service, autorun, background listener or hidden control.

**Receiver states:** `SOURCE_GENERATED_LOCAL` and `STATIC_AUDIT_PASS`; `WINDOWS_GUI=HELD`; `X2_INSTALLATION=HELD`; `MOUSE_PHYSICAL_EVENT=HELD`; `USER_TARGET_PASTE=HELD`; `COORBWARE_RUNTIME=HELD`.

**Next CoDeed:** exact Windows `-SelfTest` and one intentional non-sensitive FileDrop paste with an observed result. Treat a successful FileDrop as just one app-format probe, not blanket compatibility.

`GESTURE_NE_AUTHORITY` · `CLIPBOARD_NE_SECRET_VAULT` · `STATIC_SOURCE_NE_RUNTIME` · `PARALLEL_REPRESENTATIONS_NE_PARALLEL_SENDS` · `LOCAL_IS_NOT_LANDED` · `POINTER_NE_ACK`.

FOSS Forever | CoGoAll | EVO ALL BETTERS + | Working Together Respectfully | Privacy by design.
