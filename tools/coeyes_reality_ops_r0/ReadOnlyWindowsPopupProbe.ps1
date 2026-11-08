#requires -Version 7.0
<#
CoEyes+ / CoRunner+ R0 read-only local popup-owner inventory.
Do not install, schedule, restart, stop, hide, screenshot or mutate processes.
No command lines, task arguments, arbitrary filenames, window titles, or user data
are exported. Process/window ownership is only a bounded diagnostic hint.
#>
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$now = [DateTime]::UtcNow.ToString('o')
$allowed = @('pwsh.exe','powershell.exe','WindowsTerminal.exe',
             'OpenConsole.exe','conhost.exe','CoAllDesktop.exe','CoDesktop.exe')
$processes = @()
$processCoverage = 'READ_ATTEMPTED'
try {
    $rows = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Where-Object { $allowed -contains [string]$_.Name } |
        Sort-Object ProcessId | Select-Object -First 160)
    foreach ($row in $rows) {
        $visibleHint = $null
        try {
            $p = Get-Process -Id ([int]$row.ProcessId) -ErrorAction Stop
            $visibleHint = ([int64]$p.MainWindowHandle -ne 0)
        } catch { $visibleHint = $null }
        $created = $null
        try {
            if ($null -ne $row.CreationDate) {
                $created = ([DateTime]$row.CreationDate).ToUniversalTime().ToString('o')
            }
        } catch { $created = $null }
        $processes += [pscustomobject]@{
            name = [string]$row.Name
            pid = [int]$row.ProcessId
            parent_pid = [int]$row.ParentProcessId
            created_utc = $created
            main_window_handle_present_best_effort = $visibleHint
        }
    }
} catch {
    $processCoverage = 'UNAVAILABLE'
}
$tasks = @()
$taskCoverage = 'READ_ATTEMPTED'
try {
    foreach ($task in @(Get-ScheduledTask -ErrorAction Stop)) {
        foreach ($action in @($task.Actions)) {
            $bin = ''
            try { $bin = [IO.Path]::GetFileName([string]$action.Execute) } catch {}
            if ($bin -notin @('pwsh.exe','powershell.exe')) { continue }
            $key = ([string]$task.TaskPath + [string]$task.TaskName)
            $hashBytes = [System.Security.Cryptography.SHA256]::HashData(
                [System.Text.Encoding]::UTF8.GetBytes($key))
            $taskHash = [Convert]::ToHexString($hashBytes).ToLowerInvariant()
            $last = $null
            try {
                $info = Get-ScheduledTaskInfo -TaskName $task.TaskName -TaskPath $task.TaskPath -ErrorAction Stop
                if ($info.LastRunTime.Year -gt 2000) {
                    $last = ([DateTime]$info.LastRunTime).ToUniversalTime().ToString('o')
                }
            } catch { $last = $null }
            $tasks += [pscustomobject]@{
                task_name_sha256 = $taskHash
                launcher_basename = $bin
                last_run_utc_best_effort = $last
                state = [string]$task.State
                attribution = 'CANDIDATE_ONLY_NO_WINDOW_BINDING'
            }
        }
    }
} catch {
    $taskCoverage = 'UNAVAILABLE'
}
$out = [ordered]@{
    schema = 'CoAll.CoEyes.WindowsPopupOwnerProbe.R0.READONLY'
    observed_at_utc = $now
    rights = 'LOCAL_READ_ONLY_NO_INSTALL_NO_RESTART'
    scope = 'CONSOLE_PROCESS_FAMILY_AND_POWERSHELL_TASK_LAUNCHERS'
    process_coverage = $processCoverage
    task_coverage = $taskCoverage
    process_rows = @($processes)
    candidate_task_launchers = @($tasks | Select-Object -First 160)
    windows_user32_enumwindows_performed = $false
    observed_popup_owner = 'NOT_ESTABLISHED'
    co_desktop_runtime_healthy = 'NOT_ESTABLISHED'
    popup_effect_caused_by_task = 'NOT_ESTABLISHED'
    private_data_capture = 'NONE_REQUESTED'
    restart_attempts = 0
    next = 'CORRELATE_AN_AUTHORIZED_WINDOW_EVENT_TO_EXACT_PROCESS_AND_LAUNCHER_BEFORE_PATCH'
    nonclaims = @(
        'TASK_LIST_NE_POPUP_OWNER',
        'PROCESS_PRESENT_NE_RESPONSIVE',
        'MAIN_WINDOW_HANDLE_HINT_NE_COMPLETE_WINDOW_CENSUS',
        'POWERSHELL_HIDDEN_NE_NO_FLASH_GUARANTEE',
        'USER_REBOOT_NE_VERIFIED_CAUSAL_REPAIR',
        'LOCAL_PROBE_NE_AUTOMATED_DEPLOYMENT'
    )
}
$out | ConvertTo-Json -Depth 9
