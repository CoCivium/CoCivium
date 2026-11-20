"""CoLocalModelWorkerR3 transport regressions, model/workspace fixture only."""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

_HERE = Path(__file__).resolve()
P = _HERE.parents[1] / 'scripts' / 'CoLocalModelWorkerR3.py'
if not P.exists():
    P = _HERE.with_name('CoLocalModelWorkerR3.py')
spec = importlib.util.spec_from_file_location('colocal_r3_candidate', P)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_POST(self):
        self.server.seen.append(('POST', self.path, self.rfile.read(int(self.headers.get('Content-Length','0')))))
        if self.server.mode == 'redirect':
            self.send_response(302)
            self.send_header('Location', self.server.redirect_to)
            self.end_headers()
        elif self.server.mode == 'huge':
            data = b'x' * (w.MAX_MODEL_HTTP_BYTES + 10)
            self.send_response(200)
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            try:self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):pass
        else:
            data = json.dumps({'response':'{"analysis_summary":"fixture","proposed_deltas":[]}', 'done': True}).encode()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    def do_GET(self):
        self.server.seen.append(('GET',self.path,b''))
        self.send_response(200);self.end_headers();self.wfile.write(b'PROXY_OR_REDIRECT_HIT')

class WorkerR3Transport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.server.seen=[];cls.server.mode='ok';cls.server.redirect_to=''
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_address[1])
        cls.proxy=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.proxy.seen=[];cls.proxy.mode='ok';cls.proxy.redirect_to=''
        cls.proxythread=threading.Thread(target=cls.proxy.serve_forever,daemon=True)
        cls.proxythread.start()
        cls.proxyurl='http://127.0.0.1:'+str(cls.proxy.server_address[1])
    @classmethod
    def tearDownClass(cls):
        for server,thread in ((cls.server,cls.thread),(cls.proxy,cls.proxythread)):
            server.shutdown(); server.server_close();thread.join(2)

    def tearDown(self):
        self.server.mode='ok';self.server.redirect_to=''
        self.server.seen.clear();self.proxy.seen.clear()

    def sample(self,endpoint=None,timeout=2):
        return w.call_ollama(endpoint or self.base,'fixture-model','public-safe fixture',timeout)

    def test_normal_model_path_and_json(self):
        result=self.sample()
        self.assertEqual(result['worker_result']['analysis_summary'],'fixture')
        self.assertEqual(self.server.seen[0][1],'/api/generate')
        self.assertEqual(json.loads(self.server.seen[0][2])['format'],'json')

    def test_no_proxy_with_poisoned_env(self):
        with patch.dict(os.environ,{'HTTP_PROXY':self.proxyurl,'HTTPS_PROXY':self.proxyurl,'NO_PROXY':'','no_proxy':''}):
            self.sample()
        self.assertEqual(len(self.proxy.seen),0)
        self.assertEqual(len(self.server.seen),1)

    def test_no_redirect_to_another_local_server(self):
        self.server.mode='redirect';self.server.redirect_to=self.proxyurl+'/captured'
        with self.assertRaisesRegex(Exception,'REDIRECT_DENIED'):
            self.sample()
        self.assertEqual(self.proxy.seen,[])
        self.assertEqual(len(self.server.seen),1)

    def test_output_ceiling(self):
        self.server.mode='huge'
        with self.assertRaisesRegex(RuntimeError,'size ceiling'):
            self.sample()

    def test_bad_timeout(self):
        for value in (0,-1,301,float('inf'),float('nan'),True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.sample(timeout=value)

    def test_loopback_normalization(self):
        self.assertEqual(w.require_loopback('http://LOCALHOST:11434/'),'http://localhost:11434')
        self.assertEqual(w.require_loopback('http://127.0.0.2:11434'),'http://127.0.0.2:11434')
        self.assertEqual(w.require_loopback('http://[::1]:11434/'),'http://[::1]:11434')

    def test_bad_origins(self):
        cases=(None,42,'http://example.com:11434','https://localhost:11434',
             'http://localhost','http://localhost:0','http://localhost:65536',
             'http://localhost:bad','http://localhost:11434/path',
             'http://localhost:11434?x=y','http://localhost:11434#fragment',
             'http://user:pass@localhost:11434','http://localhost:11434@evil.example',
             'http://localhost:11434.evil.example','http://192.0.2.1:11434')
        for u in cases:
            with self.subTest(url=u),self.assertRaises(ValueError):w.require_loopback(u)

    def test_contract_private_rejected(self):
        with self.assertRaisesRegex(ValueError,'public-safe only'):
            w.validate_contract({'materialization_state':'LOGICAL_ONLY','effect_classes':['PROPOSE'],
                                 'authority_ceiling':'ADVISORY_ONLY','confidentiality':'PRIVATE'})
    def test_contract_effect_rejected(self):
        with self.assertRaisesRegex(ValueError,'effect classes'):
            w.validate_contract({'materialization_state':'LOGICAL_ONLY','effect_classes':['TRADE'],
                                 'authority_ceiling':'ADVISORY_ONLY','confidentiality':'PUBLIC'})
    def test_cli_public_output_and_no_clobber(self):
        contract = {'materialization_state':'LOGICAL_ONLY','uncertainty':None,
                    'effect_classes':['PROPOSE'],'authority_ceiling':'ADVISORY_ONLY',
                    'confidentiality':'PUBLIC'}
        with tempfile.TemporaryDirectory() as td:
            cp=Path(td)/'contract.json';out=Path(td)/'output.json'
            cp.write_text(json.dumps(contract))
            argv=['worker','--contract',str(cp),'--model','synthetic-model',
                  '--output',str(out),'--endpoint','http://127.0.0.1:11434']
            with patch.object(sys,'argv',argv),patch.object(w,'call_ollama',return_value={
                'worker_result': {'analysis_summary':'synthetic'}}) as call:
                self.assertEqual(w.main(),0)
            self.assertTrue(out.exists())
            self.assertEqual(json.loads(out.read_text())['state'],
                             'LOCAL_MODEL_CANDIDATE_OUTPUT__NO_EFFECT_EXECUTION')
            self.assertEqual(json.loads(out.read_text())['worker_result']['analysis_summary'],'synthetic')
            call.assert_called_once()
            with patch.object(sys,'argv',argv),patch.object(w,'call_ollama') as no_call:
                with self.assertRaises(SystemExit):w.main()
                no_call.assert_not_called()

    def test_cli_private_holds_before_model_call(self):
        contract={'materialization_state':'LOGICAL_ONLY','uncertainty':None,
                  'effect_classes':['PROPOSE'],'authority_ceiling':'ADVISORY_ONLY',
                  'confidentiality':'PRIVATE'}
        with tempfile.TemporaryDirectory() as td:
            cp=Path(td)/'contract.json';out=Path(td)/'output.json'
            cp.write_text(json.dumps(contract))
            argv=['worker','--contract',str(cp),'--model','synthetic',
                  '--output',str(out)]
            with patch.object(sys,'argv',argv),patch.object(w,'call_ollama') as no_call:
                with self.assertRaisesRegex(ValueError,'public-safe'):
                    w.main()
                no_call.assert_not_called()
            self.assertFalse(out.exists())

    def test_existing_selftest(self):
        self.assertEqual(0,w.selftest())

if __name__ == '__main__':unittest.main(verbosity=2)
