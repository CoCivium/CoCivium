# CoRunnerStartupInventory R0: read-only current-user startup diagnostics.
# No task/process/registry writes, no network, no credential or raw commandline output.
# GitHub CI is only a synthetic host check; running this on CI is NOT X2 evidence.
[CmdletBinding()]
param([switch]$SelfTest)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-SafeLabel([string]$Label) {
    # Even CoAll task names may contain private paths, people or tokens.
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
        console_flash_possible = [bool]$console
    }
}

function Get-ProcessRole([string]$ProcessName) {
    # Process-name classes only; no command lines, paths, window titles, tokens or users.
    $n = $ProcessName.ToLowerInvariant()
    switch -Regex ($n) {
        '^(logioptionsplus(_agent|_updater)?|lghub(_agent|_updater)?|logitech\w*|razer\w*|steelseriesgg|icue|corsair\w*)\.exe$' {
            return 'MOUSE_UTILITY_CANDIDATE'
        }
        '^ollama(\w*)?\.exe$' { return 'LOCAL_MODEL_CANDIDATE' }
        '^(rickbar|cobar|coall|coorb|cospeedo|cocivium)[a-z0-9_-]*\.exe$' { return 'COALL_SURFACE_CANDIDATE' }
        default { return 'OTHER' }
    }
}

function Get-TaskActionCandidate([string]$TaskName, [string]$ActionName, [string]$InstanceId) {
    # Opaque scheduler correlation only. No window attribution or raw task details.
    if ([string]::IsNullOrWhiteSpace($TaskName) -or [string]::IsNullOrWhiteSpace($ActionName)) { return $null }
    $kind = (Get-LaunchHint $ActionName '').launcher_class
    if ($kind -notin @('POWERSHELL7','WINDOWS_POWERSHELL','CMD','PYTHON')) { return $null }
    $taskRef = Get-SafeLabel ($TaskName + '|' + $kind)
    $instanceRef = if ([string]::IsNullOrWhiteSpace($InstanceId)) { $null } else { Get-SafeLabel ($TaskName + '|' + $InstanceId + '|' + $kind) }
    return [pscustomobject]@{
        task_identity = $taskRef
        launcher_class = $kind
        task_category = if ($TaskName -match '(?i)(coall|cocivium|rickbar|cobar|coorb|costead|cofarm|costel|corunner|cospeedo)') { 'COALL_RELATED_CANDIDATE' } else { 'UNRELATED_OR_UNKNOWN' }
        instance_correlation_ref = $instanceRef
        visible_popup = 'NOT_OBSERVED'
    }
}

