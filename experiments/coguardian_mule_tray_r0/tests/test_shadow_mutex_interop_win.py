#!/usr/bin/env python3
"""Disposable Windows CI test of Python/Win32 and .NET shadow-mule mutex interop.

Uses the exact named mutex from the bounded X2 Python canary and from the
candidate WinForms Program.cs, but NEVER runs either GUI or alters X2.
"""
import ctypes
from ctypes import wintypes
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NAME = r"Local\CoCivium.CoGuardianMule.ShadowR0.OneOwner"
DLL = HERE / "bin" / "Release" / "net8.0" / "CoGuardianMule.MutexProbe.dll"
OUT = Path("out/mule/mutex-interop-receipt.json")
ERROR_ALREADY_EXISTS = 183
results = []
owner = None
handle = None
failure = None

def check(name, condition):
    passed = bool(condition)
    results.append({"test": name, "pass": passed})
    if not passed:
        raise AssertionError("HOLD_" + name)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def csharp(mode="probe"):
    return subprocess.run(
        ["dotnet", str(DLL), mode], capture_output=True, text=True,
        timeout=15, creationflags=subprocess.CREATE_NO_WINDOW,
    )

def acquire_win32():
    h = kernel.CreateMutexW(None, False, NAME)
    if not h:
        raise ctypes.WinError(ctypes.get_last_error())
    return h, ctypes.get_last_error()

if sys.platform != "win32":
    raise SystemExit("HOLD_WINDOWS_CI_ONLY")

kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.CreateMutexW.argtypes = (ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR)
kernel.CreateMutexW.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel.CloseHandle.restype = wintypes.BOOL

try:
    program = (ROOT / "Program.cs").read_text(encoding="utf-8")
    model = (ROOT / "MuleObservation.cs").read_text(encoding="utf-8")
    check("winforms_program_reuses_shared_constant",
          "MuleObservation.ShadowTrayMutexName" in program
          and 'MuleObservation.ShadowTrayMutexName,' in program)
    check("model_exactly_pins_python_native_mutex",
          '@"' + NAME + '"' in model)
    check("disposable_probe_compiled", DLL.is_file())

    handle, winerr = acquire_win32()
    check("python_win32_first_owner", winerr != ERROR_ALREADY_EXISTS)
    blocked = csharp()
    check("python_owner_blocks_dotnet", blocked.returncode == 3
          and "BLOCKED_EXISTING_SHADOW_OWNER" in blocked.stdout)
    kernel.CloseHandle(handle)
    handle = None

    free = csharp()
    check("dotnet_acquires_after_python_releases", free.returncode == 0
          and "ACQUIRED_SHADOW_MUTEX" in free.stdout)

    owner = subprocess.Popen(
        ["dotnet", str(DLL), "hold"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    ready = owner.stdout.readline().strip()
    check("dotnet_second_process_owns_named_mutex", ready == "ACQUIRED_SHADOW_MUTEX"
          and owner.poll() is None)
    blocked_again = csharp()
    check("dotnet_owner_blocks_second_dotnet", blocked_again.returncode == 3
          and "BLOCKED_EXISTING_SHADOW_OWNER" in blocked_again.stdout)
    handle, winerr = acquire_win32()
    check("dotnet_owner_blocks_python_win32", winerr == ERROR_ALREADY_EXISTS)
    kernel.CloseHandle(handle)
    handle = None

    owner.stdin.write("RELEASE\n")
    owner.stdin.flush()
    _, stderr = owner.communicate(timeout=15)
    check("dotnet_owner_exits_cleanly_after_release", owner.returncode == 0
          and stderr.strip() == "")
    owner = None

    handle, winerr = acquire_win32()
    check("python_reacquires_after_dotnet_release", winerr != ERROR_ALREADY_EXISTS)
    kernel.CloseHandle(handle)
    handle = None
except Exception as exc:
    failure = type(exc).__name__ + ": " + str(exc)
finally:
    if handle:
        kernel.CloseHandle(handle)
    if owner is not None:
        try:
            if owner.poll() is None:
                owner.stdin.write("RELEASE\n")
                owner.stdin.flush()
                owner.communicate(timeout=5)
        except Exception:
            owner.kill()
            owner.communicate(timeout=5)

receipt = {
    "schema": "CoGuardian.Mule.ShadowCrossProcessMutex.WindowsCI.R0",
    "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "state": "PASS_FOR_SCOPE" if not failure and all(x["pass"] for x in results)
             else "HOLD_MUTEX_INTEROP",
    "tests": len(results),
    "passed": sum(x["pass"] for x in results),
    "results": results,
    "source_sha256": {
        "Program.cs": sha(ROOT / "Program.cs"),
        "MuleObservation.cs": sha(ROOT / "MuleObservation.cs"),
        "MutexProbe.cs": sha(HERE / "MutexProbe.cs")
    },
    "failure": failure,
    "effect": "TEMPORARY_KERNEL_MUTEX_ONLY_NO_GUI",
    "windows_target": "DISPOSABLE_GITHUB_RUNNER_NOT_X2",
    "provider_sessions_touched": 0,
    "tray_icons_created": 0,
    "additional_schedulers": 0,
    "independent_receiver_ack": "NOT_ESTABLISHED",
    "not_proven": [
        "WINFORMS_MAIN_EXECUTED", "X2_LIVE_CROSS_BINARY_CONTENTION",
        "USER_VISIBLE_TRAY", "CROSS_HOST_EFFECT_LEASE",
        "WORKID_RECEIVER_ORIGIN_ACK", "USEFUL_USER_WORK"
    ]
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"state": receipt["state"], "tests": receipt["tests"],
                  "passed": receipt["passed"], "failure": failure, "receipt": str(OUT)}))
raise SystemExit(0 if receipt["state"] == "PASS_FOR_SCOPE" else 2)
