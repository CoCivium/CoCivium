# CoCopy+ / CoMousePalette R0a. Paste once into PS7 on X2. No administrator rights.
$ErrorActionPreference = 'Stop'
$base = 'D:\CoCivium\CoFarm'
if (-not (Test-Path -LiteralPath $base -PathType Container)) { throw "Expected CoFarm root missing: $base" }
$dir = Join-Path $base 'CoMousePalette_R0'
if (-not (Test-Path -LiteralPath $dir)) { $null = New-Item -ItemType Directory -Path $dir }
$file = Join-Path $dir 'CoMousePalette_R0.ps1'
$url = 'https://raw.githubusercontent.com/CoCivium/CoCivium/ebca7fbb98b155be45eeedadccedcd5db3ca1bb4/experiments/comousepalette-r0/CoMousePalette_R0.ps1'
if (-not (Test-Path -LiteralPath $file)) { Invoke-WebRequest -Uri $url -OutFile $file }
$expected = '7822f9619ec212175bd4099e9fe94b3c681c8f9c2a01c16525af0a3061f8ce6d'
$actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "HALT: source hash mismatch. Existing file preserved: $file" }
$exe = (Get-Command pwsh.exe -ErrorAction Stop).Source
$check = & $exe -NoLogo -NoProfile -STA -File $file -SelfTest | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $check.status -ne 'PASS' -or $check.tests -ne 9) { throw 'HALT: Windows self-test did not pass' }
$cmd = Join-Path $dir 'Open-CoCopyPalette.cmd'
if (-not (Test-Path -LiteralPath $cmd)) {
    $text = '@echo off' + "`r`n" + 'start "" "' + $exe + '" -NoLogo -NoProfile -STA -WindowStyle Hidden -File "' + $file + '"' + "`r`n"
    [System.IO.File]::WriteAllText($cmd,$text,[System.Text.Encoding]::ASCII)
}
$receipt = [ordered]@{
  at_utc=[DateTime]::UtcNow.ToString('o'); wave='CoMousePalette_R0a'; status='PASS_LOCAL_SELFTEST';
  source_sha256=$actual; tests=$check.tests; physical_button='NOT_RUN'; outbound='NONE_IN_SCRIPT'
} | ConvertTo-Json -Compress
Add-Content -LiteralPath (Join-Path $dir 'evo.jsonl') -Value $receipt -Encoding utf8
Start-Process -FilePath $exe -ArgumentList @('-NoLogo','-NoProfile','-STA','-WindowStyle','Hidden','-File',('"'+$file+'"'))
Write-Host "PASS: CoCopy preview opened. Close or Esc to exit. For optional MX4 Actions Ring assignment use: $cmd"
