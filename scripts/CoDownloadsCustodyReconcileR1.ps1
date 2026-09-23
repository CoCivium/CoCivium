[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$R0Root,

    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Fa-f0-9]{64}$')]
    [string]$R0ReceiptSha256,

    [string]$CoFarmRoot = 'D:\CoCivium\CoFarm',
    [string]$CoSteadRoot = 'D:\CoCivium\CoStead',

    [int]$MaxObservedFilesPerRoot = 500000,
    [int]$MaxHashCandidatesPerRoot = 100000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Sha256 {
    param([Parameter(Mandatory=$true)][string]$Path)
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToUpperInvariant()
}

function Write-NewUtf8 {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Text
    )
    if (Test-Path -LiteralPath $Path) {
        throw "FAIL_CLOSED__NO_CLOBBER=$Path"
    }
    [IO.File]::WriteAllText($Path,$Text,[Text.UTF8Encoding]::new($false))
}

function Add-Match {
    param(
        [Parameter(Mandatory=$true)]$Map,
        [Parameter(Mandatory=$true)][string]$Hash,
        [Parameter(Mandatory=$true)][string]$Path
    )
    if (-not $Map.ContainsKey($Hash)) {
        $Map[$Hash] = [Collections.Generic.List[string]]::new()
    }
    [void]$Map[$Hash].Add($Path)
}

function Scan-DurableRoot {
    param(
        [Parameter(Mandatory=$true)][string]$Label,
        [Parameter(Mandatory=$true)][string]$Root,
        [Parameter(Mandatory=$true)]$TargetSizes,
        [Parameter(Mandatory=$true)]$TargetHashes,
        [Parameter(Mandatory=$true)]$MatchMap,
        [Parameter(Mandatory=$true)][string]$ExcludePrefix,
        [int]$MaxObserved,
        [int]$MaxHashCandidates
    )

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return [ordered]@{
            label = $Label
            root = $Root
            state = 'ROOT_NOT_FOUND'
            observed_files = 0
            size_candidates = 0
            hashed_candidates = 0
            hash_errors = 0
            exact_matches = 0
            coverage_complete = $false
            stop_reason = 'ROOT_NOT_FOUND'
        }
    }

    $observed = 0
    $sizeCandidates = 0
    $hashed = 0
    $hashErrors = 0
    $exactMatches = 0
    $coverageComplete = $true
    $stopReason = $null

    try {
        Get-ChildItem -LiteralPath $Root -File -Recurse -Force -ErrorAction SilentlyContinue |
        ForEach-Object {
            $f = $_

            if ($f.FullName.StartsWith($ExcludePrefix,[StringComparison]::OrdinalIgnoreCase)) {
                return
            }

            $observed++
            if ($observed -gt $MaxObserved) {
                $coverageComplete = $false
                $stopReason = "OBSERVED_FILE_LIMIT_EXCEEDED=$MaxObserved"
                throw [InvalidOperationException]::new($stopReason)
            }

            if (-not $TargetSizes.Contains([long]$f.Length)) {
                return
            }

            $sizeCandidates++
            if ($sizeCandidates -gt $MaxHashCandidates) {
                $coverageComplete = $false
                $stopReason = "HASH_CANDIDATE_LIMIT_EXCEEDED=$MaxHashCandidates"
                throw [InvalidOperationException]::new($stopReason)
            }

            try {
                $h = Sha256 $f.FullName
                $hashed++
                if ($TargetHashes.Contains($h)) {
                    Add-Match -Map $MatchMap -Hash $h -Path $f.FullName
                    $exactMatches++
                }
            }
            catch {
                $hashErrors++
                $coverageComplete = $false
            }
        }
    }
    catch {
        if ($null -eq $stopReason) {
            throw
        }
    }

    [ordered]@{
        label = $Label
        root = $Root
        state = if ($coverageComplete) { 'PASS_COMPLETE_BOUNDED_SCAN' } else { 'PARTIAL_SCAN__NO_NEGATIVE_INFERENCE_WHERE_GAPS_EXIST' }
        observed_files = $observed
        size_candidates = $sizeCandidates
        hashed_candidates = $hashed
        hash_errors = $hashErrors
        exact_matches = $exactMatches
        coverage_complete = $coverageComplete
        stop_reason = $stopReason
    }
}

