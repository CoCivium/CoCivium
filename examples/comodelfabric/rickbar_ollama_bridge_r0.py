"""RickBar-to-Ollama bridge CLI R0: local-only, not installed in native RickBar."""
import argparse
import json
import pathlib
from ollama_gateway_r0 import OllamaGateway
from test_gateway_bridge import ReceiptStore

def run(prompt, model, receipt_dir, work_id=None, gateway=None):
    gateway = gateway or OllamaGateway()
    result = gateway.generate(prompt, model, work_id)
    if result['status'] != 'MODEL_OUTPUT_UNVERIFIED':
        return {'status':'MODEL_UNAVAILABLE','result':result}
    receipt = ReceiptStore(receipt_dir).save(result['work_id'], result)
    return {'status':receipt['state'], 'work_id':result['work_id'],
            'receipt_sha256':receipt['sha256'],
            'model_status':result['status'],
            'response':result['text']}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description='Bounded local Ollama model output with durable receipt')
    p.add_argument('--prompt',required=True)
    p.add_argument('--model',default='qwen3:4b')
    p.add_argument('--receipt-dir',required=True)
    p.add_argument('--work-id')
    a=p.parse_args()
    print(json.dumps(run(a.prompt,a.model,a.receipt_dir,a.work_id),ensure_ascii=False))
