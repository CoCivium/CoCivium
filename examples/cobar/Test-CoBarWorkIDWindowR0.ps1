# Windows STA tests for a read-only CoBar native WorkID viewer donor.
# No Window.Show, user input capture, service, clipboard, network or X2 writes.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName PresentationFramework,PresentationCore,WindowsBase
. "$PSScriptRoot/CoBarWorkIDWindowR0.ps1"
$script:tested=0
function Check([string]$name,[bool]$ok) {
    if(-not $ok){throw "FAIL_COBAR_WORKID_WINDOW $name"}
    $script:tested++
    Write-Output "PASS_COBAR_WORKID_WINDOW $name"
}
$source=('a'*64)
$packet=('b'*64)
$receipt=('c'*64)
$commit=('d'*40)
$expectedId='CoPre.ReadyCycle.Synthetic.R0'
$readback=[pscustomobject]@{
    schema='CoAll.CoNarrativeWorkID.R0.Readback'
    state='COLD_SOURCE_RECONSTRUCTED'
    work_id=$expectedId
    source_ref="CoCivium/CoCivium:CoPre.md@$commit"
    source_sha256=$source
    packet_sha256=$packet
    receipt_sha256=$receipt
    local_replay_only=$true
    external_receiver_ack=$false
    independent_provider=$false
    committed_work_ids=1
    committed_effects=1
    narrative_summary='Existing public-safe synthetic WorkID.'
    next_safe_deed='Read source-bound synthetic proof only.'
}
function View($r) {
    New-CoBarWorkIDView -Readback $r -ExpectedWorkId $expectedId -ExpectedSourceSha256 $source -ExpectedPacketSha256 $packet
}
$unknown=View $null
Check 'missing_source_fails_closed' ($unknown.State -eq 'HELD' -and -not $unknown.IsLive)
$unpinned=New-CoBarWorkIDView -Readback $readback -ExpectedWorkId $expectedId
Check 'missing_digests_held' ($unpinned.State -eq 'HELD')
$wrongScope=New-CoBarWorkIDView -Readback $readback -ExpectedWorkId 'Another.Private.Work' -ExpectedSourceSha256 $source -ExpectedPacketSha256 $packet
Check 'wrong_scope_held' ($wrongScope.State -eq 'HELD')
$ok=View $readback
Check 'exact_source_projection' ($ok.State -eq 'SOURCE_BOUND_SYNTHETIC_REPLAY_ONLY' -and $ok.WorkId -eq $expectedId)
Check 'projection_never_live' (-not $ok.IsLive -and -not $ok.ReceiverAck -and $ok.EffectAuthority -eq 'NONE')
Check 'readback_six_fields_present' ((@('Current','Why','Next','Unknown','Challenge','Recover') | Where-Object {-not [string]$ok.$_}).Count -eq 0)
$wrong=$readback.PSObject.Copy();$wrong.source_sha256=('e'*64)
Check 'source_hash_mismatch_held' ((View $wrong).State -eq 'HELD')
$wrong=$readback.PSObject.Copy();$wrong.packet_sha256=('f'*64)
Check 'packet_hash_mismatch_held' ((View $wrong).State -eq 'HELD')
$wrong=$readback.PSObject.Copy();$wrong.committed_effects=2
Check 'duplicate_effect_count_held' ((View $wrong).State -eq 'HELD')
$wrong=$readback.PSObject.Copy();$wrong.external_receiver_ack=$true
Check 'forged_receiver_ack_held' ((View $wrong).State -eq 'HELD')
$wrong=$readback.PSObject.Copy();$wrong.narrative_summary=''
Check 'empty_narrative_held' ((View $wrong).State -eq 'HELD')
$wrong=$readback.PSObject.Copy();$wrong.state='PRODUCTION_OK'
Check 'unrecognized_state_held' ((View $wrong).State -eq 'HELD')
$revoked=$readback.PSObject.Copy();$revoked.state='HELD_REVOKED';$revoked.next_safe_deed=$null
$rev=View $revoked
Check 'revocation_disables_work' ($rev.State -eq 'HELD_REVOKED' -and $rev.Next -eq 'No action permitted')
$revoked.next_safe_deed='Still runnable'
Check 'revocation_conflicting_deed_held' ((View $revoked).State -eq 'HELD')
$bridge=[pscustomobject]@{schema='CoAll.CoOwnedWork.SqliteBridgeProof.R0';receiver_ack=$false;external_effects=0;receiver_readback=$readback}
Check 'explicit_synthetic_bridge_view' ((View $bridge).State -eq 'SOURCE_BOUND_SYNTHETIC_REPLAY_ONLY')
$bridge.receiver_ack=$true
Check 'bridge_forged_ack_held' ((View $bridge).State -eq 'HELD')
$native=New-CoBarWorkIDWindow -View $ok
Check 'native_window_observer_only' ($native.Tag -eq 'COBAR_NATIVE_WINDOW_READONLY_RESEARCH_R0' -and -not $native.Topmost)
$panel=[System.Windows.Controls.DockPanel]$native.Content
$buttons= @($panel.Children | Where-Object {$_ -is [System.Windows.Controls.StackPanel] -and $_.Orientation -eq 'Horizontal'})[0]
$stop=@($buttons.Children | Where-Object {$_.Content -eq 'Stop work (unavailable)'})[0]
$close=@($buttons.Children | Where-Object {$_.Content -eq 'Close viewer'})[0]
Check 'stop_work_disabled_without_receiver' ($null -ne $stop -and -not $stop.IsEnabled -and $stop.Tag -eq 'NO_NATIVE_WORK_RECEIVER')
Check 'close_viewer_available' ($null -ne $close -and $close.IsEnabled -and $close.IsCancel)
$native.Close()
$dir=Join-Path ([IO.Path]::GetTempPath()) ('cobar-workid-test-'+[Guid]::NewGuid().ToString('N'))
try {
    [void][IO.Directory]::CreateDirectory($dir)
    $file=Join-Path $dir 'synthetic-readback.json'
    [IO.File]::WriteAllText($file,(ConvertTo-Json $readback -Depth 8))
    $loaded=Read-CoBarWorkIDFile -Path $file
    Check 'read_only_file_load' ($loaded.work_id -ceq $expectedId)
    $wrongExtension=Join-Path $dir 'synthetic-readback.txt'
    [IO.File]::WriteAllText($wrongExtension,'{}')
    $held=$false
    try { $null=Read-CoBarWorkIDFile -Path $wrongExtension } catch {$held=$true}
    Check 'non_json_path_held' $held
}finally{
    [IO.Directory]::Delete($dir,$true)
}
if($script:tested -ne 21){throw "HOLD_EXPECTED_21_GOT_$script:tested"}
Write-Output "PASS_COBAR_NATIVE_WORKID_VIEW_R0 checks=$($script:tested) visible=NO runtime=NO receiver_ack=NO external_effects=0"
