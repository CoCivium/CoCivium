# CoModelFabric X2 R0. Read-only by default; no API keys, login automation, hooks or persisted data.
[CmdletBinding()]
param(
    [ValidateSet('Check','SelfTest','OpenClaude','OpenOrbSource')]
    [string]$Mode = 'Check',
    [switch]$SkipOllama
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Classify-OllamaResponse {
    param([AllowNull()][object]$Payload)
    if ($null -eq $Payload) {
        return [ordered]@{ status='HELD_INVALID_RESPONSE'; model_count=$null }
    }
    $modelsProperty = $Payload.PSObject.Properties['models']
    if ($null -eq $modelsProperty -or $null -eq $modelsProperty.Value -or
        $modelsProperty.Value -isnot [System.Array]) {
        return [ordered]@{ status='HELD_INVALID_RESPONSE'; model_count=$null }
    }
    $models = $modelsProperty.Value
    foreach ($model in $models) {
        if ($null -eq $model) {
            return [ordered]@{ status='HELD_INVALID_RESPONSE'; model_count=$null }
        }
        $nameProperty = $model.PSObject.Properties['name']
        if ($null -eq $nameProperty -or $nameProperty.Value -isnot [string] -or
            [string]::IsNullOrWhiteSpace($nameProperty.Value)) {
            return [ordered]@{ status='HELD_INVALID_RESPONSE'; model_count=$null }
        }
    }
    return [ordered]@{ status='OBSERVED_LOCAL_API'; model_count=$models.Length }
}

function Get-LocalOllamaProbe {
    param([bool]$SkipProbe)
    if ($SkipProbe) {
        return [ordered]@{ status='HELD_NOT_PROBED'; model_count=$null; endpoint='LOOPBACK_ONLY' }
    }
    try {
        $payload = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -Method Get -TimeoutSec 2
        $classified = Classify-OllamaResponse -Payload $payload
        return [ordered]@{
            status = $classified.status
            model_count = $classified.model_count
            endpoint = 'LOOPBACK_ONLY'
        }
    } catch {
        return [ordered]@{ status='HELD_LOCAL_API_UNREACHABLE'; model_count=$null; endpoint='LOOPBACK_ONLY' }
    }
}

function Get-ReadOnlyReport {
    param([bool]$SkipProbe)
    return [ordered]@{
        schema = 'CoCivium.CoModelFabric.X2Preflight.R0'
        observed_at_utc = (Get-Date).ToUniversalTime().ToString('o')
        scope = 'LOCAL_PROCESS_OBSERVATION_ONLY'
        browser_claude = [ordered]@{ state='AUTH_UNKNOWN_NOT_PROBED'; user_owned_account=$true; api_adapter='HELD_UNCONFIGURED' }
        local_ollama = (Get-LocalOllamaProbe -SkipProbe:$SkipProbe)
        pi = [ordered]@{ state='HELD_NO_QUALIFIED_ADAPTER' }
        openai = [ordered]@{ state='HELD_NO_QUALIFIED_ADAPTER' }
        external_effects = 'NONE'
        persistence = 'STDOUT_ONLY'
        no_secrets_read = $true
        x2_physical_mouse_binding = 'NOT_PROBED'
        next_proof = 'one opted-in same-task comparison through a locally qualified adapter and one authorized external API adapter'
    }
}

function Invoke-SelfTest {
    $cases = @(
        @{name='null'; payload=$null; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='missing'; payload=[pscustomobject]@{other=1}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='model_null'; payload=[pscustomobject]@{models=$null}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='model_scalar'; payload=[pscustomobject]@{models='x'}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='model_number'; payload=[pscustomobject]@{models=17}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='empty'; payload=[pscustomobject]@{models=@()}; expected='OBSERVED_LOCAL_API'; count=0},
        @{name='one'; payload=[pscustomobject]@{models=@([pscustomobject]@{name='test'})}; expected='OBSERVED_LOCAL_API'; count=1},
        @{name='two'; payload=[pscustomobject]@{models=@([pscustomobject]@{name='a'},[pscustomobject]@{name='b'})}; expected='OBSERVED_LOCAL_API'; count=2},
        @{name='null_entry'; payload=[pscustomobject]@{models=@($null)}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='no_name'; payload=[pscustomobject]@{models=@([pscustomobject]@{x='a'})}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='blank_name'; payload=[pscustomobject]@{models=@([pscustomobject]@{name=' '})}; expected='HELD_INVALID_RESPONSE'; count=$null},
        @{name='numeric_name'; payload=[pscustomobject]@{models=@([pscustomobject]@{name=7})}; expected='HELD_INVALID_RESPONSE'; count=$null}
    )
    $failed = @()
    foreach ($case in $cases) {
        $result = Classify-OllamaResponse -Payload $case.payload
        if ($result.status -ne $case.expected -or $result.model_count -ne $case.count) {
            $failed += [string]$case.name
        }
    }
    $quiet = Get-ReadOnlyReport -SkipProbe:$true
    if ($quiet.local_ollama.status -ne 'HELD_NOT_PROBED' -or
        $quiet.browser_claude.state -ne 'AUTH_UNKNOWN_NOT_PROBED' -or
        $quiet.external_effects -ne 'NONE' -or $quiet.persistence -ne 'STDOUT_ONLY') {
        $failed += 'no_effect_report'
    }
    $passCount = $cases.Count + 1 - $failed.Count
    return [ordered]@{
        schema = 'CoCivium.CoModelFabric.X2Preflight.SelfTest.R0'
        status = $(if ($failed.Count -eq 0) { 'PASS' } else { 'FAIL' })
        passed = $passCount
        total = $cases.Count + 1
        failed_cases = @($failed)
        test_scope = 'SIMULATED_RESPONSE_CLASSIFICATION_AND_NO_EFFECT_CHECK_ONLY'
    }
}

switch ($Mode) {
    'SelfTest' {
        $result = Invoke-SelfTest
        $result | ConvertTo-Json -Depth 10
        if ($result.status -ne 'PASS') { exit 1 }
        break
    }
    'Check' {
        (Get-ReadOnlyReport -SkipProbe:$SkipOllama.IsPresent) | ConvertTo-Json -Depth 10
        break
    }
    'OpenClaude' {
        if (-not $IsWindows) { throw 'OPEN_CLAUDE_REQUIRES_WINDOWS' }
        Start-Process -FilePath 'https://claude.ai/'
        [ordered]@{
            status = 'BROWSER_OPEN_REQUESTED'
            endpoint = 'https://claude.ai/'
            account_authentication = 'UNKNOWN_USER_SIGN_IN_REQUIRED_IF_NEEDED'
            external_ai_call = 'NONE'
            coorb_bridge = 'NOT_CONNECTED'
        } | ConvertTo-Json -Depth 6
        break
    }
    'OpenOrbSource' {
        if (-not $IsWindows) { throw 'OPEN_SOURCE_REQUIRES_WINDOWS' }
        Start-Process -FilePath 'https://github.com/CoCivium/CoCivium/blob/main/examples/colensmedia/index.html'
        [ordered]@{
            status = 'SOURCE_PAGE_OPEN_REQUESTED'
            live_orbware = 'NOT_PROVEN'
            external_ai_call = 'NONE'
        } | ConvertTo-Json -Depth 6
        break
    }
}
