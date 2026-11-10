#requires -Version 7.2
<#
CoCopy+ Rich Payload Palette R0. Windows-only, user-invoked, no mouse hook.
FileDrop + UnicodeText bundle or optional bitmap, prepared on explicit click.
No automatic paste, send, network, key injection, screenshot, daemon or listener.
The shared Windows clipboard stays populated after closing only if user stages it.
#>
[CmdletBinding()]
param([switch]$SelfTest)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { throw 'WINDOWS_ONLY: use Windows 10/11 and PowerShell 7.' }
if ([System.Threading.Thread]::CurrentThread.GetApartmentState().ToString() -ne 'STA') {
    throw 'STA_REQUIRED: relaunch using pwsh -NoProfile -STA -File <path>.'
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Read only the active process name, not its window title, text, images or keys.
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CoCopyWin32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr window, out uint processId);
}
'@

function Get-CoCopyContext {
    $app = 'unknown'
    try {
        [uint32]$processId = 0
        $handle = [CoCopyWin32]::GetForegroundWindow()
        if ($handle -ne [IntPtr]::Zero) {
            [void][CoCopyWin32]::GetWindowThreadProcessId($handle, [ref]$processId)
            if ($processId -gt 0) {
                $proc = Get-Process -Id $processId -ErrorAction Stop
                $app = [string]$proc.ProcessName
            }
        }
    } catch { $app = 'unknown' }
    $point = [System.Windows.Forms.Cursor]::Position
    $screen = [System.Windows.Forms.Screen]::FromPoint($point)
    $work = $screen.WorkingArea
    $relative = ($point.X - $work.Left) / [Math]::Max(1, $work.Width)
    $region = if ($relative -lt 0.33) { 'left' } elseif ($relative -gt 0.66) { 'right' } else { 'middle' }
    [pscustomobject]@{ App=$app; Point=$point; WorkArea=$work; Region=$region }
}

function New-CoCopyDataObject([string[]]$FileNames) {
    if ($null -eq $FileNames -or $FileNames.Length -lt 1 -or $FileNames.Length -gt 24) {
        throw 'Choose 1 to 24 existing files.'
    }
    $paths = [System.Collections.Specialized.StringCollection]::new()
    $displayNames = [System.Collections.Generic.List[string]]::new()
    foreach ($name in $FileNames) {
        $full = [System.IO.Path]::GetFullPath([string]$name)
        if (-not [System.IO.File]::Exists($full)) { throw 'A selected file no longer exists.' }
        [void]$paths.Add($full)
        $displayNames.Add([System.IO.Path]::GetFileName($full))
    }
    $data = [System.Windows.Forms.DataObject]::new()
    $data.SetFileDropList($paths)
    # Human-friendly fallback for text-only apps. No full paths in this text view.
    $data.SetText(("CoCopy+ file bundle ({0} items):`r`n{1}" -f $displayNames.Count, ($displayNames -join "`r`n")), [System.Windows.Forms.TextDataFormat]::UnicodeText)
    return $data
}