$R0Root = (Resolve-Path -LiteralPath $R0Root).Path
$R0Receipt = Join-Path $R0Root '99_RECEIPT.json'
$R0Report = Join-Path $R0Root '10_RECONCILIATION_REPORT.json'

foreach ($p in @($R0Receipt,$R0Report)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
        throw "FAIL_CLOSED__R0_REQUIRED_OBJECT_MISSING=$p"
    }
}

$wantReceipt = $R0ReceiptSha256.ToUpperInvariant()
$actualReceipt = Sha256 $R0Receipt
if ($actualReceipt -cne $wantReceipt) {
    throw "FAIL_CLOSED__R0_RECEIPT_HASH_DRIFT__EXPECTED=$wantReceipt__ACTUAL=$actualReceipt"
}

$r0ReceiptObj = Get-Content -LiteralPath $R0Receipt -Raw | ConvertFrom-Json -Depth 100
$r0ReportObj = Get-Content -LiteralPath $R0Report -Raw | ConvertFrom-Json -Depth 100

if ([string]$r0ReceiptObj.STATE -cne 'PASS_R0_DOWNLOADS_ORPHAN_EXPOSURE_CENSUS__READONLY_SOURCE__APPEND_ONLY_OUTPUT') {
    throw "FAIL_CLOSED__R0_STATE_UNEXPECTED=$($r0ReceiptObj.STATE)"
}

$reportSha = Sha256 $R0Report
if ([string]$r0ReceiptObj.REPORT_SHA256 -and ([string]$r0ReceiptObj.REPORT_SHA256).ToUpperInvariant() -cne $reportSha) {
    throw 'FAIL_CLOSED__R0_REPORT_HASH_DRIFT'
}

$objects = @($r0ReportObj.objects)
if ($objects.Count -lt 1) {
    throw 'FAIL_CLOSED__R0_OBJECT_SET_EMPTY'
}

$targetHashes = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$targetSizes = [Collections.Generic.HashSet[long]]::new()

foreach ($o in $objects) {
    if ($null -eq $o.sha256 -or [string]::IsNullOrWhiteSpace([string]$o.sha256)) {
        continue
    }
    [void]$targetHashes.Add(([string]$o.sha256).ToUpperInvariant())
    [void]$targetSizes.Add([long]$o.length_bytes)
}

if ($targetHashes.Count -lt 1) {
    throw 'FAIL_CLOSED__R0_HAS_NO_HASHED_TARGETS'
}

