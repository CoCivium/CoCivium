"""Actual localhost R1 HTTP tests with a fake model. Never calls hosted services or X2."""
import http.client
import json
import pathlib
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from rickbar_continuity_r1 import ContinuityStore
from rickbar_local_web_r1 import make_handler

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.store=ContinuityStore(str(pathlib.Path(cls.temp.name)/"local.sqlite"))
        cls.calls=[]
        def fake(context,model,receipt_dir,work_id):
            cls.calls.append((context,model,work_id))
            return {"status":"RECORDED_UNVERIFIED","response":"Synthetic local answer",
                    "receipt_sha256":"a"*64,"work_id":work_id}
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),
            make_handler(cls.store,"fixture-local-model",cls.temp.name,bridge=fake))
        cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=4)
        cls.store.close()
        cls.temp.cleanup()

    def request(self,method,path,payload=None,headers=None):
        conn=http.client.HTTPConnection("127.0.0.1",self.server.server_address[1],timeout=5)
        hs={"Host":"127.0.0.1:%d"%self.server.server_address[1]}
        if headers: hs.update(headers)
        if payload is not None:
            payload=json.dumps(payload)
            hs.setdefault("Content-Type","application/json")
        try:
            conn.request(method,path,body=payload,headers=hs)
            resp=conn.getresponse()
            content=resp.read().decode("utf-8")
            if "application/json" in resp.getheader("Content-Type",""):
                content=json.loads(content)
            return resp.status,content
        finally:
            conn.close()

    def create(self):
        status,response=self.request("POST","/api/conversation",{})
        self.assertEqual(status,200)
        self.assertEqual(response["state"],"CREATED")
        return response["conversation_id"]

    def test_serves_accessible_rickbar(self):
        status,html=self.request("GET","/")
        self.assertEqual(status,200)
        self.assertIn('role="log"',html)
        self.assertIn("Local Continuity R1",html)
        self.assertIn("No cloud synchronisation",html)

    def test_create_turn_replay_and_readback(self):
        cid=self.create()
        payload={"conversation_id":cid,"turn_id":"t-one","prompt":"Hello","epoch":1}
        status,answer=self.request("POST","/api/turn",payload)
        self.assertEqual(status,200)
        self.assertEqual(answer["state"],"COMMITTED")
        self.assertEqual(answer["evidence_class"],"MODEL_OUTPUT_UNVERIFIED")
        self.assertEqual(len(answer["receipt_sha256"]),64)
        old_calls=len(self.calls)
        status,answer=self.request("POST","/api/turn",payload)
        self.assertEqual(status,200)
        self.assertEqual(answer["state"],"REPLAY")
        self.assertEqual(len(self.calls),old_calls)
        status,state=self.request("GET","/api/conversation/"+cid)
        self.assertEqual(status,200)
        self.assertEqual(state["turns"][0]["response"],"Synthetic local answer")
        self.assertFalse(state["receiver_ack"])

    def test_conversation_worker_matches_actual_configured_http_route(self):
        cid=self.create()
        state=self.store.state(cid)
        self.assertEqual(state["worker"],"ollama:fixture-local-model")
        self.assertEqual(state["epoch"],1)

    def test_restarted_server_cannot_implicitly_switch_model_route(self):
        # Simulate an older conversation created for another local model.
        cid="route-mismatch-existing"
        self.assertEqual(self.store.create(
            worker="ollama:qwen3:4b",conversation_id=cid)["state"],"CREATED")
        before=len(self.calls)
        status,answer=self.request("POST","/api/turn",{
            "conversation_id":cid,"turn_id":"must-not-run","prompt":"Hello","epoch":1})
        self.assertEqual(status,409)
        self.assertEqual(answer["state"],"MODEL_ROUTE_MISMATCH")
        self.assertEqual(len(self.calls),before)
        self.assertEqual(self.store.state(cid)["turns"],[])

    def test_explicit_epoch_election_allows_new_local_model_route(self):
        from rickbar_local_web_r1 import act
        cid=self.create()
        called=[]
        def fake(context,model,receipt_dir,work_id):
            called.append((model,work_id))
            return {"status":"RECORDED_UNVERIFIED","work_id":work_id,
                    "response":"synthetic successor","receipt_sha256":"b"*64}
        old={"conversation_id":cid,"turn_id":"before-election",
             "prompt":"Hello","epoch":1}
        result=act(self.store,old,"other-model",self.temp.name,bridge=fake)
        self.assertEqual(result["state"],"MODEL_ROUTE_MISMATCH")
        self.assertEqual(called,[])
        change=self.store.elect(cid,"ollama:other-model",1)
        self.assertEqual(change["epoch"],2)
        after={**old,"epoch":2}
        result=act(self.store,after,"other-model",self.temp.name,bridge=fake)
        self.assertEqual(result["state"],"COMMITTED")
        self.assertEqual(called[0][0],"other-model")
        self.assertEqual(self.store.state(cid)["worker"],"ollama:other-model")
        self.assertEqual(self.store.state(cid)["turns"][0]["status"],"COMMITTED")

    def test_http_provenance_is_observed_not_authenticated(self):
        cid=self.create()
        payload={"conversation_id":cid,"turn_id":"provenance","prompt":"Hello",
                 "epoch":1,"trigger_kind":"SCHEDULED"}
        status,answer=self.request("POST","/api/turn",payload)
        self.assertEqual(status,200)
        self.assertEqual(answer["trigger_kind"],"LOCAL_HTTP_REQUEST")
        self.assertEqual(answer["trigger_evidence"],
                         "LOOPBACK_REQUEST_OBSERVED_USER_UNAUTHENTICATED")
        code,state=self.request("GET","/api/conversation/"+cid)
        self.assertEqual(code,200)
        self.assertEqual(state["turns"][0]["trigger_kind"],"LOCAL_HTTP_REQUEST")

    def test_same_turn_id_different_conversations_have_distinct_receipts(self):
        a,b=self.create(),self.create()
        self.assertNotEqual(a,b)
        for cid in (a,b):
            status,answer=self.request("POST","/api/turn",{
                "conversation_id":cid,"turn_id":"identical","prompt":"Same",
                "epoch":1})
            self.assertEqual(status,200)
            self.assertEqual(answer["state"],"COMMITTED")
        self.assertNotEqual(self.calls[-1][2],self.calls[-2][2])
        self.assertTrue(self.calls[-1][2].startswith("rb-"))
        self.assertEqual(len(self.calls[-1][2]),67)

    def test_receipt_replay_and_wrong_identity_not_committed(self):
        cid=self.create()
        payload={"conversation_id":cid,"turn_id":"foreign","prompt":"safe",
                 "epoch":1}
        import rickbar_local_web_r1 as surface
        for wrong in (
            {"status":"REPLAY","work_id":"irrelevant",
             "response":"untrusted","receipt_sha256":"a"*64},
            {"status":"RECORDED_UNVERIFIED","work_id":"other",
             "response":"untrusted","receipt_sha256":"a"*64},
            {"status":"RECORDED_UNVERIFIED","work_id":"rb-not-current",
             "response":"untrusted","receipt_sha256":"a"*64},
        ):
            new_id=payload["turn_id"]+"-"+wrong["status"]+"-"+wrong["work_id"]
            payload["turn_id"]=new_id[:90].replace(" ","")
            def fake(context,model,receipt_dir,work_id):
                return wrong
            result=surface.act(self.store,payload,"fixture-local-model",
                               self.temp.name,bridge=fake)
            self.assertEqual(result["state"],"MODEL_RECEIPT_UNVERIFIED")
            state=self.store.state(cid)
            self.assertNotIn("COMMITTED",
                             [t["status"] for t in state["turns"]])
            self.assertEqual(state["turns"][-1]["status"],"INDETERMINATE")

    def test_scoped_receipt_id_is_deterministic(self):
        from rickbar_local_web_r1 import scoped_receipt_work_id
        x=scoped_receipt_work_id("conversation-a","same-turn")
        self.assertEqual(x,scoped_receipt_work_id("conversation-a","same-turn"))
        self.assertNotEqual(x,scoped_receipt_work_id("conversation-b","same-turn"))
        self.assertNotEqual(x,scoped_receipt_work_id("conversation-a","different"))

    def test_exact_read_only_turn_status_does_not_reinvoke_worker(self):
        cid=self.create()
        original={"conversation_id":cid,"turn_id":"lost-response",
                  "prompt":"Persist me","epoch":1}
        status,_=self.request("POST","/api/turn",original)
        self.assertEqual(status,200)
        before=len(self.calls)
        status,readback=self.request("GET","/api/turn/"+cid+"/lost-response")
        self.assertEqual(status,200)
        self.assertEqual(readback["state"],"TURN_LOCAL_READBACK")
        self.assertEqual(readback["turn"]["status"],"COMMITTED")
        self.assertEqual(readback["turn"]["response"],"Synthetic local answer")
        self.assertFalse(readback["independent_receiver_ack"])
        self.assertFalse(readback["model_resubmitted"])
        self.assertEqual(len(self.calls),before)

    def test_exact_turn_pending_indeterminate_missing_and_invalid(self):
        cid=self.create()
        self.store.begin_turn(cid,"pending","No model invoked",1)
        before=len(self.calls)
        code,value=self.request("GET","/api/turn/"+cid+"/pending")
        self.assertEqual(code,200)
        self.assertEqual(value["turn"]["status"],"PENDING")
        self.assertEqual(self.store.elect(cid,"ollama:replacement",1)["epoch"],2)
        code,value=self.request("GET","/api/turn/"+cid+"/pending")
        self.assertEqual(code,200)
        self.assertEqual(value["turn"]["status"],"INDETERMINATE")
        self.assertEqual(self.request("GET","/api/turn/"+cid+"/never-created")[0],404)
        self.assertEqual(self.request("GET","/api/turn/"+cid+"/%2e%2e")[0],400)
        self.assertEqual(self.request("GET","/api/turn/bad")[0],404)
        self.assertEqual(len(self.calls),before)

    def test_new_turn_uses_prior_context(self):
        cid=self.create()
        base={"conversation_id":cid,"epoch":1}
        self.request("POST","/api/turn",{**base,"turn_id":"first","prompt":"One"})
        self.request("POST","/api/turn",{**base,"turn_id":"second","prompt":"Two"})
        self.assertIn("Synthetic local answer",self.calls[-1][0])
        self.assertIn("USER: Two",self.calls[-1][0])

    def test_no_foreign_origin_or_host(self):
        old=len(self.calls)
        code,_=self.request("POST","/api/conversation",{},{"Origin":"https://evil.test"})
        self.assertEqual(code,403)
        code,_=self.request("POST","/api/conversation",{},{"Host":"evil.test"})
        self.assertEqual(code,403)
        self.assertEqual(len(self.calls),old)

    def test_fenced_stale_epoch_and_no_automatic_retry(self):
        cid=self.create()
        self.assertEqual(self.store.elect(cid,"ollama:next",1)["epoch"],2)
        before=len(self.calls)
        code,result=self.request("POST","/api/turn",{
            "conversation_id":cid,"turn_id":"stale","prompt":"No","epoch":1})
        self.assertEqual(code,409)
        self.assertEqual(result["state"],"FENCED")
        self.assertEqual(len(self.calls),before)

    def test_conflicting_turn_id_and_recovery(self):
        cid=self.create()
        original={"conversation_id":cid,"turn_id":"same","prompt":"One","epoch":1}
        self.request("POST","/api/turn",original)
        before=len(self.calls)
        code,answer=self.request("POST","/api/turn",{**original,"prompt":"Two"})
        self.assertEqual(code,409)
        self.assertEqual(answer["state"],"CONFLICT")
        self.assertEqual(len(self.calls),before)

    def test_invalid_request_cannot_call_model(self):
        before=len(self.calls)
        self.assertEqual(self.request("POST","/api/turn",{"prompt":"hi"})[0],400)
        self.assertEqual(self.request("POST","/api/conversation",{"secret":"no"})[0],400)
        self.assertEqual(self.request("POST","/api/turn",{"conversation_id":"../bad","turn_id":"x","prompt":"hello","epoch":1})[0],400)
        self.assertEqual(len(self.calls),before)

    def test_restart_readback_is_not_external_ack(self):
        cid=self.create()
        self.request("POST","/api/turn",{"conversation_id":cid,"turn_id":"persist","prompt":"Persist","epoch":1})
        separate=ContinuityStore(str(pathlib.Path(self.temp.name)/"local.sqlite"))
        try:
            record=separate.state(cid)
            self.assertEqual(record["turns"][0]["status"],"COMMITTED")
            self.assertFalse(record["receiver_ack"])
            self.assertFalse(record["provider_session_deleted"])
        finally:
            separate.close()

if __name__=="__main__":
    unittest.main(verbosity=2)
