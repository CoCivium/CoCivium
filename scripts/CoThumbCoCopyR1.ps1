#requires -Version 7.0
<#
CoThumb+ / CoCopy+ R1. Local-only, user-visible Windows canary.
No mouse remapping, auto-paste, outgoing network, clipboard reads of text,
credential reads, provider calls, background services, or file deletion.
#>
param(
    [ValidateSet('UI','Worker','SelfTest')][string]$Mode = 'UI',
    [string]$RequestFile = '',
    [string]$CoFarmRoot = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = if ($CoFarmRoot -and (Test-Path -LiteralPath $CoFarmRoot -PathType Container)) {
    Join-Path $CoFarmRoot 'CoThumbR1'
} elseif ($CoFarmRoot) {
    throw 'HOLD: requested CoFarm test root does not exist.'
} elseif (Test-Path -LiteralPath 'D:\CoCivium\CoFarm' -PathType Container) {
    'D:\CoCivium\CoFarm\CoThumbR1'
} elseif (Test-Path -LiteralPath 'C:\CoCivium\CoFarm' -PathType Container) {
    'C:\CoCivium\CoFarm\CoThumbR1'
} else {
    throw 'HOLD: CoFarm root not found. Nothing installed or remapped.'
}
[void][IO.Directory]::CreateDirectory($root)
$utf8 = [Text.UTF8Encoding]::new($false)

function New-RunFolder {
    $id = 'run_' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ') + '_' + [Guid]::NewGuid().ToString('N').Substring(0,8)
    $path = Join-Path $root $id
    if (Test-Path -LiteralPath $path) { throw 'Run collision; no clobber.' }
    [void][IO.Directory]::CreateDirectory($path)
    return $path
}
function Write-NewText([string]$path,[string]$text) {
    $bytes = $utf8.GetBytes($text)
    $file = [IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $file.Write($bytes,0,$bytes.Length) } finally { $file.Dispose() }
    $readback = [IO.File]::ReadAllBytes($path)
    $originalHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
    $readbackHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($readback))
    if ($readback.Length -ne $bytes.Length -or $readbackHash -ne $originalHash) {
        throw 'HOLD: exact local file readback differs.'
    }
}
function Save-NewJson([string]$path,$obj) {
    Write-NewText $path (($obj | ConvertTo-Json -Depth 18) + [Environment]::NewLine)
}
function Kind-Of([string]$extension) {
    switch ($extension.ToLowerInvariant()) {
        { $_ -in @('.mp4','.mkv','.mov','.webm','.avi') } { return 'VIDEO' }
        { $_ -in @('.mp3','.wav','.m4a','.flac','.ogg') } { return 'AUDIO' }
        { $_ -in @('.jpg','.jpeg','.png','.webp','.gif','.tif','.tiff') } { return 'IMAGE' }
        { $_ -in @('.pdf','.docx','.txt','.md','.rtf','.odt') } { return 'DOCUMENT' }
        { $_ -in @('.zip','.7z','.tar','.gz') } { return 'ARCHIVE' }
        { $_ -in @('.ps1','.py','.js','.json','.html','.css','.cs') } { return 'SOURCE' }
        default { return 'FILE' }
    }
}
function Lane-Plan([string]$kind) {
    $base = @('SOURCE_INTEGRITY','PROVENANCE','PRIVATE_RISK_REVIEW','RELATION_MAP','RECOVERY_POINTER')
    $extra = switch ($kind) {
        VIDEO { @('FFPROBE','BLACKDETECT','THUMBNAIL','TRANSCRIPT','CAPTIONS','RIGHTS_REVIEW') }
        AUDIO { @('AUDIO_METADATA','TRANSCRIPT','WAVEFORM','RIGHTS_REVIEW') }
        IMAGE { @('DIMENSIONS','ALT_TEXT','THUMBNAIL','RIGHTS_REVIEW') }
        DOCUMENT { @('TEXT_EXTRACTION','CITATION_CHECK','ACCESSIBILITY') }
        ARCHIVE { @('ARCHIVE_INVENTORY','MALWARE_REVIEW') }
        SOURCE { @('STATIC_TEST','LICENSE_REVIEW','SECURITY_REVIEW') }
        default { @('FORMAT_REVIEW') }
    }
    $all = @($base) + @($extra)
    return $all | ForEach-Object {
        [ordered]@{ lane = $_; state = 'PROPOSED_ONLY'; executed = $false; receiver_ack = $false }
    }
}
function Process-Request([string]$path) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'Missing request.' }
    $folder = Split-Path -Parent $path
    $folderAbs = [IO.Path]::GetFullPath($folder)
    $rootAbs = [IO.Path]::GetFullPath($root)
    if (-not $folderAbs.StartsWith($rootAbs + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Request outside CoThumbR1 root.'
    }
    $request = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($request.schema -ne 'CoThumb.CoCopyRequest.R1' -or
        $request.mode -notin @('REFERENCE_ONLY','STAGE_BYTES') -or
        @($request.paths).Count -lt 1 -or @($request.paths).Count -gt 4) {
        throw 'HOLD: request schema, count, or staging authority invalid.'
    }
    $rows = @()
    $plans = @()
    $budget = 0L
    foreach ($sourcePath in @($request.paths)) {
        $entry = [ordered]@{ source_path_private = [string]$sourcePath; state = 'FAIL'; kind = 'UNKNOWN'; size_bytes = $null; sha256 = $null; staged_file_private = $null; error = $null }
        try {
            $f = Get-Item -LiteralPath ([string]$sourcePath) -ErrorAction Stop
            if ($f -isnot [IO.FileInfo]) { throw 'Not a regular file.' }
            if (($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point needs separate approval.' }
            if ($f.Length -gt 16GB) { throw 'Over 16 GiB hashing budget; use explicit large-file workflow.' }
            $budget += $f.Length
            if ($budget -gt 16GB) { throw 'Aggregate source hashing budget exceeded.' }
            $beforeLength = [int64]$f.Length
            $beforeTicks = $f.LastWriteTimeUtc.Ticks
            $kind = Kind-Of $f.Extension
            $digest = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            $later = Get-Item -LiteralPath $f.FullName
            if ($later.Length -ne $beforeLength -or $later.LastWriteTimeUtc.Ticks -ne $beforeTicks) {
                throw 'Source changed while hashing. Do not promote.'
            }
            $entry.size_bytes = $beforeLength
            $entry.kind = $kind
            $entry.sha256 = $digest
            if ($request.mode -eq 'STAGE_BYTES') {
                if ($budget -gt 2GB) { throw 'Aggregate staged-copy budget is 2 GiB.' }
                if ($beforeLength -gt 2GB) { throw 'File exceeds explicit 2 GiB staging cap.' }
                $dst = Join-Path $folder ('asset_' + ('{0:D2}' -f ($rows.Count+1)) + $f.Extension.ToLowerInvariant())
                $inStream = [IO.File]::Open($f.FullName,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
                try {
                    $outStream = [IO.File]::Open($dst,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
                    try { $inStream.CopyTo($outStream,1048576) } finally { $outStream.Dispose() }
                } finally { $inStream.Dispose() }
                $dstHash = (Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLowerInvariant()
                $dstBytes = (Get-Item -LiteralPath $dst).Length
                if ($dstHash -ne $digest -or $dstBytes -ne $beforeLength) {
                    throw 'Exact staged bytes differ; unqualified output retained for inspection.'
                }
                $entry.staged_file_private = $dst
            }
            $entry.state = if ($request.mode -eq 'STAGE_BYTES') { 'STAGED_LOCAL_VERIFIED' } else { 'SOURCE_HASHED_LOCAL' }
            $plans += [ordered]@{ source_sha256 = $digest; kind = $kind; proposed = @(Lane-Plan $kind) }
        } catch {
            $entry.error = [string]$_.Exception.Message
        }
        $rows += $entry
    }
    $overall = if (@($rows | Where-Object { $_.state -eq 'FAIL' }).Count -eq 0) { 'PASS_LOCAL' } else { 'FAIL_OR_HELD' }
    $proposalTotal = 0
    foreach ($candidate in $plans) { $proposalTotal += @($candidate.proposed).Count }
    $capsule = [ordered]@{
        schema = 'CoThumb.CoCopyCapsule.R1'; run_id = Split-Path $folder -Leaf
        observed_utc = [DateTime]::UtcNow.ToString('o')
        state = $overall; locality = 'PRIVATE_COFARM_ONLY'
        mode = [string]$request.mode; selected_files = @($rows)
        mouse_context = $request.context
        proposed_lane_groups = @($plans)
        proposal_count = $proposalTotal
        executed_derivative_lanes = 0; parallel_worker_ceiling = 1
        permissions = [ordered]@{ network = $false; external_send = $false; paste_into_app = $false; use_credentials = $false; alter_mouse_mapping = $false }
        receiver_ack = $false; CoStead_landed = $false; canon = $false; CoEx = $false
        nonclaims = @('GESTURE_NE_AUTHORITY','COPY_NE_SEND','CAPSULE_NE_DELIVERY','LOCAL_IS_NOT_LANDED','HASH_NE_SEMANTIC_ACCEPTANCE','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF')
    }
    $capsulePath = Join-Path $folder 'capsule.json'
    Save-NewJson $capsulePath $capsule
    $capsuleHash = (Get-FileHash -LiteralPath $capsulePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $receipt = [ordered]@{ schema='CoThumb.LocalReceipt.R1'; observed_utc=[DateTime]::UtcNow.ToString('o'); state=$overall; capsule_sha256=$capsuleHash; capsule_path_private=$capsulePath; source_count=@($rows).Count; source_pass_count=@($rows | Where-Object { $_.state -ne 'FAIL' }).Count; exact_file_readback=$true; receiver_ack=$false; external_sends=0; note='Local only. Actual hardware mouse binding not independently verified.' }
    Save-NewJson (Join-Path $folder 'receipt.json') $receipt
    $line = [ordered]@{ schema='CoThumb.BenchmarkEvo.R1'; state=$overall; run_id=$capsule.run_id; test='bounded_rich_media_capsule'; pass=$receipt.source_pass_count; total=$receipt.source_count; capsule_sha256=$capsuleHash; physical_button_verified=$false; external_effects=0 }
    Write-NewText (Join-Path $folder 'benchmark_evo.jsonl') (($line | ConvertTo-Json -Compress -Depth 8) + [Environment]::NewLine)
    return $receipt
}
if ($Mode -eq 'Worker') {
    $result = Process-Request $RequestFile
    $result | ConvertTo-Json -Compress -Depth 6
    if ($result.state -ne 'PASS_LOCAL') { exit 2 }
    exit 0
}
if ($Mode -eq 'SelfTest') {
    $run = New-RunFolder
    $sample = Join-Path $run 'fixture.txt'
    Write-NewText $sample 'CoThumb synthetic local fixture; never external.'
    $request = [ordered]@{ schema='CoThumb.CoCopyRequest.R1'; paths=@($sample); mode='REFERENCE_ONLY'; context=[ordered]@{ kind='SELFTEST'; region='UNOBSERVED'; source='explicit_cli'; stores_coordinates=$false } }
    $p = Join-Path $run 'request.json'
    Save-NewJson $p $request
    $receipt = Process-Request $p
    $capsule = Get-Content -LiteralPath (Join-Path $run 'capsule.json') -Raw | ConvertFrom-Json
    if ($receipt.state -ne 'PASS_LOCAL' -or @($capsule.selected_files).Count -ne 1 -or $capsule.selected_files[0].sha256 -ne (Get-FileHash -LiteralPath $sample -Algorithm SHA256).Hash.ToLowerInvariant() -or $capsule.executed_derivative_lanes -ne 0) { throw 'FAIL_SYNTHETIC_SELFTEST' }
    [pscustomobject]@{state='PASS_SYNTHETIC_LOCAL';run=$run;receipt=(Join-Path $run 'receipt.json');proposals=$capsule.proposal_count;mouse_binding='NOT_TESTED'} | ConvertTo-Json -Compress
    exit 0
}
if (-not $IsWindows) { throw 'UI requires Windows and pwsh -STA. No device changes performed.' }
if ([Threading.Thread]::CurrentThread.GetApartmentState() -ne [Threading.ApartmentState]::STA) {
    throw 'HOLD: UI requires an STA thread. Run pwsh -STA -NoProfile -File SCRIPT -Mode UI'
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CoThumbNative {
  [StructLayout(LayoutKind.Sequential)] public struct Point { public int X; public int Y; }
  [StructLayout(LayoutKind.Sequential)] public struct Rect { public int Left; public int Top; public int Right; public int Bottom; }
  [DllImport("user32.dll")] public static extern short GetAsyncKeyState(int key);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr window, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out Point point);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr window, out Rect rect);
}
'@
[Windows.Forms.Application]::EnableVisualStyles()
$form = [Windows.Forms.Form]::new()
$form.Text = 'CoThumb+ | CoCopy+ R1 | LOCAL ONLY'
$form.Size = [Drawing.Size]::new(720,510)
$form.StartPosition = 'CenterScreen'
$form.TopMost = $false
$form.AllowDrop = $true
$script:chosen = @()
$script:armed = $false
$script:wasDown = $false
$script:activeJob = $null
$script:lastRun = $null
$script:context = [ordered]@{ kind='EXPLICIT_PICKER'; region='NOT_OBSERVED'; source='visible_ui'; stores_coordinates=$false }
$script:scriptFile = $PSCommandPath
function Make-Label([string]$txt,[int]$x,[int]$y,[int]$w,[int]$h) {
    $c = [Windows.Forms.Label]::new();$c.Text=$txt;$c.SetBounds($x,$y,$w,$h);$form.Controls.Add($c);return $c
}
function Make-Button([string]$txt,[int]$x,[int]$y,[int]$w,[int]$h) {
    $b=[Windows.Forms.Button]::new();$b.Text=$txt;$b.SetBounds($x,$y,$w,$h);$form.Controls.Add($b);return $b
}
[void](Make-Label 'One gesture proposes a rich local capsule. No automatic upload, paste, execution or mouse remap.' 15 12 675 38)
$selection = Make-Label 'No file selected. Choose or copy file(s) from Windows Explorer.' 15 56 676 45
$picker = Make-Button 'Choose file(s)' 15 106 145 34
$clipboard = Make-Button 'Use copied files' 170 106 145 34
$copyBytes = [Windows.Forms.CheckBox]::new()
$copyBytes.Text='Stage actual bytes (2 GiB total, explicit approval)'
$copyBytes.SetBounds(15,153,650,26)
$form.Controls.Add($copyBytes)
$preview = Make-Label 'Default: hash source and save a PRIVATE pointer only. No file duplication.' 15 186 660 48
$submit = Make-Button 'Create local capsule' 15 237 210 40
$folderButton = Make-Button 'Open capsule folder' 240 237 180 40
$folderButton.Enabled = $false
[void](Make-Label 'Optional physical input observer. OFF unless you arm it. Native click remains unchanged.' 15 290 670 30)
$buttons = [Windows.Forms.ComboBox]::new()
$buttons.DropDownStyle='DropDownList'
$buttons.Items.AddRange([object[]]@('Ctrl+Alt+Shift+F12','XBUTTON2 thumb','XBUTTON1 thumb','MBUTTON wheel'))
$buttons.SelectedIndex=0
$buttons.SetBounds(15,321,245,29)
$form.Controls.Add($buttons)
$armButton = Make-Button 'Arm preview' 276 321 145 29
$contextLabel = Make-Label 'Context: not observed. Position is only a hint, never permission.' 15 359 668 34
$status = Make-Label 'Status: ready. Capture is explicit and private.' 15 407 665 55
function Set-Files($paths) {
    $script:chosen = @($paths | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -First 4)
    if ($script:chosen.Count) {
        $selection.Text = ('Selected: ' + (($script:chosen | ForEach-Object { [IO.Path]::GetFileName($_) }) -join ', '))
        $preview.Text = "Will make $($script:chosen.Count) verified local reference(s), with optional staged bytes."
    } else { $selection.Text='No readable regular files selected.' }
}
$picker.Add_Click({
    $dialog = [Windows.Forms.OpenFileDialog]::new()
    $dialog.Multiselect = $true
    $dialog.Filter='All files (*.*)|*.*'
    if ($dialog.ShowDialog($form) -eq [Windows.Forms.DialogResult]::OK) { Set-Files $dialog.FileNames }
    $dialog.Dispose()
})
$clipboard.Add_Click({
    try {
        if ([Windows.Forms.Clipboard]::ContainsFileDropList()) {
            $files = [Windows.Forms.Clipboard]::GetFileDropList()
            Set-Files @($files)
        } else {
            $status.Text='Clipboard contains no Explorer file list. No text or secrets were inspected.'
        }
    } catch { $status.Text='Clipboard not readable in this session. Use Choose file(s).' }
})
$form.Add_DragEnter({
    param($sender,$e)
    if ($e.Data.GetDataPresent([Windows.Forms.DataFormats]::FileDrop)) { $e.Effect=[Windows.Forms.DragDropEffects]::Copy }
})
$form.Add_DragDrop({
    param($sender,$e)
    $files=$e.Data.GetData([Windows.Forms.DataFormats]::FileDrop)
    Set-Files @($files)
})
function Observe-Context {
    $hwnd = [CoThumbNative]::GetForegroundWindow()
    $processId = [uint32]0
    [void][CoThumbNative]::GetWindowThreadProcessId($hwnd,[ref]$processId)
    $procName='unknown'
    try { $procName=(Get-Process -Id ([int]$processId) -ErrorAction Stop).ProcessName.ToLowerInvariant() } catch {}
    $class = if ($procName -eq 'explorer') {'EXPLORER'} elseif($procName -in @('msedge','chrome','firefox','brave')) {'BROWSER'} elseif ($procName -in @('code','notepad','pwsh','powershell')) {'EDITOR'} else {'OTHER'}
    $pt=[CoThumbNative+Point]::new();$rect=[CoThumbNative+Rect]::new()
    $region='UNKNOWN'
    if ([CoThumbNative]::GetCursorPos([ref]$pt) -and [CoThumbNative]::GetWindowRect($hwnd,[ref]$rect)) {
        $height=$rect.Bottom-$rect.Top
        if ($height -gt 0) {
            $position=($pt.Y-$rect.Top)/$height
            if ($position -lt 0 -or $position -gt 1) { $region='OUTSIDE' }
            elseif ($position -lt .25) { $region='TOP' }
            elseif ($position -gt .75) { $region='BOTTOM' }
            else { $region='CENTRE' }
        }
    }
    $script:context=[ordered]@{kind=$class;region=$region;source='opt_in_thumb_preview';stores_coordinates=$false;stores_window_title=$false}
    $contextLabel.Text="Context hint: $class / $region. No selected text, pixels, secrets or window title read."
    $form.WindowState='Normal';$form.Activate()
    $status.Text='Thumb gesture observed. Preview only: pick or use Explorer-copied files, then explicitly create capsule.'
}
$armButton.Add_Click({
    $script:armed = -not $script:armed
    $script:wasDown = $false
    $armButton.Text = if ($script:armed) { 'Disarm preview' } else { 'Arm preview' }
    $status.Text = if ($script:armed) { 'ARMED and visible. Input observed only to open preview. Close to stop.' } else { 'DISARMED: normal mouse and shortcuts only.' }
})
$submit.Add_Click({
    if ($script:activeJob -and $script:activeJob.State -eq 'Running') { $status.Text='A local capsule job is already running.';return }
    if ($script:chosen.Count -eq 0) { $status.Text='Choose one or more files first. No action taken.';return }
    $mode=if($copyBytes.Checked){'STAGE_BYTES'}else{'REFERENCE_ONLY'}
    if ($mode -eq 'STAGE_BYTES') {
        $choice=[Windows.Forms.MessageBox]::Show($form,'Create private duplicate bytes under CoFarm? No external sends. Up to 2 GiB total per gesture.','Explicit rich-media staging consent',[Windows.Forms.MessageBoxButtons]::YesNo,[Windows.Forms.MessageBoxIcon]::Question)
        if ($choice -ne [Windows.Forms.DialogResult]::Yes) { $status.Text='Staging cancelled; no source changed.';return }
    }
    $run=New-RunFolder
    $request=[ordered]@{schema='CoThumb.CoCopyRequest.R1';paths=@($script:chosen);mode=$mode;context=$script:context}
    $requestPath=Join-Path $run 'request.json'
    Save-NewJson $requestPath $request
    $script:lastRun=$run
    $folderButton.Enabled=$true
    $script:activeJob=Start-Job -ScriptBlock { param($file,$r,$cf) & $file -Mode Worker -RequestFile $r -CoFarmRoot $cf } -ArgumentList $script:scriptFile,$requestPath,(Split-Path $root -Parent)
    $status.Text="Processing selected files locally in a bounded worker. Work ID: $(Split-Path $run -Leaf)"
})
$folderButton.Add_Click({
    if ($script:lastRun -and (Test-Path -LiteralPath $script:lastRun)) { Start-Process -FilePath 'explorer.exe' -ArgumentList @($script:lastRun) }
})
function Key-IsDown([int]$virtualKey) { return (([int][CoThumbNative]::GetAsyncKeyState($virtualKey) -band 0x8000) -ne 0) }
$timer=[Windows.Forms.Timer]::new();$timer.Interval=90
$timer.Add_Tick({
    if ($script:armed) {
        $pressed = switch ($buttons.SelectedIndex) {
            1 { Key-IsDown 0x06 }
            2 { Key-IsDown 0x05 }
            3 { Key-IsDown 0x04 }
            default { (Key-IsDown 0x7B) -and (Key-IsDown 0x10) -and (Key-IsDown 0x11) -and (Key-IsDown 0x12) }
        }
        if ($pressed -and -not $script:wasDown) { $script:wasDown=$true;Observe-Context }
        elseif (-not $pressed) { $script:wasDown=$false }
    }
    if ($script:activeJob -and $script:activeJob.State -ne 'Running') {
        $state=$script:activeJob.State
        $details=@(Receive-Job -Job $script:activeJob -ErrorAction SilentlyContinue)
        $script:activeJob | Remove-Job -Force
        $script:activeJob=$null
        if (Test-Path -LiteralPath (Join-Path $script:lastRun 'receipt.json')) {
            $receipt=Get-Content -LiteralPath (Join-Path $script:lastRun 'receipt.json') -Raw | ConvertFrom-Json
            $status.Text="Local receipt: $($receipt.state); passed $($receipt.source_pass_count)/$($receipt.source_count). Review: $($script:lastRun)"
        } else { $status.Text="Worker ended $state without an exact receipt. HOLD. Review folder; do not claim success." }
    }
})
$form.Add_FormClosing({
    param($sender,$e)
    if ($script:activeJob -and $script:activeJob.State -eq 'Running') {
        $choice=[Windows.Forms.MessageBox]::Show($form,'A local file hashing/copying job is still running. Stop it? Its incomplete outputs remain unqualified.','Close CoThumb R1',[Windows.Forms.MessageBoxButtons]::YesNo,[Windows.Forms.MessageBoxIcon]::Warning)
        if ($choice -ne [Windows.Forms.DialogResult]::Yes) { $e.Cancel=$true;return }
        Stop-Job -Job $script:activeJob -ErrorAction SilentlyContinue
        $script:activeJob | Remove-Job -Force
        $script:activeJob=$null
    }
    $script:armed=$false
    $timer.Stop()
})
$timer.Start()
[void][Windows.Forms.Application]::Run($form)
