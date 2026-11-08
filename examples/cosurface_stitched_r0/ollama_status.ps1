# CoSurface/CoBar local-model probe, R0. Purely observational, no install.
# Intended for an existing authorized local producer, not an independent tray/daemon.
[CmdletBinding()]
param(
    [ValidateRange(1,15)][int]$TimeoutSeconds = 3,
    [string]$OutFile
)
$ErrorActionPreference = 'Stop'
$state = [ordered]@{
    schema = 'CoLocalModelStatus.R0'
    observer = 'LOCAL_PS7_EXPLICIT'
    model_runtime = 'OLLAMA'
    source = 'http://127.0.0.1:11434/api/tags'
    observed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    status = 'UNREACHABLE'
    model_names = @()
    model_count = 0
    verified_work_effects = 0
    no_model_inference = $true
    output_class = 'OBSERVATION_ONLY'
}
try {
    $u = [Uri]'http://127.0.0.1:11434/api/tags'
    $response = Invoke-RestMethod -Method Get -Uri $u -TimeoutSec $TimeoutSeconds -NoProxy
    if ($null -eq $response.models) {
        $state.status = 'MALFORMED_RESPONSE_HOLD'
    } else {
        $names = @($response.models | ForEach-Object { [string]$_.name } |
                  Where-Object { $_ -and $_.Length -le 180 } | Sort-Object -Unique)
        $state.model_names = @($names)
        $state.model_count = $names.Count
        $state.status = 'LOCAL_MODEL_INVENTORY_OBSERVED'
    }
} catch {
    # Do not report that X2 is offline when a model endpoint does not respond.
    $state.status = 'OLLAMA_ENDPOINT_UNREACHABLE'
}
$json = $state | ConvertTo-Json -Depth 5
if ($OutFile) {
    # Exact new-file atomic creation. No overwrite or startup changes.
    $full = [IO.Path]::GetFullPath($OutFile)
    $parent = [IO.Path]::GetDirectoryName($full)
    if (-not [IO.Directory]::Exists($parent)) { throw 'OUTPUT_DIRECTORY_NOT_FOUND_HOLD' }
    $bytes = [Text.Encoding]::UTF8.GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($full, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
}
$json
