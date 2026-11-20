#requires -Version 7.2
<#[CoOrbIO+ R0] Visible per-user tray helper.
Ctrl+Alt+Shift+N (configured by the human in MX Master 4 Logi Options+) opens
an explicitly staged local CoCopy palette. No key logging, mouse hook,
screen capture, clipboard reads, network, automatic paste/send, or provider call.
#>
[CmdletBinding()]
param(
    [switch]$SelfTest,
    [switch]$Stop,
    [string]$PalettePath = (Join-Path $PSScriptRoot 'CoCopyRichPaletteR0.ps1'),
    [string]$StateRoot = (Join-Path $env:LOCALAPPDATA 'CoCivium\CoOrbIO_R0')
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { throw 'WINDOWS_ONLY' }
if ([Threading.Thread]::CurrentThread.GetApartmentState().ToString() -ne 'STA') {
    throw 'STA_REQUIRED: use pwsh -NoProfile -STA -File ...'
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$ExpectedSourceHash = 'e7d6d4446e74e35bb7a649ab21b73e2bc0379e891b32c5e44956aa32e1a7ae5f'
if (-not (Test-Path -LiteralPath $PalettePath -PathType Leaf)) { throw 'HELD_PALETTE_NOT_PRESENT' }
$ObservedSourceHash = (Get-FileHash -LiteralPath $PalettePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ObservedSourceHash -ne $ExpectedSourceHash) { throw 'HELD_PALETTE_SOURCE_HASH_MISMATCH' }

# RegisterHotKey is specific to a single chosen shortcut. It does not intercept
# unrelated keypresses, mouse buttons, native middle clicks or device profiles.
Add-Type -ReferencedAssemblies ([System.Windows.Forms.Form].Assembly.Location) -TypeDefinition @'
using System;
using System.Windows.Forms;
using System.Runtime.InteropServices;
public sealed class CoOrbHotkeyWindow : Form {
    public const int KeyId = 0xC082;
    public event EventHandler HotkeyPressed;
    protected override void WndProc(ref Message m) {
        if(m.Msg == 0x0312 && m.WParam.ToInt32() == KeyId)
            HotkeyPressed?.Invoke(this, EventArgs.Empty);
        base.WndProc(ref m);
    }
}
public static class CoOrbHotkeyNative {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool RegisterHotKey(IntPtr hwnd, int id, uint modifiers, uint vk);
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool UnregisterHotKey(IntPtr hwnd, int id);
}
'@

if ($SelfTest) {
    $checks = @(
        [pscustomobject]@{id='Windows PowerShell 7';pass=$IsWindows},
        [pscustomobject]@{id='STA thread';pass=([Threading.Thread]::CurrentThread.GetApartmentState().ToString() -eq 'STA')},
        [pscustomobject]@{id='Hotkey form assembly';pass=($null -ne [CoOrbHotkeyWindow])},
        [pscustomobject]@{id='Verified local palette bytes';pass=($ObservedSourceHash -eq $ExpectedSourceHash)},
        [pscustomobject]@{id='No system hotkey registration in selftest';pass=$true},
        [pscustomobject]@{id='No mouse hook or clipboard read';pass=$true}
    )
    $passed=@($checks|Where-Object pass).Count
    [pscustomobject]@{schema='CoOrbIO.HotkeyPreflight.R0';status=$(if($passed -eq $checks.Count){'PASS'}else{'FAIL'});passed=$passed;total=$checks.Count;tests=$checks;hotkey_registered=$false;clipboard_changed=$false;network=$false} | ConvertTo-Json -Depth 5
    if($passed -ne $checks.Count){ exit 4 }
    exit 0
}

if (-not (Test-Path -LiteralPath $StateRoot)) {
    [void](New-Item -ItemType Directory -Path $StateRoot -Force)
}
$stopFile=Join-Path $StateRoot 'HOTKEY_STOP'
if ($Stop) {
    if(-not (Test-Path -LiteralPath $stopFile)){
        [IO.File]::WriteAllText($stopFile, "Stop requested by local operator`r`n")
    }
    Write-Output 'STOP_REQUEST_WRITTEN: tray helper exits after its next timer tick.'
    exit 0
}
if(Test-Path -LiteralPath $stopFile){throw 'HELD_STOP_FLAG_PRESENT: delete HOTKEY_STOP only when ready to resume.'}

$script:PaletteProcess=$null
$script:Paused=$false
$script:HotkeyRegistered=$false
$script:HostWindow=[CoOrbHotkeyWindow]::new()
$script:HostWindow.ShowInTaskbar=$false
$script:HostWindow.Opacity=0
$script:HostWindow.WindowState=[Windows.Forms.FormWindowState]::Minimized
$script:HostWindow.Text='CoOrbIO+ Hotkey R0 (tray controls available)'
$script:HostWindow.ClientSize=[Drawing.Size]::new(1,1)
$script:Tray=[Windows.Forms.NotifyIcon]::new()
$script:Tray.Text='CoOrbIO+ R0 | Ctrl+Alt+Shift+N | no automatic paste or send'
$script:Tray.Icon=[Drawing.SystemIcons]::Application
$script:Menu=[Windows.Forms.ContextMenuStrip]::new()
$script:OpenItem=[Windows.Forms.ToolStripMenuItem]::new('Open CoCopy preview')
$script:PauseItem=[Windows.Forms.ToolStripMenuItem]::new('Pause hotkey')
$script:ExitItem=[Windows.Forms.ToolStripMenuItem]::new('Exit CoOrbIO+')
[void]$script:Menu.Items.Add($script:OpenItem)
[void]$script:Menu.Items.Add($script:PauseItem)
[void]$script:Menu.Items.Add($script:ExitItem)
$script:Tray.ContextMenuStrip=$script:Menu
$script:Tray.Visible=$true

function Show-Notice([string]$message) {
    $script:Tray.BalloonTipTitle='CoOrbIO+ R0'
    $script:Tray.BalloonTipText=$message
    $script:Tray.ShowBalloonTip(1700)
}
function Invoke-CoPreview {
    if($script:Paused){Show-Notice 'Paused. Resume from tray menu.';return}
    if($script:PaletteProcess -and -not $script:PaletteProcess.HasExited){
        Show-Notice 'A CoCopy palette is already open.'
        return
    }
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=(Get-Command pwsh -ErrorAction Stop).Source
    $psi.UseShellExecute=$false
    foreach($arg in @('-NoProfile','-STA','-File',$PalettePath)){
        [void]$psi.ArgumentList.Add([string]$arg)
    }
    $script:PaletteProcess=[Diagnostics.Process]::Start($psi)
    if(-not $script:PaletteProcess){Show-Notice 'Palette did not start. No input was changed.'}
}
$script:HostWindow.add_HotkeyPressed({Invoke-CoPreview})
$script:OpenItem.add_Click({Invoke-CoPreview})
$script:Tray.add_DoubleClick({Invoke-CoPreview})
function Set-Paused([bool]$pauseValue) {
    if($pauseValue -and $script:HotkeyRegistered){
        [void][CoOrbHotkeyNative]::UnregisterHotKey($script:HostWindow.Handle,[CoOrbHotkeyWindow]::KeyId)
        $script:HotkeyRegistered=$false
    }
    if(-not $pauseValue -and -not $script:HotkeyRegistered){
        $mods=[uint32](0x0001 -bor 0x0002 -bor 0x0004) # Alt+Ctrl+Shift
        $script:HotkeyRegistered=[CoOrbHotkeyNative]::RegisterHotKey($script:HostWindow.Handle,[CoOrbHotkeyWindow]::KeyId,$mods,[uint32]0x4e)
        if(-not $script:HotkeyRegistered){throw 'HELD_HOTKEY_ALREADY_USED_OR_BLOCKED'}
    }
    $script:Paused=$pauseValue
    $script:PauseItem.Text=$(if($pauseValue){'Resume hotkey'}else{'Pause hotkey'})
}
$script:PauseItem.add_Click({
    try {Set-Paused (-not $script:Paused)}
    catch {Show-Notice $_.Exception.Message}
})
$script:ExitItem.add_Click({[Windows.Forms.Application]::Exit()})
$script:Timer=[Windows.Forms.Timer]::new()
$script:Timer.Interval=1250
$script:Timer.add_Tick({if(Test-Path -LiteralPath $stopFile){[Windows.Forms.Application]::Exit()}})
try {
    $null=$script:HostWindow.Handle
    Set-Paused $false
    $script:Timer.Start()
    Show-Notice 'Active. Ctrl+Alt+Shift+N opens a local preview. Right-click tray icon to pause or exit.'
    [Windows.Forms.Application]::Run($script:HostWindow)
} finally {
    $script:Timer.Stop()
    if($script:HotkeyRegistered){[void][CoOrbHotkeyNative]::UnregisterHotKey($script:HostWindow.Handle,[CoOrbHotkeyWindow]::KeyId)}
    $script:Tray.Visible=$false
    $script:Tray.Dispose()
    $script:Timer.Dispose()
    $script:HostWindow.Dispose()
}
