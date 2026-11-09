"""Synthetic CLI -> receipt tests, no Ollama runtime or X2 required."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from rickbar_ollama_bridge_r0 import run

class FakeGateway:
    def __init__(self, available=True, text="pong"):
        self.available=available
        self.text=text
        self.calls=[]
    def generate(self,prompt,model,work_id=None):
        self.calls.append((prompt,model,work_id))
        if not self.available:
            return {"status":"MODEL_UNAVAILABLE","work_id":work_id,"error":"URLError"}
        return {"status":"MODEL_OUTPUT_UNVERIFIED","work_id":work_id,
                "model":model,"text":self.text,"done":True}

class BridgeTests(unittest.TestCase):
    def test_success_creates_unverified_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            result=run("ping","qwen3:4b",d,"work-1",FakeGateway())
            self.assertEqual(result["status"],"RECORDED_UNVERIFIED")
            self.assertEqual(result["work_id"],"work-1")
            self.assertEqual(len(result["receipt_sha256"]),64)
            self.assertTrue((pathlib.Path(d)/"work-1.json").exists())
            self.assertEqual(result["response"],"pong")

    def test_identical_replay_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            fake=FakeGateway()
            self.assertEqual(run("ping","qwen3:4b",d,"work-2",fake)["status"],
                             "RECORDED_UNVERIFIED")
            self.assertEqual(run("ping","qwen3:4b",d,"work-2",fake)["status"],
                             "REPLAY")
            self.assertEqual(len(list(pathlib.Path(d).glob("*.json"))),1)

    def test_same_id_changed_result_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run("ping","qwen3:4b",d,"work-3",FakeGateway(text="A"))["status"],
                             "RECORDED_UNVERIFIED")
            self.assertEqual(run("ping","qwen3:4b",d,"work-3",FakeGateway(text="B"))["status"],
                             "CONFLICT")

    def test_unavailable_model_writes_no_success_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            result=run("ping","qwen3:4b",d,"work-4",FakeGateway(available=False))
            self.assertEqual(result["status"],"MODEL_UNAVAILABLE")
            self.assertEqual(list(pathlib.Path(d).glob("*.json")),[])

    def test_invalid_work_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fake=FakeGateway()
            with self.assertRaises(ValueError):
                run("ping","qwen3:4b",d,"../escape",fake)
            self.assertEqual(fake.calls,[])
            self.assertEqual(list(pathlib.Path(d).glob("*.json")),[])

    def test_nonstring_and_blank_work_id_rejected_without_model_call(self):
        with tempfile.TemporaryDirectory() as d:
            fake=FakeGateway()
            for bad in (True, 42, "", "space id", "a/b"):
                with self.subTest(work_id=bad):
                    with self.assertRaises(ValueError):
                        run("ping","qwen3:4b",d,bad,fake)
            self.assertEqual(fake.calls,[])
            self.assertEqual(list(pathlib.Path(d).glob("*.json")),[])

if __name__=="__main__":
    unittest.main(verbosity=2)
