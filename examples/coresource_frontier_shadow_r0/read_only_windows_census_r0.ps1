#Requires -Version 7.0
<#
.SYNOPSIS
  Single-shot, read-only Windows pressure census (CoResourceFrontier R0).
.DESCRIPTION
  Outputs one JSON report. Defaults to STDOUT only. Does not inspect window text,
  clipboard, browser tabs or secrets; does not kill/change/process/start a daemon.
  CPU seconds below are PROCESS LIFETIME totals, not current CPU utilization.
  Use -SavePrivate -OutputDirectory PATH only for opt-in append-only private files.
#>
[CmdletBinding()]
param(
    [switch] $SavePrivate,
    [string] $OutputDirectory = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($SavePrivate -and [string]::IsNullOrWhiteSpace($OutputDirectory)) {
    throw 'SAVE_REQUIRES_EXPLICIT_OUTPUT_DIRECTORY'
}
if ((-not $SavePrivate) -and (-not [string]::IsNullOrWhiteSpace($OutputDirectory))) {
    throw 'OUTPUT_DIRECTORY_REQUIRES_SAVE_PRIVATE'
}
function AsMib([long] $bytes) {
    return [math]::Round([double]$bytes / 1MB, 1)
}

# A bounded metadata snapshot. No CIM process command lines, filenames or window titles.
$all = @(Get-Process -ErrorAction Stop)
$processes = @($all | Sort-Object -Property WorkingSet64 -Descending | Select-Object -First 12 | ForEach-Object {
    $cpuTotal = $null
    try { if ($null -ne $_.CPU) { $cpuTotal = [math]::Round([double]$_.CPU, 1) } } catch { }
    [ordered]@{
        process_name = [string]$_.ProcessName
        pid = [int]$_.Id
        working_set_mib = AsMib ([long]$_.WorkingSet64)
        cpu_lifetime_seconds = $cpuTotal
    }
})
$browser = @('msedge','chrome','firefox','brave','vivaldi','opera','webkit')
$counts = [ordered]@{}
foreach ($b in $browser) {
    $count = @($all | Where-Object { $_.ProcessName -ieq $b }).Count
    if ($count -gt 0) { $counts[$b] = [int]$count }
}
$mem = [ordered]@{ total_mib = $null; available_mib = $null; source = 'NOT_MEASURED' }
try {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
    $mem.total_mib = [math]::Round(([double]$os.TotalVisibleMemorySize) / 1024, 1)
    $mem.available_mib = [math]::Round(([double]$os.FreePhysicalMemory) / 1024, 1)
    $mem.source = 'WINDOWS_CIM_INSTANTANEOUS'
} catch {
    $mem.source = 'CIM_UNAVAILABLE_NOT_ZERO'
}
$volumes = @()
try {
    $volumes = @(Get-PSDrive -PSProvider FileSystem | Where-Object {
        $_.Name -match '^[A-Za-z]$' -and $null -ne $_.Free
    } | Sort-Object -Property Name | ForEach-Object {
        [ordered]@{ drive = [string]$_.Name; free_mib = AsMib ([long]$_.Free) }
    })
} catch { $volumes = @() }
$report = [ordered]@{
    schema = 'CoAll.CoResourceFrontier.WindowsReadOnlyCensus.R0'
    observed_at_utc = [datetime]::UtcNow.ToString('o')
    privacy = 'PRIVATE_LOCAL'
    host_identity = 'OMITTED_BY_DEFAULT'
    sample_kind = 'ONE_INSTANT_NOT_CPU_PERCENT_OR_LONGITUDINAL_DIAGNOSIS'
    logical_processors = [Environment]::ProcessorCount
    process_count = [int]$all.Count
    browser_process_counts = $counts
    memory = $mem
    top_working_set_processes = $processes
    drive_free = $volumes
    effects = [ordered]@{ processes_terminated = 0; device_changes = 0; startup_changes = 0; network_calls = 0; hidden_daemons = 0 }
    limits = @(
        'NO_INFERENCE_OF_FOREGROUND_WINDOW_VISIBILITY',
        'NO_INFERENCE_OF_PROCESS_CPU_PERCENT',
        'ONE_SAMPLE_NE_PERFORMANCE_ROOT_CAUSE',
        'THIS_REPORT_DOES_NOT_INFER_REMOTE_BRIDGE_HEALTH',
        'PROCESS_METADATA_MAY_BE_PRIVATE_DO_NOT_PUBLICIZE'
    )
}
$json = ConvertTo-Json -InputObject $report -Depth 6 -Compress
if ($SavePrivate) {
    if (-not (Test-Path -LiteralPath $OutputDirectory -PathType Container)) {
        [void](New-Item -ItemType Directory -Path $OutputDirectory -Force)
    }
    $dest = Join-Path -Path $OutputDirectory -ChildPath ('CoResourceCensus_' + [datetime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ') + '_' + [guid]::NewGuid().ToString('N') + '.json')
    # New GUID filename + no overwrite, append-only; no deletion, process or registry writes.
    $stream = [System.IO.File]::Open($dest, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
        $stream.Write($bytes, 0, $bytes.Length)
    } finally {
        $stream.Dispose()
    }
    # The only output is path+hash to keep process metadata out of terminal histories.
    $digest = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{ state = 'PRIVATE_LOCAL_NEW_FILE_ONLY'; path = $dest; sha256 = $digest } | ConvertTo-Json -Compress
} else {
    Write-Output $json
}
