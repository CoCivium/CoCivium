"""Local RickBar browser boundary regression tests; no Ollama calls."""
import http.client
import sys
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rickbar_local_web_r0 import allowed_local_request,make_handler

class PolicyTest(unittest.TestCase):
    def test_ordinary_loopback(self):
        self.assertTrue(allowed_local_request("127.0.0.1:8765","http://127.0.0.1:8765"))
        self.assertTrue(allowed_local_request("localhost:8765","http://localhost:8765"))
    def test_native_local_client_without_origin(self):
        self.assertTrue(allowed_local_request("127.0.0.1:8765"))
    def test_remote_host_refused(self):
        self.assertFalse(allowed_local_request("evil.example:8765","http://evil.example:8765"))
    def test_foreign_origin_refused(self):
        self.assertFalse(allowed_local_request("127.0.0.1:8765","https://evil.example"))
    def test_wrong_scheme_refused(self):
        self.assertFalse(allowed_local_request("127.0.0.1:8765","https://127.0.0.1:8765"))
    def test_wrong_port_refused(self):
        self.assertFalse(allowed_local_request("127.0.0.1:8765","http://127.0.0.1:8766"))
    def test_missing_host_refused(self):
        self.assertFalse(allowed_local_request(""))
    def test_invalid_host_userinfo_refused(self):
        self.assertFalse(allowed_local_request("evil@127.0.0.1:8765"))
    def test_null_origin_refused(self):
        self.assertFalse(allowed_local_request("127.0.0.1:8765","null"))
    def test_public_network_dns_rebinding_refused(self):
        self.assertFalse(allowed_local_request("attacker.invalid:8765"))
    def test_malformed_port_refused(self):
        self.assertFalse(allowed_local_request("127.0.0.1:bogus"))
    def test_ipv6_loopback(self):
        self.assertTrue(allowed_local_request("[::1]:8765","http://[::1]:8765"))

class RealHttpGuardTest(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(("127.0.0.1",0),make_handler("fixture-model","/tmp/fixture-receipts"))
        self.server.daemon_threads=True
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.worker.start()
        self.port=self.server.server_address[1]
    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=2)
    def request(self,method,path,host,origin=None,body=None):
        conn=http.client.HTTPConnection("127.0.0.1",self.port,timeout=2)
        headers={"Host":host}
        if origin is not None:
            headers["Origin"]=origin
        conn.request(method,path,body=body,headers=headers)
        res=conn.getresponse()
        status=res.status
        data=res.read().decode("utf-8")
        conn.close()
        return status,data
    def test_foreign_host_blocks_get(self):
        s,body=self.request("GET","/","evil.invalid")
        self.assertEqual(s,403)
        self.assertIn("LOCAL_ORIGIN_REQUIRED",body)
    def test_foreign_origin_blocks_post_before_model(self):
        s,body=self.request("POST","/api/chat",f"127.0.0.1:{self.port}","http://evil.invalid",b'{"prompt":"test"}')
        self.assertEqual(s,403)
        self.assertIn("LOCAL_ORIGIN_REQUIRED",body)
    def test_local_get_works(self):
        s,body=self.request("GET","/",f"127.0.0.1:{self.port}",f"http://127.0.0.1:{self.port}")
        self.assertEqual(s,200)
        self.assertIn("Local Ollama",body)

if __name__=="__main__":
    unittest.main()