if ($SelfTest) {
    $checks = [System.Collections.Generic.List[object]]::new()
    function Add-Check([string]$label, [bool]$ok) {
        $script:checks.Add([pscustomobject]@{ id=$label; result=$(if ($ok) {'PASS'} else {'FAIL'}) })
    }
    Add-Check 'Windows environment' $IsWindows
    Add-Check 'STA clipboard thread' ([System.Threading.Thread]::CurrentThread.GetApartmentState().ToString() -eq 'STA')
    Add-Check 'Windows Forms Clipboard API exists' ($null -ne [System.Windows.Forms.Clipboard].GetMethod('SetDataObject',[type[]]@([object],[bool],[int],[int])))
    Add-Check 'DataObject FileDrop supported' ($null -ne [System.Windows.Forms.DataObject].GetMethod('SetFileDropList',[type[]]@([System.Collections.Specialized.StringCollection])))
    Add-Check 'Screen context nonempty' ((Get-CoCopyContext).WorkArea.Width -gt 0)
    $bundle = New-CoCopyDataObject -FileNames @($PSCommandPath)
    Add-Check 'In-memory FileDrop representation' ($bundle.GetDataPresent([System.Windows.Forms.DataFormats]::FileDrop))
    Add-Check 'In-memory text fallback' ($bundle.GetDataPresent([System.Windows.Forms.DataFormats]::UnicodeText))
    # Never access actual clipboard or any user file content during selftest.
    $passed = @($checks | Where-Object result -eq 'PASS').Count
    [pscustomobject]@{schema='CoCopyRichPalette.LocalPreflight.R0';status=$(if($passed -eq $checks.Count){'PASS'}else{'FAIL'});passed=$passed;total=$checks.Count;tests=$checks;clipboard_changed=$false;mouse_hook=$false;network=$false} | ConvertTo-Json -Depth 5
    if ($passed -ne $checks.Count) { exit 2 }
    exit 0
}

$script:Files = [string[]]@()
$script:Context = Get-CoCopyContext
$script:Palette = [System.Windows.Forms.Form]::new()
$script:Palette.Text = 'CoCopy+ | Rich payload preview R0'
$script:Palette.ClientSize = [System.Drawing.Size]::new(690, 565)
$script:Palette.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
$script:Palette.MaximizeBox = $false
$script:Palette.MinimizeBox = $false
$script:Palette.ShowInTaskbar = $true
$script:Palette.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
$script:Palette.Font = [System.Drawing.Font]::new('Segoe UI', 10)
$script:Palette.KeyPreview = $true
$script:Palette.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::Dpi

$work = $script:Context.WorkArea
$p = $script:Context.Point
$x = [Math]::Max($work.Left, [Math]::Min($p.X + 14, $work.Right - $script:Palette.Width))
$y = [Math]::Max($work.Top, [Math]::Min($p.Y + 12, $work.Bottom - $script:Palette.Height))
$script:Palette.Location = [System.Drawing.Point]::new([int]$x,[int]$y)

$top = [System.Windows.Forms.Label]::new()
$top.Location = [System.Drawing.Point]::new(16,12)
$top.Size = [System.Drawing.Size]::new(660,50)
$top.Text = "EVO ALL BETTERS +  |  CoCopy+ CoOrbWare+`r`nVisible local preview. Nothing pasted, uploaded, sent, or captured automatically."
$script:Palette.Controls.Add($top)

$context = [System.Windows.Forms.Label]::new()
$context.Location = [System.Drawing.Point]::new(16,68)
$context.Size = [System.Drawing.Size]::new(655,22)
$context.Text = ('Foreground app: {0}  |  Screen region: {1}  |  Pointer: {2},{3}' -f $script:Context.App,$script:Context.Region,$p.X,$p.Y)
$script:Palette.Controls.Add($context)

$tabs = [System.Windows.Forms.TabControl]::new()
$tabs.Location = [System.Drawing.Point]::new(16,100)
$tabs.Size = [System.Drawing.Size]::new(655,330)
$filesTab = [System.Windows.Forms.TabPage]::new('File bundle (1-24)')
$textTab = [System.Windows.Forms.TabPage]::new('Text')
$imageTab = [System.Windows.Forms.TabPage]::new('Image pixels')
[void]$tabs.TabPages.Add($filesTab)
[void]$tabs.TabPages.Add($textTab)
[void]$tabs.TabPages.Add($imageTab)
$script:Palette.Controls.Add($tabs)

$pick = [System.Windows.Forms.Button]::new()
$pick.Text = 'Choose existing file(s)...'
$pick.Location = [System.Drawing.Point]::new(12,14)
$pick.Size = [System.Drawing.Size]::new(210,34)
$filesTab.Controls.Add($pick)

$script:FilesList = [System.Windows.Forms.ListBox]::new()
$script:FilesList.Location = [System.Drawing.Point]::new(12,60)
$script:FilesList.Size = [System.Drawing.Size]::new(615,167)
$filesTab.Controls.Add($script:FilesList)

