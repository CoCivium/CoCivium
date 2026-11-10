#!/usr/bin/env python3
"""Version-local candidate test for the isolated CoPre first-use CLI.

This is not the pinned consumer acceptance contract, and cannot
independently certify MVP, native receiver pickup, or useful first use.
"""
from pathlib import Path
import os
import subprocess
import sys

if not __debug__:
    raise RuntimeError("HOLD_OPTIMIZED_MODE_SOURCE_CONTRACT_ASSERTS_DISABLED")

path = Path(os.environ["COMVP_ARTIFACT_PATH"]).resolve()
root = Path.cwd().resolve()
assert path.is_relative_to(root / "scripts"), "wrong CoPre artifact family"
assert path.name == "CoMVPCoPreFirstUseR0.py", "wrong candidate entrypoint"
result = subprocess.run(
    [sys.executable, "-B", str(path), "--selftest"],
    cwd=root, timeout=12, capture_output=True, text=True, check=False,
)
assert result.returncode == 0, result.stderr[-2000:]
assert "CoCivium.CoMVPCoPreFirstUseSelftest.R0" in result.stdout
print("SOURCE_CANDIDATE_SELFTEST_ONLY")
