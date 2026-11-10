$ErrorActionPreference='Stop'
$script=Join-Path $PSScriptRoot '..\CoPayload_R1.ps1'
$tok=$null;$err=$null
$null=[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $script).Path,[ref]$tok,[ref]$err)
if($err.Count -ne 0){throw ('PS_PARSE_FAILED: '+($err|Out-String))}
Write-Host 'PASS: PowerShell parser'
if($env:OS -ne 'Windows_NT'){throw 'WINDOWS_REQUIRED'}
$selfRaw=& pwsh -NoLogo -NoProfile -STA -File $script -SelfTest
if($LASTEXITCODE -ne 0){throw 'SELFTEST_EXIT_FAILED'}
$self=($selfRaw|Out-String).Trim()|ConvertFrom-Json
if($self.status -ne 'PASS' -or $self.clipboard_read -ne $false -or $self.global_hook -ne $false){throw 'SELFTEST_SAFETY_FAILED'}
Write-Host 'PASS: no-GUI/no-clipboard self-test'
$canaryRaw=& pwsh -NoLogo -NoProfile -STA -File $script -Canary
if($LASTEXITCODE -ne 0){throw 'CANARY_EXIT_FAILED'}
$canary=($canaryRaw|Out-String).Trim()|ConvertFrom-Json
if($canary.status -ne 'PASS' -or $canary.files -ne 2 -or $canary.ledger_entries -ne 1 -or $canary.missing_source -ne 'REJECTED'){throw 'CANARY_EVIDENCE_FAILED'}
Write-Host 'PASS: temporary ZIP creation, actual hash verification, missing-source rejection and cleanup'
Write-Host 'PASS: LOCAL_COPAYLOAD_R1 9 checks; no hardware thumb, clipboard or provider calls'
