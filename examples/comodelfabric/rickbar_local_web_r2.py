"""rickBar R2: layered front door on top of R1 (W09, 2026-11-27).

Simple by default, honest always, depth on demand:
  L0 chat, L1 always-on "answered by" + stayed-on-X2 badge, L2 opt-in federation details.
Reuses R1's continuity store, fenced turns and receipts unchanged. Separate port and store,
so R1 keeps running untouched. Local Ollama only; models whose name marks them as cloud are refused.
"""
import datetime, json, pathlib, sys, threading, time, urllib.request, uuid
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rickbar_local_web_r1 as r1
from rickbar_continuity_r1 import ContinuityStore
from rickbar_ollama_bridge_r0 import run as bridge_run
from ollama_gateway_r0 import OllamaGateway

OLLAMA = "http://127.0.0.1:11434"
_meta_lock = threading.Lock()


def is_cloud(name):
    n = name.lower()
    return n.endswith(":cloud") or "-cloud" in n or n.endswith("cloud")


def providers(fetch=None):
    """Registry built from installed Ollama models. Every entry says where the text goes."""
    try:
        if fetch is None:
            with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
        else:
            data = fetch()
        names = [m["name"] for m in data.get("models", []) if isinstance(m, dict) and isinstance(m.get("name"), str)]
    except Exception:
        names = []
    out = []
    for n in sorted(names):
        if n.startswith(("qwen3-embedding", "nomic-embed", "mxbai-embed")):
            continue
        out.append({"id": "ollama:" + n, "model": n, "label": n,
                    "locality": "LEFT_X2" if is_cloud(n) else "LOCAL_X2",
                    "allowed": not is_cloud(n)})
    return out


def pick_default(provs, preferred=("qwen3.5:9b", "qwen3:14b", "qwen3:4b")):
    allowed = [p["model"] for p in provs if p["allowed"]]
    for p in preferred:
        if p in allowed:
            return p
    return allowed[0] if allowed else None


NUM_PREDICT = 4096          # R1 uses 512; thinking models can spend that on reasoning alone
KEEP_ALIVE = "30m"          # keep the model loaded between questions so the next answer starts fast
WALL_SEC = 180              # a turn that runs longer than this is stopped and reported, never left hanging
_why = {}                   # work_id -> plain reason when a turn produced no answer
DEEP = {}                   # work_id -> True when the person ticked "Think harder"
_caps = {}                  # model -> True if Ollama says it can switch thinking off/on
PROGRESS = {}               # work_id -> live progress for the page (phase, seconds, words so far)


