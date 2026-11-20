#requires -Version 7.2
<#[CoOrbIO] Setup and reversible per-user recurring safe local cycles.
No admin privileges, no new services, no Logitech mutation, no external sends.
The source ZIP should be SHA-256 checked by the one-paste bootstrap.
#>
[CmdletBinding()]
param([ValidateSet('Check','Install','Remove','CycleOnce','Status')][string]$Mode='Check')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if(-not $IsWindows){throw 'WINDOWS_ONLY'}
$bundleRoot=$PSScriptRoot
$manifestFile=Join-Path $bundleRoot 'manifest.json'
if(-not (Test-Path -LiteralPath $manifestFile)){throw 'PACKAGE_MANIFEST_MISSING'}
$manifest=Get-Content -LiteralPath $manifestFile -Raw | ConvertFrom-Json
if($manifest.schema -ne 'CoCivium.CoOrbIO.Package.R0'){throw 'PACKAGE_SCHEMA_MISMATCH'}
$sourceNames=@('CoOmniCycleR0.mjs','CoOmniCycleR0.test.mjs','CoOrbIOHotkeyR0.ps1','CoCopyRichPaletteR0.ps1','Setup-CoOrbIO_R0.ps1','README.md')
foreach($name in $sourceNames){
  $item=$manifest.files.PSObject.Properties[$name]
  if(-not $item){throw ('MISSING_HASH_ENTRY: '+$name)}
  $local=Join-Path $bundleRoot $name
  if(-not (Test-Path -LiteralPath $local -PathType Leaf)){throw ('MISSING_FILE: '+$name)}
  $actual=(Get-FileHash -LiteralPath $local -Algorithm SHA256).Hash.ToLowerInvariant()
  if($actual -ne [string]$item.Value){throw ('HOLD_HASH_MISMATCH: '+$name)}
}
$base=if(Test-Path -LiteralPath 'D:\CoCivium\CoFarm' -PathType Container){'D:\CoCivium\CoFarm'}else{Join-Path $env:LOCALAPPDATA 'CoCivium'}
$target=Join-Path $base 'CoOrbIO_R0'
$state=Join-Path $target 'state'
$nodeCommand=Get-Command node -ErrorAction SilentlyContinue
$nodeExe=if($nodeCommand){$nodeCommand.Source}else{$null}
$pwshExe=(Get-Command pwsh -ErrorAction Stop).Source
$taskName='CoCivium-CoOmniCycle-R0'
$startup=[Environment]::GetFolderPath('Startup')
$shortcut=Join-Path $startup 'CoOrbIO_R0.lnk'

function Invoke-LocalNode([string[]]$cliArgs){
 if(-not $nodeExe){throw 'HELD_NODE22_NOT_INSTALLED'}
 $p=[Diagnostics.ProcessStartInfo]::new()
 $p.FileName=$nodeExe
 $p.UseShellExecute=$false
 $p.RedirectStandardOutput=$true
 $p.RedirectStandardError=$true
 foreach($a in $cliArgs){[void]$p.ArgumentList.Add($a)}
 $proc=[Diagnostics.Process]::Start($p)
 if(-not $proc.WaitForExit(180000)){$proc.Kill();throw 'LOCAL_NODE_TIMEOUT'}
 $out=$proc.StandardOutput.ReadToEnd()
 $err=$proc.StandardError.ReadToEnd()
 if($proc.ExitCode -ne 0){throw ('LOCAL_NODE_FAILED: '+$err)}
 return $out.Trim()
}
function Inspect-Task {
 try{return Get-ScheduledTask -TaskName $taskName -ErrorAction Stop}catch{return $null}
}
function Test-LocalSources {
 if(-not $nodeExe){throw 'HELD_NODE22_NOT_INSTALLED'}
 $version=(& $nodeExe --version)
 $major=[int]($version -replace '^v(\d+).*','$1')
 if($major -lt 22){throw 'HELD_NODE_VERSION_LT_22'}
 $null=Invoke-LocalNode @((Join-Path $bundleRoot 'CoOmniCycleR0.mjs'),'--selftest')
 $run=@('-NoProfile','-STA','-File',(Join-Path $bundleRoot 'CoCopyRichPaletteR0.ps1'),'-SelfTest')
 & $pwshExe @run | Out-Null
 if($LASTEXITCODE -ne 0){throw 'HELD_PALETTE_STA_PREFLIGHT'}
 $hotkey=@('-NoProfile','-STA','-File',(Join-Path $bundleRoot 'CoOrbIOHotkeyR0.ps1'),'-SelfTest','-PalettePath',(Join-Path $bundleRoot 'CoCopyRichPaletteR0.ps1'))
 & $pwshExe @hotkey | Out-Null
 if($LASTEXITCODE -ne 0){throw 'HELD_HOTKEY_PREVIEW_PREFLIGHT'}
 return [pscustomobject]@{status='PASS_BOUNDED_WINDOWS_NON_EFFECT_PREFLIGHT';node=$version;windows_gui_actual_paste='HELD_NOT_TESTED';mouse_button='HELD_NOT_REASSIGNED'}
}

