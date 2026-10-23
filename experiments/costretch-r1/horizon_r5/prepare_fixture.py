"""Prepare the pinned, synthetic R4 manifest expected by CoStretch R5.
No network, provider calls, system startup changes, credentials or overwrite.
"""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parent
DEST=ROOT.parent/"R4_LogicalHorizonMultiprocess_20261023"/"run_20261023T222000450181Z_772db0"
PIN="51ad110be355006afae96e1fa0a202bd70c00e113359f63c8ae2ddd7f3a332b5"

def digest(b):return hashlib.sha256(b).hexdigest()

def main():
    src_manifest=(ROOT/"fixtures"/"R4_manifest.json").read_bytes()
    src_receipt=(ROOT/"fixtures"/"R4_receipt.json").read_bytes()
    manifest=json.loads(src_manifest.decode("utf-8"))
    receipt=json.loads(src_receipt.decode("utf-8"))
    if digest(src_manifest)!=PIN or receipt.get("source_sha256")!=PIN:
        raise SystemExit("HOLD: public fixture identity differs from pinned R4 evidence")
    if manifest.get("schema")!="CoStretch.LogicalHorizon.R4" or len(manifest.get("work",[]))!=8:
        raise SystemExit("HOLD: synthetic R4 fixture shape mismatch")
    if manifest.get("authority")!="READ_ONLY" or receipt.get("receiver_origin_ack") is not False:
        raise SystemExit("HOLD: fixture scope mismatch")
    DEST.mkdir(parents=True,exist_ok=True)
    created=[]
    for name,raw in (("10_manifest.json",src_manifest),("90_receipt.json",src_receipt)):
        path=DEST/name
        if path.exists():
            if path.read_bytes()!=raw:raise SystemExit("HOLD_NO_CLOBBER: differing existing "+name)
        else:
            with path.open("xb") as f:f.write(raw)
            if path.read_bytes()!=raw:raise SystemExit("HOLD: local readback mismatch")
            created.append(name)
    print(json.dumps({"status":"FIXTURE_EXACT_READBACK","files_created":created,
        "source_sha256":PIN,"synthetic_only":True,"receiver_ack":False}))
if __name__=="__main__":main()

