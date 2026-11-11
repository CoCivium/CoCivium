# CoRunnerStartupInventory R0: read-only current-user startup diagnostics.
# No task/process/registry writes, no network, no credential or raw commandline output.
# GitHub CI is only a synthetic host check; running this on CI is NOT X2 evidence.
[CmdletBinding()]
param([switch]$SelfTest)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-SafeLabel([string]$Label) {
    if ($Label -match '(?i)(coall|cocivium|rickbar|cobar|coorb|costead|cofarm|costel|corunner)') {
        return $Label.Substring(0, [Math]::Min($Label.Length, 100))
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Label)
    $hash = [System.Security.Cryptography.SHA256]::HashData($bytes)
    return 'other-sha256-' + [Convert]::ToHexString($hash).Substring(0, 16).ToLowerInvariant()
}

function Get-LaunchHint([string]$Executable, [string]$Arguments) {
    $leaf = [IO.Path]::GetFileName($Executable).ToLowerInvariant()
    $kind = switch -Regex ($leaf) {
        '^pwsh(\.exe)?$' { 'POWERSHELL7'; break }
        '^powershell(\.exe)?$' { 'WINDOWS_POWERSHELL'; break }
        '^cmd(\.exe)?$' { 'CMD'; break }
        '^pythonw(\.exe)?$' { 'PYTHONW'; break }
        '^python(\.exe)?$' { 'PYTHON'; break }
        '^[wc]script(\.exe)?$' { 'WSH'; break }
        default { 'OTHER' }
    }
    $hiddenFlag = $Arguments -match '(?i)(?:^|\s)-(?:windowstyle\s+hidden|w\s+hidden)(?:\s|$)'
    $console = $kind -in @('POWERSHELL7','WINDOWS_POWERSHELL','CMD','PYTHON')
    $risk = if ($console -and -not $hiddenFlag) {
        'POSSIBLE_CONSOLE_WINDOW_UNPROVEN'
    } else {
        'WINDOW_VISIBILITY_UNPROVEN'
    }
    return [pscustomobject]@{
        launcher_class = $kind
        hidden_window_argument_present = [bool]$hiddenFlag
        window_risk = $risk
    }
}

if ($SelfTest) {
    $plain = Get-LaunchHint 'pwsh.exe' '-NoProfile -File C:\Private\DO_NOT_OUTPUT.ps1 -Token secret'
    $hidden = Get-LaunchHint 'pwsh.exe' '-NoProfile -WindowStyle Hidden -File x.ps1'
    $py = Get-LaunchHint 'pythonw.exe' 'x.py'
    $safe = Get-SafeLabel 'Unrelated task with private details'
    if ($plain.window_risk -ne 'POSSIBLE_CONSOLE_WINDOW_UNPROVEN' -or
        $hidden.hidden_window_argument_present -ne $true -or
        $hidden.window_risk -ne 'WINDOW_VISIBILITY_UNPROVEN' -or
        $py.launcher_class -ne 'PYTHONW' -or
        $safe -notmatch '^other-sha256-[0-9a-f]{16}$') {
        throw 'SELFTEST_FAILED'
    }
    [pscustomobject]@{
        schema = 'CoAll.CoRunnerStartupInventory.R0'
        state = 'SYNTHETIC_CLASSIFIER_PASS'
        windows_host_observed = $false
        x2_host_observed = $false
        raw_arguments_emitted = $false
    } | ConvertTo-Json -Compress
    exit 0
}
if ($env:OS -ne 'Windows_NT') {
    throw 'HOLD_WINDOWS_HOST_REQUIRED'
}

$errors = [System.Collections.Generic.List[string]]::new()
$tasks = [System.Collections.Generic.List[object]]::new()
$runEntries = [System.Collections.Generic.List[object]]::new()
$startupFiles = [System.Collections.Generic.List[object]]::new()
$processes = [System.Collections.Generic.List[object]]::new()
$taskTotal = 0
try {
    # This only inventories task metadata and action launch flags. It cannot
    # identify the initiating task for a visible popup without a runtime trace.
    foreach ($task in @(Get-ScheduledTask -ErrorAction Stop)) {
        if ($taskTotal -ge 1500) {
            $errors.Add('TASK_LIST_BOUNDED_AT_1500')
            break
        }
        $taskTotal += 1
        foreach ($action in @($task.Actions)) {
            $exe = [string]$action.Execute
            $argsText = [string]$action.Arguments
            $hint = Get-LaunchHint $exe $argsText
            $name = [string]$task.TaskPath + [string]$task.TaskName
            $relevant = $name -match '(?i)(coall|cocivium|rickbar|cobar|coorb|costead|cofarm|costel|corunner)'
            if (-not $relevant -and $hint.launcher_class -notin @('POWERSHELL7','WINDOWS_POWERSHELL','CMD','PYTHON')) {
                continue
            }
            $triggers = @($task.Triggers | ForEach-Object {
                [string]$_.CimClass.CimClassName
            })
            $tasks.Add([pscustomobject]@{
                task_identity = Get-SafeLabel $name
                launcher_class = $hint.launcher_class
                hidden_window_argument_present = $hint.hidden_window_argument_present
                window_risk = $hint.window_risk
                task_hidden_setting = [bool]$task.Settings.Hidden
                has_logon_trigger = [bool](@($triggers | Where-Object { $_ -match 'Logon' }).Count)
                has_boot_trigger = [bool](@($triggers | Where-Object { $_ -match 'Boot' }).Count)
            })
            if ($tasks.Count -ge 250) {
                $errors.Add('MATCHED_TASKS_BOUNDED_AT_250')
                break
            }
        }
        if ($tasks.Count -ge 250) { break }
    }
} catch { $errors.Add('TASK_READ_UNAVAILABLE') }

