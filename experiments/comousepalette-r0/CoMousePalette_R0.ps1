# CoMousePalette R0 - bounded, interactive CoCopy context palette.
# Windows PowerShell 7; use pwsh -NoProfile -STA -File <thisfile>.
# No global hooks, clipboard read until explicit button, disk writes, or network requests.
[CmdletBinding()]
param([switch]$SelfTest)

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'WINDOWS_REQUIRED' }
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'POWERSHELL_7_REQUIRED' }
if ([System.Threading.Thread]::CurrentThread.GetApartmentState().ToString() -ne 'STA') {
    throw 'STA_REQUIRED: Run pwsh -NoProfile -STA -File <path>'
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$win32Source = @'
using System;
using System.Runtime.InteropServices;
public static class CoMouseWin32 {
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
    [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(POINT p);
    [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr hwnd, uint flags);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
}
'@
Add-Type -TypeDefinition $win32Source -ErrorAction Stop

function Get-CoMode([string]$App) {
    switch -Regex ($App.ToLowerInvariant()) {
        '^(msedge|chrome|firefox|brave|vivaldi|opera)$' { return 'SOURCE / BROWSER' }
        '^(code|codium|cursor|pwsh|powershell|windowsterminal|wt|devenv|notepad\+\+)$' { return 'BUILD / CODE' }
        '^(explorer|totalcmd|files)$' { return 'FILES / LOCAL' }
        '^(whatsapp|slack|teams|discord|signal|telegram|outlook|olk)$' { return 'PRIVATE COMMUNICATION' }
        '^(bitwarden|keepass|keepassxc|1password|authy)$' { return 'PRIVACY HOLD' }
        default { return 'GENERAL / UNKNOWN' }
    }
}

function Get-CoZone([double]$XRatio,[double]$YRatio) {
    $h = if ($XRatio -lt (1.0 / 3.0)) { 'LEFT' } elseif ($XRatio -gt (2.0 / 3.0)) { 'RIGHT' } else { 'CENTER' }
    $v = if ($YRatio -lt 0.5) { 'TOP' } else { 'BOTTOM' }
    return "$h-$v"
}

function Get-CoContext {
    $pos = [System.Windows.Forms.Cursor]::Position
    $screen = [System.Windows.Forms.Screen]::FromPoint($pos)
    $bounds = $screen.WorkingArea
    $rx = [math]::Max(0,[math]::Min(1,($pos.X-$bounds.Left) / [double][math]::Max(1,$bounds.Width)))
    $ry = [math]::Max(0,[math]::Min(1,($pos.Y-$bounds.Top) / [double][math]::Max(1,$bounds.Height)))
    $pt = [CoMouseWin32+POINT]::new()
    $pt.X = $pos.X
    $pt.Y = $pos.Y
    $window = [CoMouseWin32]::GetAncestor([CoMouseWin32]::WindowFromPoint($pt), 2)
    if ($window -eq [IntPtr]::Zero) { $window = [CoMouseWin32]::GetForegroundWindow() }
    [uint32]$pidValue = 0
    $null = [CoMouseWin32]::GetWindowThreadProcessId($window, [ref]$pidValue)
    $app = 'unknown'
    if ($pidValue -gt 0) {
        try { $app = (Get-Process -Id $pidValue -ErrorAction Stop).ProcessName } catch { $app='unknown' }
    }
    return [pscustomobject]@{App=$app; Mode=(Get-CoMode $app); Zone=(Get-CoZone $rx $ry); X=$pos.X; Y=$pos.Y}
}

if ($SelfTest) {
    $cases = @(
        @('msedge','SOURCE / BROWSER'),
        @('Code','BUILD / CODE'),
        @('explorer','FILES / LOCAL'),
        @('WhatsApp','PRIVATE COMMUNICATION'),
        @('Bitwarden','PRIVACY HOLD'),
        @('somethingelse','GENERAL / UNKNOWN')
    )
    $passed=0
    foreach ($c in $cases) {
        if ((Get-CoMode $c[0]) -cne $c[1]) { throw "MODE_TEST_FAIL: $($c[0])" }
        $passed++
    }
    foreach ($v in @(@(0.1,0.1,'LEFT-TOP'),@(0.5,0.9,'CENTER-BOTTOM'),@(0.9,0.2,'RIGHT-TOP'))) {
        if ((Get-CoZone $v[0] $v[1]) -cne $v[2]) { throw "ZONE_TEST_FAIL: $($v[2])" }
        $passed++
    }
    [pscustomobject]@{
        status='PASS'; tests=$passed; windowsFormsLoaded=$true;
        win32TypeLoaded=$true; externalRequests=0;
        mouseHookInstalled=$false; globalKeyHookInstalled=$false;
        physicalThumbMapping='NOT_TESTED'
    } | ConvertTo-Json -Compress
    exit 0
}

$context = Get-CoContext
$state = [pscustomobject]@{ Loaded=$false; Truncated=$false }
$form = [System.Windows.Forms.Form]::new()
$form.Text='CoCopy+ | LOCAL PREVIEW - NOT SENT'
$form.Size=[System.Drawing.Size]::new(640,430)
$form.MinimumSize=[System.Drawing.Size]::new(580,380)
$form.StartPosition='Manual'
$form.FormBorderStyle='Sizable'
$form.TopMost=$true
$form.ShowInTaskbar=$true
$form.KeyPreview=$true

$screenBounds = [System.Windows.Forms.Screen]::FromPoint([System.Windows.Forms.Cursor]::Position).WorkingArea
$left = [math]::Min($screenBounds.Right-$form.Width,[math]::Max($screenBounds.Left,$context.X+12))
$top  = [math]::Min($screenBounds.Bottom-$form.Height,[math]::Max($screenBounds.Top,$context.Y+12))
$form.Location=[System.Drawing.Point]::new([int]$left,[int]$top)

$header = [System.Windows.Forms.Label]::new()
$header.AutoSize=$false
$header.Dock='Top'
$header.Height=68
$header.Padding=[System.Windows.Forms.Padding]::new(12,10,8,0)
$header.Text="CoCopy+ (LOCAL ONLY) | $($context.Mode)`r`nPointer: $($context.Zone)  App: $($context.App)`r`nType or press Preview clipboard deliberately; no auto-paste or recording."
$layout=[System.Windows.Forms.TableLayoutPanel]::new()
$layout.Dock='Fill'
$layout.ColumnCount=1
$layout.RowCount=3
$layout.RowStyles.Add(([System.Windows.Forms.RowStyle]::new([System.Windows.Forms.SizeType]::Absolute,68))) | Out-Null
$layout.RowStyles.Add(([System.Windows.Forms.RowStyle]::new([System.Windows.Forms.SizeType]::Percent,100))) | Out-Null
$layout.RowStyles.Add(([System.Windows.Forms.RowStyle]::new([System.Windows.Forms.SizeType]::Absolute,78))) | Out-Null
$form.Controls.Add($layout)
$layout.Controls.Add($header,0,0)

$panel=[System.Windows.Forms.FlowLayoutPanel]::new()
$panel.Dock='Fill'
$panel.Padding=[System.Windows.Forms.Padding]::new(8)
$panel.AutoScroll=$true
$layout.Controls.Add($panel,0,2)

$preview=[System.Windows.Forms.TextBox]::new()
$preview.Multiline=$true
$preview.AcceptsReturn=$true
$preview.ScrollBars='Vertical'
$preview.Dock='Fill'
$preview.Font=[System.Drawing.Font]::new('Consolas',10)
$preview.Text='' # Type here, or explicitly preview clipboard with the button below.
$layout.Controls.Add($preview,0,1)

function New-CoButton([string]$Name,[int]$Width) {
    $button=[System.Windows.Forms.Button]::new()
    $button.Text=$Name
    $button.Width=$Width
    $button.Height=35
    $button.Margin=[System.Windows.Forms.Padding]::new(3)
    $panel.Controls.Add($button)
    return $button
}

$bPreview=New-CoButton 'Preview clipboard' 127
$bCapsule=New-CoButton 'Copy capsule' 112
$bPlain=New-CoButton 'Copy text only' 112
$bClear=New-CoButton 'Clear preview' 105
$bClose=New-CoButton 'Close' 65

$bPreview.Add_Click({
    try {
        if (![System.Windows.Forms.Clipboard]::ContainsText()) {
            [System.Windows.Forms.MessageBox]::Show('Clipboard contains no text. No change made.','CoCopy+');return
        }
        $contents=[System.Windows.Forms.Clipboard]::GetText()
        $state.Truncated=$contents.Length -gt 4000
        $preview.Text=if($state.Truncated){$contents.Substring(0,4000)}else{$contents}
        $state.Loaded=$true
        if($state.Truncated){
            [System.Windows.Forms.MessageBox]::Show('Preview limited to 4,000 characters. The original clipboard is unchanged.','CoCopy+') | Out-Null
        }
    } catch {
        [System.Windows.Forms.MessageBox]::Show('Clipboard read failed; nothing sent or saved.','CoCopy+') | Out-Null
    }
})
$bCapsule.Add_Click({
    $text=$preview.Text
    if($text.Length -eq 0){return}
    $message="CoCopy+/R0 (manual review required)`r`nApp class: $($context.Mode)`r`nPointer zone: $($context.Zone)`r`nOrigin: user-previewed or user-entered content`r`nAuthority: NONE / NOT SENT`r`n---`r`n$text"
    try {
        [System.Windows.Forms.Clipboard]::SetText($message)
        $form.Text='CoCopy+ | capsule copied locally, PASTE IS YOUR CHOICE'
    } catch {
        [System.Windows.Forms.MessageBox]::Show('Clipboard write failed. No other effects.','CoCopy+') | Out-Null
    }
})
$bPlain.Add_Click({
    try {
        if ($preview.Text.Length -gt 0) { [System.Windows.Forms.Clipboard]::SetText($preview.Text) }
        $form.Text='CoCopy+ | text copied locally, PASTE IS YOUR CHOICE'
    } catch { [System.Windows.Forms.MessageBox]::Show('Clipboard write failed.','CoCopy+') | Out-Null }
})
$bClear.Add_Click({$preview.Clear();$state.Loaded=$false;$state.Truncated=$false})
$bClose.Add_Click({$form.Close()})
$form.Add_KeyDown({if($_.KeyCode -eq [System.Windows.Forms.Keys]::Escape){$form.Close()}})
$form.Add_FormClosed({$preview.Clear();$state.Loaded=$false})
try {[System.Windows.Forms.Application]::Run($form)} finally {$form.Dispose()}
