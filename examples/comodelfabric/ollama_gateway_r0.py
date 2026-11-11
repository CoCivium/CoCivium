"""CoModelFabric Ollama gateway R0. Standard library only; no X2 deployment."""
import json
import urllib.request
import urllib.error
from urllib.parse import urlsplit
import math
import uuid


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Fail closed before urllib can forward a local prompt elsewhere."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "REDIRECT_DENIED", headers, fp)


def verified_loopback_base_url(value):
    """Accept only exact HTTP Ollama origins, never prefix-matching authorities."""
    if not isinstance(value, str):
        raise ValueError("R0 permits exact loopback Ollama origins only")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("R0 permits exact loopback Ollama origins only") from exc
    if (parsed.scheme != "http" or host not in {"127.0.0.1", "localhost"}
            or port is None or not 1 <= port <= 65535
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("R0 permits exact loopback Ollama origins only")
    return "http://" + host + ":" + str(port)


class OllamaGateway:
    def __init__(self, base_url="http://127.0.0.1:11434", timeout=8, opener=None):
        self.base_url = verified_loopback_base_url(base_url)
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("positive finite Ollama timeout required")
        self.timeout = timeout
        # No env proxies, no redirects, and no external network origin for model prompts.
        self.opener = opener or urllib.request.build_opener(
            urllib.request.ProxyHandler({}), _NoRedirect()).open

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