if ($SelfTest) {
    $plain = Get-LaunchHint 'pwsh.exe' '-NoProfile -File C:\Private\DO_NOT_OUTPUT.ps1 -Token secret'
    $hidden = Get-LaunchHint 'pwsh.exe' '-NoProfile -WindowStyle Hidden -File x.ps1'
    $py = Get-LaunchHint 'pythonw.exe' 'x.py'
    $safe = Get-SafeLabel 'Unrelated task with private details'
    $safeCoAll = Get-SafeLabel 'CoAll PRIVATE_PERSON_DO_NOT_ECHO'
    $mouseRole = Get-ProcessRole 'logioptionsplus_agent.exe'
    $localModelRole = Get-ProcessRole 'ollama.exe'
    $coallRole = Get-ProcessRole 'CoAllDesktop.exe'
    $ordinaryRole = Get-ProcessRole 'browser.exe'
    $eventProbe = Get-TaskActionCandidate '\CoAll\PRIVATE_PERSON_DO_NOT_ECHO' 'C:\Program Files\PowerShell\7\pwsh.exe' '{PRIVATE_GUID}'
    $eventOther = Get-TaskActionCandidate '\Other\Private' 'wscript.exe' '{PRIVATE_GUID}'
    if ($plain.window_risk -ne 'POSSIBLE_CONSOLE_WINDOW_UNPROVEN' -or
        $hidden.hidden_window_argument_present -ne $true -or
        $hidden.window_risk -ne 'WINDOW_VISIBILITY_UNPROVEN' -or
        $py.launcher_class -ne 'PYTHONW' -or
        $safe -notmatch '^other-sha256-[0-9a-f]{16}$' -or
        $safeCoAll -notmatch '^other-sha256-[0-9a-f]{16}$' -or
        $hidden.console_flash_possible -ne $true -or
        $mouseRole -ne 'MOUSE_UTILITY_CANDIDATE' -or
        $localModelRole -ne 'LOCAL_MODEL_CANDIDATE' -or
        $coallRole -ne 'COALL_SURFACE_CANDIDATE' -or
        $ordinaryRole -ne 'OTHER' -or
        $eventProbe.launcher_class -ne 'POWERSHELL7' -or
        $eventProbe.task_category -ne 'COALL_RELATED_CANDIDATE' -or
        $eventProbe.task_identity -notmatch '^other-sha256-[0-9a-f]{16}$' -or
        $eventProbe.instance_correlation_ref -notmatch '^other-sha256-[0-9a-f]{16}$' -or
        $null -ne $eventOther) {
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
$processRoles = [System.Collections.Generic.List[object]]::new()
$audioServices = [System.Collections.Generic.List[object]]::new()
$displayDriverModes = [System.Collections.Generic.List[object]]::new()
$bootUtc = $null
$uptimeSeconds = $null
$taskTotal = 0
try {
    $osRecord = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
    $bootDate = ([DateTime]$osRecord.LastBootUpTime).ToUniversalTime()
    if ($bootDate.Year -lt 2020 -or $bootDate -gt [DateTime]::UtcNow) {
        $errors.Add('BOOT_TIME_INCONSISTENT')
    } else {
        $bootUtc = $bootDate.ToString('o')
        $uptimeSeconds = [int][Math]::Floor(([DateTime]::UtcNow - $bootDate).TotalSeconds)
    }
} catch { $errors.Add('BOOT_TIME_READ_UNAVAILABLE') }

foreach ($serviceName in @('Audiosrv','AudioEndpointBuilder')) {
    try {
        $svc = Get-Service -Name $serviceName -ErrorAction Stop
        $audioServices.Add([pscustomobject]@{
            service_role = $serviceName
            status = if ($svc.Status -eq 'Running') { 'RUNNING' } else { 'NOT_RUNNING' }
            actual_mute_state = 'NOT_OBSERVED'
        })
    } catch {
        $audioServices.Add([pscustomobject]@{
            service_role = $serviceName
            status = 'NOT_OBSERVED'
            actual_mute_state = 'NOT_OBSERVED'
        })
        $errors.Add('AUDIO_SERVICE_READ_UNAVAILABLE')
    }
}
try {
    foreach ($adapter in @(Get-CimInstance -ClassName Win32_VideoController -ErrorAction Stop | Select-Object -First 8)) {
        $w = [int]$adapter.CurrentHorizontalResolution
        $h = [int]$adapter.CurrentVerticalResolution
        if ($w -gt 0 -and $h -gt 0) {
            $displayDriverModes.Add([pscustomobject]@{
                width_px = $w
                height_px = $h
                evidence = 'VIDEO_DRIVER_REPORTED_NOT_PER_MONITOR_DPI_OR_UI_GEOMETRY'
            })
        }
    }
} catch { $errors.Add('DISPLAY_DRIVER_READ_UNAVAILABLE') }

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
        $role = Get-ProcessRole $name
        if ($role -ne 'OTHER' -and $processRoles.Count -lt 80) {
            $processRoles.Add([pscustomobject]@{
                process_role = $role
                process_name = $name
                evidence = 'PROCESS_NAME_PRESENT_NOT_HEALTH_OR_AUTOSTART_PROOF'
            })
        }
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
    boot_time_utc = $bootUtc
    uptime_seconds_at_observation = $uptimeSeconds
    audio_service_readback = @($audioServices.ToArray())
    audio_muted_state = 'NOT_OBSERVED'
    peripheral_utility_process_candidates = @($processRoles.ToArray())
    display_driver_modes = @($displayDriverModes.ToArray())
    per_monitor_dpi = 'NOT_OBSERVED'
    owned_desktop_background = 'NOT_OBSERVED'
    surface_alignment_and_scale = 'NOT_OBSERVED'
    post_login_restoration_state = 'NOT_ATTESTED'
    visible_ui_screenshot_accepted = $false
    observation_errors = @($errors.ToArray())
    nonclaims = @('TASK_EXISTS_NE_AUTOSTART_PROVEN','HIDDEN_FLAG_NE_NO_WINDOW_PROVEN',
        'PROCESS_EXISTS_NE_HEALTHY','BRIDGE_OFFLINE_NE_PC_OFF',
        'LOCAL_SNAPSHOT_NE_X2_ATTESTATION','NO_RECEIVER_ACK_OR_RUNTIME_REPAIR',
        'AUDIO_SERVICE_RUNNING_NE_AUDIO_UNMUTED',
        'MOUSE_PROCESS_PRESENT_NE_MOUSE_MAPPING_READY',
        'DISPLAY_DRIVER_MODE_NE_PER_MONITOR_DPI_OR_LAYOUT',
        'BOOT_TIME_NE_POST_LOGIN_RESTORATION',
        'WALLPAPER_VISIBLE_NE_COCIVIUM_OWNED_SURFACE')
}
$report | ConvertTo-Json -Depth 6 -Compress
