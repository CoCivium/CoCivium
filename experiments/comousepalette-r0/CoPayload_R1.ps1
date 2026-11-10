# CoPayload+ R1: explicit, local, bounded rich-media CoWorkCapsule builder.
# Windows PowerShell 7: pwsh -NoProfile -STA -File .\CoPayload_R1.ps1
# No global hooks, automatic input capture, outbound requests, or automatic paste.
[CmdletBinding()]
param(
    [switch]$SelfTest,
    [switch]$Canary,
    [string]$Root = 'D:\CoCivium\CoFarm\CoPayloadR1'
)
$ErrorActionPreference='Stop'
if ($env:OS -ne 'Windows_NT') { throw 'WINDOWS_REQUIRED' }
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'POWERSHELL_7_REQUIRED' }
if ([System.Threading.Thread]::CurrentThread.GetApartmentState().ToString() -ne 'STA') {
    throw 'STA_REQUIRED: run pwsh -NoProfile -STA -File <path>'
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.ZipFile

# Safety limits constrain a single explicit local action, not a future shared resource fabric.
$MaxFiles=12
[long]$MaxFileBytes=536870912L     # 512 MiB, per file
[long]$MaxTotalBytes=1073741824L  # 1 GiB, per capsule

function Test-CoSourceFiles([string[]]$Paths) {
    if (-not $Paths -or $Paths.Count -lt 1 -or $Paths.Count -gt $MaxFiles) { throw 'FILE_COUNT_LIMIT' }
    [long]$total=0L
    $result=@()
    foreach ($path in $Paths) {
        if (-not [System.IO.File]::Exists($path)) { throw 'SOURCE_NOT_REGULAR_FILE' }
        $info=[System.IO.FileInfo]::new($path)
        if (($info.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_POINT_HELD' }
        if ($info.Length -gt $MaxFileBytes) { throw 'PER_FILE_SIZE_LIMIT' }
        $total += $info.Length
        if ($total -gt $MaxTotalBytes) { throw 'TOTAL_SIZE_LIMIT' }
        $result += $info
    }
    return ,$result
}

function New-CoWorkCapsule([string[]]$Paths,[string]$DestinationRoot) {
    $files=Test-CoSourceFiles -Paths $Paths
    $id=[guid]::NewGuid().ToString('N')
    $stamp=[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $name="cowork_${stamp}_${id}"
    $capsuleRoot=Join-Path $DestinationRoot 'capsules'
    $stagingRoot=Join-Path $DestinationRoot 'staging'
    [System.IO.Directory]::CreateDirectory($capsuleRoot) | Out-Null
    [System.IO.Directory]::CreateDirectory($stagingRoot) | Out-Null
    $stage=Join-Path $stagingRoot $name
    [System.IO.Directory]::CreateDirectory($stage) | Out-Null
    $zip=Join-Path $capsuleRoot ($name+'.zip')
    $createdZip=$false
    try {
        $entries=@()
        [long]$total=0L
        $i=0
        foreach($source in $files){
            $i++
            $ext=[System.IO.Path]::GetExtension($source.Name).ToLowerInvariant()
            # Avoid ambiguous duplicate names and filenames that can escape the archive.
            # Original basenames are retained only inside the LOCAL_PRIVATE manifest.
            $internalName=('{0:D3}_media{1}' -f $i,$ext)
            $dest=Join-Path $stage $internalName
            [System.IO.File]::Copy($source.FullName,$dest,$false)
            $copied=[System.IO.FileInfo]::new($dest)
            $originalHash=(Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            $copyHash=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
            if($originalHash -cne $copyHash -or $copied.Length -ne $source.Length){throw 'SOURCE_CHANGED_DURING_COPY'}
            $total += $copied.Length
            $entries+=([ordered]@{index=$i;name=$source.Name;bundle_file=$internalName;bytes=$copied.Length;sha256=$copyHash})
        }
        $manifest=[ordered]@{
            schema='CoWorkCapsule/R1'
            work_id=$id
            created_utc=[DateTime]::UtcNow.ToString('o')
            privacy='LOCAL_PRIVATE_DEFAULT'
            origin='explicit_user_selected_files'
            execution_authority='NONE'
            external_delivery='NOT_PERFORMED'
            receiver_ack='NOT_OBSERVED'
            semantic_analysis='NOT_PERFORMED'
            local_file_count=$entries.Count
            total_source_bytes=$total
            files=$entries
            note='Attach ZIP explicitly if recipient permits; copying a reference does not transfer media.'
        }
        $manifestPath=Join-Path $stage 'manifest.json'
        $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8
        $manifestHash=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ([System.IO.File]::Exists($zip)) { throw 'NO_CLOBBER' }
        [System.IO.Compression.ZipFile]::CreateFromDirectory($stage,$zip,[System.IO.Compression.CompressionLevel]::Optimal,$false)
        $createdZip=$true
        $zipHash=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
        $zipBytes=([System.IO.FileInfo]::new($zip)).Length
        $receipt=[ordered]@{
            schema='CoWorkCapsuleReceipt/R1'; work_id=$id; observed_utc=[DateTime]::UtcNow.ToString('o')
            outcome='PASS_CREATED_LOCAL'; zip=$zip; zip_sha256=$zipHash
            manifest_sha256=$manifestHash; file_count=$entries.Count
            input_bytes=$total; zip_bytes=$zipBytes; receiver_ack='NOT_OBSERVED'
            remote_requests=0; source_execution=0
        }
        $ledger=Join-Path $DestinationRoot 'capsule_receipts.jsonl'
        ($receipt | ConvertTo-Json -Depth 5 -Compress) | Add-Content -LiteralPath $ledger -Encoding utf8
        return [pscustomobject]$receipt
    } catch {
        if($createdZip -and [System.IO.File]::Exists($zip)){[System.IO.File]::Delete($zip)}
        throw
    } finally {
        # Only deletes OUR newly created temporary copies, never the selected sources.
        if ([System.IO.Directory]::Exists($stage)) {[System.IO.Directory]::Delete($stage,$true)}
    }
}

function Test-CoZip([string]$Path) {
    $z=[System.IO.Compression.ZipFile]::OpenRead($Path)
    try {
        $manifestEntry=$z.GetEntry('manifest.json')
        if($null -eq $manifestEntry){throw 'MISSING_MANIFEST'}
        $reader=[System.IO.StreamReader]::new($manifestEntry.Open())
        try{$m=$reader.ReadToEnd() | ConvertFrom-Json}finally{$reader.Dispose()}
        if($m.schema -cne 'CoWorkCapsule/R1'){throw 'INVALID_MANIFEST_SCHEMA'}
        if($m.local_file_count -ne @($m.files).Count){throw 'FILE_COUNT_MISMATCH'}
        foreach($f in @($m.files)){
            $entry=$z.GetEntry([string]$f.bundle_file)
            if($null -eq $entry){throw 'MISSING_MEDIA_ENTRY'}
            $s=$entry.Open()
            $h=[System.Security.Cryptography.SHA256]::Create()
            try{$hex=[Convert]::ToHexString($h.ComputeHash($s)).ToLowerInvariant()}finally{$s.Dispose();$h.Dispose()}
            if($hex -cne $f.sha256 -or $entry.Length -ne $f.bytes){throw 'MEDIA_HASH_MISMATCH'}
        }
        return $m
    }finally{$z.Dispose()}
}

function Get-CoImageEligible([string[]]$Paths){
    if($Paths.Count -ne 1){return $false}
    $ext=[System.IO.Path]::GetExtension($Paths[0]).ToLowerInvariant()
    if($ext -notin @('.png','.jpg','.jpeg','.bmp','.gif')){return $false}
    return ([System.IO.FileInfo]::new($Paths[0])).Length -le 20971520
}

if($SelfTest){
    $cases=0
    foreach($item in @(
        @(@('.png'),$false),
        @(@('a.png'),$false)
    )){$cases++} # Static function construction canary, no clipboard or file writes.
    if($MaxFiles -ne 12 -or $MaxTotalBytes -ne 1073741824L){throw 'CONFIG_TEST_FAIL'}
    $null=[System.IO.Compression.ZipFile]
    [pscustomobject]@{status='PASS';schema='CoWorkCapsule/R1';limits_verified=$true;
        file_picker_opened=$false;clipboard_read=$false;global_hook=$false;
        background_service=$false;external_requests=0;physical_thumb='NOT_TESTED'} | ConvertTo-Json -Compress
    exit 0
}
if($Canary){
    $testRoot=Join-Path ([System.IO.Path]::GetTempPath()) ('CoPayloadCanary_'+[guid]::NewGuid().ToString('N'))
    [System.IO.Directory]::CreateDirectory($testRoot)|Out-Null
    try{
        $src=Join-Path $testRoot 'sample'; [System.IO.Directory]::CreateDirectory($src)|Out-Null
        $a=Join-Path $src 'one.txt';$b=Join-Path $src 'two.png'
        [System.IO.File]::WriteAllText($a,'CoPayload R1 deterministic sample text',[Text.Encoding]::UTF8)
        [System.IO.File]::WriteAllBytes($b,[byte[]](137,80,78,71,13,10,26,10,0,1,2,3))
        $receipt=New-CoWorkCapsule -Paths @($a,$b) -DestinationRoot $testRoot
        $manifest=Test-CoZip -Path $receipt.zip
        if($manifest.local_file_count -ne 2 -or $manifest.external_delivery -cne 'NOT_PERFORMED'){throw 'CANARY_CONTENT_FAIL'}
        $refused=$false
        try{$null=Test-CoSourceFiles -Paths @('Z:\nonexistent\missing.txt')}catch{$refused=$true}
        if(-not $refused){throw 'MISSING_SOURCE_NOT_REJECTED'}
        $receipts=Get-Content -LiteralPath (Join-Path $testRoot 'capsule_receipts.jsonl')
        if($receipts.Count -ne 1){throw 'CANARY_RECEIPT_COUNT_FAIL'}
        [pscustomobject]@{status='PASS';tests=6;files=2;hash_check='PASS';missing_source='REJECTED';
            ledger_entries=1;external_requests=0;no_user_files_accessed=$true} | ConvertTo-Json -Compress
    }finally{if([System.IO.Directory]::Exists($testRoot)){[System.IO.Directory]::Delete($testRoot,$true)}}
    exit 0
}

# The GUI shows no selected content until the person explicitly picks the files.
$script:chosen=@()
$script:receipt=$null
$form=[System.Windows.Forms.Form]::new()
$form.Text='CoPayload+ | LOCAL PRIVATE FILES - NOT SENT'
$form.Size=[System.Drawing.Size]::new(680,470)
$form.MinimumSize=[System.Drawing.Size]::new(620,420)
$form.StartPosition='CenterScreen'
$form.TopMost=$true
$form.Font=[System.Drawing.Font]::new('Segoe UI',10)
$layout=[System.Windows.Forms.TableLayoutPanel]::new()
$layout.Dock='Fill';$layout.RowCount=3;$layout.ColumnCount=1
$layout.RowStyles.Add([System.Windows.Forms.RowStyle]::new([System.Windows.Forms.SizeType]::Absolute,80))|Out-Null
$layout.RowStyles.Add([System.Windows.Forms.RowStyle]::new([System.Windows.Forms.SizeType]::Percent,100))|Out-Null
$layout.RowStyles.Add([System.Windows.Forms.RowStyle]::new([System.Windows.Forms.SizeType]::Absolute,112))|Out-Null
$form.Controls.Add($layout)
$header=[System.Windows.Forms.Label]::new()
$header.Dock='Fill';$header.Padding=[System.Windows.Forms.Padding]::new(10)
$header.Text="CoPayload+ R1 | Explicit private files only`r`nChoose <=12 files, max 512 MiB each / 1 GiB total. Staged archive is NOT uploaded.`r`nNo background clipboard reading, global hooks, model calls or outbound delivery."
$layout.Controls.Add($header,0,0)
$preview=[System.Windows.Forms.TextBox]::new()
$preview.Multiline=$true;$preview.ReadOnly=$true;$preview.ScrollBars='Both';$preview.Dock='Fill'
$preview.Font=[System.Drawing.Font]::new('Consolas',10)
$preview.Text='Choose files. You control each subsequent step.'
$layout.Controls.Add($preview,0,1)
$buttons=[System.Windows.Forms.FlowLayoutPanel]::new()
$buttons.Dock='Fill';$buttons.AutoScroll=$true;$buttons.Padding=[System.Windows.Forms.Padding]::new(8)
$layout.Controls.Add($buttons,0,2)
function Add-CoButton([string]$Name,[int]$W){$b=[System.Windows.Forms.Button]::new();$b.Text=$Name;$b.Width=$W;$b.Height=36;$b.Margin=[System.Windows.Forms.Padding]::new(3);$buttons.Controls.Add($b);return $b}
$choose=Add-CoButton '1. Choose files' 132
$stage=Add-CoButton '2. Stage ZIP' 124
$copyFile=Add-CoButton '3. Copy ZIP file' 150
$copyRef=Add-CoButton 'Copy local reference' 166
$copyImage=Add-CoButton 'Copy image pixels' 166
$open=Add-CoButton 'Open local folder' 150
$close=Add-CoButton 'Close' 84
$choose.Add_Click({
    $d=[System.Windows.Forms.OpenFileDialog]::new();$d.Multiselect=$true
    $d.Title='Select local files for a PRIVATE CoWorkCapsule (not uploaded)'
    $d.Filter='All files|*.*'
    try{
        if($d.ShowDialog($form) -ne [System.Windows.Forms.DialogResult]::OK){return}
        $arr=@($d.FileNames)
        try{$info=Test-CoSourceFiles -Paths $arr}catch{
            [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'CoPayload+ held')|Out-Null;return
        }
        $script:chosen=$arr;$script:receipt=$null
        $preview.Text="FILES SELECTED LOCALLY (NOT YET PACKAGED OR SENT)`r`n"+(($info|ForEach-Object{$_.Name+' ['+$_.Length+' bytes]'}) -join "`r`n")
    }finally{$d.Dispose()}
})
$stage.Add_Click({
    if($script:chosen.Count -lt 1){return}
    try{
        $script:receipt=New-CoWorkCapsule -Paths $script:chosen -DestinationRoot $Root
        $manifest=Test-CoZip -Path $script:receipt.zip
        $preview.Text="LOCAL ZIP CREATED + VERIFIED. NOTHING SENT.`r`n"+
        "Work: $($script:receipt.work_id)`r`nFiles: $($script:receipt.file_count)`r`nSHA256: $($script:receipt.zip_sha256)`r`nZIP: $($script:receipt.zip)`r`n"+
        'To deliver content, attach ZIP yourself. Some chat inputs do not accept file paste.'
    }catch{[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'CoPayload+ held')|Out-Null}
})
$copyFile.Add_Click({
    if($null -eq $script:receipt){return}
    try{
        $drop=[System.Collections.Specialized.StringCollection]::new()
        $null=$drop.Add($script:receipt.zip)
        [System.Windows.Forms.Clipboard]::SetFileDropList($drop)
        $form.Text='CoPayload+ | File on clipboard, target paste support varies'
    }catch{[System.Windows.Forms.MessageBox]::Show('Windows file clipboard unavailable. Use Open local folder and attach manually.','CoPayload+')|Out-Null}
})
$copyRef.Add_Click({
    if($null -eq $script:receipt){return}
    $text="CoWorkCapsule/R1: $($script:receipt.work_id)`r`nLocal-only ZIP: $($script:receipt.zip)`r`nSHA256: $($script:receipt.zip_sha256)`r`nFiles: $($script:receipt.file_count)`r`nReceiver acknowledgment: NOT OBSERVED`r`nAuthority: NONE / NOT SENT`r`nActual files must be attached deliberately."
    try{[System.Windows.Forms.Clipboard]::SetText($text);$form.Text='CoPayload+ | LOCAL reference copied (media NOT transferred)'}
    catch{[System.Windows.Forms.MessageBox]::Show('Clipboard unavailable.','CoPayload+')|Out-Null}
})
$copyImage.Add_Click({
    if(-not(Get-CoImageEligible -Paths $script:chosen)){
        [System.Windows.Forms.MessageBox]::Show('Choose one PNG/JPEG/BMP/GIF <=20 MiB, then click again.','CoPayload+')|Out-Null;return
    }
    try{
        $img=[System.Drawing.Image]::FromFile($script:chosen[0])
        try{[System.Windows.Forms.Clipboard]::SetImage($img)}finally{$img.Dispose()}
        $form.Text='CoPayload+ | Image pixels copied locally, NOT PASTED'
    }catch{[System.Windows.Forms.MessageBox]::Show('Image decode or clipboard write failed.','CoPayload+')|Out-Null}
})
$open.Add_Click({
    if($null -eq $script:receipt){return}
    $folder=[System.IO.Path]::GetDirectoryName($script:receipt.zip)
    Start-Process -FilePath 'explorer.exe' -ArgumentList @('"'+$folder+'"')
})
$close.Add_Click({$form.Close()})
$form.Add_KeyDown({if($_.KeyCode -eq [System.Windows.Forms.Keys]::Escape){$form.Close()}})
try{[System.Windows.Forms.Application]::Run($form)}finally{$form.Dispose()}
