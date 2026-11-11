"""Regression bridge: ensure CoFuture pull vectors run in existing CoLoop CI."""
import pathlib
import subprocess
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
TARGET=ROOT/"experiments"/"gdside"/"cofuture_pull_vector_r0.py"

class CoFutureCI(unittest.TestCase):
    def test_existing_co_loop_workflow_executes_pull_vector_suite(self):
        proc=subprocess.run([sys.executable,"-B",str(TARGET)],
                            cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(proc.returncode,0,proc.stdout+"\n"+proc.stderr)
        self.assertIn("Ran 10 tests",proc.stderr)
        self.assertIn("OK",proc.stderr)

if __name__=="__main__":
    unittest.main(verbosity=2)
