# CoDevice Human-Time Pulse R0

**State:** \`CANDIDATE_ON_BRANCH__NOT_DEPLOYED_ON_X2__NO_NODE_ENROLLED\`

## Why

CoCivium already has the [CoNode participant contract](../Architecture/CONODE_PARTICIPATION_R0.md), [RickBar R4 UX contract](../UX/COFLEET_RICKBAR_R4.md), and the X2 scoped discovery script (\`scripts/CoParticipantEdge_X2_R0B.ps1\`). The missing first-use acceptance check is a **short, reproducible, human-visible local device pulse**, not another global fleet architecture.

This standalone PowerShell 7 script reports: a few named process-presence hints for CoBar/RickBar, Ollama and Desktop Commander; whether PowerShell, Git and Ollama commands are discoverable; whether two elected CoCivium directories exist; and exactly what was observed. It deliberately does not recurse through personal files or enumerate LAN devices. A process name does not certify runtime health.

## Windows execution

In a **trusted local clone** of CoCivium, run:

\`\`\`powershell
pwsh -NoProfile -File .\scripts\CoDeviceHumanTimePulseR0.ps1
\`\`\`

Optional: \`-OutputRoot 'D:\CoCivium\CoFarm\CoDevicePulse'\`. The script writes a uniquely named local directory with \`device_pulse.json\` and self-contained, accessible \`index.html\`; it prints their absolute paths. It does **not** open a browser, start programs or grant device access. By default, if the CoFarm root exists on D:, receipts are placed under \`D:\CoCivium\CoFarm\CoDevicePulse\`, otherwise under the executing user's local application data directory.

The HTML shows three useful elements first: **Here Now**, **Meaning**, and **Next Safe Action**, then a small table of local evidence. Source-script SHA-256 and time are recorded in the JSON. A fresh subdirectory for each pulse avoids replacing existing evidence.

No network calls, token/API access, account changes, installers, background watchers, Bluetooth discovery, microphones, cameras, device screenshots or full machine scans occur. Any information remains on the machine unless the human knowingly copies it. No phone, Quest, child-owned device or remote user is automatically enrolled.

## Candidate device ladder

- **X2:** first local run, in a fresh terminal; verify JSON and rendered HTML in an actual user session. Check that capture finishes quickly without stealing focus.
- **CoStead:** after X2 approval, explicitly choose an allowed receiver and verify an exact-object readproof; directory visibility alone does not prove receiver pickup.
- **Other PCs:** repeat the same local read-only pulse with each device owner's authorization and local disconnect.
- **Android/iPad/Quest:** use a purpose-built consented adapter, *not* a PowerShell clone or unrestricted remote-control installer.

## Acceptance evidence, not promises

1. GitHub Windows CI: deterministic structure and no-effects regressions, new paths on repeated runs, plus process/runtime distinction.
2. X2: actual execution, local elapsed time, UI readability, and external readback of the produced receipt.
3. CoStead: explicitly authenticated receiving process, separate origin, readproof and feedback.
4. Second-person first use: one task completed without human copying work between provider tabs.

**Nonclaims:** CI is not X2 deployment. X2 is not the whole fleet. A file path is not a receiver ACK. A visible status page is not proof of full desktop integration. A discovered executable does not grant effect authority.

**Upgrade direction:** only after first use, connect this minimal state to existing CoFleetProjection, event-triggered local/open model adapters and CoPhoenix cold-start recovery. Keep every model replaceable and preserve privacy, receipts, safe rollback and user-owned control.
