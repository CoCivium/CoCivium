"""Actual loopback HTTP canary using a fake model and temporary receipt store.

Runs on ephemeral localhost port in CI; never calls Ollama, X2 or an outside
provider. Tests HTTP, response/WorkID boundaries and foreign Origin rejection.
"""
import http.client
import json
import pathlib
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rickbar_local_web_r0 import allowed_local_request, make_handler, respond

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipts=tempfile.TemporaryDirectory()
        cls.calls=[]
        def fake(prompt, model, receipt_dir, work_id):
            cls.calls.append((prompt, model, work_id))
            return {"status":"RECORDED_UNVERIFIED","work_id":work_id,
                    "receipt_sha256":"a"*64,"response":"synthetic model reply"}
        cls.old_respond=respond
        import rickbar_local_web_r0 as web
        cls.web=web
        def bounded_response(prompt,model,receipt_dir):
            return respond(prompt,model,receipt_dir,bridge=fake)
        web.respond=bounded_response
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),make_handler("fixture-model",cls.receipts.name))
        cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.web.respond=cls.old_respond
        cls.receipts.cleanup()

    def request(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection("127.0.0.1",self.server.server_address[1],timeout=3)
        hs={"Host":"127.0.0.1:%d"%self.server.server_address[1]}
        if headers:
            hs.update(headers)
        try:
            conn.request(method,path,body=body,headers=hs)
            res=conn.getresponse()
            return res.status,res.read().decode()
        finally:
            conn.close()

    def test_page_served_as_real_http(self):
        status,data=self.request("GET","/")
        self.assertEqual(status,200)
        self.assertIn("WorkID",data)
    def test_valid_chat_produces_work_id_not_ack(self):
        status,data=self.request("POST","/api/chat",json.dumps({"prompt":"hello"}),{"Content-Type":"application/json"})
        self.assertEqual(status,200)
        j=json.loads(data)
        self.assertEqual(j["status"],"RECORDED_UNVERIFIED")
        self.assertEqual(len(j["receipt_sha256"]),64)
        self.assertTrue(j["work_id"].startswith("rb-"))
        self.assertEqual(self.calls[-1][0],"hello")
    def test_empty_prompt_not_dispatched(self):
        before=len(self.calls)
        status,data=self.request("POST","/api/chat",json.dumps({"prompt":" "}))
        self.assertEqual(status,400)
        self.assertEqual(len(self.calls),before)
    def test_foreign_browser_origin_rejected(self):
        before=len(self.calls)
        status,_=self.request("POST","/api/chat",json.dumps({"prompt":"attack"}),
                              {"Origin":"https://attacker.example"})
        self.assertEqual(status,403)
        self.assertEqual(len(self.calls),before)
    def test_host_rebinding_rejected(self):
        before=len(self.calls)
        status,_=self.request("POST","/api/chat",json.dumps({"prompt":"attack"}),
                              {"Host":"attacker.example"})
        self.assertEqual(status,403)
        self.assertEqual(len(self.calls),before)
    def test_oversize_body_rejected(self):
        before=len(self.calls)
        status,_=self.request("POST","/api/chat","a"*16001)
        self.assertEqual(status,413)
        self.assertEqual(len(self.calls),before)
    def test_missing_route_rejected(self):
        status,_=self.request("POST","/send",json.dumps({"prompt":"no"}))
        self.assertEqual(status,404)
    def test_host_origin_local_restrictions(self):
        self.assertFalse(allowed_local_request("127.0.0.1:8765","http://evil.test"))
        self.assertTrue(allowed_local_request("127.0.0.1:8765","http://127.0.0.1:8765"))
        self.assertFalse(allowed_local_request("0.0.0.0:8765"))
if __name__=="__main__":
    unittest.main(verbosity=2)