if($Mode -eq 'Check'){
  $r=Test-LocalSources
  [pscustomobject]@{schema='CoOrbIO.SetupCheck.R0';result=$r;package_verified=$true;task_registered=($null -ne (Inspect-Task));source_location=$bundleRoot;authority='LOCAL_NON_EFFECT_ONLY'} | ConvertTo-Json -Depth 4
  exit 0
}
if($Mode -eq 'Status'){
  [pscustomobject]@{schema='CoOrbIO.SetupStatus.R0';installed=(Test-Path -LiteralPath (Join-Path $target 'CoOmniCycleR0.mjs'));recurring_task_present=($null -ne (Inspect-Task));tray_autostart_present=(Test-Path -LiteralPath $shortcut);device_button_mapped='UNKNOWN_EXTERNAL_LOGI_OPTIONS';state_root=$state;human_controls=@('Tray > Pause','Tray > Exit','Setup Remove')} | ConvertTo-Json -Depth 4
  exit 0
}
if($Mode -eq 'Remove'){
  $task=Inspect-Task
  if($task){Unregister-ScheduledTask -TaskName $taskName -Confirm:$false}
  if(Test-Path -LiteralPath $shortcut){
    $link=(New-Object -ComObject WScript.Shell).CreateShortcut($shortcut)
    if($link.Arguments -notlike '*CoOrbIOHotkeyR0.ps1*'){throw 'HOLD_SHORTCUT_NAME_COLLISION'}
    Remove-Item -LiteralPath $shortcut
  }
  if(Test-Path -LiteralPath $state){
    $flag=Join-Path $state 'HOTKEY_STOP'
    if(-not (Test-Path -LiteralPath $flag)){[IO.File]::WriteAllText($flag,'Stop requested by installer remove')}
    if($nodeExe -and (Test-Path -LiteralPath (Join-Path $target 'CoOmniCycleR0.mjs'))){
       $null=Invoke-LocalNode @((Join-Path $target 'CoOmniCycleR0.mjs'),'--pause',$state)
    }
  }
  [pscustomobject]@{schema='CoOrbIO.Remove.R0';status='STOP_AND_UNSCHEDULE_REQUESTED';source_and_receipts_preserved=$true;task_removed=$true;tray_exit_requested=$true} | ConvertTo-Json
  exit 0
}
if($Mode -eq 'CycleOnce'){
  if(-not (Test-Path -LiteralPath (Join-Path $target 'CoOmniCycleR0.mjs'))){throw 'HOLD_NOT_INSTALLED'}
  Invoke-LocalNode @((Join-Path $target 'CoOmniCycleR0.mjs'),'--cycle',$state)
  exit 0
}
if($Mode -ne 'Install'){throw 'UNRECOGNIZED_MODE'}

$check=Test-LocalSources
[void](New-Item -ItemType Directory -Path $target -Force)
foreach($name in $sourceNames){
  $src=Join-Path $bundleRoot $name
  $dst=Join-Path $target $name
  if(Test-Path -LiteralPath $dst){
    $old=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLowerInvariant()
    if($old -ne [string]$manifest.files.PSObject.Properties[$name].Value){throw ('HOLD_NO_CLOBBER: '+$dst)}
  }else{Copy-Item -LiteralPath $src -Destination $dst}
}
# Copy the exact verified manifest as part of reversible installed custody.
$installedManifest=Join-Path $target 'manifest.json'
if(Test-Path -LiteralPath $installedManifest){
  if((Get-FileHash -LiteralPath $installedManifest -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $manifestFile -Algorithm SHA256).Hash){throw 'HOLD_NO_CLOBBER: manifest changed'}
}else{Copy-Item -LiteralPath $manifestFile -Destination $installedManifest}

