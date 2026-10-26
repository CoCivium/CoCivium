# CoOmniIO+ R0 | MX Master 4 preview + bounded local auto-cycles

**Executable candidate, not an installed X2 runtime or universal device takeover.**

This combines the existing source-hashed CoCopy+ R0 foreground file/text/image palette with a Windows tray hotkey and a Node 22+ local queue. The pieces are independent and reversible. No account is linked, no network is contacted, and no existing Logitech assignment is changed by setup.

## What happens after an explicit install

1. Verify every package source file by SHA-256. Run non-effect PowerShell 7 Windows STA and Node preflights. Refuse changed files rather than overwriting them.
2. Place the candidate under `D:\CoCivium\CoFarm\CoOrbIO_R0` if that directory exists, otherwise under the current user's LocalAppData directory.
3. Run a **single safe local hash task** against an example file. It writes a private append-only receipt. No human message, OS input, network or model is invoked.
4. Attempt a **per-user Scheduled Task** executing one bounded local queue cycle every **15 minutes** (a 365-day trigger requiring later renewal), when the Windows user is logged in. The queue does not automatically discover arbitrary folders, providers or messages. It handles only explicitly submitted files inside its dedicated `state\objects` root.
5. Attempt to create a **per-user startup shortcut** and launch a **visible system-tray hotkey**. Pressing Ctrl+Alt+Shift+N opens the existing foreground CoCopy+ palette near the pointer. The palette's ordinary UI requires an explicit user click before changing the system clipboard, and manual paste afterward.
6. To bind the MX Master 4 Haptic Sense Panel / middle-thumb control, use **Logi Options+** to place the same key chord in an **Actions Ring bubble** first; preserve the panel's normal Actions Ring behaviour. A direct button assignment needs its own saved mapping and rollback. **This setup deliberately does not change Logitech mappings or the native middle-click/scroll.** Existing mappings must be inspected first.

**Pause:** right-click the tray icon > Pause hotkey; Esc cancels the palette. `node CoOmniCycleR0.mjs --pause <state-root>` stops task selection. **Remove:** run `pwsh -NoProfile -STA -File .\Setup-CoOrbIO_R0.ps1 -Mode Remove` from the installed directory. This requests tray stop and removes the specific task and startup shortcut; it does not delete original sources, queue manifests or receipts. If a collision or Windows policy prevents scheduling, installation reports HELD and leaves the non-effect local pieces usable.

## Queue semantics

Only three task types are accepted:

- `HASH_OBJECT`: stream a file from the explicit local `state/objects` folder and record SHA-256 and bytes, without copying content to a provider.
- `INSPECT_JSON`: inspect a local JSON file with size cap and report its shape, not its content.
- `COPY_PLAN`: hash up to 24 local files and prepare a typed source reference list; **does not read or change the clipboard, transmit bytes, send messages, or paste**.

Maximum 4 queued tasks per cycle, 2 concurrent bounded tasks, 32 GiB total bytes per cycle, 16 GiB per object, 24 files per copy plan and 5 MiB for JSON inspection. This uses streaming so a file's bytes do not become a model's token context. Limits are finite and subject to available hardware. No subprocesses or provider sessions are started by the Node queue.

Manual example after install:

```powershell
$root = 'D:\CoCivium\CoFarm\CoOrbIO_R0\state'
$module = 'D:\CoCivium\CoFarm\CoOrbIO_R0\CoOmniCycleR0.mjs'
# Already includes a harmless first task. These just inspect state:
node $module --status $root
node $module --cycle $root
```

For an additional file, copy a **non-sensitive** object into `state/objects`, then create an explicit task manifest under `state/inbox/` or call `node CoOmniCycleR0.mjs --submit <state> <task.json>`. Do not put passwords, private keys, confidential medical records, trading credentials, private inventions or bystander images into that folder. Clipboard data can persist through Windows Clipboard History, synchronization or managers.

## Shortcut binding

The hardware is an **MX Master 4**, where the haptic panel, gesture button, physical middle wheel click, back/forward and thumb wheel are different controls. Preserve the natural middle click. Logi Options+ supports app-specific assignments and Actions Ring. The same explicit shortcut can be put in a bubble, without installing an operating-system mouse hook. Use one *preview* shortcut rather than mapping a hardware control directly to Ctrl+V, send, broadcast, or process execution.

## Boundaries

- Shared manifests and provenance do **not** grant infinite token windows or compute. Agents read needed chunks on demand, use pinned sources, retain checkpoint receipts, and inherit parent resource/authority ceilings. Logical trillion-member candidate pools do not run a trillion workers.
- Continuous local polling is only possible when the scheduled task actually registers and the user/session/computer is available. The chat itself does not run in the background and cannot reach X2 when Desktop Commander reports offline. No claim of globally synchronized provider contexts or live CoOrbWare runtime.
- A local SHA-256 receipt is `VERIFIED_LOCAL` evidence only, never a CoStead landing, outside receiver pickup, integration, CoEx, or public adoption.
- CoOmniCycle R0 is explicitly **not** a trading bot, wallet controller, surveillance tool, microphone/camera agent, credential scanner, unattended email sender, or broad I/O interceptor. Those remain separate permission and validation gates.
- Nonphysical/spiritual/G_d explorations can be recorded as clearly labelled hypotheses or metaphors but do not provide compute, storage, evidence or software permissions.

## Reproduce without Windows

With Node 22+: `node --test CoOmniCycleR0.test.mjs`. The tests use a temporary local directory and clean it up. Run `node CoOmniCycleR0.mjs --selftest` for its no-effect preflight. PowerShell scripts receive static structural review only outside Windows; actual Windows STA, tray, Task Scheduler, Logitech mapping, rich-media and cross-app clipboard tests remain HELD until independently run on X2.

**EVO ALL BETTERS + | CoStretch+ | CoTurtle+ | FOSS Forever | CoGoAll | Working Together Respectfully | privacy by design.**
