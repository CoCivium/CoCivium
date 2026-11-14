// Windows CI-only console probe. No CoGuardian tray/UI/WorkID operation is created.
using CoCivium.CoGuardian;
using System.Threading;

internal static class MutexProbe
{
    private static int Main(string[] args)
    {
        if (args.Length != 1 || (args[0] != "probe" && args[0] != "hold"))
        {
            Console.WriteLine("HOLD_UNEXPECTED_PROBE_ARGS");
            return 64;
        }

        using var mutex = new Mutex(true, MuleObservation.ShadowTrayMutexName, out bool createdNew);
        if (!createdNew)
        {
            Console.WriteLine("BLOCKED_EXISTING_SHADOW_OWNER");
            return 3;
        }

        Console.WriteLine("ACQUIRED_SHADOW_MUTEX");
        Console.Out.Flush();
        try
        {
            if (args[0] == "hold" && Console.ReadLine() != "RELEASE")
            {
                Console.Error.WriteLine("HOLD_NO_RELEASE_SIGNAL");
                return 75;
            }
            return 0;
        }
        finally
        {
            mutex.ReleaseMutex();
        }
    }
}