# Private local state remains on the same host; no upload and no remote host claim.
$null=Invoke-LocalNode @((Join-Path $target 'CoOmniCycleR0.mjs'),'--init',$state)
$stopFile=Join-Path $state 'HOTKEY_STOP'
if(Test-Path -LiteralPath $stopFile){Remove-Item -LiteralPath $stopFile}
$generated=Join-Path $state 'objects\hello-public-example.txt'
if(-not(Test-Path -LiteralPath $generated)){[IO.File]::WriteAllText($generated,'CoOmniCycle R0 local example; not a provider session, email, device command or trade.')}
$sampleTask=[ordered]@{schema='CoCivium.CoOmniCycle.Task.R0';id='first-safe-hash';kind='HASH_OBJECT';authority='LOCAL_READ_ONLY';confidentiality='LOCAL_ONLY';external_effects=$false;relative_path='hello-public-example.txt'}
$sample=Join-Path $state 'inbox\first-safe-hash.json'
if(-not(Test-Path -LiteralPath $sample)){[IO.File]::WriteAllText($sample,(ConvertTo-Json $sampleTask -Depth 4))}
$cycleResult=Invoke-LocalNode @((Join-Path $target 'CoOmniCycleR0.mjs'),'--cycle',$state)

# The scheduled task executes only a local read-only cycle every 15 minutes
# while the current Windows user is logged on. No hidden network requests.
$scheduled=$false;$scheduledError=$null
if(-not (Inspect-Task)){
 try{
  Import-Module ScheduledTasks -ErrorAction Stop
  $action=New-ScheduledTaskAction -Execute $nodeExe -Argument ('"{0}" --cycle "{1}"' -f (Join-Path $target 'CoOmniCycleR0.mjs'),$state)
  $trigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
  $settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 6) -StartWhenAvailable
  $principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
  Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -ErrorAction Stop | Out-Null
  $scheduled=$true
 }catch{$scheduledError=$_.Exception.Message}
}else{$scheduled=$true}

$trayAutostart=$false;$trayError=$null
try{
 if(Test-Path -LiteralPath $shortcut){
  $existing=(New-Object -ComObject WScript.Shell).CreateShortcut($shortcut)
  if($existing.Arguments -notlike '*CoOrbIOHotkeyR0.ps1*'){throw 'HOLD_SHORTCUT_NAME_COLLISION'}
  $trayAutostart=$true
 }else{
  $shell=New-Object -ComObject WScript.Shell
  $link=$shell.CreateShortcut($shortcut)
  $link.TargetPath=$pwshExe
  $link.Arguments='-NoProfile -STA -WindowStyle Hidden -File "'+(Join-Path $target 'CoOrbIOHotkeyR0.ps1')+'" -PalettePath "'+(Join-Path $target 'CoCopyRichPaletteR0.ps1')+'" -StateRoot "'+$state+'"'
  $link.WorkingDirectory=$target
  $link.Description='CoOrbIO visible tray hotkey, Ctrl+Alt+Shift+N, local preview only'
  $link.Save()
  $trayAutostart=$true
 }
}catch{$trayError=$_.Exception.Message}

# Start visible tray now, and allow user to pause/exit or uninstall at any time.
$trayStart='NOT_ATTEMPTED'
if($trayAutostart){
 try{
  $args=@('-NoProfile','-STA','-File',(Join-Path $target 'CoOrbIOHotkeyR0.ps1'),'-PalettePath',(Join-Path $target 'CoCopyRichPaletteR0.ps1'),'-StateRoot',$state)
  Start-Process -FilePath $pwshExe -ArgumentList ($args|ForEach-Object {if($_ -match '\s'){ '"'+$_+'"' }else{$_}}) -WindowStyle Hidden -ErrorAction Stop
  $trayStart='LAUNCHED_NOT_RUNTIME_ACK'
 }catch{$trayStart='HELD_'+$_.Exception.Message}
}
[pscustomobject]@{schema='CoOrbIO.InstallReceipt.R0';observed_at=(Get-Date).ToUniversalTime().ToString('o');status='LOCAL_CANDIDATE_SETUP_COMPLETE';non_effect_preflight=$check.status;source_hashes_verified=$true;first_safe_cycle=$cycleResult;recurring_local_task_enabled=$scheduled;recurring_task_error=$scheduledError;tray_autostart_enabled=$trayAutostart;tray_error=$trayError;tray_initial_start=$trayStart;physical_mouse_button='HELD_ASSIGN_IN_LOGI_OPTIONS';no_login_or_remote_autonomy=$true;off_host_receiver='HELD';rollback='Setup-CoOrbIO_R0.ps1 -Mode Remove';state_root=$state} | ConvertTo-Json -Depth 7