$cofarmMatches = @{}
$costeadMatches = @{}
$excludePrefix = $R0Root.TrimEnd('\') + '\'

Write-Host 'COHEARTBEAT | R1 | SCAN_COFARM'
$cofarmScan = Scan-DurableRoot -Label 'COFARM' -Root $CoFarmRoot -TargetSizes $targetSizes -TargetHashes $targetHashes -MatchMap $cofarmMatches -ExcludePrefix $excludePrefix -MaxObserved $MaxObservedFilesPerRoot -MaxHashCandidates $MaxHashCandidatesPerRoot

Write-Host 'COHEARTBEAT | R1 | SCAN_COSTEAD'
$costeadScan = Scan-DurableRoot -Label 'COSTEAD' -Root $CoSteadRoot -TargetSizes $targetSizes -TargetHashes $targetHashes -MatchMap $costeadMatches -ExcludePrefix $excludePrefix -MaxObserved $MaxObservedFilesPerRoot -MaxHashCandidates $MaxHashCandidatesPerRoot

$fullCoverage = [bool]$cofarmScan.coverage_complete -and [bool]$costeadScan.coverage_complete

$rows = [Collections.Generic.List[object]]::new()
$both = 0
$cofarmOnly = 0
$costeadOnly = 0
$none = 0
$unresolved = 0
$secretHold = 0

foreach ($o in $objects) {
    $h = if ($o.sha256) { ([string]$o.sha256).ToUpperInvariant() } else { $null }
    $cf = @()
    $cs = @()

    if ($h -and $cofarmMatches.ContainsKey($h)) {
        $cf = @($cofarmMatches[$h])
    }
    if ($h -and $costeadMatches.ContainsKey($h)) {
        $cs = @($costeadMatches[$h])
    }

    $secretSignals = @($o.secret_signal_labels)
    $privacy = [string]$o.privacy_disposition
    $isSecretHold = ($secretSignals.Count -gt 0) -or ($privacy -like 'PRIVATE_HOLD*')
    if ($isSecretHold) {
        $secretHold++
    }

    if ($cf.Count -gt 0 -and $cs.Count -gt 0) {
        $custody = 'EXACT_HASH_PRESENT_IN_COFARM_AND_COSTEAD'
        $both++
    }
    elseif ($cf.Count -gt 0) {
        $custody = 'EXACT_HASH_PRESENT_IN_COFARM_ONLY'
        $cofarmOnly++
    }
    elseif ($cs.Count -gt 0) {
        $custody = 'EXACT_HASH_PRESENT_IN_COSTEAD_ONLY'
        $costeadOnly++
    }
    elseif ($fullCoverage) {
        $custody = 'NO_EXACT_HASH_MATCH_IN_BOUNDED_COFARM_OR_COSTEAD_SCAN'
        $none++
    }
    else {
        $custody = 'UNRESOLVED_DUE_TO_DURABLE_SCAN_GAPS'
        $unresolved++
    }

    if ($isSecretHold) {
        $next = 'PRIVATE_HOLD__NO_PUBLICATION__CLASSIFY_LOCALLY'
    }
    elseif ($custody -eq 'EXACT_HASH_PRESENT_IN_COFARM_AND_COSTEAD') {
        $next = 'CUSTODY_MATCH_PROVEN__SEMANTIC_AND_RECEIVER_RECONCILIATION_NEXT'
    }
    elseif ($custody -like 'EXACT_HASH_PRESENT_*') {
        $next = 'SECOND_CUSTODY_OR_RECEIVER_RELATION_REVIEW_NEXT'
    }
    elseif ($custody -eq 'NO_EXACT_HASH_MATCH_IN_BOUNDED_COFARM_OR_COSTEAD_SCAN') {
        $next = 'UNBOUND_EXPOSURE_CANDIDATE__ELECT_DURABLE_DESTINATION_BEFORE_MOVE_DELETE_OR_PUBLICATION'
    }
    else {
        $next = 'NO_NEGATIVE_INFERENCE__REPAIR_OR_NARROW_DURABLE_SCAN'
    }

    $rows.Add([ordered]@{
        relative_path = [string]$o.relative_path
        sha256 = $h
        length_bytes = [long]$o.length_bytes
        content_class = [string]$o.content_class
        r0_staging_class = [string]$o.staging_class
        privacy_disposition = $privacy
        secret_signal_labels = $secretSignals
        cofarm_exact_paths = $cf
        costead_exact_paths = $cs
        custody_reconciliation = $custody
        lifecycle_state = if ($cf.Count -gt 0 -or $cs.Count -gt 0) { 'VERIFIED_LOCAL__DURABLE_DUPLICATE_CANDIDATE_OBSERVED' } else { 'VERIFIED_LOCAL' }
        semantic_review = 'NOT_SEMANTICALLY_REVIEWED'
        next_deed = $next
        nonclaims = @(
            'HASH_MATCH_NE_RECEIVER_PICKUP',
            'HASH_MATCH_NE_INTEGRATION',
            'NO_MATCH_NE_ORPHAN_UNLESS_SCAN_COVERAGE_AND_RECEIVER_EXPECTATION_ARE_BOUND',
            'SECRET_SIGNAL_NE_SECRET_PROOF'
        )
    })
}

$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$outBase = 'D:\CoCivium\CoFarm\CoDownloadsCustodyReconcileR1'
$outRoot = Join-Path $outBase $stamp
if (Test-Path -LiteralPath $outRoot) {
    throw "FAIL_CLOSED__OUTPUT_EXISTS=$outRoot"
}
New-Item -ItemType Directory -Path $outRoot -Force:$false | Out-Null

$report = [ordered]@{
    coverage = [ordered]@{
        r0_root = $R0Root
        r0_receipt_sha256 = $wantReceipt
        r0_report_sha256 = $reportSha
        r0_objects = $objects.Count
        target_hashes = $targetHashes.Count
        cofarm_scan = $cofarmScan
        costead_scan = $costeadScan
        full_negative_inference_coverage = $fullCoverage
    }
    objects = @($rows)
    hashes = [ordered]@{
        algorithm = 'SHA256'
        target_hashes = $targetHashes.Count
        cofarm_exact_match_events = [int]$cofarmScan.exact_matches
        costead_exact_match_events = [int]$costeadScan.exact_matches
    }
    duplicates = [ordered]@{
        both_custody_roots = $both
        cofarm_only = $cofarmOnly
        costead_only = $costeadOnly
        no_match_with_full_coverage = $none
        unresolved_due_to_scan_gaps = $unresolved
    }
    graph_validation = [ordered]@{
        state = 'NOT_RUN'
        reason = 'R1_EXACT_HASH_CUSTODY_RECONCILIATION_ONLY'
    }
    missing_relations = @(
        'INTENDED_DURABLE_RECEIVER',
        'RECEIVER_READPROOF',
        'INTEGRATION_DISPOSITION',
        'SEMANTIC_EQUIVALENCE_OR_SUPERSESSION',
        'PUBLICATION_AUTHORITY',
        'RETIREMENT_CONDITION'
    )
    content_classes = $r0ReportObj.content_classes
    semantic_coverage = [ordered]@{
        state = 'NOT_SEMANTICALLY_REVIEWED'
        note = 'R1 proves exact-byte duplicate presence only where scans complete; it does not inspect meaning.'
    }
    claim_evidence_audit = @(
        [ordered]@{
            Claim = 'A Downloads object has an exact-byte counterpart in an elected durable root.'
            ExactObject = 'R1 object row'
            Evidence = 'SHA256 equality from bounded local scan'
            VerifiedState = 'VERIFIED_LOCAL__DURABLE_DUPLICATE_CANDIDATE_OBSERVED'
            Contradiction = $null
            Downgrade = 'Hash equality does not prove receiver pickup, integration, authority, supersession, or delete safety.'
            NextProof = 'receiver contract and exact-object readproof'
        }
    )
    lifecycle_evidence = [ordered]@{
        discovered_local = $objects.Count
        verified_local = @($objects | Where-Object sha256).Count
        durable_hash_match_both = $both
        durable_hash_match_cofarm_only = $cofarmOnly
        durable_hash_match_costead_only = $costeadOnly
        landed = 0
        picked_up = 0
        integrated = 0
        coex = 0
        secret_or_private_hold_rows = $secretHold
    }
    eligible_next_transitions = @(
        'R2_BIND_INTENDED_RECEIVERS_FOR_EXACT_MATCHED_OBJECTS',
        'R2_ELECT_DURABLE_DESTINATIONS_FOR_UNBOUND_EXPOSURE_CANDIDATES',
        'R2_PRIVATE_PUBLIC_SEMANTIC_CLASSIFICATION',
        'R2_METADATA_MINIMIZED_PUBLIC_INDEX_AFTER_CLASSIFICATION'
    )
    blocked_transitions = @(
        'DELETE',
        'MOVE',
        'PUBLIC_UPLOAD',
        'PUBLIC_GITHUB_BULK_PUSH',
        'SECRET_EXPORT',
        'PICKED_UP_INFERENCE',
        'INTEGRATED_INFERENCE',
        'COEX_INFERENCE'
    )
    ux_summary = [ordered]@{
        state = 'UX_NOT_EVALUATED'
        CoHereNow = "Compared $($objects.Count) Downloads objects against CoFarm and CoStead by exact SHA-256."
        Meaning = if ($fullCoverage) { 'Negative no-match results are boundedly meaningful for the scanned roots.' } else { 'Some negative results remain unresolved because at least one durable-root scan had gaps.' }
        NextSafeAction = 'R2 receiver binding and privacy/semantic classification; no deletion or publication.'
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
        'HASH_MATCH_NE_DELETE_SAFE'
    )
}

$reportPath = Join-Path $outRoot '10_CUSTODY_RECONCILIATION_R1.json'
Write-NewUtf8 $reportPath (($report | ConvertTo-Json -Depth 100) + [Environment]::NewLine)
$reportOutSha = Sha256 $reportPath

$receipt = [ordered]@{
    STATE = if ($fullCoverage) { 'PASS_R1_DOWNLOADS_EXACT_HASH_CUSTODY_RECONCILIATION__COFARM_COSTEAD_BOUNDED_SCANS_COMPLETE__NO_SOURCE_MUTATION' } else { 'PASS_WITH_GAPS_R1_DOWNLOADS_EXACT_HASH_CUSTODY_RECONCILIATION__NO_NEGATIVE_INFERENCE_FOR_GAPPED_ROOTS__NO_SOURCE_MUTATION' }
    ROOT = $outRoot
    R0_ROOT = $R0Root
    R0_RECEIPT_SHA256 = $wantReceipt
    REPORT_SHA256 = $reportOutSha
    FILES = $objects.Count
    BOTH_ROOTS = $both
    COFARM_ONLY = $cofarmOnly
    COSTEAD_ONLY = $costeadOnly
    NO_MATCH_FULL_COVERAGE = $none
    UNRESOLVED_SCAN_GAPS = $unresolved
    SECRET_OR_PRIVATE_HOLD_ROWS = $secretHold
    FULL_COVERAGE = $fullCoverage
    SOURCE_MUTATIONS = 0
    DELETES = 0
    MOVES = 0
    NETWORK = 0
    PUBLIC_UPLOAD = 0
    NEXT = 'R2_RECEIVER_BINDING_PRIVACY_AND_SEMANTIC_CLASSIFICATION'
    RICK_ACTION = 'NONE__RETURN_ONLY_TERMINAL_JSON_IF_REQUESTED'
}

$receiptPath = Join-Path $outRoot '99_RECEIPT.json'
Write-NewUtf8 $receiptPath (($receipt | ConvertTo-Json -Depth 30) + [Environment]::NewLine)
$receiptSha = Sha256 $receiptPath

[ordered]@{
    STATE = $receipt.STATE
    ROOT = $outRoot
    RECEIPT_SHA256 = $receiptSha
    FILES = $objects.Count
    BOTH_ROOTS = $both
    COFARM_ONLY = $cofarmOnly
    COSTEAD_ONLY = $costeadOnly
    NO_MATCH_FULL_COVERAGE = $none
    UNRESOLVED_SCAN_GAPS = $unresolved
    SECRET_OR_PRIVATE_HOLD_ROWS = $secretHold
    FULL_COVERAGE = $fullCoverage
    NEXT = $receipt.NEXT
    RICK_ACTION = $receipt.RICK_ACTION
} | ConvertTo-Json -Depth 20 -Compress