$script:FileInfo = [System.Windows.Forms.Label]::new()
$script:FileInfo.Location = [System.Drawing.Point]::new(12,237)
$script:FileInfo.Size = [System.Drawing.Size]::new(615,34)
$script:FileInfo.Text = 'No files selected. File bundles stage references only, not duplicated bytes.'
$filesTab.Controls.Add($script:FileInfo)

$script:Editor = [System.Windows.Forms.TextBox]::new()
$script:Editor.Multiline = $true
$script:Editor.ScrollBars = [System.Windows.Forms.ScrollBars]::Vertical
$script:Editor.AcceptsReturn = $true
$script:Editor.Location = [System.Drawing.Point]::new(12,14)
$script:Editor.Size = [System.Drawing.Size]::new(615,234)
$textTab.Controls.Add($script:Editor)

$textHint = [System.Windows.Forms.Label]::new()
$textHint.Location = [System.Drawing.Point]::new(12,255)
$textHint.Size = [System.Drawing.Size]::new(615,30)
$textHint.Text = 'Only text deliberately entered here is staged. No reading another app or clipboard.'
$textTab.Controls.Add($textHint)

$imageHint = [System.Windows.Forms.Label]::new()
$imageHint.Location = [System.Drawing.Point]::new(12,17)
$imageHint.Size = [System.Drawing.Size]::new(615,95)
$imageHint.Text = "Use Choose existing file(s) on the File bundle tab, select exactly one PNG/JPEG/BMP/GIF, then choose Copy image pixels below.`r`nMaximum 32 MiB compressed file and 16 megapixels decoded. No screenshots, screen inspection or image manipulation."
$imageTab.Controls.Add($imageHint)

$contextHint = [System.Windows.Forms.Label]::new()
$contextHint.Location = [System.Drawing.Point]::new(16,438)
$contextHint.Size = [System.Drawing.Size]::new(660,42)
$contextHint.Text = 'Clipboard is shared system-wide. Stage only non-sensitive items. Return to your target app and paste manually if it supports the format.'
$script:Palette.Controls.Add($contextHint)

$script:State = [System.Windows.Forms.Label]::new()
$script:State.Location = [System.Drawing.Point]::new(16,482)
$script:State.Size = [System.Drawing.Size]::new(660,22)
$script:State.Text = 'READY: nothing staged; original mouse and clipboard are untouched.'
$script:Palette.Controls.Add($script:State)

$stageFiles = [System.Windows.Forms.Button]::new()
$stageFiles.Text = 'Stage file bundle'
$stageFiles.Location = [System.Drawing.Point]::new(16,517)
$stageFiles.Size = [System.Drawing.Size]::new(150,34)
$script:Palette.Controls.Add($stageFiles)

$stageText = [System.Windows.Forms.Button]::new()
$stageText.Text = 'Copy entered text'
$stageText.Location = [System.Drawing.Point]::new(176,517)
$stageText.Size = [System.Drawing.Size]::new(150,34)
$script:Palette.Controls.Add($stageText)

$stageImage = [System.Windows.Forms.Button]::new()
$stageImage.Text = 'Copy image pixels'
$stageImage.Location = [System.Drawing.Point]::new(336,517)
$stageImage.Size = [System.Drawing.Size]::new(155,34)
$script:Palette.Controls.Add($stageImage)

$cancel = [System.Windows.Forms.Button]::new()
$cancel.Text = 'Close (Esc)'
$cancel.Location = [System.Drawing.Point]::new(501,517)
$cancel.Size = [System.Drawing.Size]::new(170,34)
$cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$script:Palette.CancelButton = $cancel
$script:Palette.Controls.Add($cancel)

