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

# Regression: extract and exercise the launcher's pure byte verifier with no actual palette launch.
$installer=Get-Content -LiteralPath (Resolve-Path -LiteralPath $p).Path -Raw
$ast2=[System.Management.Automation.Language.Parser]::ParseInput($installer,[ref]$tok,[ref]$err)
if($err.Count -gt 0){throw ('INSTALLER_PARSE_FAILURE_AFTER_EDIT: '+($err|Out-String))}
$verifiers=$ast2.FindAll({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Assert-CoLauncherBytes'},$true)
if(@($verifiers).Count -ne 1){throw 'MISSING_LAUNCHER_VERIFIER'}
. ([scriptblock]::Create($verifiers[0].Extent.Text))
$root=Join-Path ([System.IO.Path]::GetTempPath()) ('CoLauncherTest_'+[guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($root)|Out-Null
try {
    $launcher=Join-Path $root 'launcher.cmd'
    [byte[]]$expected=[System.Text.Encoding]::ASCII.GetBytes('@echo off'+[Environment]::NewLine+'echo safe'+[Environment]::NewLine)
    $first=Assert-CoLauncherBytes -Path $launcher -ExpectedBytes $expected
    if($first -cne ([Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($expected)).ToLowerInvariant())){throw 'LAUNCHER_HASH_MISMATCH'}
    $second=Assert-CoLauncherBytes -Path $launcher -ExpectedBytes $expected
    if($first -cne $second){throw 'LAUNCHER_IDEMPOTENT_FAIL'}
    [System.IO.File]::WriteAllText($launcher,'@echo off'+[Environment]::NewLine+'echo altered',[System.Text.Encoding]::ASCII)
    $denied=$false
    try{$null=Assert-CoLauncherBytes -Path $launcher -ExpectedBytes $expected}catch{if($_.Exception.Message -match 'HALT_LAUNCHER_BYTES_MISMATCH'){$denied=$true}else{throw}}
    if(-not $denied){throw 'ALTERED_LAUNCHER_ACCEPTED'}
    if(-not ([System.IO.File]::ReadAllText($launcher)).Contains('altered')){throw 'EXISTING_FILE_CLOBBERED'}
    [System.IO.File]::Delete($launcher)
    [System.IO.Directory]::CreateDirectory($launcher)|Out-Null
    $deniedDir=$false
    try{$null=Assert-CoLauncherBytes -Path $launcher -ExpectedBytes $expected}catch{if($_.Exception.Message -match 'HALT_UNSAFE_LAUNCHER_PATH'){$deniedDir=$true}else{throw}}
    if(-not $deniedDir){throw 'DIRECTORY_LAUNCHER_ACCEPTED'}
    Write-Host 'PASS: new launcher pinned; exact existing launcher idempotent; altered launcher held/no-clobber; directory held'
} finally {
    if([System.IO.Directory]::Exists($root)){[System.IO.Directory]::Delete($root,$true)}
}
