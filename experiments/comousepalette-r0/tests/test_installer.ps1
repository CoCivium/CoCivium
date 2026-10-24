$ErrorActionPreference='Stop'
$p=Join-Path $PSScriptRoot '..\PASTE_ON_X2_R1.ps1'
$tok=$null;$err=$null
$null=[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $p).Path,[ref]$tok,[ref]$err)
if($err.Count -gt 0){throw ('INSTALLER_PARSE_FAILURE: '+($err|Out-String))}
Write-Host 'PASS: X2 paste script parse, NOT EXECUTED ON RUNNER'
