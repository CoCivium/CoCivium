# CoPayload+ R1 | Opt-in rich media files for CoMousePalette

**Scope:** Windows 11 / PowerShell 7 / STA. No hooks, no remote delivery, no model calls, no automatic paste, and no background capture. The user explicitly picks files and chooses what to copy.

**Launch:** `pwsh -NoProfile -STA -File .\CoPayload_R1.ps1`. The optional `-SelfTest` and `-Canary` modes do not open the GUI or touch the real clipboard. `-Canary` stages and verifies tiny temporary synthetic files, then removes only its own temporary files.

1. **Choose files** intentionally in the Windows file picker. The palette shows basenames and sizes; nothing is yet packaged.
2. **Stage ZIP** copies up to 12 files, 512 MiB each, 1 GiB total, into a unique temporary staging directory, compares source/copy SHA-256, creates a ZIP with `manifest.json`, verifies every ZIP member, then removes only its own staging copies. The ZIP stays in `D:\CoCivium\CoFarm\CoPayloadR1\capsules` by default. Never overwrites an existing capsule.
3. **Copy ZIP file** uses the Windows FileDrop clipboard format. Some recipients accept Ctrl+V as an attachment, some do not. Open folder and use the application's attachment picker when needed. **No content is uploaded by the tool.**
4. **Copy image pixels** is explicitly available for one chosen image up to 20 MiB. The target application must accept pasted images.
5. **Copy local reference** copies only work ID, local ZIP path, hash, and *unverified* receiver status. The referenced file stays local until deliberately transferred.

Safety: The local ZIP may contain sensitive data. `manifest.json` retains original basenames inside the private archive, but no original full source paths. Never paste a local reference and claim a remote model saw the media. Credentials, audio/video sensors, private chats, financial actions, and mouse remapping are **not** automatically activated. There is no indefinite retention service; locally produced ZIPs require user-controlled retention/deletion policy.

The package format is `CoWorkCapsule/R1` with `work_id`, privacy/authority, source bytes, per-member SHA-256 and file names. A cheap context summary is not a replacement for the actual files. Agents can later request individual verified pieces, with explicit budgets and authority.

**Not yet tested on X2:** physical Logitech MX Master 4 thumb mapping, paste acceptance by specific programs, accessibility/screen-reader behavior, resource overhead for 1 GiB archives, multiple-machine custody, and backend CoVIA receipts.
