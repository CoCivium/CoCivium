"""CoModelFabric Ollama gateway R0. Standard library only; no X2 deployment."""
import json
import urllib.request
import urllib.error
import uuid

class OllamaGateway:
    def __init__(self, base_url="http://127.0.0.1:11434", timeout=8, opener=None):
        if not (base_url.startswith("http://127.0.0.1:") or base_url.startswith("http://localhost:")):
            raise ValueError("R0 permits loopback Ollama only")
        self.base_url=base_url.rstrip("/")
        self.timeout=timeout
        self.opener=opener or urllib.request.urlopen

    def _request(self, path, payload=None):
        data=None if payload is None else json.dumps(payload).encode("utf-8")
        req=urllib.request.Request(self.base_url+path,data=data,headers={"Content-Type":"application/json"},method="POST" if data is not None else "GET")
        with self.opener(req,timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def models(self):
        result=self._request("/api/tags")
        return [m["name"] for m in result.get("models",[]) if isinstance(m,dict) and isinstance(m.get("name"),str)]

    def generate(self, prompt, model, work_id=None):
        if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>12000:
            raise ValueError("prompt must be 1..12000 characters")
        if not isinstance(model,str) or not model.strip():
            raise ValueError("model required")
        wid=work_id or str(uuid.uuid4())
        try:
            reply=self._request("/api/generate",{"model":model,"prompt":prompt,"stream":False,"options":{"num_predict":512}})
            return {"work_id":wid,"model":model,"status":"MODEL_OUTPUT_UNVERIFIED","text":reply.get("response",""),"done":reply.get("done") is True}
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            return {"work_id":wid,"model":model,"status":"MODEL_UNAVAILABLE","error":type(exc).__name__}

if __name__=="__main__":
    import unittest
    from io import BytesIO
    class Response:
        def __init__(self,data): self.data=data
        def __enter__(self): return self
        def __exit__(self,*args): return False
        def read(self): return json.dumps(self.data).encode()
    class Tests(unittest.TestCase):
        def test_models(self):
            def fake(req,timeout): return Response({"models":[{"name":"qwen3:4b"}]})
            self.assertEqual(OllamaGateway(opener=fake).models(),["qwen3:4b"])
        def test_generation_is_not_effect_receipt(self):
            def fake(req,timeout):
                self.assertEqual(json.loads(req.data)["stream"],False)
                return Response({"response":"hello","done":True})
            result=OllamaGateway(opener=fake).generate("hello","qwen3:4b","work-1")
            self.assertEqual(result["status"],"MODEL_OUTPUT_UNVERIFIED")
            self.assertEqual(result["work_id"],"work-1")
        def test_failure_is_explicit(self):
            def fail(req,timeout): raise urllib.error.URLError("down")
            self.assertEqual(OllamaGateway(opener=fail).generate("hi","qwen3:4b")["status"],"MODEL_UNAVAILABLE")
        def test_nonlocal_rejected(self):
            with self.assertRaises(ValueError): OllamaGateway("http://example.com:11434")
        def test_blank_prompt_rejected(self):
            with self.assertRaises(ValueError): OllamaGateway().generate(" ","qwen3:4b")
    unittest.main(verbosity=2)
