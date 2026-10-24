$ErrorActionPreference='Stop'
$p=Join-Path $PSScriptRoot '..\PASTE_ON_X2_R1.ps1'
$tok=$null;$err=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $p).Path,[ref]$tok,[ref]$err)
if($err.Count -gt 0){throw ('INSTALLER_PARSE_FAILURE: '+($err|Out-String))}
Write-Host 'PASS: X2 paste script parse; the installer was NOT executed on this runner'
$f=$ast.FindAll({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-CoGitBlob'},$true)
if(@($f).Count -ne 1){throw 'MISSING_HASH_FUNCTION'}
. ([scriptblock]::Create($f[0].Extent.Text))
$payload=Join-Path $PSScriptRoot '..\CoPayload_R1.ps1'
$h=Get-CoGitBlob -Path (Resolve-Path -LiteralPath $payload).Path
if($h -cne '2a8e731aebba60eb21d29c06ed7bf8ee3ebfc95f'){throw ('GIT_BLOB_ALGORITHM_BROKEN '+$h)}
Write-Host 'PASS: installer source hash verifier matched exact known CoPayload source bytes'
