#requires -Version 7.0
# Read-only Windows gate. Never pass -ConfirmChange in CI.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$TargetScript=Join-Path $PSScriptRoot 'CoStelDesktopLogonR0.ps1'
$Notepad=Join-Path $env:WINDIR 'System32\notepad.exe'
$Sha=(Get-FileHash -LiteralPath $Notepad -Algorithm SHA256).Hash
$Count=0
$Errors=New-Object 'System.Collections.Generic.List[string]'

function Ensure([bool]$Ok,[string]$Reason) {if(-not $Ok){throw $Reason}}
function Probe([string[]]$ArgsList) {
  $output=@(& pwsh -NoLogo -NoProfile -NonInteractive -File $TargetScript @ArgsList 2>&1)
  return @{text=($output -join [Environment]::NewLine); exit=$LASTEXITCODE}
}
function Check([string]$Name,[scriptblock]$Test) {
  $script:Count++
  try {& $Test; Write-Output ("PASS "+$Name)}
  catch {$script:Errors.Add($Name+' : '+$_.Exception.Message);Write-Output ("FAIL "+$Name)}
}
function HoldExpected([string[]]$ArgsList,[string]$Reason) {
  $result=Probe $ArgsList
  Ensure ($result.exit -ne 0) 'Must refuse'
  Ensure ($result.text.Contains('COSTEL_HOLD:'+$Reason)) ('Wrong hold: '+$result.text)
}
function ReadPlan {
  $result=Probe @('-Mode','Plan','-DesktopExe',$Notepad,'-ExpectedSha256',$Sha)
  Ensure ($result.exit -eq 0) $result.text
  return ($result.text|ConvertFrom-Json)
}

$prior=Get-ScheduledTask -TaskName 'CoStel.CoAllDesktop.UserLogon.R0' -ErrorAction SilentlyContinue

