#requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$utc=[DateTime]::UtcNow
$stamp=$utc.ToString('yyyyMMddTHHmmssfffffffZ')
$roots=@('D:\CoCivium','C:\CoCivium','D:\PS7','C:\PS7') | Where-Object { Test-Path $_ }
$base=@('D:\CoCivium\CoFarm','C:\CoCivium\CoFarm') | Where-Object { Test-Path (Split-Path $_ -Parent) } | Select-Object -First 1
if(-not $base){throw 'NO_COCIVIUM_ROOT'}
$out=Join-Path $base "CoParticipantEdge\R0B_X2_Discovery\$stamp"
New-Item -ItemType Directory -Path $out -Force | Out-Null
$terms=@('RickBar','NickBar','CoBar','CoDesktop','CoEyes','CoFleet','DesktopCommander','Desktop Commander','CoCivium.exe')
$proc=Get-Process -ErrorAction SilentlyContinue | ForEach-Object {
  $p=$_;$path=$null;try{$path=$p.Path}catch{}
  [pscustomobject]@{name=$p.ProcessName;id=$p.Id;path=$path;title=$p.MainWindowTitle}
} | Where-Object {
  $s=(($_.name,$_.path,$_.title)-join ' ')
  @($terms | Where-Object {$s -like "*$_*"}).Count -gt 0
}
$hits=@()
foreach($root in $roots){
  $hits += Get-ChildItem -LiteralPath $root -File -Depth 5 -ErrorAction SilentlyContinue |
    Where-Object {$_.FullName -match 'RickBar|NickBar|CoBar|CoDesktop|CoEyes|CoFleet|DesktopCommander|CoCivium'} |
    Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 500 |
    ForEach-Object {
      $sha=$null;try{$sha=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}catch{}
      [pscustomobject]@{path=$_.FullName;bytes=$_.Length;lastWriteUtc=$_.LastWriteTimeUtc.ToString('o');sha256=$sha}
    }
}
$obj=[ordered]@{
  schema='CoAll.ParticipantEdge.X2Discovery.R0B.v0.1'
  observed_at_utc=$utc.ToString('o')
  machine=$env:COMPUTERNAME
  roots=$roots
  processes=@($proc)
  file_hits=@($hits)
  authority='READ_ONLY_DISCOVERY__APPEND_ONLY_RECEIPT'
  next='RECONCILE_RICKBAR_NICKBAR_COEYES_LOCAL_LINEAGE'
  nonclaims=@('LOCAL_IS_NOT_LANDED','PROCESS_PRESENT_NE_PRODUCT_HEALTHY','DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY','HASHING_IS_NOT_SEMANTIC_INGESTION')
}
$j=Join-Path $out 'inventory.json'
$obj | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $j -Encoding utf8NoBOM
$sha=(Get-FileHash -LiteralPath $j -Algorithm SHA256).Hash
$r=[ordered]@{state='PASS_BOUNDED_X2_PARTICIPANT_EDGE_DISCOVERY';inventory=$j;sha256=$sha;processes=@($proc).Count;file_hits=@($hits).Count}
$rp=Join-Path $out 'receipt.json'
$r | ConvertTo-Json | Set-Content -LiteralPath $rp -Encoding utf8NoBOM
Write-Host ("PASS_BOUNDED_X2_PARTICIPANT_EDGE_DISCOVERY|OUT=$out|PROC=$($r.processes)|HITS=$($r.file_hits)|SHA=$sha|RECEIPT=$rp")
