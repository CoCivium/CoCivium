#requires -Version 7.0
<#
CoDevice Human-Time Pulse R0: a short, local-only device checkpoint.
Run locally: pwsh -NoProfile -File .\scripts\CoDeviceHumanTimePulseR0.ps1
Option: -OutputRoot D:\CoCivium\CoFarm\CoDevicePulse
No device enrollment, app launch, scheduled task, network access, or credential access.
#>
[CmdletBinding()]
param([string]$OutputRoot = '')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$timer = [System.Diagnostics.Stopwatch]::StartNew()
$utc = [DateTime]::UtcNow
if (-not $OutputRoot) {
  if (Test-Path -LiteralPath 'D:\CoCivium\CoFarm' -PathType Container) {
    $OutputRoot = 'D:\CoCivium\CoFarm\CoDevicePulse'
  } else {
    $OutputRoot = Join-Path $env:LOCALAPPDATA 'CoCivium\CoDevicePulse'
  }
}
$allPaths = @(
  @{ name='CoFarm'; path='D:\CoCivium\CoFarm' },
  @{ name='CoCiviumRoot'; path='D:\CoCivium' }
)
$checkedPaths = @($allPaths | ForEach-Object {
  @{ name=$_.name; observed=([bool](Test-Path -LiteralPath $_.path -PathType Container)) }
})
$programs = @('pwsh','git','ollama')
$commandStatus = @{}
foreach ($program in $programs) {
  $commandStatus[$program] = if (Get-Command -Name $program -ErrorAction SilentlyContinue) {
    'DISCOVERABLE_IN_PATH'
  } else {
    'NOT_OBSERVED_IN_PATH'
  }
}
# No paths, command lines, window titles, file contents, or credentials are collected.
$processGroups = [ordered]@{
  'RickBar_or_CoBar' = @('RickBar','CoBar')
  'Ollama' = @('ollama','ollama app')
  'DesktopCommander' = @('DesktopCommander','desktop-commander')
}
$processStatus = [ordered]@{}
foreach ($group in $processGroups.Keys) {
  $match = @(Get-Process -Name $processGroups[$group] -ErrorAction SilentlyContinue).Count -gt 0
  $processStatus[$group] = if ($match) { 'OBSERVED_PROCESS_NAME' } else { 'NOT_OBSERVED_THIS_CHECK' }
}
$home = 'Device snapshot captured locally. No device enrollment or service activation performed.'
$meaning = 'A named process is not proof that its user experience or receiver is working.'
$next = if ($processStatus['RickBar_or_CoBar'] -eq 'OBSERVED_PROCESS_NAME') {
  'Verify one visible RickBar/CoBar interaction on this device and record its result.'
} else {
  'Find the existing RickBar/CoBar executable through a separate, scoped inventory before any installation or launch.'
}
$scriptHash = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash
$receipt = [ordered]@{
  schema = 'CoDevice.HumanTimePulse.R0'
  state = 'BOUNDED_LOCAL_OBSERVATION_ONLY'
  observed_at_utc = $utc.ToString('o')
  host_name_local_only = $env:COMPUTERNAME
  platform = [System.Environment]::OSVersion.Platform.ToString()
  powershell_version = $PSVersionTable.PSVersion.ToString()
  source_script_sha256 = $scriptHash
  coverage = 'SELECTED_PATHS_COMMAND_NAMES_PROCESS_NAMES_ONLY'
  observed_path_presence = $checkedPaths
  command_discovery = $commandStatus
  process_name_observations = $processStatus
  here_now = $home
  meaning = $meaning
  next_safe_action = $next
  device_enrolled = $false
  external_receiver_ack = 'NOT_TESTED'
  stop_or_disconnect = 'Close the local HTML viewer; the scan is already finished and no persistent worker is created.'
  elapsed_ms = 0
  effects = [ordered]@{
    remote_provider_calls=0; service_changes=0; program_installs=0
    credentials_read=0; device_enrollments=0; internet_exposure_changes=0
    processes_started_by_pulse=0; existing_files_overwritten=0
  }
  nonclaims = @(
    'PROCESS_NAME_NE_RUNTIME_HEALTH','PATH_PRESENT_NE_SERVICE_WORKING',
    'ONE_DEVICE_NE_FLEET_CENSUS','LOCAL_OBSERVATION_NE_RECEIVER_ACK',
    'NO_SENSOR_CAMERA_MICROPHONE_OR_PRIVATE_FILE_SCAN',
    'NO_PROVIDER_NE_FLEET_SYNC'
  )
}
$run = $utc.ToString('yyyyMMddTHHmmssfffffffZ') + '_' + [Guid]::NewGuid().ToString('N')
[void][System.IO.Directory]::CreateDirectory($OutputRoot)
$runDir = Join-Path $OutputRoot ('Pulse_'+$run)
if (Test-Path -LiteralPath $runDir) { throw 'NO_CLOBBER_RUN_DIRECTORY_EXISTS' }
[void](New-Item -ItemType Directory -Path $runDir -ErrorAction Stop)
$receipt.elapsed_ms = $timer.ElapsedMilliseconds
$jsonPath = Join-Path $runDir 'device_pulse.json'
$htmlPath = Join-Path $runDir 'index.html'
$receipt | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $jsonPath -Encoding utf8NoBOM -NoNewline
function Escape([string]$value) { [System.Net.WebUtility]::HtmlEncode($value) }
function DisplayStatus([string]$key, [string]$value) {
  '<tr><th scope="row">' + (Escape $key) + '</th><td>' + (Escape $value) + '</td></tr>'
}
$tableRows = @(
  DisplayStatus 'RickBar / CoBar process' $processStatus['RickBar_or_CoBar']
  DisplayStatus 'Ollama process' $processStatus['Ollama']
  DisplayStatus 'Desktop Commander process name' $processStatus['DesktopCommander']
  DisplayStatus 'Local Ollama command' $commandStatus['ollama']
  DisplayStatus 'CoFarm directory' ([string]($checkedPaths | Where-Object name -eq 'CoFarm' | Select-Object -ExpandProperty observed))
)
$html = @"
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CoDevice | Here Now</title>
<style>
:root{font-family:system-ui,Arial,sans-serif;color-scheme:light dark}
body{max-width:760px;margin:2rem auto;padding:0 1rem;line-height:1.55}
main{display:grid;gap:1rem}
section{border:1px solid #8a8a8a;border-radius:12px;padding:1rem}
h1,h2{margin:.2em 0}.meta{font-size:.85rem}table{border-collapse:collapse;width:100%}
td,th{text-align:left;border-bottom:1px solid #999;padding:.55rem;vertical-align:top}
:focus-visible{outline:3px solid #277ac5}
</style></head><body><main>
<h1>CoDevice | Here Now</h1>
<p class="meta">Observed on $(Escape $utc.ToString('u')) | One local device only</p>
<section><h2>Here now</h2><p>$(Escape $home)</p></section>
<section><h2>Meaning</h2><p>$(Escape $meaning)</p></section>
<section><h2>Next safe action</h2><p>$(Escape $next)</p></section>
<section><h2>Evidence</h2><table><tbody>$($tableRows -join [Environment]::NewLine)</tbody></table>
<p class="meta">Source SHA-256: $(Escape $scriptHash)</p>
<p class="meta">No network requests, no installs, no device enrollment, no background agent.</p>
</section></main></body></html>
"@
[System.IO.File]::WriteAllText($htmlPath,$html,[System.Text.UTF8Encoding]::new($false))
$written = Get-Content -LiteralPath $jsonPath -Raw -Encoding utf8 | ConvertFrom-Json
if ($written.schema -cne $receipt.schema -or $written.source_script_sha256 -cne $scriptHash) {
  throw 'POST_WRITE_READBACK_FAILED'
}
Write-Output ('PASS_LOCAL_PULSE|RECEIPT=' + $jsonPath + '|VIEW=' + $htmlPath + '|ELAPSED_MS=' + $timer.ElapsedMilliseconds)
