// Review-only WinForms tray SHADOW. Never installs itself, dispatches a WorkID,
// touches a provider session, changes R5/R6/R8, or grants receiver authority.
using CoCivium.CoGuardian;
using System.Drawing;
using System.Windows.Forms;

namespace CoCivium.CoGuardianTrayShadow;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        // Reuse the bounded Python SHADOW canary's exact Windows session mutex.
        // Suppresses a second tray of either implementation while one holds it.
        // This is NOT a distributed cross-origin pre-effect authority lease.
        using var mutex = new Mutex(true, MuleObservation.ShadowTrayMutexName,
                                    out bool isFirstInstance);
        if (!isFirstInstance)
            return;
        try
        {
            ApplicationConfiguration.Initialize();
            Application.Run(new TrayShadowContext());
        }
        finally
        {
            mutex.ReleaseMutex();
        }
    }
}

internal sealed class TrayShadowContext : ApplicationContext
{
    private readonly NotifyIcon icon;
    private readonly ContextMenuStrip menu;
    private readonly ToolStripMenuItem status;
    private readonly ToolStripMenuItem work;

    public TrayShadowContext()
    {
        status = new ToolStripMenuItem("State: HOLD_SOURCE_UNBOUND") { Enabled = false };
        work = new ToolStripMenuItem("WorkID: NONE") { Enabled = false };
        var refresh = new ToolStripMenuItem("Refresh local evidence (read-only)");
        var stop = new ToolStripMenuItem("Stop tray shadow (no WorkID changes)");
        refresh.Click += (_, _) => RefreshEvidence();
        stop.Click += (_, _) => ExitThread();

        menu = new ContextMenuStrip();
        menu.Items.Add(new ToolStripMenuItem("CoGuardian Mule SHADOW") { Enabled = false });
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(status);
        menu.Items.Add(work);
        menu.Items.Add(new ToolStripMenuItem("Receiver ACK: UNPROVEN") { Enabled = false });
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(refresh);
        menu.Items.Add(stop);
        icon = new NotifyIcon
        {
            Icon = SystemIcons.Information,
            Text = "CoGuardian Mule SHADOW | Receiver unverified",
            ContextMenuStrip = menu,
            Visible = true
        };
        RefreshEvidence();
    }

    private void RefreshEvidence()
    {
        MuleState state;
        try
        {
            string evidenceDirectory = Path.Combine(AppContext.BaseDirectory, "evidence");
            string evidenceFile = Path.Combine(evidenceDirectory, "mule-observation.json");
            if (Directory.Exists(evidenceDirectory) &&
                (File.GetAttributes(evidenceDirectory) & FileAttributes.ReparsePoint) != 0)
                state = new MuleState("HOLD_LINKED_SOURCE_DIR", "NONE", false);
            else if (!File.Exists(evidenceFile))
                state = MuleObservation.Read(null, DateTimeOffset.UtcNow);
            else if ((File.GetAttributes(evidenceFile) & FileAttributes.ReparsePoint) != 0)
                state = new MuleState("HOLD_LINKED_SOURCE_FILE", "NONE", false);
            else if (new FileInfo(evidenceFile).Length > 4096)
                state = new MuleState("HOLD_SOURCE_OVERSIZE", "NONE", false);
            else
                state = MuleObservation.Read(File.ReadAllText(evidenceFile),
                                             DateTimeOffset.UtcNow);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException
                                   or ArgumentException)
        {
            state = new MuleState("HOLD_SOURCE_READ", "NONE", false);
        }
        status.Text = "State: " + state.Code;
        work.Text = "WorkID: " + state.WorkId;
        // No green icon, apparent success, pop-up balloon, telemetry, or polling.
        // This menu is the entire no-effect surface until owner-approved adoption.
    }

    protected override void ExitThreadCore()
    {
        icon.Visible = false;
        icon.Dispose();
        menu.Dispose();
        base.ExitThreadCore();
    }
}
