# CoSurface R0 portable visual canary. Does not install, replace, supervise, or start R5.
# Place this file beside index.html. Run explicitly in PowerShell 7 on the target machine.
[CmdletBinding()]
param([switch]$NoLaunch)
$ErrorActionPreference = 'Stop'
$index = Join-Path $PSScriptRoot 'index.html'
if (-not (Test-Path -LiteralPath $index -PathType Leaf)) {
    throw 'CoSurface HOLD: index.html must be beside preview.ps1; no network or automatic download.'
}
$html = [IO.File]::ReadAllText($index)
foreach ($required in @('id="r5-rail"', 'id="orb"', 'id="workspace" hidden', 'NO LIVE EFFECT')) {
    if (-not $html.Contains($required)) {
        throw "CoSurface HOLD: required local UI contract is missing: $required"
    }
}
$sha = (Get-FileHash -LiteralPath $index -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "COSURFACE_PREVIEW_ONLY SHA256=$sha"
Write-Output "NO_INSTALL=TRUE NO_AUTOSTART=TRUE R5_UNCHANGED=TRUE"
if ($NoLaunch) { return }
$uri = [Uri]::new((Resolve-Path -LiteralPath $index).Path).AbsoluteUri
# Open the existing default browser through the OS file association.
# Explicit launch, not an unattended service, replacement shell, or background worker.
Start-Process -FilePath $uri
Write-Output 'PREVIEW_LAUNCH_ATTEMPTED (browser render and user acceptance not verified)'
