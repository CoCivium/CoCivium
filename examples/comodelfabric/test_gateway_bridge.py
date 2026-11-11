"""Durable model-output receipts for CoModelFabric; not an effect ACK or native RickBar integration."""
import json, pathlib, tempfile, unittest, hashlib, os

class ReceiptStore:
    def __init__(self, root):
        self.root=pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
    def save(self, work_id, model_result):
        if not work_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in work_id):
            raise ValueError('invalid work id')
        data={'work_id':work_id,'status':'MODEL_OUTPUT_UNVERIFIED','result':model_result}
        payload=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
        digest=hashlib.sha256(payload).hexdigest()
        target=self.root/(work_id+'.json')
        if target.exists():
            if target.read_bytes()==payload: return {'state':'REPLAY','sha256':digest}
            return {'state':'CONFLICT','sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
        fd,tmp=tempfile.mkstemp(dir=self.root,prefix='.pending-')
        try:
            with os.fdopen(fd,'wb') as f:
                f.write(payload); f.flush(); os.fsync(f.fileno())
            try: os.link(tmp,target)
            except FileExistsError:
                return {'state':'REPLAY' if target.read_bytes()==payload else 'CONFLICT','sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
            return {'state':'RECORDED_UNVERIFIED','sha256':digest}
        finally: os.unlink(tmp)

class Tests(unittest.TestCase):
    def test_record_and_replay(self):
        with tempfile.TemporaryDirectory() as d:
            s=ReceiptStore(d)
            self.assertEqual(s.save('w1',{'text':'hi'})['state'],'RECORDED_UNVERIFIED')
            self.assertEqual(s.save('w1',{'text':'hi'})['state'],'REPLAY')
            self.assertEqual(s.save('w1',{'text':'different'})['state'],'CONFLICT')
    def test_restart_persists(self):
        with tempfile.TemporaryDirectory() as d:
            ReceiptStore(d).save('w2',{'text':'hello'})
            self.assertEqual(ReceiptStore(d).save('w2',{'text':'hello'})['state'],'REPLAY')
    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): ReceiptStore(d).save('../bad',{})
    def test_model_output_not_verified(self):
        with tempfile.TemporaryDirectory() as d:
            ReceiptStore(d).save('w3',{'done':True})
            self.assertEqual(json.loads((pathlib.Path(d)/'w3.json').read_text())['status'],'MODEL_OUTPUT_UNVERIFIED')
if __name__=='__main__': unittest.main(verbosity=2)
