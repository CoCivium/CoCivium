# CoMousePalette + CoPayload R1 | One-paste launch on X2

**Current X2 status:** Offline to Desktop Commander. This paste does not remap a physical button. It installs pinned, verified scripts in a new CoFarm folder and opens a visible palette only when you paste it into **your own PowerShell 7** session.

```powershell
$ErrorActionPreference = 'Stop'
$base = 'D:\CoCivium\CoFarm'
if (-not (Test-Path -LiteralPath $base -PathType Container)) { throw 'CoFarm missing' }
$dir = Join-Path $base 'CoMousePalette_R1'
[IO.Directory]::CreateDirectory($dir) | Out-Null
# A NEW filename keeps previously staged bootstrap versions intact.
$path = Join-Path $dir 'PASTE_ON_X2_R1_FIXED_4b3d6cf.ps1'
$url = 'https://raw.githubusercontent.com/CoCivium/CoCivium/4b3d6cfb202c68395917c5514ca042d7094ada15/experiments/comousepalette-r0/PASTE_ON_X2_R1.ps1'
$expected = '0a6a04e23f5d49b3c00b9c79138cd478a978572d333d59bf9305224c4a76ffbd'
if ([IO.Directory]::Exists($path)) { throw 'HALT_BOOTSTRAP_PATH_IS_DIRECTORY' }
if (-not [IO.File]::Exists($path)) {
    $temp = Join-Path $dir ('.download_' + [guid]::NewGuid().ToString('N'))
    try {
        Invoke-WebRequest -Uri $url -OutFile $temp -MaximumRedirection 3 -ErrorAction Stop
        if ((Get-FileHash -LiteralPath $temp -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expected) { throw 'HALT_DOWNLOADED_BOOTSTRAP_HASH_MISMATCH' }
        [IO.File]::Move($temp, $path) # Fail if another file appeared; no overwrite.
    } finally {
        if ([IO.File]::Exists($temp)) { [IO.File]::Delete($temp) }
    }
}
if (([IO.File]::GetAttributes($path) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'HALT_BOOTSTRAP_REPARSE_POINT' }
if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expected) { throw 'HALT_BOOTSTRAP_HASH_MISMATCH' }
& pwsh -NoLogo -NoProfile -STA -File $path
```

**Correction and source pin:** This uses the immutable `4b3d6cf` version, whose bootstrap checks the exact bytes of any existing `Open-CoCopy-R1.cmd` launcher. The older `1f1497e` installer did **not** check an existing launcher’s bytes. The new filename prevents silently overwriting that older bootstrap. Verified source SHA-256: `0a6a04e23f5d49b3c00b9c79138cd478a978572d333d59bf9305224c4a76ffbd`. The corrected installer’s Windows/Linux CI succeeded at [run 40158597769](https://github.com/CoCivium/CoCivium/actions/runs/40158597769). This is not X2 hardware acceptance.

Once started, select **Rich files...** from the visible CoCopy palette. Select one or more local files, click **Stage ZIP**, and then explicitly choose **Copy ZIP file**, **Copy local reference**, or **Copy image pixels**. No automatic paste or external upload occurs. The local capsule stays in `D:\CoCivium\CoFarm\CoPayloadR1\capsules` until you decide how to retain or delete it.

To map a physical thumb button later, open Logitech Options+ for the *specific* MX Master 4 profile and manually assign its chosen button / Actions Ring slot to the generated `D:\CoCivium\CoFarm\CoMousePalette_R1\Open-CoCopy-R1.cmd`, preserving existing assignments and checking whether the slot is actually a middle button. Do not make this system-wide until a physical canary demonstrates the desired behavior. Mouse activation remains OPTIONAL; the palette can be launched without a special button.

**What it does not do:** install a global hook, monitor all I/O, read a private clipboard without a click, auto-upload a media file, grant permissions to an AI, remove paid accounts, or make every model context limitless. Reconnect Desktop Commander separately if you want verified remote X2 activity.
