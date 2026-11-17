# CoDesktopActiveOwner R0: one-shot read-only election by actual Windows window ownership.
# No screen or title inventory output, no task edits, no process termination, no polling.
[CmdletBinding()]
param([string]$ReceiptPath = "$PSScriptRoot\CoDesktopActiveOwnerR0.json")
$ErrorActionPreference='Stop'
if(-not ('CoDesktopOwnerNativeR0' -as [type])){
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class CoDesktopOwnerNativeR0 {
 public delegate bool WinCallback(IntPtr hwnd,IntPtr lparam);
 [DllImport("user32.dll")] public static extern bool EnumWindows(WinCallback cb,IntPtr lp);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd,StringBuilder txt,int count);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd,out uint pid);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
}
'@
}
$matched=[System.Collections.Generic.List[object]]::new()
$callback=[CoDesktopOwnerNativeR0+WinCallback]{
 param([IntPtr]$hwnd,[IntPtr]$lp)
 $txt=[Text.StringBuilder]::new(128)
 [void][CoDesktopOwnerNativeR0]::GetWindowText($hwnd,$txt,127)
 $title=$txt.ToString()
 if($title -eq 'CoCivium CoBar R5' -or $title -eq 'CoCivium CoOrb R5'){
   [uint32]$windowOwner=0
   [void][CoDesktopOwnerNativeR0]::GetWindowThreadProcessId($hwnd,[ref]$windowOwner)
   $matched.Add([ordered]@{role=if($title -eq 'CoCivium CoBar R5'){'bar'}else{'orb'};pid=[int]$windowOwner;visible=[bool][CoDesktopOwnerNativeR0]::IsWindowVisible($hwnd)})
 }
 return $true
}
[void][CoDesktopOwnerNativeR0]::EnumWindows($callback,[IntPtr]::Zero)
$bar=@($matched|Where-Object{$_.role -eq 'bar' -and $_.visible})
$orb=@($matched|Where-Object{$_.role -eq 'orb' -and $_.visible})
$status='HELD_NOT_QUALIFIED'
$reason='MISSING_OR_DUPLICATE_VISIBLE_WINDOWS'
$ownerId=$null
$sha=$null
$sourcePath=$null
$sourceAge=$null
$statusHash=$null
$sourceFreshness=$null
if($bar.Count -eq 1 -and $orb.Count -eq 1 -and $bar[0].pid -gt 0 -and $bar[0].pid -eq $orb[0].pid){
 $ownerId=[int]$bar[0].pid
 $proc=Get-CimInstance Win32_Process -Filter "ProcessId = $ownerId" -ErrorAction SilentlyContinue
 $reason='OWNER_PROCESS_OR_SOURCE_NOT_QUALIFIED'
 if($proc -and $proc.Name -in @('pwsh.exe','powershell.exe')){
   $cmd=[string]$proc.CommandLine
   $m=[regex]::Match($cmd,'(?i)(?:^|\s)-File\s+(?:"([^"]+)"|(\S+))')
   if($m.Success){
     $candidate=if($m.Groups[1].Success){$m.Groups[1].Value}else{$m.Groups[2].Value}
     $candidate=[IO.Path]::GetFullPath($candidate)
     $root='D:\CoCivium\CoFarm\'
     if($candidate.StartsWith($root,[StringComparison]::OrdinalIgnoreCase) -and
        ([IO.Path]::GetFileName($candidate) -ieq 'Start-CoDesktopR5.ps1') -and
        (Test-Path -LiteralPath $candidate)){
       $sourcePath=$candidate
       $adjacent=Join-Path ([IO.Path]::GetDirectoryName($candidate)) 'renderer_status.json'
       $sha=(Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
       if(Test-Path -LiteralPath $adjacent){
         try{
           $st=Get-Content -LiteralPath $adjacent -Raw|ConvertFrom-Json -ErrorAction Stop
           $time=[DateTimeOffset]::Parse([string]$st.observed_at)
           $sourceAge=[int]([DateTimeOffset]::UtcNow-$time).TotalSeconds
           $sourceFreshness=[string]$st.source_freshness
           $statusHash=(Get-FileHash -LiteralPath $adjacent -Algorithm SHA256).Hash
           if($st.schema -eq 'CoCivium.CoDesktop.RendererObservation.v1' -and
              [int]$st.pid -eq $ownerId -and $sourceAge -ge 0 -and $sourceAge -le 120){
             $status='VERIFIED_LOCAL_ACTIVE_OWNER'
             $reason='LIVE_WINDOWS_AND_FRESH_ADJACENT_STATUS_AGREE'
           }else{$reason='OWNER_STATUS_STALE_OR_MISMATCHED'}
         }catch{$reason='OWNER_STATUS_UNREADABLE'}
       }
     }else{$reason='SOURCE_OUTSIDE_ALLOWED_COFARM_OR_MISSING'}
   }
 }
}
$record=[ordered]@{
 schema='CoAll.CoDesktop.ActiveOwnerElection.R0'
 observed_utc=[DateTimeOffset]::UtcNow.ToString('o')
 state=$status; reason=$reason
 visible_bar_count=$bar.Count;visible_orb_count=$orb.Count
 owner_pid=$ownerId;source_script_path=$sourcePath;source_sha256=$sha
 status_age_seconds=$sourceAge;status_file_sha256=$statusHash
 status_source_freshness=$sourceFreshness
 receiver_ack=$null;effect_authority='READ_ONLY'
 nonclaims=@('SINGLE_POLL_NE_CONTINUOUS_HEALTH','LOCAL_OWNER_NE_GLOBAL_OWNER','LOCAL_VERIFICATION_NE_RECEIVER_ACK','NO_RESTART_PROVEN','NO_POPUP_CAUSATION_PROVEN','NO_SIDE_EFFECTS_ON_HOST')
}
$record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
[ordered]@{state=$status;reason=$reason;owner_pid=$ownerId;windows=@($bar.Count,$orb.Count);source_age_seconds=$sourceAge;source_sha256=$sha;receipt_sha256=(Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash;receipt_path=$ReceiptPath}|ConvertTo-Json -Depth 4
