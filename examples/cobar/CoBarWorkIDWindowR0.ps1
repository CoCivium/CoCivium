# CoBar WorkID window R0: explicit, read-only Windows WPF candidate.
# Source-only donor within existing CoBar PR. Not an installed X2 service or native receiver.
# Never reads private chats, captures global input, sends data, controls a worker or claims ACK.
param(
    [switch]$Show,
    [string]$ReadbackPath = '',
    [string]$ExpectedWorkId = 'CoPre.ReadyCycle.Synthetic.R0',
    [string]$ExpectedSourceSha256 = '',
    [string]$ExpectedPacketSha256 = ''
)
$ErrorActionPreference = 'Stop'

function New-CoBarHeldView {
    param([string]$Reason)
    return [pscustomobject]@{
        Schema = 'CoAll.CoBar.WorkIDWindow.R0'
        State = 'HELD'
        WorkId = 'UNKNOWN'
        Current = 'No qualified WorkID view'
        Why = $Reason
        Next = 'Recover an exact, trusted source-bound readback'
        Unknown = 'Local currentness and receiver origin unverified'
        Challenge = 'Inspect source, identity, hash and authority'
        Recover = 'Last-good work is not established by this window'
        ReceiverAck = $false
        EffectAuthority = 'NONE'
        IsLive = $false
    }
}

function Read-CoBarWorkIDFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not [IO.Path]::IsPathFullyQualified($Path)) { throw 'HELD_ABSOLUTE_PATH_REQUIRED' }
    if ([IO.Path]::GetExtension($Path) -cne '.json') { throw 'HELD_JSON_ONLY' }
    if (-not [IO.File]::Exists($Path)) { throw 'HELD_SOURCE_MISSING' }
    $fi = [IO.FileInfo]::new($Path)
    if (($fi.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'HELD_REPARSE_POINT'
    }
    if ($fi.Length -lt 1 -or $fi.Length -gt 65536) { throw 'HELD_SIZE' }
    $raw = [IO.File]::ReadAllText($Path)
    return ConvertFrom-Json -InputObject $raw -Depth 24 -ErrorAction Stop
}

function New-CoBarWorkIDView {
    param(
        $Readback,
        [string]$ExpectedWorkId = 'CoPre.ReadyCycle.Synthetic.R0',
        [string]$ExpectedSourceSha256 = '',
        [string]$ExpectedPacketSha256 = ''
    )
    $held = New-CoBarHeldView 'Invalid or untrusted readback'
    if ($null -eq $Readback) { return New-CoBarHeldView 'No readback was supplied' }
    # Exactly this synthetic research WorkID is supported. Do not accept live scoped work here.
    if ($ExpectedWorkId -cne 'CoPre.ReadyCycle.Synthetic.R0') {
        return New-CoBarHeldView 'HELD_SCOPE_NOT_QUALIFIED'
    }
    $hex = '^[a-f0-9]{64}$'
    if ($ExpectedSourceSha256 -cnotmatch $hex -or
        $ExpectedPacketSha256 -cnotmatch $hex) {
        return New-CoBarHeldView 'HELD_EXPECTED_DIGESTS_REQUIRED'
    }

    $item = $Readback
    if ($Readback.schema -ceq 'CoAll.CoOwnedWork.SqliteBridgeProof.R0') {
        if (($Readback.receiver_ack -isnot [bool]) -or
            $Readback.receiver_ack -or $Readback.external_effects -ne 0) {
            return New-CoBarHeldView 'HELD_BRIDGE_EFFECT_OR_ACK_CLAIM'
        }
        $item = $Readback.receiver_readback
    }

    if ($null -eq $item -or
        $item.schema -cne 'CoAll.CoNarrativeWorkID.R0.Readback' -or
        $item.work_id -cne $ExpectedWorkId -or
        $item.state -cnotin @('COLD_SOURCE_RECONSTRUCTED', 'HELD_REVOKED') -or
        $item.source_ref -cnotmatch '^CoCivium/CoCivium:CoPre[.]md@[a-f0-9]{40}$' -or
        $item.source_sha256 -cne $ExpectedSourceSha256 -or
        $item.packet_sha256 -cne $ExpectedPacketSha256 -or
        $item.receipt_sha256 -cnotmatch $hex) {
        return New-CoBarHeldView 'HELD_WORKID_SOURCE_OR_REVISION_MISMATCH'
    }
    if (($item.local_replay_only -isnot [bool]) -or
        $item.local_replay_only -ne $true -or
        ($item.external_receiver_ack -isnot [bool]) -or
        $item.external_receiver_ack -ne $false -or
        ($item.independent_provider -isnot [bool]) -or
        $item.independent_provider -ne $false -or
        $item.committed_work_ids -ne 1 -or
        $item.committed_effects -ne 1) {
        return New-CoBarHeldView 'HELD_NONCLAIMS_OR_COUNTS_VIOLATION'
    }
    if ($item.state -ceq 'HELD_REVOKED') {
        if ($null -ne $item.next_safe_deed) {
            return New-CoBarHeldView 'HELD_REVOKED_BUT_NEXT_ACTION_PRESENT'
        }
        return [pscustomobject]@{
            Schema = 'CoAll.CoBar.WorkIDWindow.R0'
            State = 'HELD_REVOKED'
            WorkId = $ExpectedWorkId
            Current = 'Synthetic WorkID revoked'
            Why = 'Exact source-bound record is present, but no work is eligible'
            Next = 'No action permitted'
            Unknown = 'Independent receiver and currentness remain unverified'
            Challenge = 'Review revocation and exact source'
            Recover = 'Preserve record; never silently re-enable'
            ReceiverAck = $false
            EffectAuthority = 'NONE'
            IsLive = $false
        }
    }
    if ($item.next_safe_deed -isnot [string] -or
        $item.next_safe_deed.Length -lt 1 -or $item.next_safe_deed.Length -gt 240 -or
        $item.narrative_summary -isnot [string] -or
        $item.narrative_summary.Length -lt 1 -or
        $item.narrative_summary.Length -gt 240) {
        return New-CoBarHeldView 'HELD_NARRATIVE_CONTENT_INVALID'
    }
    return [pscustomobject]@{
        Schema = 'CoAll.CoBar.WorkIDWindow.R0'
        State = 'SOURCE_BOUND_SYNTHETIC_REPLAY_ONLY'
        WorkId = $ExpectedWorkId
        Current = 'Synthetic WorkID recovered from bounded SQLite readback'
        Why = $item.narrative_summary
        Next = $item.next_safe_deed
        Unknown = 'No timestamped live X2 feed; no independently authenticated CoAll receiver ACK'
        Challenge = 'Expected source/packet hashes supplied by caller, not an authentication service'
        Recover = 'Close and reopen with the exact same local readback; native runtime not qualified'
        ReceiverAck = $false
        EffectAuthority = 'NONE'
        IsLive = $false
    }
}

