# CoCopy+ Forest Green: one verified paste on X2

**Candidate only.** This code downloads a pinned, immutable public GitHub script into a new CoFarm filename, checks Git's exact blob hash twice, runs the Windows STA self-test, and opens **one visible** Forest-green window. It does not remap a mouse button, change wallpaper, persist a service, read clipboard silently, or send content anywhere.

Requirements: Windows, PowerShell 7 (`pwsh`), Git, existing `D:\CoCivium\CoFarm`, and internet access to GitHub. The existing CoMousePalette R1 scripts are not overwritten. The Rich files helper appears only if the prior R1 package is already installed alongside this script.

```powershell
$ErrorActionPreference='Stop'
$base='D:\CoCivium\CoFarm'
if (-not (Test-Path -LiteralPath $base -PathType Container)) { throw 'CoFarm is not present; stop.' }
$dir=Join-Path $base 'CoMousePalette_R1'
[IO.Directory]::CreateDirectory($dir) | Out-Null
$target=Join-Path $dir 'CoMousePalette_Green_R1_48bc4eb.ps1'
$raw='https://raw.githubusercontent.com/CoCivium/CoCivium/48bc4eb551691184d77f81f41a3be341ed795b8e/experiments/comousepalette-r0/CoMousePalette_R0.ps1'
$expected='539bd8239aa3a9996bcc6c624e0272d983aa49d3'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is required to verify the pinned source.' }
if ([IO.Directory]::Exists($target)) { throw 'Target is a directory, stopping.' }
if (-not [IO.File]::Exists($target)) {
    $temp=Join-Path $dir ('.download_'+[guid]::NewGuid().ToString('N'))
    try {
        Invoke-WebRequest -Uri $raw -OutFile $temp -MaximumRedirection 3 -ErrorAction Stop
        $check=(& git hash-object -- $temp).Trim().ToLowerInvariant()
        if ($LASTEXITCODE -ne 0 -or $check -cne $expected) { throw 'Source hash mismatch; nothing launched.' }
        [IO.File]::Move($temp,$target)
    } finally { if ([IO.File]::Exists($temp)) { [IO.File]::Delete($temp) } }
}
if (([IO.File]::GetAttributes($target) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Refusing a reparse point.' }
$check=(& git hash-object -- $target).Trim().ToLowerInvariant()
if ($LASTEXITCODE -ne 0 -or $check -cne $expected) { throw 'Pinned hash mismatch; no execution.' }
& pwsh -NoLogo -NoProfile -STA -File $target -SelfTest -Theme Forest
if ($LASTEXITCODE -ne 0) { throw 'Forest self-test failed; no GUI launched.' }
& pwsh -NoLogo -NoProfile -STA -File $target -Theme Forest
```

To use light green, change the final `-Theme Forest` to `-Theme Sage`; to use the untouched Windows colors, use `-Theme Classic`. The in-script Windows High Contrast fallback also forces Classic.

**Physical MX Master 4 gesture is NOT tested.** After verifying the visible window, an explicit Logitech Options+ per-app mapping could launch this file without replacing native middle-click or other existing macros. X2 Desktop Commander has not verified any installation.

The pinned script commit is `48bc4eb551691184d77f81f41a3be341ed795b8e`; the expected Git blob ID is `539bd8239aa3a9996bcc6c624e0272d983aa49d3`. A Git hash is source identity, not a code-signing certificate, vendor audit, or runtime security guarantee.

`COLOR_NE_AUTHORITY | COPY_NE_SEND | SOURCE_HASH_NE_PHYSICAL_TEST`
