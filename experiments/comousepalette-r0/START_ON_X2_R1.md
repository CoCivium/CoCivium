# CoMousePalette + CoPayload R1 | One-paste launch on X2

**Current X2 status:** Offline to Desktop Commander. This paste does not remap a physical button. It installs pinned, verified scripts in a new CoFarm folder and opens a visible palette only when you paste it into **your own PowerShell 7** session.

```powershell
$ErrorActionPreference='Stop'
$b='D:\CoCivium\CoFarm'; if(!(Test-Path -LiteralPath $b -PathType Container)){throw 'CoFarm missing'}
$d=Join-Path $b 'CoMousePalette_R1'; [IO.Directory]::CreateDirectory($d)|Out-Null
$f=Join-Path $d 'PASTE_ON_X2_R1.ps1'
$u='https://raw.githubusercontent.com/CoCivium/CoCivium/1f1497edbc85842abfdd669adbecef7f1f89ab22/experiments/comousepalette-r0/PASTE_ON_X2_R1.ps1'
if(!(Test-Path -LiteralPath $f -PathType Leaf)){Invoke-WebRequest -Uri $u -OutFile $f -ErrorAction Stop}
$hash=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
if($hash -ne '48380e3b72e53c5910642fbcf12932fe7255873022e8c050b95914f1820b159b'){throw 'HALT: installer SHA256 mismatch'}
& pwsh -NoLogo -NoProfile -STA -File $f
```

Once started, select **Rich files...** from the visible CoCopy palette. Select one or more local files, click **Stage ZIP**, and then explicitly choose **Copy ZIP file**, **Copy local reference**, or **Copy image pixels**. No automatic paste or external upload occurs. The local capsule stays in `D:\CoCivium\CoFarm\CoPayloadR1\capsules` until you decide how to retain or delete it.

To map a physical thumb button later, open Logitech Options+ for the *specific* MX Master 4 profile and manually assign its chosen button / Actions Ring slot to the generated `D:\CoCivium\CoFarm\CoMousePalette_R1\Open-CoCopy-R1.cmd`, preserving existing assignments and checking whether the slot is actually a middle button. Do not make this system-wide until a physical canary demonstrates the desired behavior. Mouse activation remains OPTIONAL; the palette can be launched without a special button.

**What it does not do:** install a global hook, monitor all I/O, read a private clipboard without a click, auto-upload a media file, grant permissions to an AI, remove paid accounts, or make every model context limitless. Reconnect Desktop Commander separately if you want verified remote X2 activity.
