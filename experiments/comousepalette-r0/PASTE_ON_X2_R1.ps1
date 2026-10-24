# CoCopy+ high-payload R1. Paste into an EXISTING PS7 prompt on X2, no admin rights.
# Stages two pinned scripts in a new append-only CoFarm directory, verifies bytes, runs offline tests,
# and opens a visible palette. Does NOT rebind your mouse or send any data.
$ErrorActionPreference='Stop'
if($env:OS -ne 'Windows_NT'){throw 'WINDOWS_REQUIRED'}
if($PSVersionTable.PSVersion.Major -lt 7){throw 'POWERSHELL_7_REQUIRED'}
$base='D:\CoCivium\CoFarm'
if(-not(Test-Path -LiteralPath $base -PathType Container)){throw "Expected CoFarm does not exist: $base"}
$dir=Join-Path $base 'CoMousePalette_R1'
[System.IO.Directory]::CreateDirectory($dir)|Out-Null
$revision='745d8de07e25ce60554efff31a3389a5926bb5d8'
$source="https://raw.githubusercontent.com/CoCivium/CoCivium/$revision/experiments/comousepalette-r0"
$files=@(
    [pscustomobject]@{Name='CoMousePalette_R0.ps1';GitBlob='7622ed69aa314b45cec804739ef560ad7dfc4351';Sha256=''},
    [pscustomobject]@{Name='CoPayload_R1.ps1';GitBlob='2a8e731aebba60eb21d29c06ed7bf8ee3ebfc95f';Sha256='6204c8c86405272a72e499ca74bff12653d2ac1bf51d58f60deaed7f4d883e2f'}
)
function Get-CoGitBlob([string]$Path){
    [byte[]]$bytes=[System.IO.File]::ReadAllBytes($Path)
    [byte[]]$header=[System.Text.Encoding]::ASCII.GetBytes('blob '+$bytes.Length+[char]0)
    [byte[]]$combined=New-Object byte[] ($header.Length+$bytes.Length)
    [Array]::Copy($header,0,$combined,0,$header.Length)
    [Array]::Copy($bytes,0,$combined,$header.Length,$bytes.Length)
    return [Convert]::ToHexString([System.Security.Cryptography.SHA1]::HashData($combined)).ToLowerInvariant()
}
function Assert-CoFile([string]$Path,$Expected){
    if(-not(Test-Path -LiteralPath $Path -PathType Leaf)){throw 'MISSING_DOWNLOADED_SOURCE'}
    if((Get-CoGitBlob $Path) -cne $Expected.GitBlob){throw "HALT_GIT_SOURCE_HASH: $Path"}
    if($Expected.Sha256){
        $got=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if($got -cne $Expected.Sha256){throw "HALT_SHA256: $Path"}
    }
}
foreach($item in $files){
    $target=Join-Path $dir $item.Name
    if(-not(Test-Path -LiteralPath $target -PathType Leaf)){
        $tmp=Join-Path $dir ('.download_'+[guid]::NewGuid().ToString('N'))
        try{
            Invoke-WebRequest -Uri ($source+'/'+$item.Name) -OutFile $tmp -MaximumRedirection 3 -ErrorAction Stop
            Assert-CoFile -Path $tmp -Expected $item
            [System.IO.File]::Move($tmp,$target) # no clobber
        }finally{if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Force}}
    }
    Assert-CoFile -Path $target -Expected $item
}
$exe=(Get-Command pwsh -ErrorAction Stop).Source
$palette=Join-Path $dir 'CoMousePalette_R0.ps1'
$payload=Join-Path $dir 'CoPayload_R1.ps1'
$original=& $exe -NoLogo -NoProfile -STA -File $palette -SelfTest | ConvertFrom-Json
if($LASTEXITCODE -ne 0 -or $original.status -ne 'PASS' -or $original.tests -ne 9){throw 'ORIGINAL_SELFTEST_FAILED'}
$check=& $exe -NoLogo -NoProfile -STA -File $payload -SelfTest | ConvertFrom-Json
if($LASTEXITCODE -ne 0 -or $check.status -ne 'PASS' -or $check.clipboard_read -ne $false){throw 'PAYLOAD_SELFTEST_FAILED'}
$canary=& $exe -NoLogo -NoProfile -STA -File $payload -Canary | ConvertFrom-Json
if($LASTEXITCODE -ne 0 -or $canary.status -ne 'PASS' -or $canary.hash_check -ne 'PASS'){throw 'PAYLOAD_CANARY_FAILED'}
$launcher=Join-Path $dir 'Open-CoCopy-R1.cmd'
if(-not(Test-Path -LiteralPath $launcher)){
    $body='@echo off'+"`r`n"+'start "" "'+$exe+'" -NoLogo -NoProfile -STA -WindowStyle Hidden -File "'+$palette+'"'+"`r`n"
    [System.IO.File]::WriteAllText($launcher,$body,[System.Text.Encoding]::ASCII)
}
$receipt=[ordered]@{schema='CoMousePaletteR1InstallReceipt/1';at_utc=[DateTime]::UtcNow.ToString('o');
    commit=$revision;source_verified=$true;selftests='PASS';payload_canary='PASS';
    physical_mouse='NOT_TESTED';remote_receiver='NOT_OBSERVED';outbound_payloads=0;
    installed_files=@($files|ForEach-Object{$_.Name})}
($receipt|ConvertTo-Json -Compress -Depth 5)|Add-Content -LiteralPath (Join-Path $dir 'evo.jsonl') -Encoding utf8
Start-Process -FilePath $exe -ArgumentList @('-NoLogo','-NoProfile','-STA','-WindowStyle','Hidden','-File',('"'+$palette+'"')) -ErrorAction Stop
Write-Host "PASS: visible CoCopy+ R1 opened. Choose 'Rich files...' to stage large media locally."
Write-Host "OPTIONAL mouse mapping target (manually set in Logitech Options+): $launcher"
Write-Host 'X2 button gesture and actual app paste still require physical testing; nothing was sent.'