$pick.Add_Click({
    $dlg = [System.Windows.Forms.OpenFileDialog]::new()
    $dlg.Title = 'CoCopy+ R0 | Select explicit local files; nothing is sent'
    $dlg.Multiselect = $true
    $dlg.CheckFileExists = $true
    $dlg.Filter = 'All files (*.*)|*.*'
    try {
        if ($dlg.ShowDialog($script:Palette) -eq [System.Windows.Forms.DialogResult]::OK) {
            if ($dlg.FileNames.Count -gt 24) {
                [System.Windows.Forms.MessageBox]::Show('Select at most 24 files per bundle.','CoCopy+ cap') | Out-Null
                return
            }
            $script:Files = [string[]]$dlg.FileNames
            $script:FilesList.Items.Clear()
            [long]$total = 0
            foreach ($f in $script:Files) {
                $info = [System.IO.FileInfo]::new($f)
                $total += $info.Length
                [void]$script:FilesList.Items.Add(('{0} | {1:N1} MiB' -f $info.Name, ($info.Length / 1MB)))
            }
            $script:FileInfo.Text = ('Selected {0} file(s), {1:N1} MiB total. References only until a target app deliberately pastes.' -f $script:Files.Length,($total / 1MB))
            $script:State.Text = 'PREVIEW: files selected, no clipboard change yet.'
        }
    } finally { $dlg.Dispose() }
})

$stageFiles.Add_Click({
    try {
        $data = New-CoCopyDataObject -FileNames $script:Files
        [System.Windows.Forms.Clipboard]::SetDataObject($data, $true, 5, 100)
        if (-not [System.Windows.Forms.Clipboard]::ContainsFileDropList()) { throw 'Clipboard file-drop not accepted.' }
        $script:State.Text = ('STAGED: {0} file reference(s). Use manual paste in a supported target.' -f $script:Files.Length)
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'CoCopy+ FileDrop HELD') | Out-Null
    }
})
$stageText.Add_Click({
    try {
        $value = [string]$script:Editor.Text
        if ([string]::IsNullOrWhiteSpace($value)) { throw 'Enter non-empty text in the Text tab first.' }
        if ($value.Length -gt 65536) { throw 'Text preview is capped at 65,536 characters; stage a file bundle instead.' }
        [System.Windows.Forms.Clipboard]::SetText($value,[System.Windows.Forms.TextDataFormat]::UnicodeText)
        $script:State.Text = ('STAGED: {0} characters of user-entered text. No automatic paste.' -f $value.Length)
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'CoCopy+ Text HELD') | Out-Null
    }
})
$stageImage.Add_Click({
    try {
        if ($script:Files.Length -ne 1) { throw 'Choose exactly one image in the File bundle tab first.' }
        $file = $script:Files[0]
        if ([System.IO.Path]::GetExtension($file).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.bmp','.gif')) { throw 'Select PNG, JPEG, BMP or GIF only.' }
        $info = [System.IO.FileInfo]::new($file)
        if ($info.Length -gt 32MB) { throw 'Image file is above the 32 MiB decoded-preview limit.' }
        $image = [System.Drawing.Image]::FromFile($file)
        try {
            if ([long]$image.Width * [long]$image.Height -gt 16000000) { throw 'Image exceeds the 16 megapixel limit.' }
            $bitmap = [System.Drawing.Bitmap]::new($image)
            try { [System.Windows.Forms.Clipboard]::SetImage($bitmap) }
            finally { $bitmap.Dispose() }
        } finally { $image.Dispose() }
        $script:State.Text = 'STAGED: bitmap image pixels. Use manual paste in a compatible target.'
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'CoCopy+ Bitmap HELD') | Out-Null
    }
})
$script:Palette.Add_FormClosed({ $script:Files = [string[]]@() })

# Context only influences the suggested tab. Nothing auto-stages or acts on the target.
if ($script:Context.App -match '^(explorer|msedge|chrome|firefox)$') { $tabs.SelectedTab = $filesTab }
else { $tabs.SelectedTab = $textTab }

try { [void]$script:Palette.ShowDialog() }
finally { $script:Palette.Dispose() }
