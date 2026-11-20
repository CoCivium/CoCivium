# CoCopy WPF bulk text donor R0, source candidate only.
# For a dedicated owned WPF TextBox. Never calls clipboard, SendInput, Enter, or Send.
# Live caller must supply explicit consent and real WPF keyboard focus.
$ErrorActionPreference='Stop'
function New-CoCopyWpfBulkContext {
    param([string]$WorkId='CoCopy.OwnedInput.Synthetic.R0')
    return @{ WorkId=$WorkId; Records=@{}; Busy=$false }
}
function New-CoCopyWpfHold {
    param([string]$State)
    return [pscustomobject]@{state=$State; insertion_calls=0; sent=$false; receiver_ack=$false}
}
function Convert-CoCopyLineEndings {
    param([AllowEmptyString()][string]$Text)
    $crlf=([string][char]13+[string][char]10)
    $lf=[string][char]10
    $cr=[string][char]13
    return $Text.Replace($crlf,$lf).Replace($cr,$lf)
}
function Invoke-CoCopyWpfBulkInsert {
    param(
        [Parameter(Mandatory)]$Context,
        [Parameter(Mandatory)][System.Windows.Controls.TextBox]$Target,
        [Parameter(Mandatory)][string]$RequestId,
        [AllowEmptyString()][string]$Payload,
        [Parameter(Mandatory)][bool]$Authorized,
        [AllowEmptyString()][string]$ExpectedValue,
        [switch]$FixtureUnfocused
    )
    if(-not $Authorized){return New-CoCopyWpfHold 'HELD_NOT_AUTHORIZED'}
    if($RequestId -cnotmatch '^[A-Za-z0-9._:-]{1,100}$'){return New-CoCopyWpfHold 'HELD_REQUEST_ID'}
    if($null -eq $Payload -or $Payload.Length -gt 150000){return New-CoCopyWpfHold 'HELD_PAYLOAD'}
    if($Context.Busy){return New-CoCopyWpfHold 'HELD_CONTEXT_BUSY'}
    if($Target.Tag -cne 'CoCopy.Owned.LocalTest.R0'){return New-CoCopyWpfHold 'HELD_TARGET_NOT_OWNED'}
    if(-not $Target.IsEnabled -or $Target.IsReadOnly){return New-CoCopyWpfHold 'HELD_READ_ONLY'}
    if(-not $Target.AcceptsReturn -and $Payload -match '[\r\n]'){return New-CoCopyWpfHold 'HELD_SINGLE_LINE'}
    if(-not $FixtureUnfocused -and -not $Target.IsKeyboardFocusWithin){return New-CoCopyWpfHold 'HELD_FOCUS_UNKNOWN'}
    if($Context.Records.ContainsKey($RequestId)){
        $prior=$Context.Records[$RequestId]
        if($prior.Payload -cne $Payload){return New-CoCopyWpfHold 'HELD_REQUEST_CONFLICT'}
        if($prior.State -ne 'VERIFIED'){return New-CoCopyWpfHold 'HELD_PRIOR_AMBIGUOUS_OR_REVOKED'}
        if((Convert-CoCopyLineEndings $Target.Text) -cne $prior.Normalized){return New-CoCopyWpfHold 'HELD_DESTINATION_CHANGED'}
        return New-CoCopyWpfHold 'DUPLICATE_SUPPRESSED'
    }
    if($Target.Text -cne $ExpectedValue){return New-CoCopyWpfHold 'HELD_PRESTATE_CHANGED'}
    # Restrict R0 to an initially empty dedicated field, never overwrite a user draft.
    if($Target.Text.Length -ne 0){return New-CoCopyWpfHold 'HELD_EXISTING_TEXT'}
    if($Target.MaxLength -gt 0 -and $Payload.Length -gt $Target.MaxLength){return New-CoCopyWpfHold 'HELD_MAX_LENGTH'}
    $expected=Convert-CoCopyLineEndings $Payload
    $record=@{State='AMBIGUOUS';Payload=$Payload;Normalized=$expected}
    $Context.Records[$RequestId]=$record  # Fence replay before first mutation.
    $Context.Busy=$true
    try{
        $Target.Text=$Payload  # Exactly one WPF property assignment, never per-char.
        if((Convert-CoCopyLineEndings $Target.Text) -cne $expected){
            return [pscustomobject]@{state='HELD_READBACK_MISMATCH';insertion_calls=1;sent=$false;receiver_ack=$false}
        }
        $record.State='VERIFIED'
        return [pscustomobject]@{state='INSERTED_VERIFIED_WPF_VALUE';insertion_calls=1;length=$Target.Text.Length;sent=$false;receiver_ack=$false}
    }catch{
        return [pscustomobject]@{state='HELD_INSERT_EXCEPTION';insertion_calls=1;sent=$false;receiver_ack=$false}
    }finally{$Context.Busy=$false}
}
function Invoke-CoCopyWpfBulkUndo {
    param(
        [Parameter(Mandatory)]$Context,
        [Parameter(Mandatory)][System.Windows.Controls.TextBox]$Target,
        [Parameter(Mandatory)][string]$RequestId,
        [Parameter(Mandatory)][bool]$Authorized,
        [switch]$FixtureUnfocused
    )
    if(-not $Authorized){return New-CoCopyWpfHold 'HELD_NOT_AUTHORIZED'}
    if($Context.Busy){return New-CoCopyWpfHold 'HELD_CONTEXT_BUSY'}
    if($Target.Tag -cne 'CoCopy.Owned.LocalTest.R0'){return New-CoCopyWpfHold 'HELD_TARGET_NOT_OWNED'}
    if(-not $FixtureUnfocused -and -not $Target.IsKeyboardFocusWithin){return New-CoCopyWpfHold 'HELD_FOCUS_UNKNOWN'}
    if(-not $Context.Records.ContainsKey($RequestId)){return New-CoCopyWpfHold 'HELD_NO_RECORD'}
    $record=$Context.Records[$RequestId]
    if($record.State -ne 'VERIFIED'){return New-CoCopyWpfHold 'HELD_PRIOR_AMBIGUOUS_OR_REVOKED'}
    if((Convert-CoCopyLineEndings $Target.Text) -cne $record.Normalized){
        return New-CoCopyWpfHold 'HELD_DESTINATION_CHANGED'
    }
    $record.State='AMBIGUOUS'
    $Context.Busy=$true
    try{
        $Target.Text=''
        if($Target.Text -cne ''){return New-CoCopyWpfHold 'HELD_UNDO_READBACK'}
        $record.State='UNDONE'
        return [pscustomobject]@{state='UNDO_VERIFIED_WPF_VALUE';insertion_calls=1;sent=$false;receiver_ack=$false}
    }catch{return New-CoCopyWpfHold 'HELD_UNDO_EXCEPTION'}
    finally{$Context.Busy=$false}
}
