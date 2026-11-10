#requires -Version 7.0
<#
CoStel Desktop Logon R0. Audit/Plan do not mutate Windows.
Install/Disable require explicit confirmation. Candidate source only.
No credentials, provider sessions, elevation, network or process launch.
#>
[CmdletBinding()]
param(
  [ValidateSet('Audit','Plan','Install','Disable')][string]$Mode='Audit',
  [string]$DesktopExe='',
  [string]$ExpectedSha256='',
  [switch]$ConfirmChange
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$TaskName = 'CoStel.CoAllDesktop.UserLogon.R0'
$TaskDescription='CoStel CoAll Desktop user logon task. Stop and rollback available.'
$CandidateRegex = '(?i)(CoAll.?Desktop|CoDesktop|RickBar|CoBar)'

function Hold([string]$Reason) { throw ('COSTEL_HOLD:' + $Reason) }

function Report([string]$State, [hashtable]$Extra=@{}) {
  $obj = [ordered]@{
    schema='CoAll.CoStel.WindowsLogon.R0'
    state=$State
    task_name=$TaskName
    mode=$Mode
    scope='CURRENT_USER_INTERACTIVE_LOGON_ONLY'
    credentials_read=$false
    provider_auth_modified=$false
    network_requests=0
    processes_started=0
    effects_verified=$false
    native_x2_acceptance='NOT_TESTED'
  }
  foreach($k in $Extra.Keys) { $obj[$k]=$Extra[$k] }
  Write-Output ($obj | ConvertTo-Json -Compress -Depth 5)
}

if (-not $IsWindows) { Hold 'WINDOWS_REQUIRED' }
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $identity.User) { Hold 'CURRENT_USER_SID_UNAVAILABLE' }
$user=$identity.Name
$sid=$identity.User.Value

function OwnedTask {
  $found=@(Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue)
  if ($found.Count -gt 1) { Hold 'DUPLICATE_NAMED_TASK' }
  if ($found.Count -eq 0) { return $null }
  return $found[0]
}

function CandidateCounts {
  $otherTasks=@(Get-ScheduledTask -ErrorAction Stop | Where-Object {
    $task=$_
    if ($task.TaskName -eq $TaskName) { return $false }
    # Inspect action executable PATH only, never action Arguments.
    # A generic task name must not hide a second CoAll startup owner.
    $matchesExe=@($task.Actions | Where-Object {
      $_.Execute -match '(?i)(CoCivium|CoAll.?Desktop|CoDesktop|RickBar|CoBar)'
    })
    return ($task.TaskName -match $CandidateRegex -or $matchesExe.Count -gt 0)
  })
  $startupDir=Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
  $shortcuts=@()
  if (Test-Path -LiteralPath $startupDir) {
    $shortcuts=@(Get-ChildItem -LiteralPath $startupDir -File -ErrorAction Stop |
      Where-Object { $_.Name -match $CandidateRegex })
  }
  $runNames=@()
  # Enumerate value NAMES only. Never load a Run value that might contain
  # a secret-bearing command argument. Name-based detection is PARTIAL.
  $runKey=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey(
    'Software\Microsoft\Windows\CurrentVersion\Run', $false)
  if ($null -ne $runKey) {
    try {
      $runNames=@($runKey.GetValueNames() | Where-Object {
        $_ -match $CandidateRegex
      })
    } finally {
      $runKey.Close()
    }
  }
  return @{
    task_count=$otherTasks.Count
    shortcut_count=$shortcuts.Count
    run_count=$runNames.Count
    total=$otherTasks.Count+$shortcuts.Count+$runNames.Count
  }
}

function VerifyExecutable {
  if (-not $DesktopExe) { Hold 'EXE_PATH_REQUIRED' }
  if ($DesktopExe -match '^\\\\') { Hold 'UNC_OR_NETWORK_EXECUTABLE_FORBIDDEN' }
  if (-not [IO.Path]::IsPathFullyQualified($DesktopExe)) {
    Hold 'ABSOLUTE_EXECUTABLE_PATH_REQUIRED'
  }
  if (-not (Test-Path -LiteralPath $DesktopExe -PathType Leaf)) {
    Hold 'EXECUTABLE_NOT_FOUND'
  }
  $file=Get-Item -LiteralPath $DesktopExe -ErrorAction Stop
  if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    Hold 'REPARSE_POINT_EXECUTABLE_FORBIDDEN'
  }
  if ($file.Extension -ine '.exe') { Hold 'EXE_ONLY_NO_SCRIPT_SPAWNER' }
  if ($ExpectedSha256 -cnotmatch '^[0-9A-Fa-f]{64}$') {
    Hold 'EXPECTED_SHA256_REQUIRED'
  }
  $sha=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256 -ErrorAction Stop).Hash
  if ($sha -ine $ExpectedSha256) { Hold 'EXECUTABLE_HASH_MISMATCH' }
  return @{ path=$file.FullName; sha256=$sha.ToLowerInvariant() }
}

