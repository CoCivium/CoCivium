[CmdletBinding()]
param(
    [string]$DownloadsRoot = (Join-Path $env:USERPROFILE 'Downloads'),
    [string]$OutBase = 'D:\CoCivium\CoFarm\CoDownloadsOrphanExposureCensus',
    [datetime]$Since = [datetime]'2026-09-22T00:00:00',
    [int]$MaxFiles = 10000,
    [long]$MaxHashBytes = 1073741824,
    [ValidateSet('TopLevel','Depth1')]
    [string]$ScanMode = 'TopLevel'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Write-NewUtf8 {
    param([string]$Path,[string]$Text)
    if (Test-Path -LiteralPath $Path) { throw "FAIL_CLOSED__NO_CLOBBER=$Path" }
    [IO.File]::WriteAllText($Path,$Text,[Text.UTF8Encoding]::new($false))
}

function Sha256 {
    param([string]$Path)
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToUpperInvariant()
}

function Get-ContentClass {
    param([string]$Name)
    $e = [IO.Path]::GetExtension($Name).ToLowerInvariant()
    if ($e -in @('.png','.jpg','.jpeg','.webp','.gif','.bmp','.svg')) { return 'IMAGE_EVIDENCE_CANDIDATE' }
    if ($Name -match '(?i)(\.tmp$|\.part$|\.crdownload$|\.download$|\.lock$|~$)') { return 'TRANSIENT_CONTROL_FILE' }
    if ($Name -match '(?i)(upload|sidecar|metadata).*\.(json|txt)$') { return 'UPLOAD_SIDECAR' }
    if ($e -in @('.md','.txt','.json','.jsonl','.yaml','.yml','.xml','.html','.htm','.csv','.tsv','.ps1','.psm1','.py','.js','.ts','.css','.ini','.cfg','.conf','.log','.sql')) { return 'SUBSTANTIVE_TEXT_CANDIDATE' }
    return 'SUBSTANTIVE_BINARY_CANDIDATE'
}

function Test-ProjectRelated {
    param([string]$Name,[string]$FullName,[datetime]$LastWriteUtc)
    if ($Name -match '(?i)^(co|rickbar|cocivium|coall|costead|cofarm|grail|strawbe|sowcc)') { return $true }
    if ($FullName -match '(?i)\\(CoCivium|CoFarm|CoStead|CoTemp|CoBuild|CoProject|Co[A-Za-z0-9_+-]+)\\') { return $true }
    if ($LastWriteUtc -ge $Since.ToUniversalTime()) { return $true }
    return $false
}

function Get-SecretSignalLabels {
    param([IO.FileInfo]$File)
    $labels = [Collections.Generic.List[string]]::new()
    $ext = $File.Extension.ToLowerInvariant()
    $textLike = $ext -in @('.md','.txt','.json','.jsonl','.yaml','.yml','.xml','.html','.htm','.csv','.tsv','.ps1','.psm1','.py','.js','.ts','.css','.ini','.cfg','.conf','.log','.sql','.env')
    if (-not $textLike) { return @() }
    if ($File.Length -gt 2097152) { return @('TEXT_SECRET_SCAN_SKIPPED_GT_2MIB') }

    try {
        $t = [IO.File]::ReadAllText($File.FullName)
        $tests = [ordered]@{
            PRIVATE_KEY_MARKER = '-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'
            GITHUB_TOKEN_LIKE = 'gh[pousr]_[A-Za-z0-9]{20,}'
            AWS_ACCESS_KEY_LIKE = 'AKIA[0-9A-Z]{16}'
            OPENAI_KEY_LIKE = '\bsk-[A-Za-z0-9_-]{20,}'
            GENERIC_CREDENTIAL_ASSIGNMENT = '(?im)\b(password|passwd|api[_-]?key|access[_-]?token|secret[_-]?key)\b\s*[:=]'
            CONNECTION_STRING_CREDENTIAL = '(?im)\b(User ID|UID|Password|PWD)\s*='
        }
        foreach ($k in $tests.Keys) {
            if ($t -match $tests[$k]) { [void]$labels.Add([string]$k) }
        }
    } catch {
        [void]$labels.Add('TEXT_SECRET_SCAN_READ_ERROR')
    }
    return @($labels)
}

if (-not (Test-Path -LiteralPath $DownloadsRoot -PathType Container)) {
    throw "FAIL_CLOSED__DOWNLOADS_ROOT_NOT_FOUND=$DownloadsRoot"
}

$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$run = Join-Path $OutBase $stamp
if (Test-Path -LiteralPath $run) { throw "FAIL_CLOSED__RUN_EXISTS=$run" }
New-Item -ItemType Directory -Path $run -Force:$false | Out-Null

$sourceFiles =
    if ($ScanMode -eq 'Depth1') {
        Get-ChildItem -LiteralPath $DownloadsRoot -File -Recurse -Depth 1 -Force -ErrorAction SilentlyContinue
    } else {
        Get-ChildItem -LiteralPath $DownloadsRoot -File -Force -ErrorAction SilentlyContinue
    }

$all = @(
    $sourceFiles |
    Where-Object {
        $_.LastWriteTimeUtc -ge $Since.ToUniversalTime() -or
        $_.Name -match '(?i)^(co|rickbar|cocivium|coall|costead|cofarm|grail|strawbe|sowcc)'
    } |
    Sort-Object FullName
)

if ($all.Count -gt $MaxFiles) {
    throw "FAIL_CLOSED__CANDIDATE_COUNT_EXCEEDS_MAX__COUNT=$($all.Count)__MAX=$MaxFiles"
}

$objects = [Collections.Generic.List[object]]::new()
foreach ($f in $all) {
    $hash = $null
    $hashState = 'VERIFIED_LOCAL'
    if ($f.Length -gt $MaxHashBytes) {
        $hashState = 'DISCOVERED_LOCAL__HASH_SKIPPED_OVERSIZE'
    } else {
        try { $hash = Sha256 $f.FullName } catch { $hashState = 'DISCOVERED_LOCAL__HASH_ERROR' }
    }

    $secretSignals = @(Get-SecretSignalLabels $f)
    $projectRelated = Test-ProjectRelated $f.Name $f.FullName $f.LastWriteTimeUtc

    $privacy = if ($secretSignals.Count -gt 0) {
        'PRIVATE_HOLD__SECRET_SIGNAL_HEURISTIC'
    } elseif ($projectRelated) {
        'UNKNOWN_PROJECT__CLASSIFY_BEFORE_PUBLIC'
    } else {
        'UNKNOWN__CLASSIFY_BEFORE_PUBLIC'
    }

    $objects.Add([ordered]@{
        relative_path = [IO.Path]::GetRelativePath($DownloadsRoot,$f.FullName)
        full_path = $f.FullName
        name = $f.Name
        extension = $f.Extension
        length_bytes = [long]$f.Length
        created_utc = $f.CreationTimeUtc.ToString('o')
        modified_utc = $f.LastWriteTimeUtc.ToString('o')
        content_class = Get-ContentClass $f.Name
        project_related_heuristic = [bool]$projectRelated
        sha256 = $hash
        lifecycle_state = $hashState
        staging_class = 'STAGED_UNBOUND_RISK'
        privacy_disposition = $privacy
        secret_signal_labels = $secretSignals
        semantic_review = 'NOT_SEMANTICALLY_REVIEWED'
    })
}

$hashGroups = @(
    $objects |
    Where-Object { $_.sha256 } |
    Group-Object sha256 |
    Where-Object Count -gt 1
)

$duplicates = @(
    foreach ($g in $hashGroups) {
        [ordered]@{
            sha256 = $g.Name
            count = $g.Count
            paths = @($g.Group | ForEach-Object relative_path)
            disposition = 'DUPLICATE_CONTENT_CANDIDATE__NO_SUPERSESSION_OR_DELETE_INFERRED'
        }
    }
)

$classCounts = [ordered]@{}
foreach ($g in ($objects | Group-Object content_class | Sort-Object Name)) {
    $classCounts[$g.Name] = $g.Count
}

$secretFlagged = @($objects | Where-Object { @($_.secret_signal_labels).Count -gt 0 }).Count
$hashed = @($objects | Where-Object sha256).Count

$report = [ordered]@{
    coverage = [ordered]@{
        scan_root = $DownloadsRoot
        since_utc = $Since.ToUniversalTime().ToString('o')
        max_files = $MaxFiles
        observed_candidates = $objects.Count
        hashed_files = $hashed
        scan_mode = $ScanMode
        rule = if ($ScanMode -eq 'TopLevel') {
            'TOP_LEVEL_ONLY__RECENT_SINCE_BOUNDARY_OR_PROJECT_PREFIX'
        } else {
            'DEPTH1_ONLY__RECENT_SINCE_BOUNDARY_OR_PROJECT_PREFIX'
        }
    }
    objects = @($objects)
    hashes = [ordered]@{
        algorithm = 'SHA256'
        hashed_count = $hashed
        unverified_count = $objects.Count - $hashed
    }
    duplicates = $duplicates
    graph_validation = [ordered]@{
        state = 'NOT_RUN'
        reason = 'R0_DOWNLOADS_CENSUS_ONLY'
    }
    missing_relations = @(
        'DURABLE_PARENT',
        'INTENDED_RECEIVER',
        'PICKUP_READPROOF',
        'RETIREMENT_CONDITION',
        'CROSS_SURFACE_DUPLICATE_RELATION',
        'PUBLICATION_AUTHORITY'
    )
    content_classes = $classCounts
    semantic_coverage = [ordered]@{
        state = 'NOT_SEMANTICALLY_REVIEWED'
        note = 'Mechanical inventory, hashing, extension classification, and secret-signal labels only.'
    }
    claim_evidence_audit = @(
        [ordered]@{
            Claim = 'Files are visible in Downloads.'
            ExactObject = 'R0 manifest'
            Evidence = 'bounded local filesystem scan'
            VerifiedState = 'DISCOVERED_LOCAL_OR_VERIFIED_LOCAL_PER_OBJECT'
            Contradiction = $null
            Downgrade = 'Visibility does not prove orphaning, landing, pickup, integration, or public safety.'
            NextProof = 'receiver/custody reconciliation'
        },
        [ordered]@{
            Claim = 'Secret-like material may exist.'
            ExactObject = 'R0 manifest signal labels'
            Evidence = 'heuristic text-pattern scan without exporting matched values'
            VerifiedState = if ($secretFlagged -gt 0) { 'HEURISTIC_SIGNALS_PRESENT' } else { 'NO_HEURISTIC_SIGNALS_OBSERVED' }
            Contradiction = $null
            Downgrade = 'Pattern scanning is neither complete nor proof of a secret.'
            NextProof = 'private classification review'
        }
    )
    lifecycle_evidence = [ordered]@{
        discovered_or_verified = $objects.Count
        verified_local = $hashed
        landed = 0
        picked_up = 0
        integrated = 0
        coex = 0
        secret_signal_files = $secretFlagged
    }
    eligible_next_transitions = @(
        'R1_COMPARE_EXACT_HASHES_TO_COFARM_COSTEAD_AND_OTHER_ELECTED_DURABLE_SURFACES',
        'R1_CLASSIFY_CONFIDENTIALITY_BEFORE_ANY_PUBLICATION',
        'R1_BUILD_METADATA_MINIMIZED_PUBLIC_SAFE_INDEX_AFTER_CLASSIFICATION'
    )
    blocked_transitions = @(
        'DELETE',
        'MOVE',
        'PUBLIC_UPLOAD',
        'GITHUB_BULK_PUSH',
        'SECRET_EXPORT',
        'LANDED_INFERENCE',
        'PICKED_UP_INFERENCE',
        'INTEGRATED_INFERENCE',
        'COEX_INFERENCE'
    )
    ux_summary = [ordered]@{
        state = 'UX_NOT_EVALUATED'
        CoHereNow = 'Downloads candidate set inventoried without mutation.'
        Meaning = 'Exact hashes and duplicate groups exist locally; orphan/public/custody status remains receiver-relative.'
        NextSafeAction = 'R1 cross-surface hash reconciliation.'
    }
    nonclaims = @(
        'LOCAL_IS_NOT_LANDED',
        'VALIDATION_IS_NOT_ACCEPTANCE',
        'NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF',
        'NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE',
        'HASHING_IS_NOT_SEMANTIC_INGESTION',
        'DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY',
        'STAGED_NE_ORPHANED',
        'UNKNOWN_NE_PUBLIC',
        'SECRET_SCAN_NE_SECRET_PROOF'
    )
}

$reportPath = Join-Path $run '10_RECONCILIATION_REPORT.json'
Write-NewUtf8 $reportPath (($report | ConvertTo-Json -Depth 50) + [Environment]::NewLine)
$reportSha = Sha256 $reportPath

$receipt = [ordered]@{
    STATE = 'PASS_R0_DOWNLOADS_ORPHAN_EXPOSURE_CENSUS__READONLY_SOURCE__APPEND_ONLY_OUTPUT'
    RUN_ROOT = $run
    DOWNLOADS_ROOT = $DownloadsRoot
    SINCE_UTC = $Since.ToUniversalTime().ToString('o')
    SCAN_MODE = $ScanMode
    SCAN_MODE = $ScanMode
    FILES = $objects.Count
    HASHED = $hashed
    DUPLICATE_GROUPS = $duplicates.Count
    SECRET_SIGNAL_FILES = $secretFlagged
    REPORT_PATH = $reportPath
    REPORT_SHA256 = $reportSha
    SOURCE_MUTATIONS = 0
    DELETES = 0
    MOVES = 0
    NETWORK = 0
    PUBLIC_UPLOAD = 0
    NEXT = 'R1_COMPARE_HASHES_TO_COFARM_COSTEAD_AND_ELECTED_SURFACES'
    RICK_ACTION = 'NONE__RETURN_ONLY_TERMINAL_JSON_IF_REQUESTED'
}

$receiptPath = Join-Path $run '99_RECEIPT.json'
Write-NewUtf8 $receiptPath (($receipt | ConvertTo-Json -Depth 20) + [Environment]::NewLine)
$receiptSha = Sha256 $receiptPath

[ordered]@{
    STATE = $receipt.STATE
    ROOT = $run
    RECEIPT_SHA256 = $receiptSha
    FILES = $objects.Count
    HASHED = $hashed
    DUPLICATE_GROUPS = $duplicates.Count
    SECRET_SIGNAL_FILES = $secretFlagged
    NEXT = $receipt.NEXT
    RICK_ACTION = $receipt.RICK_ACTION
} | ConvertTo-Json -Depth 10 -Compress