function New-CoBarWorkIDWindow {
    param([Parameter(Mandatory)]$View)
    Add-Type -AssemblyName PresentationFramework,PresentationCore,WindowsBase
    $window = [System.Windows.Window]::new()
    $window.Title = 'CoBar | Source-bound WorkID (R0 canary)'
    $window.Tag = 'COBAR_NATIVE_WINDOW_READONLY_RESEARCH_R0'
    $window.Width = 960
    $window.Height = 300
    $window.MinWidth = 480
    $window.MinHeight = 230
    $window.Topmost = $false
    $window.ShowInTaskbar = $true
    $window.WindowStartupLocation = 'Manual'
    $window.ResizeMode = 'CanResize'
    $window.WindowStyle = 'SingleBorderWindow'
    $work = [System.Windows.SystemParameters]::WorkArea
    $window.Left = [Math]::Max($work.Left, $work.Left + ($work.Width - $window.Width) / 2)
    $window.Top = [Math]::Max($work.Top, $work.Bottom - $window.Height)

    $outer = [System.Windows.Controls.DockPanel]::new()
    $outer.Margin = [System.Windows.Thickness]::new(14)
    $window.Content = $outer

    $top = [System.Windows.Controls.StackPanel]::new()
    [System.Windows.Controls.DockPanel]::SetDock($top, 'Top')
    [void]$outer.Children.Add($top)
    $headline = [System.Windows.Controls.TextBlock]::new()
    $headline.Text = 'CoHereNow | ' + [string]$View.State
    $headline.FontWeight = 'Bold'
    $headline.FontSize = 17
    [void]$top.Children.Add($headline)
    $identity = [System.Windows.Controls.TextBlock]::new()
    $identity.Text = [string]$View.WorkId + ' | Receiver ACK: NO | LIVE: NO'
    $identity.FontSize = 12
    $identity.Margin = [System.Windows.Thickness]::new(0,3,0,9)
    [void]$top.Children.Add($identity)

    $details = [System.Windows.Controls.ScrollViewer]::new()
    $details.VerticalScrollBarVisibility = 'Auto'
    [void]$outer.Children.Add($details)
    $fields = [System.Windows.Controls.StackPanel]::new()
    $details.Content = $fields
    foreach ($key in @('Current','Why','Next','Unknown','Challenge','Recover')) {
        $line = [System.Windows.Controls.TextBlock]::new()
        $line.Text = $key.ToUpperInvariant() + '  ' + [string]$View.$key
        $line.TextWrapping = 'Wrap'
        $line.Margin = [System.Windows.Thickness]::new(0,1,0,3)
        [void]$fields.Children.Add($line)
    }

    $buttons = [System.Windows.Controls.StackPanel]::new()
    $buttons.Orientation = 'Horizontal'
    $buttons.HorizontalAlignment = 'Right'
    $buttons.Margin = [System.Windows.Thickness]::new(0,8,0,0)
    [System.Windows.Controls.DockPanel]::SetDock($buttons,'Bottom')
    # Ensure action dock is inserted *before* the scroll viewer.
    [void]$outer.Children.Remove($details)
    [void]$outer.Children.Add($buttons)
    [void]$outer.Children.Add($details)

    $stop = [System.Windows.Controls.Button]::new()
    $stop.Content = 'Stop work (unavailable)'
    $stop.IsEnabled = $false
    $stop.Tag = 'NO_NATIVE_WORK_RECEIVER'
    $stop.Margin = [System.Windows.Thickness]::new(0,0,8,0)
    [void]$buttons.Children.Add($stop)
    $close = [System.Windows.Controls.Button]::new()
    $close.Content = 'Close viewer'
    $close.Tag = 'RENDERER_ONLY_CLOSE'
    $close.IsCancel = $true
    $close.Add_Click({ $window.Close() }.GetNewClosure())
    [void]$buttons.Children.Add($close)
    return $window
}

if ($Show) {
    if (-not $IsWindows) { throw 'HELD_WINDOWS_WPF_ONLY' }
    try {
        $readback = Read-CoBarWorkIDFile -Path $ReadbackPath
        $view = New-CoBarWorkIDView -Readback $readback -ExpectedWorkId $ExpectedWorkId -ExpectedSourceSha256 $ExpectedSourceSha256 -ExpectedPacketSha256 $ExpectedPacketSha256
    } catch {
        $view = New-CoBarHeldView ('HELD_LOCAL_READ: ' + $_.Exception.Message)
    }
    $window = New-CoBarWorkIDWindow -View $view
    [void]$window.ShowDialog()
}