Check 'audit returns scoped schema' {
  $r=Probe @('-Mode','Audit')
  Ensure ($r.exit -eq 0) $r.text
  $j=$r.text|ConvertFrom-Json
  Ensure ($j.schema -eq 'CoAll.CoStel.WindowsLogon.R0') 'Schema'
  Ensure ($j.state -eq 'READ_ONLY_OBSERVATION__NOT_UI_HEALTH') 'Status'
}
Check 'audit does not diagnose authentication by guessing' {
  $r=Probe @('-Mode','Audit')
  $j=$r.text|ConvertFrom-Json
  Ensure (-not $j.credentials_read) 'Credentials read'
  Ensure ($j.user_reauth_cause -eq 'NOT_DETERMINED') 'False root cause'
  Ensure ($j.native_x2_acceptance -eq 'NOT_TESTED') 'False native proof'
}
Check 'valid executable plan is read only' {
  $j=ReadPlan
  Ensure ($j.state -eq 'PLAN_ONLY__NO_STARTUP_MUTATION') 'No effect plan'
  Ensure ($j.exe_sha256 -eq $Sha.ToLowerInvariant()) 'Source hash changed'
}
Check 'plan is per-user limited logon with bounded retry' {
  $j=ReadPlan
  Ensure ($j.proposed_trigger -eq 'CURRENT_USER_LOGON') 'Prelogin GUI risk'
  Ensure ($j.proposed_run_level -eq 'LIMITED') 'Privilege escalation'
  Ensure ($j.proposed_restart_attempts -eq 1) 'Crash loop'
}
Check 'digest mismatch held' {
  HoldExpected @('-Mode','Plan','-DesktopExe',$Notepad,'-ExpectedSha256',('0'*64)) 'EXECUTABLE_HASH_MISMATCH'
}
Check 'missing digest held' {
  HoldExpected @('-Mode','Plan','-DesktopExe',$Notepad) 'EXPECTED_SHA256_REQUIRED'
}
Check 'script launcher not accepted as executable' {
  $sh=(Get-FileHash -LiteralPath $TargetScript -Algorithm SHA256).Hash
  HoldExpected @('-Mode','Plan','-DesktopExe',$TargetScript,'-ExpectedSha256',$sh) 'EXE_ONLY_NO_SCRIPT_SPAWNER'
}
Check 'UNC path refused' {
  HoldExpected @('-Mode','Plan','-DesktopExe','\\untrustedhost\share\gui.exe','-ExpectedSha256',('a'*64)) 'UNC_OR_NETWORK_EXECUTABLE_FORBIDDEN'
}
Check 'relative exe refused' {
  HoldExpected @('-Mode','Plan','-DesktopExe','launcher.exe','-ExpectedSha256',('a'*64)) 'ABSOLUTE_EXECUTABLE_PATH_REQUIRED'
}
Check 'nonexistent exe refused' {
  HoldExpected @('-Mode','Plan','-DesktopExe','C:\CoAll-NoSuchThing-20261110\gui.exe','-ExpectedSha256',('a'*64)) 'EXECUTABLE_NOT_FOUND'
}
Check 'silent Install is refused' {
  HoldExpected @('-Mode','Install','-DesktopExe',$Notepad,'-ExpectedSha256',$Sha) 'EXPLICIT_CONFIRMATION_REQUIRED'
}
Check 'silent Disable is refused' {
  HoldExpected @('-Mode','Disable') 'EXPLICIT_CONFIRMATION_REQUIRED'
}
Check 'no direct process start' {
  $text=Get-Content -LiteralPath $TargetScript -Raw
  Ensure ($text -notmatch '(?i)Start-Process|Start-ScheduledTask') 'Unexpected spawn'
}
Check 'no credential reader or password helper' {
  $text=Get-Content -LiteralPath $TargetScript -Raw
  Ensure ($text -notmatch '(?i)(Get-Credential|Export-Clixml|PasswordVault|CredentialManager|cookie[s]?\.sqlite|dpapi|Set-ItemProperty)') 'Credential handling'
}
Check 'audit enumerates Run names without reading command values' {
  $src=Get-Content -LiteralPath $TargetScript -Raw
  Ensure ($src.Contains('GetValueNames()')) 'Registry names not enumerated'
  Ensure (-not $src.Contains('Get-ItemProperty')) 'Registry values could be read'
}
Check 'startup audit declares partial coverage' {
  $r=Probe @('-Mode','Audit')
  Ensure ($r.exit -eq 0) $r.text
  $j=$r.text|ConvertFrom-Json
  Ensure ($j.startup_scan_coverage -eq 'NAME_FILTERED_ONLY__ACTION_ARGUMENTS_NOT_INSPECTED') 'Overclaimed complete scan'
}
Check 'disable requires own task provenance' {
  $src=Get-Content -LiteralPath $TargetScript -Raw
  Ensure ($src.Contains('UNRECOGNIZED_TASK_PROVENANCE')) 'Untrusted same-name task could be disabled'
  Ensure ($src.Contains('FOREIGN_TASK_OWNER')) 'Foreign task owner not checked'
}
Check 'no task installed by test' {
  $after=Get-ScheduledTask -TaskName 'CoStel.CoAllDesktop.UserLogon.R0' -ErrorAction SilentlyContinue
  Ensure ($null -eq $prior -and $null -eq $after) 'Mutated startup state'
}
Check 'no made-up effects' {
  $r=Probe @('-Mode','Audit')
  $j=$r.text|ConvertFrom-Json
  Ensure ($j.effects_verified -eq $false) 'False success'
  Ensure ($j.processes_started -eq 0) 'Fake process'
}
if($Errors.Count -gt 0) {
  foreach($e in $Errors){Write-Output ('FAIL_DETAIL '+$e)}
  throw ('CoStel Windows source tests failed '+$Errors.Count+'/'+$Count)
}
Write-Output ('PASS_COSTEL_WINDOWS_LOGON_SOURCE_TESTS '+$Count+'/'+$Count)