def supports_thinking(model):
    if model not in _caps:
        try:
            req = urllib.request.Request(OLLAMA + "/api/show", data=json.dumps({"model": model}).encode("utf-8"),
                                         headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                _caps[model] = "thinking" in (json.loads(r.read().decode("utf-8")).get("capabilities") or [])
        except Exception:
            return False
    return _caps[model]


class R2Gateway(OllamaGateway):
    """Same loopback-only gateway, streamed internally so the page can show progress.
    Room to finish, a hard time limit, and an empty answer is never an answer."""

    def generate(self, prompt, model, work_id=None):
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 12000:
            raise ValueError("prompt must be 1..12000 characters")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model required")
        wid = work_id or str(uuid.uuid4())
        t0 = time.monotonic()
        while len(PROGRESS) > 200:
            PROGRESS.pop(next(iter(PROGRESS)))
        prog = PROGRESS[wid] = {"phase": "loading", "seconds": 0, "thinking_words": 0, "answer_words": 0, "model": model,
                               "partial": "", "t0": t0}
        text, thinking, last = [], [], {}
        try:
            req_body = {"model": model, "prompt": prompt, "stream": True, "keep_alive": KEEP_ALIVE,
                        "options": {"num_predict": NUM_PREDICT}}
            deep = DEEP.pop(wid, False)
            if supports_thinking(model):
                req_body["think"] = bool(deep)   # fast by default; "Think harder" turns reasoning on
            prog["deep"] = bool(deep)
            body = json.dumps(req_body).encode("utf-8")
            req = urllib.request.Request(self.base_url + "/api/generate", data=body,
                                         headers={"Content-Type": "application/json"}, method="POST")
            with self.opener(req, timeout=self.timeout) as resp:
                for line in resp:
                    if not line.strip():
                        continue
                    chunk = json.loads(line.decode("utf-8"))
                    if chunk.get("thinking"):
                        thinking.append(chunk["thinking"]); prog["phase"] = "thinking"
                    if chunk.get("response"):
                        text.append(chunk["response"]); prog["phase"] = "answering"
                    prog["seconds"] = int(time.monotonic() - t0)
                    prog["thinking_words"] = len("".join(thinking).split())
                    prog["answer_words"] = len("".join(text).split())
                    prog["partial"] = "".join(text)[-6000:]
                    prog["thinking_tail"] = "".join(thinking)[-240:]
                    if chunk.get("done"):
                        last = chunk
                        break
                    if time.monotonic() - t0 > WALL_SEC:
                        _why[wid] = ("Stopped after %d s (limit %d s) while %s; try again, ask more simply, or pick a smaller model"
                                     % (prog["seconds"], WALL_SEC, prog["phase"]))
                        return {"work_id": wid, "model": model, "status": "MODEL_TIMEOUT", "phase": prog["phase"]}
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            _why[wid] = "Ollama did not answer (" + type(exc).__name__ + ")"
            return {"work_id": wid, "model": model, "status": "MODEL_UNAVAILABLE", "error": type(exc).__name__}
        finally:
            prog["phase"] = "done"
        answer = "".join(text)
        info = {"done_reason": last.get("done_reason"), "eval_count": last.get("eval_count"),
                "thinking_chars": len("".join(thinking)), "seconds": round(time.monotonic() - t0, 1)}
        if not answer.strip():
            _why[wid] = ("The model used its whole budget on hidden reasoning and gave no answer; try again or pick another model"
                         if info["thinking_chars"] else "The model returned an empty answer")
            return {"work_id": wid, "model": model, "status": "MODEL_EMPTY_ANSWER", **info}
        return {"work_id": wid, "model": model, "status": "MODEL_OUTPUT_UNVERIFIED", "text": answer,
                "done": last.get("done") is True, **info}


def preamble(model):
    now = datetime.datetime.now().astimezone()
    return ("[rickBar note, not from the user] You are " + model + ", running locally on X2 (Rick's own PC) "
            "through Ollama. Nothing you read or write leaves this computer. X2's clock says it is "
            + now.strftime("%A %Y-%m-%d %H:%M %Z") + ". Answer directly and briefly unless asked for detail.\n")


def long_bridge(context, model, receipt_dir, work_id=None):
    # R1's gateway: 8 s timeout and 512 tokens. R2: 300 s per read, 180 s per turn, 4096 tokens, empty = failure.
    pre = preamble(model)
    prompt = pre + context[-(12000 - len(pre)):]
    return bridge_run(prompt, model, receipt_dir, work_id=work_id,
                      gateway=R2Gateway(base_url=OLLAMA, timeout=300))


def meta_path(receipt_dir):
    return pathlib.Path(receipt_dir) / "r2_turn_meta.jsonl"


def record_meta(receipt_dir, row):
    p = meta_path(receipt_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with _meta_lock, p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_meta(receipt_dir, conversation_id):
    p = meta_path(receipt_dir)
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("conversation_id") == conversation_id:
                out[row.get("turn_id")] = row
    return out


def loopback_ok(handler, port):
    if handler.client_address[0] not in ("127.0.0.1", "::1"):
        return False
    host = (handler.headers.get("Host") or "").lower()
    if host not in ("127.0.0.1:%d" % port, "localhost:%d" % port):
        return False
    origin = handler.headers.get("Origin")
    if origin and origin.lower() not in ("http://127.0.0.1:%d" % port, "http://localhost:%d" % port):
        return False
    return True


def make_handler(store, receipt_dir, port, provider_fn=providers, bridge=long_bridge, act=None):
    act = act or r1.act
    default_model = pick_default(provider_fn()) or "qwen3:4b"
    Base = r1.make_handler(store, default_model, receipt_dir, bridge)

    class Handler(Base):
        def _send(self, code, data, ctype="application/json; charset=utf-8"):
            body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path.startswith("/api/progress/"):
                if not loopback_ok(self, port):
                    return self._send(403, {"error": "LOOPBACK_ONLY"})
                parts = path[len("/api/progress/"):].split("/")
                try:
                    wid = r1.scoped_receipt_work_id(parts[0], parts[1])
                except (IndexError, ValueError):
                    return self._send(400, {"error": "BAD_ID"})
                g = PROGRESS.get(wid)
                if not g:
                    return self._send(200, {"phase": "waiting"})
                out = {k: v for k, v in g.items() if k != "t0"}
                if g["phase"] != "done":
                    out["seconds"] = int(time.monotonic() - g["t0"])
                return self._send(200, out)
            if path in ("/", "/api/providers") or path.startswith("/api/r2meta/"):
                if not loopback_ok(self, port):
                    return self._send(403, {"error": "LOOPBACK_ONLY"})
                if path == "/":
                    return self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
                if path == "/api/providers":
                    provs = provider_fn()
                    return self._send(200, {"providers": provs, "default": pick_default(provs)})
                cid = path[len("/api/r2meta/"):]
                return self._send(200, {"meta": read_meta(receipt_dir, cid)})
            return super().do_GET()

        def do_POST(self):
            path = urlsplit(self.path).path
            if path != "/api/turn":
                return super().do_POST()
            if not loopback_ok(self, port):
                return self._send(403, {"error": "LOOPBACK_ONLY"})
            try:
                n = int(self.headers.get("Content-Length") or 0)
                if n <= 0 or n > 64000:
                    return self._send(400, {"error": "BAD_LENGTH"})
                payload = json.loads(self.rfile.read(n).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return self._send(400, {"error": "BAD_JSON"})
            if not isinstance(payload, dict):
                return self._send(400, {"error": "BAD_JSON"})
            wanted = payload.pop("model", None)
            deep = payload.pop("deep", False) is True
            provs = {p["model"]: p for p in provider_fn()}
            model = wanted or default_model
            prov = provs.get(model)
            if not prov:
                return self._send(400, {"state": "UNKNOWN_MODEL", "model": model})
            if not prov["allowed"]:
                return self._send(403, {"state": "CLOUD_MODEL_REFUSED", "model": model,
                                        "why": "R2 keeps text on X2; cloud routes need an explicit owner gate"})
            # R1 binds each conversation to one model worker and refuses silent switches
            # (MODEL_ROUTE_MISMATCH). Picking a model in R2 is an explicit choice, so R2
            # elects that model as successor via R1's own fenced elect() before the turn.
            route_change = None
            cid0, ep0 = payload.get("conversation_id"), payload.get("epoch")
            if isinstance(cid0, str) and type(ep0) is int:
                try:
                    cur = store.state(cid0, limit=1)
                except ValueError:
                    cur = {}
                want = "ollama:" + model
                if cur.get("worker") and cur["worker"] != want and cur.get("epoch") == ep0:
                    el = store.elect(cid0, want, ep0)
                    if el.get("state") != "SUCCESSOR_ELECTED_SOURCE_ONLY":
                        return self._send(409, {"state": el.get("state", "FENCED"), "conversation_id": cid0})
                    route_change = {"from": cur["worker"], "to": want, "epoch": el["epoch"]}
                    payload["epoch"] = el["epoch"]
            try:
                DEEP[r1.scoped_receipt_work_id(payload.get("conversation_id"), payload.get("turn_id"))] = deep
            except (ValueError, TypeError):
                pass
            result = act(store, payload, model, receipt_dir, bridge)
            if route_change:
                result["route_change"] = route_change
            state = result.get("state")
            cid, tid = payload.get("conversation_id"), payload.get("turn_id")
            if state in ("COMMITTED", "REPLAY") and isinstance(cid, str) and isinstance(tid, str):
                record_meta(receipt_dir, {"conversation_id": cid, "turn_id": tid, "provider": prov["id"],
                                          "model": model, "locality": prov["locality"],
                                          "work_id": r1.scoped_receipt_work_id(cid, tid),
                                          "receipt_sha256": result.get("model_output_receipt"),
                                          "route_change": route_change})
            result["answered_by"] = {"model": model, "locality": prov["locality"]}
            if state not in ("COMMITTED", "REPLAY") and isinstance(cid, str) and isinstance(tid, str):
                why = _why.pop(r1.scoped_receipt_work_id(cid, tid), None)
                if why:
                    result["why"] = why
            code = 200 if state in ("COMMITTED", "REPLAY") else (409 if state in ("STALE_EPOCH", "CONFLICT", "BUSY", "FENCED", "ALREADY_PENDING") else 503)
            return self._send(code, result)

    return Handler


HTML = r'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><title>rickBar</title>
<style>
:root{font:16px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:#101221;color:#eef2ff}
main{max-width:860px;margin:auto;padding:22px 16px}
h1{margin:.3em 0;color:#e4beff;font-size:26px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.status{background:#23294a;border:1px solid #8893c6;border-radius:12px;padding:8px 12px;font-size:14px}
#log{min-height:210px;height:56vh;overflow:auto;background:#171a30;border:1px solid #7381a7;border-radius:14px;padding:12px;margin:12px 0}
.entry{padding:11px;border-bottom:1px solid #3b3e5a;white-space:pre-wrap;overflow-wrap:anywhere}
.you{color:#c1e8ff}.badge{display:inline-block;margin-top:6px;font-size:12px;padding:2px 8px;border-radius:999px;background:#1e3a2f;color:#9ff0c8;border:1px solid #3f8a6a}
.badge.left{background:#3a2a1e;color:#ffd39a;border-color:#a8773f}.badge.none{background:#2a2a35;color:#c4cde0;border-color:#555}
.live{opacity:.85;white-space:pre-wrap}.l2{display:none;font:12px/1.4 Consolas,monospace;color:#aab6d3;margin-top:6px}body.showl2 .l2{display:block}
form{display:flex;gap:8px;margin-top:12px}
input,select{padding:12px;background:#222840;color:white;border:1px solid #92a4c9;border-radius:9px}
input{flex:1;min-width:40px}
button{cursor:pointer;background:#aee8d5;color:#0d2020;border:none;border-radius:9px;padding:12px;font-weight:700}
button:disabled{opacity:.5;cursor:wait}
button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #ffdd86;outline-offset:2px}
small,label{color:#c4cde0;font-size:13px}
</style></head><body><main>
<h1>rickBar</h1>
<div class="bar"><label>Model <select id="model" aria-label="Model"></select></label>
<label><input type="checkbox" id="deep"> Think harder (slower)</label>
<label><input type="checkbox" id="l2"> Show how it works</label>
<button id="new" type="button">New conversation</button></div>
<div id="state" class="status" role="status" aria-live="polite">Opening…</div>
<div id="log" role="log" aria-live="polite" aria-label="Conversation"></div>
<form id="chat"><input id="prompt" aria-label="Message" placeholder="Ask anything" required maxlength="12000" autocomplete="off">
<button id="send" type="submit" disabled>Send</button></form>
<p><small>Every answer shows which model wrote it and whether your words stayed on this computer. This page runs on X2 only.</small></p>
</main><script>
"use strict";
const $=id=>document.getElementById(id);
let cid=null,epoch=null,busy=false,meta={};
const key="rickbar-r2-conversation",l2key="rickbar-r2-show-l2",mkey="rickbar-r2-model";
function msg(t){$("state").textContent=t}
function safeGet(k){try{return localStorage.getItem(k)}catch(e){return null}}
function safeSet(k,v){try{localStorage.setItem(k,v)}catch(e){}}
async function api(path,payload){
  const opts=payload===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)};
  const r=await fetch(path,opts);const d=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(d.why||d.state||d.error||("HTTP "+r.status));return d;
}
function badge(m){
  const b=document.createElement("span");
  if(!m){b.className="badge none";b.textContent="answered by: not recorded (earlier turn)";return b}
  const local=m.locality==="LOCAL_X2";
  b.className="badge"+(local?"":" left");
  b.textContent="answered by "+m.model+" · "+(local?"stayed on X2":"left X2");return b;
}
function render(s){
  cid=s.conversation_id;epoch=s.epoch;$("log").replaceChildren();
  (s.turns||[]).forEach(t=>{
    const e=document.createElement("div");e.className="entry";
    const you=document.createElement("div");you.className="you";you.textContent="You: "+t.prompt;e.append(you);
    const a=document.createElement("div");
    a.textContent=t.status==="COMMITTED"?(t.response||""):"Not answered ("+t.status+"). Nothing was resent.";e.append(a);
    if(t.status==="COMMITTED")e.append(badge(meta[t.turn_id]));
    const d=document.createElement("div");d.className="l2";const m=meta[t.turn_id]||{};
    d.textContent="turn "+t.turn_id+" · status "+t.status+" · source "+(t.trigger_kind||"?")+" ["+(t.trigger_evidence||"NONE")+"]"+
      (m.work_id?"\nWorkID "+m.work_id:"")+(m.receipt_sha256?" · receipt sha256 "+m.receipt_sha256:"")+(m.provider?" · route "+m.provider:"");
    e.append(d);$("log").append(e);
  });
  $("log").scrollTop=$("log").scrollHeight;
  msg("Ready · conversation "+cid+" · stored on X2");$("send").disabled=busy;
}
async function refresh(){meta=(await api("/api/r2meta/"+encodeURIComponent(cid))).meta||{};render(await api("/api/conversation/"+encodeURIComponent(cid)))}
async function loadModels(){
  const p=await api("/api/providers");const sel=$("model");sel.replaceChildren();
  p.providers.forEach(x=>{const o=document.createElement("option");o.value=x.model;o.disabled=!x.allowed;
    o.textContent=x.label+(x.allowed?" (on X2)":" (cloud, blocked)");sel.append(o)});
  const saved=safeGet(mkey);sel.value=(saved&&p.providers.some(x=>x.model===saved&&x.allowed))?saved:(p.default||"");
}
async function load(){
  busy=true;$("send").disabled=true;
  try{
    await loadModels();
    let id=safeGet(key),s=null;
    if(id){const r=await fetch("/api/conversation/"+encodeURIComponent(id));if(r.status===200)s=await r.json()}
    if(!s){const c=await api("/api/conversation",{});s=await api("/api/conversation/"+encodeURIComponent(c.conversation_id))}
    safeSet(key,s.conversation_id);cid=s.conversation_id;await refresh();
  }catch(e){msg("rickBar unavailable: "+e.message)}
  finally{busy=false;$("send").disabled=!cid}
}
$("l2").checked=safeGet(l2key)==="1";document.body.classList.toggle("showl2",$("l2").checked);
$("l2").addEventListener("change",()=>{document.body.classList.toggle("showl2",$("l2").checked);safeSet(l2key,$("l2").checked?"1":"0")});
$("model").addEventListener("change",()=>safeSet(mkey,$("model").value));
$("deep").checked=safeGet("rickbar-r2-deep")==="1";$("deep").addEventListener("change",()=>safeSet("rickbar-r2-deep",$("deep").checked?"1":"0"));
$("chat").addEventListener("submit",async e=>{
  e.preventDefault();if(busy||!cid)return;const prompt=$("prompt").value.trim();if(!prompt)return;
  busy=true;$("send").disabled=true;msg("Thinking with "+$("model").value+" on X2…");
  const tid="t-"+crypto.randomUUID().replaceAll("-","");
  const m=$("model").value,words=n=>n+" word"+(n===1?"":"s");
  const live=document.createElement("div");live.className="entry";
  const you=document.createElement("div");you.className="you";you.textContent="You: "+prompt;
  const ans=document.createElement("div");ans.className="live";ans.textContent="…";
  live.append(you,ans);$("log").append(live);$("log").scrollTop=$("log").scrollHeight;$("prompt").value="";
  const tick=setInterval(async()=>{try{const p=await (await fetch("/api/progress/"+encodeURIComponent(cid)+"/"+encodeURIComponent(tid))).json();
    if(p.phase==="waiting")msg(m+" on X2 · starting…");
    else if(p.phase==="loading")msg(m+" on X2 · loading the model into memory · "+p.seconds+" s");
    else if(p.phase==="thinking"){msg(m+" on X2 · thinking · "+p.seconds+" s · "+words(p.thinking_words)+" of reasoning so far");if(p.thinking_tail&&!p.partial)ans.textContent="(thinking) …"+p.thinking_tail;}
    else if(p.phase==="answering"){msg(m+" on X2 · writing · "+p.seconds+" s");}
    if(p.partial){ans.textContent=p.partial;$("log").scrollTop=$("log").scrollHeight;}}catch(e){}},500);
  try{const r=await api("/api/turn",{conversation_id:cid,turn_id:tid,prompt,epoch,model:m,deep:$("deep").checked});
      if(!(r.state==="COMMITTED"||r.state==="REPLAY"))$("prompt").value=prompt;}
  catch(e){$("prompt").value=prompt;clearInterval(tick);try{await refresh()}catch(x){};busy=false;$("send").disabled=!cid;msg("No answer: "+e.message+". Nothing was resent; your question is back in the box.");return}
  clearInterval(tick);try{await refresh()}catch(e){};busy=false;$("send").disabled=!cid
});
$("new").addEventListener("click",async()=>{if(busy)return;try{const c=await api("/api/conversation",{});safeSet(key,c.conversation_id);cid=c.conversation_id;await refresh()}catch(e){msg("Could not start: "+e.message)}});
load();
</script></body></html>'''


def reconcile_orphans(store):
    """At startup nothing can be in flight, so any PENDING turn was cut off by a restart.
    Mark it unanswered (INDETERMINATE) through R1's own fenced fail_turn; never resend it."""
    with store.lock:
        rows = store.db.execute("SELECT t.conversation_id, t.turn_id, t.epoch FROM turns t "
                                "JOIN conversations c ON c.conversation_id=t.conversation_id "
                                "WHERE t.status='PENDING' AND t.epoch=c.epoch").fetchall()
    n = 0
    for cid, tid, ep in rows:
        if store.fail_turn(cid, tid, ep) == "INDETERMINATE":
            n += 1
    return n


def warm_up():
    """Load the default model into memory once at start, so the first question is not a cold start."""
    try:
        m = pick_default(providers())
        if m:
            req = urllib.request.Request(OLLAMA + "/api/generate", data=json.dumps(
                {"model": m, "keep_alive": KEEP_ALIVE}).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=300).read()
    except Exception:
        pass


def main():
    import argparse
    p = argparse.ArgumentParser(description="rickBar R2: layered local front door on R1")
    p.add_argument("--port", type=int, default=8767)
    p.add_argument("--store", default=str(pathlib.Path.home() / "CoBarState" / "continuity-r2.sqlite"))
    p.add_argument("--receipt-dir", default=str(pathlib.Path.home() / "CoBarReceipts" / "r2"))
    a = p.parse_args()
    if not 1024 <= a.port <= 65535:
        p.error("port must be 1024..65535")
    pathlib.Path(a.store).parent.mkdir(parents=True, exist_ok=True)
    store = ContinuityStore(a.store)
    print("orphaned turns from a previous run marked unanswered: %d" % reconcile_orphans(store), flush=True)
    threading.Thread(target=warm_up, daemon=True).start()
    print("rickBar R2: http://127.0.0.1:%d" % a.port, flush=True)
    try:
        ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(store, a.receipt_dir, a.port)).serve_forever()
    finally:
        store.close()


if __name__ == "__main__":
    main()
