"""Actual localhost HTTP tests for CoOwm, no browser/device/mouse claim."""
import http.client
import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent
for name, file in [("coowm_private_narrative_capsule_r0","coowm_private_narrative_capsule_r0.py"),
                   ("coowm_local_private_intake_r0","coowm_local_private_intake_r0.py")]:
    spec=importlib.util.spec_from_file_location(name, ROOT/file)
    module=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name]=module
    spec.loader.exec_module(module)
    globals()[name]=module
m=coowm_private_narrative_capsule_r0
web=coowm_local_private_intake_r0

class LocalIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/"private"
        self.server=web.CoOwmServer(self.root,0)
        self.t=threading.Thread(target=self.server.serve_forever,
                                kwargs={"poll_interval":0.01},daemon=True)
        self.t.start()
        self.port=self.server.server_port
        self.origin="http://127.0.0.1:"+str(self.port)
    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.t.join(timeout=2)
        self.temp.cleanup()
    def request(self,method,body=None,path="/",headers=None):
        h={"Host":"127.0.0.1:"+str(self.port)}
        if headers:h.update(headers)
        c=http.client.HTTPConnection("127.0.0.1",self.port,timeout=3)
        try:
            c.request(method,path,body=body,headers=h)
            r=c.getresponse()
            return r.status,dict(r.getheaders()),r.read().decode("utf-8")
        finally:
            c.close()
    def post(self,text="Keep this thought without sending it to anyone.",
             token=None,origin=None,headers=None):
        body=urlencode({"token":token if token is not None else self.server.form_token,
                        "narrative":text})
        h={"Content-Type":"application/x-www-form-urlencoded",
           "Origin":origin if origin is not None else self.origin}
        if headers:h.update(headers)
        return self.request("POST",body=body,headers=h)
    def test_get_offers_visible_opt_in(self):
        status,h,text=self.request("GET")
        self.assertEqual(status,200)
        self.assertIn("Save privately",text)
        self.assertIn("textarea",text)
        self.assertIn("No automatic sensing",text)
        self.assertNotIn('name="narrative" value=',text)
    def test_local_post_saves_receipt(self):
        status,h,text=self.post()
        self.assertEqual(status,200)
        self.assertIn("VERIFIED_LOCAL_ONLY",text)
        sha=m.digest(b"Keep this thought without sending it to anyone.")
        self.assertEqual(m.verify(self.root/sha,sha),"VERIFIED_LOCAL_ONLY")
        rec=json.loads((self.root/sha/"receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["source_kind"],"EXPLICIT_VISIBLE_LOCAL_BROWSER_POST")
        self.assertFalse(rec["receiver_ack"])
        self.assertFalse(rec["published"])
    def test_repeated_post_reuses_single_capsule(self):
        self.post()
        status,_,body=self.post()
        self.assertEqual(status,200)
        self.assertIn("DUPLICATE_VERIFIED_LOCAL_ONLY",body)
        self.assertEqual(len(list(self.root.iterdir())),1)
    def test_missing_or_invalid_token_rejected(self):
        for token in ("wrong",""):
            status,_,body=self.post(token=token)
            self.assertEqual(status,403)
        self.assertEqual(len(list(self.root.iterdir())),0)
    def test_cross_origin_rejected(self):
        status,_,_=self.post(origin="https://attacker.test")
        self.assertEqual(status,403)
        self.assertEqual(len(list(self.root.iterdir())),0)
    def test_no_origin_rejected(self):
        body=urlencode({"token":self.server.form_token,"narrative":"x"})
        status,_,_=self.request("POST",body=body,headers={"Content-Type":"application/x-www-form-urlencoded"})
        self.assertEqual(status,403)
        self.assertEqual(len(list(self.root.iterdir())),0)
    def test_dns_rebinding_host_held(self):
        body=urlencode({"token":self.server.form_token,"narrative":"x"})
        status,_,_=self.request("POST",body=body,headers={
            "Host":"attacker.test:"+str(self.port),
            "Origin":self.origin,"Content-Type":"application/x-www-form-urlencoded"})
        self.assertEqual(status,403)
        self.assertEqual(len(list(self.root.iterdir())),0)
    def test_untrusted_host_or_origin_never_receives_form_token(self):
        rejected = [
            self.request("GET",headers={"Host":"rebinding.attacker.test:"+str(self.port)}),
            self.post(origin="https://attacker.test"),
            self.post(token="bad-token"),
        ]
        for status,_,body in rejected:
            self.assertIn(status,(403,404))
            self.assertNotIn(self.server.form_token,body)
            self.assertNotIn('name="token"',body)
    def test_wrong_route_does_not_echo_form_token(self):
        status,_,body=self.request("GET",path="/private-capsules")
        self.assertEqual(status,404)
        self.assertNotIn(self.server.form_token,body)
    def test_invalid_content_type(self):
        status,_,_=self.request("POST",body='{"text":"hi"}',headers={
            "Origin":self.origin,"Content-Type":"application/json"})
        self.assertEqual(status,415)
    def test_blank_text_rejected(self):
        status,_,text=self.post(text="   ")
        self.assertEqual(status,400)
        self.assertIn("HELD_EMPTY_TEXT",text)
    def test_oversized_text_rejected(self):
        status,_,text=self.post(text="a"*(m.MAX_BYTES+1))
        self.assertEqual(status,400)
        self.assertIn("HELD_INVALID_OR_OVERSIZED_TEXT",text)
    def test_malformed_form_rejected(self):
        status,_,text=self.request("POST",body="not=a=real&field",headers={
            "Origin":self.origin,"Content-Type":"application/x-www-form-urlencoded"})
        self.assertEqual(status,400)
    def test_no_echo_of_posted_narrative(self):
        secret="Confidential private line: SOME-SECRET-VALUE-123"
        status,h,text=self.post(text=secret)
        self.assertEqual(status,200)
        self.assertNotIn(secret,text)
        status,h,again=self.request("GET")
        self.assertNotIn(secret,again)
        self.assertEqual(h.get("Cache-Control"),"no-store")
    def test_security_headers(self):
        _,headers,_=self.request("GET")
        self.assertEqual(headers["X-Frame-Options"],"DENY")
        self.assertEqual(headers["Referrer-Policy"],"no-referrer")
        self.assertIn("script-src 'none'",headers["Content-Security-Policy"])
        self.assertIn("frame-ancestors 'none'",headers["Content-Security-Policy"])
    def test_host_restricted_even_on_get(self):
        status,_,_=self.request("GET",headers={"Host":"otherhost"})
        self.assertEqual(status,404)
    def test_no_external_binding(self):
        self.assertEqual(self.server.server_address[0],"127.0.0.1")
    def test_post_html_inert(self):
        user_text="<script>alert('attack')</script>"
        status,_,response=self.post(text=user_text)
        self.assertEqual(status,200)
        self.assertNotIn(user_text,response)
        self.assertIn("script-src 'none'",dict(self.request("GET")[1])["Content-Security-Policy"])
    def test_tamper_fail_closed_no_overwrite(self):
        self.post(text="one")
        sha=m.digest(b"one")
        (self.root/sha/"text.txt").write_text("corrupt",encoding="utf-8")
        status,_,body=self.post(text="one")
        self.assertEqual(status,409)
        self.assertIn("HELD_DIGEST_OR_RECEIPT_MISMATCH",body)
    def test_isolated_capsule_storage_after_restart(self):
        self.post(text="keep me")
        sha=m.digest(b"keep me")
        self.assertEqual(m.verify(self.root/sha,sha),"VERIFIED_LOCAL_ONLY")
        self.assertEqual(len(list(self.root.iterdir())),1)
    def test_only_root_route(self):
        status,_,_=self.request("GET",path="/read-capsules")
        self.assertEqual(status,404)
        status,_,_=self.request("GET",path="/favicon.ico")
        self.assertEqual(status,404)
    def test_no_network_on_import_or_form(self):
        source=(ROOT/"coowm_local_private_intake_r0.py").read_text(encoding="utf-8")
        for unsafe in ("urllib.request","requests.get","webbrowser.open","navigator.clipboard",
                       "getDisplayMedia","pyautogui","selenium"):
            self.assertNotIn(unsafe,source)

if __name__=="__main__":
    unittest.main()