function SameTask([object]$Task,[string]$Path) {
  if (-not $Task) { return $false }
  $actions=@($Task.Actions)
  $triggers=@($Task.Triggers)
  if ($actions.Count -ne 1 -or $triggers.Count -ne 1) { return $false }
  if ($actions[0].Arguments) { return $false }
  if ([IO.Path]::GetFullPath($actions[0].Execute) -ine [IO.Path]::GetFullPath($Path)) {
    return $false
  }
  if ($triggers[0].CimClass.CimClassName -ne 'MSFT_TaskLogonTrigger') { return $false }
  if ($Task.Principal.LogonType -ne 'Interactive') { return $false }
  if ($Task.Principal.RunLevel -ne 'Limited') { return $false }
  if ($Task.Principal.UserId -notin @($user,$sid)) { return $false }
  return $true
}

$existing=OwnedTask
$counts=CandidateCounts
if ($Mode -eq 'Audit') {
  $enabled=$false
  if ($existing) { $enabled=($existing.State -ne 'Disabled') }
  Report 'READ_ONLY_OBSERVATION__NOT_UI_HEALTH' @{
    task_present=($null -ne $existing)
    task_enabled=$enabled
    other_matching_tasks=$counts.task_count
    startup_shortcuts=$counts.shortcut_count
    hkcu_run_names=$counts.run_count
    executable_identity='NOT_INSPECTED'
    startup_scan_coverage='TASK_NAME_OR_EXECUTABLE__RUN_AND_SHORTCUT_NAMES_ONLY__ARGUMENTS_NOT_SCANNED'
    provider_session_status='NOT_INSPECTED'
    user_reauth_cause='NOT_DETERMINED'
  }
  exit 0
}
if ($Mode -eq 'Disable') {
  if (-not $ConfirmChange) { Hold 'EXPLICIT_CONFIRMATION_REQUIRED' }
  if (-not $existing) {
    Report 'NO_OWNED_TASK_TO_DISABLE' @{task_present=$false}
    exit 0
  }
  if ($existing.Principal.UserId -notin @($user,$sid)) {
    Hold 'FOREIGN_TASK_OWNER'
  }
  if ($existing.Description -ne $TaskDescription) {
    Hold 'UNRECOGNIZED_TASK_PROVENANCE'
  }
  Disable-ScheduledTask -TaskName $TaskName -ErrorAction Stop | Out-Null
  Report 'OWN_TASK_DISABLED__RUNNING_APP_NOT_TERMINATED' @{
    task_present=$true
    task_enabled=$false
    os_registration_mutation=1
  }
  exit 0
}
$verified=VerifyExecutable
if ($existing) {
  if (-not (SameTask $existing $verified.path)) {
    Hold 'EXISTING_TASK_DIFFERENT__NO_CLOBBER'
  }
  Report 'MATCHING_TASK_ALREADY_REGISTERED__RUNTIME_UNPROVEN' @{
    task_present=$true
    task_enabled=($existing.State -ne 'Disabled')
    exe_sha256=$verified.sha256
    other_matching_tasks=$counts.task_count
  }
  exit 0
}
if ($counts.total -gt 0) {
  Hold 'OTHER_DESKTOP_STARTUP_OWNERS_EXIST__RECONCILE_FIRST'
}
if ($Mode -eq 'Plan') {
  Report 'PLAN_ONLY__NO_STARTUP_MUTATION' @{
    task_present=$false
    exe_sha256=$verified.sha256
    proposed_trigger='CURRENT_USER_LOGON'
    proposed_run_level='LIMITED'
    proposed_restart_attempts=1
    rollback='DISABLE_OWN_TASK_WITH_CONFIRMATION'
  }
  exit 0
}
if (-not $ConfirmChange) { Hold 'EXPLICIT_CONFIRMATION_REQUIRED' }
if ($verified.path -notmatch '(?i)(CoCivium|CoAll|CoDesktop|RickBar)') {
  Hold 'EXECUTABLE_IDENTITY_NOT_COCIVIUM_SCOPED'
}

# Register only the GUI after login. Windows Session 0 is not a GUI.
$action=New-ScheduledTaskAction -Execute $verified.path -WorkingDirectory (Split-Path $verified.path -Parent)
$trigger=New-ScheduledTaskTrigger -AtLogOn -User $user
$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -RestartCount 1 -RestartInterval (New-TimeSpan -Minutes 5) -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
$arguments=@{
  TaskName=$TaskName
  Action=$action
  Trigger=$trigger
  Principal=$principal
  Settings=$settings
  Description=$TaskDescription
  ErrorAction='Stop'
}
Register-ScheduledTask @arguments | Out-Null
$registered=OwnedTask
if (-not (SameTask $registered $verified.path)) {
  Hold 'POST_REGISTER_TASK_MISMATCH__REVIEW_AND_DISABLE'
}
Report 'PER_USER_LOGON_TASK_REGISTERED__REBOOT_CANARY_REQUIRED' @{
  task_present=$true
  exe_sha256=$verified.sha256
  os_registration_mutation=1
  login_boundary='AFTER_INTERACTIVE_SIGN_IN'
  rollback='Disable own Task Scheduler entry using explicit confirmation'
}
