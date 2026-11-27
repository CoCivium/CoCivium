"""rickBar R2 tests against the real R1 core with a stand-in loopback Ollama (no network, no real model)."""
import json, socket, tempfile, threading, time, unittest, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import rickbar_local_web_r2 as r2
from rickbar_continuity_r1 import ContinuityStore

class FakeOllama(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    seen = []
    def log_message(self, *a): pass
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/api/show":
            d = json.dumps({"capabilities": ["completion", "thinking"] if b["model"] == "think:1" else ["completion"]}).encode()
            self.send_response(200); self.send_header("Content-Length", str(len(d))); self.end_headers(); self.wfile.write(d); return
        FakeOllama.seen.append(b); self.send_response(200); self.end_headers()
        p = b["prompt"]
        def put(o): self.wfile.write((json.dumps(o) + "\n").encode()); self.wfile.flush()
        if "EMPTY" in p:
            put({"thinking": "x" * 50}); put({"done": True, "done_reason": "length"}); return
        if "SLOW" in p:
            for _ in range(30): put({"thinking": "hmm "}); time.sleep(0.2)
            return
        time.sleep(0.6)
        for w in ["It ", "is ", "fine."]: put({"response": w}); time.sleep(0.2)
        put({"done": True, "done_reason": "stop"})

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

class R2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o = ThreadingHTTPServer(("127.0.0.1", 0), FakeOllama); threading.Thread(target=o.serve_forever, daemon=True).start()
        r2.OLLAMA = "http://127.0.0.1:%d" % o.server_address[1]
        cls.d = tempfile.mkdtemp(); cls.store = ContinuityStore(cls.d + "/s.sqlite")
        prov = lambda: [{"id": "ollama:" + m, "model": m, "label": m, "locality": "LOCAL_X2", "allowed": True} for m in ("think:1", "plain:1")] + \
                       [{"id": "ollama:x:cloud", "model": "x:cloud", "label": "x", "locality": "LEFT_X2", "allowed": False}]
        cls.port = free_port()
        srv = ThreadingHTTPServer(("127.0.0.1", cls.port), r2.make_handler(cls.store, cls.d, cls.port, provider_fn=prov))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    def req(self, m, p, b=None, host=None):
        h = {"Content-Type": "application/json"}
        if host: h["Host"] = host
        r = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, p), data=None if b is None else json.dumps(b).encode(), method=m, headers=h)
        try:
            with urllib.request.urlopen(r) as x: return x.status, json.loads(x.read())
        except urllib.error.HTTPError as e: return e.code, json.loads(e.read())
    def conv(self):
        cid = self.req("POST", "/api/conversation", {})[1]["conversation_id"]; return cid
    def turn(self, cid, tid, prompt, model, deep=False):
        e = self.req("GET", "/api/conversation/" + cid)[1]["epoch"]
        return self.req("POST", "/api/turn", {"conversation_id": cid, "turn_id": tid, "prompt": prompt, "epoch": e, "model": model, "deep": deep})
    def test_answer_switch_and_badge(self):
        cid = self.conv()
        c, r = self.turn(cid, "a", "hi", "think:1"); self.assertEqual((c, r["state"]), (200, "COMMITTED"))
        c, r = self.turn(cid, "b", "hi", "plain:1"); self.assertEqual(r["state"], "COMMITTED"); self.assertEqual(r["route_change"]["to"], "ollama:plain:1")
        self.assertEqual(r["answered_by"]["locality"], "LOCAL_X2")
    def test_fast_by_default_and_deep_on_request(self):
        cid = self.conv(); FakeOllama.seen.clear()
        self.turn(cid, "f", "hi", "think:1"); self.turn(cid, "g", "hi", "think:1", deep=True)
        self.assertEqual([b.get("think") for b in FakeOllama.seen], [False, True])
        self.assertTrue(all(b["keep_alive"] == r2.KEEP_ALIVE for b in FakeOllama.seen))
        self.assertTrue(FakeOllama.seen[0]["prompt"].startswith("[rickBar note, not from the user]"))
    def test_no_think_flag_for_models_without_it(self):
        cid = self.conv(); FakeOllama.seen.clear(); self.turn(cid, "p", "hi", "plain:1")
        self.assertNotIn("think", FakeOllama.seen[0])
    def test_empty_answer_fails_with_reason(self):
        cid = self.conv(); c, r = self.turn(cid, "e", "EMPTY", "think:1")
        self.assertEqual(c, 503); self.assertIn("hidden reasoning", r["why"])
    def test_time_limit(self):
        old = r2.WALL_SEC; r2.WALL_SEC = 1
        try:
            cid = self.conv(); c, r = self.turn(cid, "s", "SLOW", "think:1", deep=True)
            self.assertEqual(c, 503); self.assertIn("Stopped after", r["why"])
        finally: r2.WALL_SEC = old
    def test_live_progress(self):
        cid = self.conv(); out = {}
        t = threading.Thread(target=lambda: out.update(r=self.turn(cid, "l", "hi", "plain:1"))); t.start()
        time.sleep(0.4); g = self.req("GET", "/api/progress/%s/l" % cid)[1]
        self.assertIn(g["phase"], ("loading", "waiting")); t.join()
        g = self.req("GET", "/api/progress/%s/l" % cid)[1]; self.assertEqual((g["phase"], g["partial"]), ("done", "It is fine."))
    def test_cloud_refused_and_stale_fenced(self):
        cid = self.conv(); self.assertEqual(self.turn(cid, "c", "hi", "x:cloud")[0], 403)
        self.turn(cid, "z1", "hi", "plain:1")  # switch bumps the epoch
        c, r = self.req("POST", "/api/turn", {"conversation_id": cid, "turn_id": "z2", "prompt": "hi", "epoch": 1, "model": "think:1"})
        self.assertEqual((c, r["state"]), (409, "FENCED"))
    def test_orphan_pending_reconciled(self):
        st = ContinuityStore(tempfile.mkdtemp() + "/o.sqlite"); c = st.create(worker="ollama:think:1")
        st.begin_turn(c["conversation_id"], "o", "hi", 1, trigger_kind="LOCAL_HTTP_REQUEST")
        self.assertEqual(r2.reconcile_orphans(st), 1)
        self.assertEqual(st.state(c["conversation_id"])["turns"][0]["status"], "INDETERMINATE")
    def test_foreign_host_refused(self):
        self.assertEqual(self.req("GET", "/api/providers", host="evil.example:%d" % self.port)[0], 403)

if __name__ == "__main__":
    unittest.main(verbosity=2)
