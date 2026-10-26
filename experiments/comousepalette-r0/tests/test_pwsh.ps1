$ErrorActionPreference='Stop'
$script=Join-Path $PSScriptRoot '..\CoMousePalette_R0.ps1'
$tokens=$null;$errors=$null
$null=[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $script).Path,[ref]$tokens,[ref]$errors)
if($errors.Count -gt 0){$errors | Out-String | Write-Error;exit 1}
Write-Host 'PASS: PowerShell parse has no errors'
if($env:OS -eq 'Windows_NT'){
  $out=& pwsh -NoProfile -STA -File $script -SelfTest
  if($LASTEXITCODE -ne 0){throw 'SELFTEST_EXIT_NONZERO'}
  $obj=($out | Out-String).Trim() | ConvertFrom-Json
  if($obj.status -ne 'PASS' -or $obj.tests -ne 9 -or $obj.mouseHookInstalled -ne $false){throw 'SELFTEST_NOT_PASS'}
  Write-Host 'PASS: nine live Windows mode/zone and Win32 interop tests'
}