foreach ($keyPath in @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
)) {
    try {
        if (-not (Test-Path -LiteralPath $keyPath)) { continue }
        $values = Get-ItemProperty -LiteralPath $keyPath -ErrorAction Stop
        foreach ($property in @($values.PSObject.Properties |
            Where-Object { $_.Name -notmatch '^PS(Path|ParentPath|ChildName|Drive|Provider)$' })) {
            if ($runEntries.Count -ge 100) {
                $errors.Add('RUN_ENTRIES_BOUNDED_AT_100')
                break
            }
            $valueText = [string]$property.Value
            $launcherClass = if ($valueText -match '(?i)pwsh(\.exe)?') {
                'POWERSHELL7'
            } elseif ($valueText -match '(?i)powershell(\.exe)?') {
                'WINDOWS_POWERSHELL'
            } elseif ($valueText -match '(?i)pythonw(\.exe)?') {
                'PYTHONW'
            } elseif ($valueText -match '(?i)coall|cocivium|rickbar|cobar|coorb') {
                'COALL_CANDIDATE'
            } else { 'OTHER' }
            $runEntries.Add([pscustomobject]@{
                hive = if ($keyPath -match '^HKCU:') { 'CURRENT_USER' } else { 'LOCAL_MACHINE' }
                value_identity = Get-SafeLabel ([string]$property.Name)
                launcher_class = $launcherClass
                raw_value_emitted = $false
            })
        }
    } catch { $errors.Add('RUN_KEY_READ_UNAVAILABLE') }
}
foreach ($kind in @('Startup','CommonStartup')) {
    try {
        $folder = [Environment]::GetFolderPath($kind)
        if (-not $folder -or -not (Test-Path -LiteralPath $folder)) { continue }
        foreach ($file in @(Get-ChildItem -LiteralPath $folder -File -ErrorAction Stop | Select-Object -First 80)) {
            $startupFiles.Add([pscustomobject]@{
                scope = $kind
                item_identity = Get-SafeLabel $file.Name
                extension = $file.Extension.ToLowerInvariant()
                shortcut_target_uninspected = $true
            })
        }
    } catch { $errors.Add('STARTUP_FOLDER_READ_UNAVAILABLE') }
}
try {
    foreach ($p in @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop)) {
        $name = [string]$p.Name
        if ($name -notmatch '(?i)^(pwsh|powershell|cmd|pythonw?|wscript|cscript|conhost|coall\w*)\.exe$') {
            continue
        }
        $processes.Add([pscustomobject]@{
            process_id = [int]$p.ProcessId
            parent_process_id = [int]$p.ParentProcessId
            process_class = (Get-LaunchHint $name '').launcher_class
            process_name = $name
            window_visibility = 'NOT_OBSERVED'
            command_line = 'REDACTED_NOT_EMITTED'
        })
        if ($processes.Count -ge 200) {
            $errors.Add('PROCESS_LIST_BOUNDED_AT_200')
            break
        }
    }
} catch { $errors.Add('PROCESS_READ_UNAVAILABLE') }

$report = [ordered]@{
    schema = 'CoAll.CoRunnerStartupInventory.R0'
    state = 'READ_ONLY_LOCAL_WINDOWS_SNAPSHOT'
    observed_at_utc = [DateTime]::UtcNow.ToString('o')
    host_identity = 'LOCAL_UNATTESTED'
    x2_host_observed = $false
    observed_x2_executable_or_startup = 'NOT_ATTESTED'
    windows_interactive_session = 'NOT_ATTESTED'
    reboot_autostart_success = 'NOT_TESTED'
    manual_login_recovery = 'NOT_TESTED'
    visible_popup_attribution = 'NOT_TESTED'
    no_registry_or_task_writes = $true
    no_network_or_external_effect = $true
    raw_command_lines_emitted = $false
    credentials_or_tokens_emitted = $false
    scheduled_task_count_scanned = $taskTotal
    candidate_tasks = @($tasks.ToArray())
    run_entries = @($runEntries.ToArray())
    startup_folder_items = @($startupFiles.ToArray())
    process_candidates = @($processes.ToArray())
    observation_errors = @($errors.ToArray())
    nonclaims = @('TASK_EXISTS_NE_AUTOSTART_PROVEN','HIDDEN_FLAG_NE_NO_WINDOW_PROVEN',
        'PROCESS_EXISTS_NE_HEALTHY','BRIDGE_OFFLINE_NE_PC_OFF',
        'LOCAL_SNAPSHOT_NE_X2_ATTESTATION','NO_RECEIVER_ACK_OR_RUNTIME_REPAIR')
}
$report | ConvertTo-Json -Depth 6 -Compress
