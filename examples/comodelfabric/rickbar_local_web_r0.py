"""Local-only RickBar browser surface. Source candidate, not installed on X2."""
import json
import os
import pathlib
import re
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rickbar_ollama_bridge_r0 import run

HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RickBar Local</title>
<style>
body{margin:0;background:#10121d;color:#e7e7f4;font:16px system-ui}
main{max-width:760px;margin:5vh auto;padding:24px}h1{color:#d9a8ff}
#log{height:58vh;overflow:auto;white-space:pre-wrap;border:1px solid #434052;border-radius:12px;padding:16px}
.entry{padding:12px;border-bottom:1px solid #333}
form{display:flex;gap:8px;margin-top:16px}input{flex:1;padding:14px;border-radius:8px;border:1px solid #666;background:#222438;color:white}
button{padding:12px;border-radius:8px;background:#8c54cc;color:white;border:0}
small{color:#a6a4b6}
</style><main><h1>CoBar / RickBar</h1><small>Local Ollama · Model output is not an effect ACK</small>
<div id="log" role="log" aria-live="polite"></div>
<form id="chat"><input id="prompt" aria-label="Message" placeholder="Ask or describe a task" required autocomplete="off"><button>Send</button></form>
<script>
const log=document.getElementById('log'), form=document.getElementById('chat');
function line(t){const e=document.createElement('div');e.className='entry';e.textContent=t;log.appendChild(e);log.scrollTop=log.scrollHeight;}
form.addEventListener('submit',async e=>{e.preventDefault();const input=document.getElementById('prompt'),prompt=input.value.trim();if(!prompt)return;input.value='';line('You: '+prompt);
try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});const d=await r.json();line('RickBar ['+d.status+'] '+(d.response||d.error||'')+'\nWorkID: '+(d.work_id||'unavailable')+'\nReceipt: '+(d.receipt_sha256||'unavailable'));}
catch(err){line('Unavailable: '+err.message);}});
</script></main></html>"""

def respond(prompt, model, receipt_dir, bridge=run):
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 12000:
        return 400, {"status": "INVALID_PROMPT", "error": "Prompt must be 1..12000 characters"}
    work_id = "rb-" + uuid.uuid4().hex
    result = bridge(prompt, model, receipt_dir, work_id=work_id)
    return 200, result

def make_handler(model, receipt_dir):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, code, value):
            data = json.dumps(value).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            if self.path != "/":
                return self.send_json(404, {"error": "NOT_FOUND"})
            data = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def do_POST(self):
            if self.path != "/api/chat":
                return self.send_json(404, {"error": "NOT_FOUND"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 16000:
                    return self.send_json(413, {"error": "BODY_SIZE"})
                obj = json.loads(self.rfile.read(length))
                code, result = respond(obj.get("prompt"), model, receipt_dir)
                return self.send_json(code, result)
            except (ValueError, TypeError, json.JSONDecodeError):
                return self.send_json(400, {"error": "INVALID_JSON"})
            except Exception:
                return self.send_json(503, {"status": "UNAVAILABLE", "error": "Local model or receipt store failed"})
    return Handler

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--model", default="qwen3:4b")
    p.add_argument("--receipt-dir", default=str(pathlib.Path.home() / "CoBarReceipts"))
    a = p.parse_args()
    if not 1024 <= a.port <= 65535:
        p.error("port must be 1024..65535")
    print(f"RickBar local: http://127.0.0.1:{a.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.model, a.receipt_dir)).serve_forever()
