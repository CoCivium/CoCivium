# CoRunnerPopupObserver R0 | READ-ONLY LOCAL DIAGNOSTIC
# Purpose: identify possible PowerShell popup owners without launching, stopping,
# altering tasks, changing startup, reading private command arguments or opening UI.
# Run only from an existing PowerShell terminal, not from an auto-start task.
[CmdletBinding()]
param([int]$MaxItems = 200)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($MaxItems -lt 1 -or $MaxItems -gt 1000) { throw 'MaxItems must be between 1 and 1000.' }
$script:Warnings = [System.Collections.Generic.List[string]]::new()
function BaseName([string]$Raw) {
    if ([string]::IsNullOrWhiteSpace($Raw)) { return '(unknown)' }
    $trim = $Raw.Trim().Trim('"')
    # Only the executable's basename; never retain full paths or arguments.
    return [System.IO.Path]::GetFileName($trim).ToLowerInvariant()
}
# One-time foreground PID sample; no title, screen content, hooks or polling.
# Running from a terminal may foreground the terminal itself. This is a clue,
# never attribution without independent window/process correlation.
$foreground = [ordered]@{ pid = $null; sampled_utc = [datetime]::UtcNow.ToString('o'); reliability = 'UNKNOWN' }
try {
    if (-not ('CoRunnerForegroundProbeR0' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CoRunnerForegroundProbeR0 {
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
}
'@
    }
    $hwnd = [CoRunnerForegroundProbeR0]::GetForegroundWindow()
    if ($hwnd -ne [IntPtr]::Zero) {
        [uint32]$foregroundPid = 0
        [void][CoRunnerForegroundProbeR0]::GetWindowThreadProcessId($hwnd, [ref]$foregroundPid)
        if ($foregroundPid -gt 0) {
            $foreground.pid = [int]$foregroundPid
            $foreground.reliability = 'ONE_INSTANT_NOT_POPUP_ATTRIBUTION'
        }
    }
} catch { $script:Warnings.Add('Foreground PID unavailable in this context.') }
$processes = @()
try {
    $cim = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Where-Object { $_.Name -in @('pwsh.exe','powershell.exe','conhost.exe','WindowsTerminal.exe','wt.exe','cmd.exe','wscript.exe','cscript.exe') } |
        Select-Object -First $MaxItems)
    $windowByPid = @{}
    try {
        Get-Process -ErrorAction Stop | ForEach-Object {
            $windowByPid[[int]$_.Id] = ([int64]$_.MainWindowHandle -ne 0)
        }
    } catch { $script:Warnings.Add('Process window handles partially unavailable.') }
    foreach ($p in $cim) {
        $pidValue = [int]$p.ProcessId
        $visible = if ($windowByPid.ContainsKey($pidValue)) { [bool]$windowByPid[$pidValue] } else { $null }
        $processes += [ordered]@{
            pid = $pidValue
            parent_pid = [int]$p.ParentProcessId
            executable = BaseName ([string]$p.Name)
            has_main_window = $visible
            started_utc = if ($p.CreationDate) { ([datetime]$p.CreationDate).ToUniversalTime().ToString('o') } else { $null }
            # CommandLine deliberately excluded; it can hold secrets or private paths.
        }
    }
} catch { $script:Warnings.Add('Process inventory unavailable to current user.') }
$tasks = @()
try {
    $registered = @(Get-ScheduledTask -ErrorAction Stop | Select-Object -First $MaxItems)
    foreach ($task in $registered) {
        foreach ($action in @($task.Actions)) {
            $exe = BaseName ([string]$action.Execute)
            if ($exe -notin @('pwsh.exe','powershell.exe','cmd.exe','wscript.exe','cscript.exe','wt.exe','python.exe','pythonw.exe')) { continue }
            $arg = [string]$action.Arguments
            $explicitHidden = [bool]($arg -match '(?i)(?:-|/)windowstyle\s+hidden|(?:-|/)w\s+hidden')
            $nonInteractive = [bool]($arg -match '(?i)(?:-|/)noninteractive\b')
            $backgroundCapable = $exe -in @('pythonw.exe','wscript.exe')
            $tasks += [ordered]@{
                # Local task names retained for owner diagnosis; output must stay local.
                task_path = [string]$task.TaskPath
                task_name = [string]$task.TaskName
                executable = $exe
                explicitly_hidden = $explicitHidden
                noninteractive = $nonInteractive
                possible_foreground_console = (-not $explicitHidden -and -not $backgroundCapable)
                enabled = ([string]$task.State -ne 'Disabled')
                # Arguments and other private details deliberately excluded.
            }
        }
    }
} catch { $script:Warnings.Add('Scheduled task inventory unavailable; no changes performed.') }
$report = [ordered]@{
    schema = 'CoRunner.PopupOriginObservation.R0'
    observed_utc = [datetime]::UtcNow.ToString('o')
    scope = 'LOCAL_READ_ONLY_SAMPLE_NOT_COMPLETE_RUNNER_CENSUS'
    host = 'LOCAL_ONLY_NOT_PUBLISHED'
    sampled_processes = $processes.Count
    sampled_power_related_tasks = $tasks.Count
    foreground_sample = $foreground
    processes = $processes
    task_candidates = $tasks
    warnings = @($script:Warnings)
    nonclaims = @(
        'FOREGROUND_SAMPLE_NE_POPUP_CAUSATION',
        'POSSIBLE_FOREGROUND_NE_ACTUAL_POPUP_CAUSATION',
        'PROCESS_PRESENT_NE_WINDOW_VISIBLE',
        'TASK_CONFIGURED_NE_TASK_EXECUTED',
        'NO_PROCESS_TERMINATED',
        'NO_TASK_DISABLED',
        'NO_AUTOSTART_CHANGED',
        'NO_REMOTE_RECEIVER_ACK'
    )
    next_proof = 'Correlate one real popup with PID/window ownership and task launch time before changing anything.'
}
$report | ConvertTo-Json -Depth 6
