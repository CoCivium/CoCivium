# Hosted Windows WPF object tests. No Window.Show, clipboard, HID or X2 action.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName PresentationFramework,PresentationCore,WindowsBase
. "$PSScriptRoot/CoCopyWpfBulkInputR0.ps1"
$script:count=0
function Assert-CoCopy([string]$Name,[bool]$Condition) {
    if(-not $Condition){throw "FAIL_COCOPY_WPF $Name"}
    $script:count++
    Write-Output "PASS_COCOPY_WPF $Name"
}
function New-OwnedBox {
    $box=[Windows.Controls.TextBox]::new()
    $box.Tag='CoCopy.Owned.LocalTest.R0'
    $box.AcceptsReturn=$true
    $box.MaxLength=150000
    return $box
}
$ctx=New-CoCopyWpfBulkContext
$t=New-OwnedBox
$script:eventCount=0
$t.Add_TextChanged({$script:eventCount++})
$unauthed=Invoke-CoCopyWpfBulkInsert -Context $ctx -Target $t -RequestId 'work.1' -Payload 'a' -Authorized $false -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'unauthed_held' ($unauthed.state -eq 'HELD_NOT_AUTHORIZED' -and $t.Text -eq '')
$noFocus=Invoke-CoCopyWpfBulkInsert -Context $ctx -Target $t -RequestId 'work.1' -Payload 'a' -Authorized $true -ExpectedValue ''
Assert-CoCopy 'no_actual_focus_held' ($noFocus.state -eq 'HELD_FOCUS_UNKNOWN' -and $t.Text -eq '')
$t.Tag='another-app'
$wrong=Invoke-CoCopyWpfBulkInsert -Context $ctx -Target $t -RequestId 'work.1' -Payload 'a' -Authorized $true -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'wrong_owner_held' ($wrong.state -eq 'HELD_TARGET_NOT_OWNED')
$t.Tag='CoCopy.Owned.LocalTest.R0'
$payload=('First'+[char]13+[char]10+'Second'+[char]10+'Unicode '+[char]0x263A)
$ok=Invoke-CoCopyWpfBulkInsert -Context $ctx -Target $t -RequestId 'work.1' -Payload $payload -Authorized $true -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'wpf_bulk_verified' ($ok.state -eq 'INSERTED_VERIFIED_WPF_VALUE' -and $ok.insertion_calls -eq 1)
Assert-CoCopy 'newline_unicode_readback' ((Convert-CoCopyLineEndings $t.Text) -ceq (Convert-CoCopyLineEndings $payload))
Assert-CoCopy 'one_text_changed_event' ($script:eventCount -eq 1)
$replay=Invoke-CoCopyWpfBulkInsert -Context $ctx -Target $t -RequestId 'work.1' -Payload $payload -Authorized $true -ExpectedValue $t.Text -FixtureUnfocused
Assert-CoCopy 'no_duplicate_replay' ($replay.state -eq 'DUPLICATE_SUPPRESSED' -and $script:eventCount -eq 1)
$conflict=Invoke-CoCopyWpfBulkInsert -Context $ctx -Target $t -RequestId 'work.1' -Payload 'different' -Authorized $true -ExpectedValue $t.Text -FixtureUnfocused
Assert-CoCopy 'conflicting_request_held' ($conflict.state -eq 'HELD_REQUEST_CONFLICT')
$t.Text=$t.Text+' human edit'
$undo=Invoke-CoCopyWpfBulkUndo -Context $ctx -Target $t -RequestId 'work.1' -Authorized $true -FixtureUnfocused
Assert-CoCopy 'undo_respects_human_edit' ($undo.state -eq 'HELD_DESTINATION_CHANGED' -and $t.Text.EndsWith(' human edit'))
$ctx2=New-CoCopyWpfBulkContext
$t2=New-OwnedBox
$long=('row'+[char]13+[char]10+'A').ToString()*20000
$big=Invoke-CoCopyWpfBulkInsert -Context $ctx2 -Target $t2 -RequestId 'large.1' -Payload $long -Authorized $true -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'large_bulk_one_assignment' ($big.state -eq 'INSERTED_VERIFIED_WPF_VALUE' -and $big.insertion_calls -eq 1)
Assert-CoCopy 'large_text_readback' ((Convert-CoCopyLineEndings $t2.Text) -ceq (Convert-CoCopyLineEndings $long))
$undone=Invoke-CoCopyWpfBulkUndo -Context $ctx2 -Target $t2 -RequestId 'large.1' -Authorized $true -FixtureUnfocused
Assert-CoCopy 'exact_undo' ($undone.state -eq 'UNDO_VERIFIED_WPF_VALUE' -and $t2.Text -eq '')
$reinsert=Invoke-CoCopyWpfBulkInsert -Context $ctx2 -Target $t2 -RequestId 'large.1' -Payload $long -Authorized $true -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'undone_request_cannot_replay' ($reinsert.state -eq 'HELD_PRIOR_AMBIGUOUS_OR_REVOKED')
$ctx3=New-CoCopyWpfBulkContext
$t3=New-OwnedBox
$t3.AcceptsReturn=$false
$single=Invoke-CoCopyWpfBulkInsert -Context $ctx3 -Target $t3 -RequestId 'single' -Payload $payload -Authorized $true -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'no_multiline_in_single_line' ($single.state -eq 'HELD_SINGLE_LINE' -and $t3.Text -eq '')
$t3.AcceptsReturn=$true
$t3.MaxLength=2
$tooLong=Invoke-CoCopyWpfBulkInsert -Context $ctx3 -Target $t3 -RequestId 'max' -Payload 'three' -Authorized $true -ExpectedValue '' -FixtureUnfocused
Assert-CoCopy 'maxlength_held' ($tooLong.state -eq 'HELD_MAX_LENGTH')
$t3.MaxLength=0
$t3.Text='unsent human draft'
$noClobber=Invoke-CoCopyWpfBulkInsert -Context $ctx3 -Target $t3 -RequestId 'existing' -Payload 'xyz' -Authorized $true -ExpectedValue $t3.Text -FixtureUnfocused
Assert-CoCopy 'nonempty_draft_never_clobbered' ($noClobber.state -eq 'HELD_EXISTING_TEXT' -and $t3.Text -eq 'unsent human draft')
Assert-CoCopy 'no_receiver_no_send' (-not $ok.sent -and -not $big.receiver_ack)
if($script:count -ne 18){throw "HOLD_EXPECTED_18_GOT_$script:count"}
Write-Output "PASS_COCOPY_NATIVE_WPF_SOURCE_R0 tests=$script:count focus_real=UNPROVEN no_window=TRUE clipboard=0 send=0 receiver_ack=UNPROVEN"
