#requires -Version 7.0
<#
CoSurfacePresence/RickBar R4 read-only shadow observer.
Does not install, launch, stop, enumerate windows, intercept input, or modify a task.
Only inspects bounded Win32_Process pwsh/powershell launch metadata when invoked.
Raw process command lines, arguments and environment values are NEVER emitted.
Output is a candidate launch signature, not GUI visibility, responsiveness or receiver ACK.
#>
[CmdletBinding()]
param(
  [switch]$SelfTest,
  [string]$FixtureJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RecordProperty {
  param([AllowNull()][object]$Record, [string]$Name)
  if ($null -eq $Record) { return $null }
  $property = $Record.PSObject.Properties[$Name]
  if ($null -eq $property) { return $null }
  return $property.Value
}

function Get-PinnedR4FileArgument {
  param([AllowNull()][string]$CommandLine)
  if ([string]::IsNullOrWhiteSpace($CommandLine)) { return $null }
  # Do not treat text in a PowerShell -Command string as a -File launch.
  if ($CommandLine -match '(?i)(?:^|\s)-command(?:\s|$)') { return $null }
  $fileArg = [regex]::Match(
    $CommandLine,
    '(?i)(?:^|\s)-(?:file|f)\s+(?:"(?<quoted>[^"]+)"|(?<bare>[^\s]+))'
  )
  if (-not $fileArg.Success) { return $null }
  $candidate = $fileArg.Groups['quoted'].Value
  if (-not $candidate) { $candidate = $fileArg.Groups['bare'].Value }
  $candidate = $candidate.Replace('/', '\')
  # Pinned known CoFarm R4 launch role. Another location remains unverified, not absent.
  $pattern = '^[A-Za-z]:\\CoCivium\\CoFarm\\CoDesktop\\[^\\]+_RickBar_R4\\Start-RickBarR4\.ps1$'
  if (-not [regex]::IsMatch($candidate, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
    return $null
  }
  return 'PINNED_COFARM_RICKBAR_R4_SCRIPT'
}

function Get-R4ShadowObservation {
  param(
    [AllowNull()][object[]]$Processes = @(),
    [ValidateSet('OK','ERROR')][string]$ObserverState = 'OK',
    [string]$Source = 'FIXTURE'
  )
  $matched = [System.Collections.Generic.List[object]]::new()
  $hostCount = 0
  $opaqueCount = 0
  if ($ObserverState -eq 'OK') {
    foreach ($process in @($Processes)) {
      $name = [string](Get-RecordProperty -Record $process -Name 'Name')
      if ($name -notmatch '^(?:pwsh|powershell)(?:\.exe)?$') { continue }
      $hostCount++
      $rawCommandLine = [string](Get-RecordProperty -Record $process -Name 'CommandLine')
      if ([string]::IsNullOrWhiteSpace($rawCommandLine)) { $opaqueCount++; continue }
      $role = Get-PinnedR4FileArgument -CommandLine $rawCommandLine
      if ($null -eq $role) { continue }
      [int]$pidNumber = 0
      $idValue = Get-RecordProperty -Record $process -Name 'ProcessId'
      if (-not [int]::TryParse([string]$idValue, [ref]$pidNumber) -or $pidNumber -le 0) {
        $opaqueCount++
        continue
      }
      [void]$matched.Add([pscustomobject]@{
        process_id = $pidNumber
        launch_role = $role
      })
    }
  }
  $state = if ($ObserverState -ne 'OK') {
    'HOLD_OBSERVER_ERROR'
  } elseif ($matched.Count -gt 1) {
    'HOLD_MULTIPLE_R4_LAUNCH_SIGNATURES'
  } elseif ($matched.Count -eq 1) {
    'R4_LAUNCH_SIGNATURE_OBSERVED'
  } elseif ($opaqueCount -gt 0) {
    'HOLD_OPAQUE_PROCESS_METADATA'
  } else {
    'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  }
  return [pscustomobject]@{
    schema = 'CoAll.CoSurfacePresence.RickBarR4Shadow.R0'
    status = $state
    observation_source = $Source
    scope = 'WIN32_PROCESS_PWSH_FILE_LAUNCH_SIGNATURE_ONLY'
    r4_matches = @($matched.ToArray())
    host_processes_examined = $hostCount
    incomplete_host_records = $opaqueCount
    commandline_output = 'REDACTED_NOT_EMITTED'
    authority = 'READ_ONLY_OBSERVATION'
    effects = [pscustomobject]@{
      writes = 0
      window_actions = 0
      input_interception = 0
      network = 0
      process_changes = 0
      task_changes = 0
      credential_access = 0
    }
    nonclaims = @(
      'MATCHING_LAUNCH_ARGS_NE_RESPONSIVE_WINDOW',
      'NO_MATCH_NE_R4_ABSENT',
      'CURRENT_PROCESS_SNAPSHOT_NE_GUI_PICKUP',
      'OBSERVER_OFFLINE_NE_DEVICE_OFF',
      'STATUS_NE_RECEIVER_ACK',
      'SHADOW_NE_INSTALLED_PRODUCTION_WRITER'
    )
  }
}

function New-Fixture {
  param([string]$Name='pwsh.exe', [string]$Line='', [int]$Id=5884)
  return [pscustomobject]@{ Name=$Name; CommandLine=$Line; ProcessId=$Id }
}

function Run-SelfTest {
  $p = 'D:\CoCivium\CoFarm\CoDesktop\20261016T002714Z_RickBar_R4\Start-RickBarR4.ps1'
  $good = 'pwsh.exe -NoProfile -File "' + $p + '"'
  $t = [System.Collections.Generic.List[object]]::new()
  function Check-Case([string]$Title,[object[]]$Records,[string]$Expected,[string]$Observer='OK') {
    $r=Get-R4ShadowObservation -Processes $Records -ObserverState $Observer -Source 'SELFTEST'
    [void]$t.Add([pscustomobject]@{
      test=$Title
      expected=$Expected
      observed=$r.status
      status=if ($r.status -eq $Expected) { 'PASS' } else { 'FAIL' }
    })
  }
  Check-Case 'pinned R4 launcher' @((New-Fixture -Line $good)) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  Check-Case 'unquoted path' @((New-Fixture -Line ('pwsh -File '+$p))) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  Check-Case 'short flag' @((New-Fixture -Line ('pwsh -f "'+$p+'"'))) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  Check-Case 'PowerShell.exe host' @((New-Fixture -Name 'powershell.exe' -Line $good)) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  Check-Case 'case folding' @((New-Fixture -Name 'PWSH.EXE' -Line $good.ToUpperInvariant())) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  Check-Case 'forward slash path accepted' @((New-Fixture -Line ('pwsh -File '+$p.Replace('\','/')))) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  Check-Case 'other root is not pinned' @((New-Fixture -Line ($good.Replace('D:\CoCivium','D:\Other')))) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'other version not pinned' @((New-Fixture -Line ($good.Replace('_RickBar_R4','_RickBar_R3')))) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'other script not pinned' @((New-Fixture -Line ($good.Replace('Start-RickBarR4.ps1','Start-RickBarR3.ps1')))) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'script suffix denied' @((New-Fixture -Line ($good.Replace('.ps1"','.ps1.bak"')))) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'notepad is not a host' @((New-Fixture -Name 'notepad.exe' -Line $good)) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'no explicit File command' @((New-Fixture -Line ('pwsh "'+$p+'"'))) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'command string is not a File launch' @((New-Fixture -Line ('pwsh -Command "Write-Host -File '+$p+'"'))) 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT'
  Check-Case 'wrong PID cannot qualify' @((New-Fixture -Line $good -Id -5)) 'HOLD_OPAQUE_PROCESS_METADATA'
  Check-Case 'missing commandline holds' @((New-Fixture -Line '')) 'HOLD_OPAQUE_PROCESS_METADATA'
  Check-Case 'CIM observer failed holds' @() 'HOLD_OBSERVER_ERROR' 'ERROR'
  Check-Case 'multiple pinned hosts requires review' @(
    (New-Fixture -Line $good -Id 5884),
    (New-Fixture -Line $good -Id 5885)
  ) 'HOLD_MULTIPLE_R4_LAUNCH_SIGNATURES'
  Check-Case 'one pinned plus unrelated remains one' @(
    (New-Fixture -Line $good -Id 5884),
    (New-Fixture -Line 'pwsh -File C:\Different\Utility.ps1' -Id 5885)
  ) 'R4_LAUNCH_SIGNATURE_OBSERVED'
  $secret='PRIVATE_FIXTURE_SECRET_DO_NOT_PUBLISH'
  $redacted=Get-R4ShadowObservation -Processes @((New-Fixture -Line ($good+' -Token '+$secret))) -Source 'SELFTEST'
  $safeJson=$redacted | ConvertTo-Json -Depth 8 -Compress
  [void]$t.Add([pscustomobject]@{
    test='process commandline and arguments are not emitted'
    expected='PASS'
    observed=if ($safeJson.Contains($secret)) { 'FAIL' } else { 'PASS' }
    status=if ($safeJson.Contains($secret)) { 'FAIL' } else { 'PASS' }
  })
  $noEffect=@($redacted.effects.PSObject.Properties | Where-Object { $_.Value -ne 0 }).Count -eq 0
  [void]$t.Add([pscustomobject]@{
    test='all effect counters remain zero'
    expected='PASS'
    observed=if ($noEffect) { 'PASS' } else { 'FAIL' }
    status=if ($noEffect) { 'PASS' } else { 'FAIL' }
  })
  $missing = Get-R4ShadowObservation -Processes @() -Source 'SELFTEST'
  [void]$t.Add([pscustomobject]@{
    test='no match does not assert device or R4 absence'
    expected='PASS'
    observed=if ($missing.status -eq 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT' -and
      $missing.nonclaims -contains 'NO_MATCH_NE_R4_ABSENT') { 'PASS' } else { 'FAIL' }
    status=if ($missing.status -eq 'R4_NOT_PROVEN_IN_SCOPED_SNAPSHOT' -and
      $missing.nonclaims -contains 'NO_MATCH_NE_R4_ABSENT') { 'PASS' } else { 'FAIL' }
  })
  return [pscustomobject]@{
    schema='CoAll.CoSurfacePresence.RickBarR4Shadow.R0.Tests'
    test_class='SYNTHETIC_POWERSHELL_FIXTURES'
    passed=@($t | Where-Object status -eq 'PASS').Count
    total=$t.Count
    tests=$t.ToArray()
    nonclaims=@('SELFTEST_NE_X2_RUNTIME','PROCESS_SIGNATURE_NE_VISIBLE_RICKBAR')
  }
}

if ($SelfTest) {
  $report = Run-SelfTest
  $report | ConvertTo-Json -Depth 9
  if ($report.passed -ne $report.total) { exit 1 }
  exit 0
}

if ($FixtureJson) {
  $fixture=Get-Content -LiteralPath $FixtureJson -Raw -Encoding utf8 | ConvertFrom-Json
  $state=[string](Get-RecordProperty -Record $fixture -Name 'observer_status')
  if ($state -ne 'ERROR') { $state='OK' }
  $rows=Get-RecordProperty -Record $fixture -Name 'processes'
  $result=Get-R4ShadowObservation -Processes @($rows) -ObserverState $state -Source 'EXPLICIT_FIXTURE'
} else {
  if (-not $IsWindows) {
    $result=Get-R4ShadowObservation -Processes @() -ObserverState 'ERROR' -Source 'NON_WINDOWS_NO_CIM'
  } else {
    try {
      $rows=@(Get-CimInstance -ClassName Win32_Process -Filter "Name='pwsh.exe' OR Name='powershell.exe'" -ErrorAction Stop)
      $result=Get-R4ShadowObservation -Processes $rows -ObserverState 'OK' -Source 'LIVE_WINDOWS_CIM_SCOPED'
    } catch {
      $result=Get-R4ShadowObservation -Processes @() -ObserverState 'ERROR' -Source 'LIVE_WINDOWS_CIM_FAILED'
    }
  }
}
$result | ConvertTo-Json -Depth 8
