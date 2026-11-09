"""Local RickBar R1 conversation HTTP surface.

Proof scope: same-host localhost browser + Ollama. This does NOT attach to
ChatGPT sessions, switch paid account sessions, delete provider data, install
native rickBar, or prove cross-machine pickup. Separate from R0 intentionally.
"""
import json
import pathlib
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rickbar_continuity_r1 import ContinuityStore
from rickbar_local_web_r0 import allowed_local_request
from rickbar_ollama_bridge_r0 import run as local_ollama_run

HTML = r'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><title>rickBar | Local Continuity R1</title>
<style>
:root{font:16px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:#101221;color:#eef2ff}
main{max-width:860px;margin:auto;padding:22px 16px}
h1{margin:.3em 0;color:#e4beff}a{color:#c1e8ff}
.status{background:#23294a;border:1px solid #8893c6;border-radius:12px;padding:10px 14px}
small{color:#c4cde0}
#log{min-height:210px;height:50vh;overflow:auto;background:#171a30;
border:1px solid #7381a7;border-radius:14px;padding:12px;margin:12px 0}
.entry{padding:11px;border-bottom:1px solid #3b3e5a;white-space:pre-wrap;overflow-wrap:anywhere}
form{display:flex;gap:8px;margin-top:12px}
input{flex:1;min-width:40px;padding:13px;background:#222840;color:white;
border:1px solid #92a4c9;border-radius:9px}
button{cursor:pointer;background:#aee8d5;color:#0d2020;border:none;
border-radius:9px;padding:12px;font-weight:700}
button:disabled{opacity:.5;cursor:wait}
button:focus-visible,input:focus-visible{outline:3px solid #ffdd86;outline-offset:2px}
</style></head><body><main>
<h1>rickBar <small>Local Continuity R1</small></h1>
<p>One local conversation, recoverable after browser or worker restart. Model text is not an effect acknowledgment. No external ChatGPT session access.</p>
<div id="state" class="status" role="status" aria-live="polite">Opening local conversation…</div>
<div id="log" role="log" aria-live="polite" aria-label="Conversation history"></div>
<form id="chat"><input id="prompt" aria-label="Message" placeholder="Type your message" required maxlength="12000" autocomplete="off">
<button id="send" type="submit" disabled>Send</button></form>
<p><button id="new" type="button">Start a separate conversation</button></p>
<p><small>Stored only in this local app's selected SQLite file. Browser storage remembers a conversation pointer, not the transcript. No cloud synchronisation, automatic deletion, worker immortality, or native bar installation is claimed.</small></p>
<p><a href="https://github.com/CoCivium/CoCivium/blob/main/docs/Onramp/COGOALL_PUBLIC_REBOUND_HUB_20261108.md">Project and recovery context</a></p>
</main><script>
"use strict";
const $=id=>document.getElementById(id);
let conversationId=null,epoch=null,busy=false;
const key="rickbar-r1-local-conversation";
function message(text){$("state").textContent=text}
function render(data){
  conversationId=data.conversation_id; epoch=data.epoch;
  $("log").replaceChildren();
  (data.turns||[]).forEach(t=>{
    const item=document.createElement("div");item.className="entry";
    item.textContent="You: "+t.prompt+"\n"+
      (t.status==="COMMITTED"?"Local model (unverified): "+(t.response||""):
       "Status: "+t.status+" (not a confirmed answer)")+
      "\nSource: "+(t.trigger_kind||"UNKNOWN")+" ["+
      (t.trigger_evidence||"NONE")+"]");
    $("log").append(item);
  });
  $("log").scrollTop=$("log").scrollHeight;
  message("Conversation: "+conversationId+" · worker epoch "+epoch+
          " · LOCAL_STORE_READBACK · no remote ACK");
  $("send").disabled=busy;
}
async function api(path,payload){
  const opts=payload===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)};
  const result=await fetch(path,opts);
  const data=await result.json();
  if(!result.ok)throw Error(data.error||data.status||"LOCAL_UNAVAILABLE");
  return data;
}
async function load(){
  busy=true;$("send").disabled=true;
  try{
    let id=localStorage.getItem(key),state;
    if(id){
      const response=await fetch("/api/conversation/"+encodeURIComponent(id));
      if(response.status===200)state=await response.json();
      else if(response.status!==404)throw Error("Unable to read local conversation");
    }
    if(!state){
      const created=await api("/api/conversation",{});
      state=await api("/api/conversation/"+encodeURIComponent(created.conversation_id));
    }
    localStorage.setItem(key,state.conversation_id);render(state);
  }catch(e){message("Local continuity unavailable: "+e.message);conversationId=null;epoch=null}
  finally{busy=false;$("send").disabled=!conversationId}
}
$("chat").addEventListener("submit",async e=>{
  e.preventDefault();if(busy||!conversationId)return;
  const prompt=$("prompt").value.trim();if(!prompt)return;
  busy=true;$("send").disabled=true;message("Submitting one bounded local turn…");
  // One TurnID per user submission; never automatically resubmit after unknown result.
  const turnId="t-"+crypto.randomUUID().replaceAll("-","");
  try{
    const reply=await api("/api/turn",{conversation_id:conversationId,turn_id:turnId,prompt,epoch});
    if(reply.state!=="COMMITTED"&&reply.state!=="REPLAY")message("Unverified or unresolved turn: "+reply.state);
    else $("prompt").value="";
  }catch(e){message("Result uncertain or unavailable: "+e.message+". Reopen to inspect stored state before retry.")}
  finally{
    try{const state=await api("/api/conversation/"+encodeURIComponent(conversationId));render(state)}
    catch(e){message("Recovery readback unavailable: "+e.message)}
    busy=false;$("send").disabled=!conversationId;
  }
});
$("new").addEventListener("click",async()=>{
  if(busy)return;
  busy=true;$("send").disabled=true;
  try{
    const c=await api("/api/conversation",{});
    localStorage.setItem(key,c.conversation_id);
    render(await api("/api/conversation/"+encodeURIComponent(c.conversation_id)));
  }catch(e){message("Could not create conversation: "+e.message)}
  finally{busy=false;$("send").disabled=!conversationId}
});
load();
</script></body></html>'''


def act(store, payload, model, receipt_dir, bridge=local_ollama_run):
    """Dispatch one explicit Ollama turn after local fenced reservation."""
    cid=payload.get("conversation_id")
    tid=payload.get("turn_id")
    prompt=payload.get("prompt")
    epoch=payload.get("epoch")
    # An HTTP caller cannot self-assert SCHEDULED, EVENT or authenticated USER.
    # Loopback request observed does not identify the human or upstream cause.
    started=store.begin_turn(cid,tid,prompt,epoch,
                             trigger_kind="LOCAL_HTTP_REQUEST")
    if started["state"] != "STARTED":
        return started
    try:
        context=store.model_context(cid,prompt)
        result=bridge(context,model,receipt_dir,work_id=tid)
        if result.get("status") not in ("RECORDED_UNVERIFIED","REPLAY"):
            store.fail_turn(cid,tid,epoch)
            return {"state":"MODEL_UNAVAILABLE","conversation_id":cid,
                    "turn_id":tid,"evidence_class":"NONE"}
        response=result.get("response")
        if not isinstance(response,str):
            store.fail_turn(cid,tid,epoch)
            return {"state":"INVALID_MODEL_RESPONSE"}
        committed=store.commit_turn(cid,tid,response,epoch)
        committed["model_output_receipt"]=result.get("receipt_sha256")
        return committed
    except Exception:
        store.fail_turn(cid,tid,epoch)
        return {"state":"INDETERMINATE","conversation_id":cid,
                "turn_id":tid,"evidence_class":"NONE"}


def make_handler(store, model, receipt_dir, bridge=local_ollama_run):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # avoid logging conversation identifiers or prompt content

        def json_response(self, code, data):
            raw=json.dumps(data,ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def allowed(self):
            if not allowed_local_request(self.headers.get("Host"),self.headers.get("Origin")):
                self.json_response(403,{"error":"LOCAL_ORIGIN_REQUIRED"})
                return False
            return True

        def do_GET(self):
            if not self.allowed(): return
            path=urlsplit(self.path).path
            if path=="/":
                data=HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Cache-Control","no-store")
                self.send_header("X-Content-Type-Options","nosniff")
                self.send_header("Content-Length",str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path.startswith("/api/conversation/"):
                try:
                    cid=unquote(path.rsplit("/",1)[-1])
                    item=store.state(cid)
                    self.json_response(404 if item["state"]=="UNKNOWN_CONVERSATION" else 200,item)
                except ValueError:
                    self.json_response(400,{"error":"INVALID_CONVERSATION"})
                return
            self.json_response(404,{"error":"NOT_FOUND"})

        def do_POST(self):
            if not self.allowed(): return
            path=urlsplit(self.path).path
            if path not in ("/api/conversation","/api/turn"):
                self.json_response(404,{"error":"NOT_FOUND"})
                return
            try:
                length=int(self.headers.get("Content-Length","0"))
                if length<2 or length>20000:
                    self.json_response(413,{"error":"BODY_SIZE"});return
                if self.headers.get("Content-Type","").split(";")[0].strip().lower()!="application/json":
                    self.json_response(415,{"error":"JSON_REQUIRED"});return
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict):
                    raise ValueError("object required")
                if path=="/api/conversation":
                    if payload: raise ValueError("empty request expected")
                    result=store.create()
                else:
                    result=act(store,payload,model,receipt_dir,bridge=bridge)
                state=result["state"]
                code=200 if state in {"CREATED","EXISTS","COMMITTED","REPLAY"} else (
                    409 if state in {"FENCED","CONFLICT","ALREADY_PENDING","INDETERMINATE"} else 503
                    if state in {"MODEL_UNAVAILABLE","INVALID_MODEL_RESPONSE"} else 400)
                self.json_response(code,result)
            except (ValueError,TypeError,KeyError,json.JSONDecodeError):
                self.json_response(400,{"error":"INVALID_REQUEST"})
            except Exception:
                self.json_response(503,{"error":"LOCAL_STORE_UNAVAILABLE"})
    return Handler


def main():
    import argparse
    p=argparse.ArgumentParser(description="Local RickBar continuity R1 source experiment")
    p.add_argument("--port",type=int,default=8766)
    p.add_argument("--model",default="qwen3:4b")
    p.add_argument("--store",default=str(pathlib.Path.home()/"CoBarState"/"continuity-r1.sqlite"))
    p.add_argument("--receipt-dir",default=str(pathlib.Path.home()/"CoBarReceipts"))
    args=p.parse_args()
    if not 1024 <= args.port <= 65535: p.error("port must be 1024..65535")
    store=ContinuityStore(args.store)
    print("Local RickBar R1: http://127.0.0.1:"+str(args.port),flush=True)
    try:
        ThreadingHTTPServer(("127.0.0.1",args.port),
                            make_handler(store,args.model,args.receipt_dir)).serve_forever()
    finally: store.close()


if __name__=="__main__":
    main()
