#!/usr/bin/env python3
"""CoThumb R1: explicit-selection, local-only rich payload capsule.

This makes no OS hooks or network calls. It neither sends nor pastes content.
It does not claim that a physical mouse button or agent provider is connected.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import uuid
import zipfile

SCHEMA = 'CoCopy.RichIntentCapsule.R1-CANDIDATE'
CHUNK = 4 * 1024 * 1024
LIMIT_PER_FILE = 128 * 1024 * 1024
LIMIT_TOTAL = 256 * 1024 * 1024
MAX_FILES = 8
RECEIPT_SCHEMA = 'CoMx.LocalRichCapsuleReceipt.R1-CANDIDATE'
VALID_EXT = re.compile(r'^\.[a-zA-Z0-9]{1,12}$')


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_new(path: Path, data: bytes):
    # Refuse silent clobber.
    with path.open('xb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def selected_regular_file(path: Path) -> os.stat_result:
    if path.is_symlink():
        raise ValueError('Symlink input is not accepted in R1')
    s = path.stat()
    if not stat.S_ISREG(s.st_mode):
        raise ValueError('Only explicitly selected regular files are accepted')
    return s


def create_capsule(inputs: list[str], outdir: str, intent: str = 'inspect', origin: str = 'EXPLICIT_FILE_SELECTION', max_bytes: int = LIMIT_TOTAL):
    if not (1 <= len(inputs) <= MAX_FILES):
        raise ValueError(f'Select 1 to {MAX_FILES} files')
    if not (0 < max_bytes <= LIMIT_TOTAL):
        raise ValueError('Max payload must be positive and at most 256 MiB')
    if intent not in {'inspect', 'compare', 'summarize', 'challenge', 'archive-local'}:
        raise ValueError('Intent not permitted in R1')
    if origin not in {'EXPLICIT_FILE_SELECTION', 'CLI_EXPLICIT_FILE'}:
        raise ValueError('Origin not permitted in R1')
    paths = [Path(p).expanduser() for p in inputs]
    identities = [str(p.resolve()) for p in paths]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate source path rejected')
    sizes = [selected_regular_file(p).st_size for p in paths]
    if any(s > LIMIT_PER_FILE for s in sizes) or sum(sizes) > max_bytes:
        raise ValueError('Selected payload exceeds finite per-file or aggregate budget')
    out = Path(outdir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    capsule_id = 'cothumb-' + utc_now().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:12]
    staging = out / ('.' + capsule_id + '.staging')
    final = out / capsule_id
    staging.mkdir(mode=0o700)
    try:
        objects = staging / 'objects'
        objects.mkdir()
        descriptors = []
        aggregate = 0
        for i, src in enumerate(paths, 1):
            before = selected_regular_file(src)
            # Object identifiers deliberately avoid source filenames and paths.
            object_name = f'objects/object-{i:03d}.blob'
            target = staging / object_name
            h = hashlib.sha256()
            total = 0
            chunks = []
            with src.open('rb') as fin, target.open('xb') as fout:
                while True:
                    buf = fin.read(CHUNK)
                    if not buf:
                        break
                    total += len(buf)
                    if total > LIMIT_PER_FILE or aggregate + total > max_bytes:
                        raise ValueError('Stream exceeded finite size budget')
                    fout.write(buf)
                    h.update(buf)
                    chunks.append(digest(buf))
                fout.flush()
                os.fsync(fout.fileno())
            after = selected_regular_file(src)
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino) or total != before.st_size:
                raise RuntimeError('Selected source changed while copying; capture withheld')
            mime, _ = mimetypes.guess_type(src.name)
            descriptor = {
                'object_id': f'object-{i:03d}',
                'payload_relpath': object_name,
                'size_bytes': total,
                'sha256': h.hexdigest(),
                'chunk_bytes': CHUNK,
                'chunk_sha256': chunks,
                'mime_hint_unverified': mime or 'application/octet-stream',
                'original_name_and_path': 'REDACTED',
            }
            descriptors.append(descriptor)
            aggregate += total
        now = utc_now()
        manifest = {
            'schema': SCHEMA,
            'capsule_id': capsule_id,
            'captured_at': now.isoformat(),
            'authority_expires_at': (now + timedelta(hours=24)).isoformat(),
            'intent': intent,
            'input_origin': origin,
            'objects': descriptors,
            'total_bytes': sum(d['size_bytes'] for d in descriptors),
            'source_path_retained': False,
            'effects': {'network': 0, 'provider_calls': 0, 'messages_sent': 0, 'mouse_remap': 0},
            'authority': {'local_capture': 'EXPLICIT_SELECTION', 'remote_use': 'NONE', 'execution': 'NONE', 'publish': 'NONE', 'credential_access': 'NONE'},
            'receiver': {'selected_receiver': None, 'readproof': 'NOT_RECEIVED'},
            'privacy': {'scope': 'LOCAL_PRIVATE_UNLESS_USER_SEPARATELY_REVIEWS', 'warning': 'Archive holds FULL original file bytes, not just hashes. Do not upload without reviewing contents.'},
            'lineage': {'reference': 'CoCopy.IntentCapsule.v0.1', 'note': 'R1 candidate, not integration or supersession'},
            'nonclaims': ['LOCAL_IS_NOT_LANDED', 'POINTER_NE_ACK', 'HASH_NE_TRUTH', 'MANIFEST_NE_UNLIMITED_CONTEXT', 'VIRTUAL_WORKER_NE_LIVE_AGENT']
        }
        manifest_bytes = json_bytes(manifest)
        write_new(staging / 'manifest.json', manifest_bytes)
        # Self-contained, inspectable ZIP (no compression tricks or remote endpoints).
        archive = staging / 'bundle.copack.zip'
        with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
            z.write(staging / 'manifest.json', 'manifest.json')
            for desc in descriptors:
                z.write(staging / desc['payload_relpath'], desc['payload_relpath'])
        final_manifest_sha = digest(manifest_bytes)
        receipt = {
            'schema': RECEIPT_SCHEMA,
            'capsule_id': capsule_id,
            'at': utc_now().isoformat(),
            'manifest_sha256': final_manifest_sha,
            'archive_sha256': hash_file(archive),
            'state': 'LOCAL_CAPSULE_CREATED__FANOUT_UNRUN',
            'external_effects': 0,
            'physical_button': 'NOT_OBSERVED',
            'independent_receiver_ack': 'NONE',
        }
        write_new(staging / 'receipt.json', json_bytes(receipt))
        if final.exists():
            raise FileExistsError('Capsule collision')
        staging.rename(final)
        return final, manifest, receipt
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as fin:
        while b := fin.read(CHUNK):
            h.update(b)
    return h.hexdigest()


def check_structure(base: Path, manifest: dict) -> dict:
    errs = []
    if manifest.get('schema') != SCHEMA:
        errs.append('schema mismatch')
    if manifest.get('source_path_retained') is not False:
        errs.append('privacy/path redaction contract missing')
    objects = manifest.get('objects', [])
    if not isinstance(objects, list) or not (1 <= len(objects) <= MAX_FILES):
        errs.append('object count not bounded')
    else:
        for i, obj in enumerate(objects, 1):
            expected = f'objects/object-{i:03d}.blob'
            if obj.get('payload_relpath') != expected:
                errs.append('unexpected object relative path')
            if obj.get('original_name_and_path') != 'REDACTED':
                errs.append('private filename/path leaked')
            if not re.fullmatch(r'[0-9a-f]{64}', str(obj.get('sha256',''))):
                errs.append('invalid object hash')
            if not isinstance(obj.get('size_bytes'), int) or obj['size_bytes'] < 0:
                errs.append('invalid object size')
            if obj.get('chunk_bytes') != CHUNK:
                errs.append('unexpected chunk size')
    return {'worker':'schema_and_privacy', 'status':'FAIL' if errs else 'PASS', 'findings':errs}


def check_bytes(base: Path, manifest: dict) -> dict:
    errors = []
    for obj in manifest.get('objects', []):
        rel = obj.get('payload_relpath')
        if not re.fullmatch(r'objects/object-[0-9]{3}\.blob', str(rel)):
            errors.append('unsafe relative path')
            continue
        path = base / rel
        if path.is_symlink() or not path.is_file():
            errors.append(f'missing or symlink object: {rel}')
            continue
        h = hashlib.sha256()
        chunks = []
        count = 0
        with path.open('rb') as f:
            while data := f.read(CHUNK):
                h.update(data)
                chunks.append(digest(data))
                count += len(data)
        if h.hexdigest() != obj.get('sha256') or count != obj.get('size_bytes') or chunks != obj.get('chunk_sha256'):
            errors.append(f'byte or chunk mismatch: {rel}')
    # Archive must be independently complete and byte-for-byte consistent.
    archive = base / 'bundle.copack.zip'
    expected_members = {'manifest.json'} | {o['payload_relpath'] for o in manifest.get('objects', []) if re.fullmatch(r'objects/object-[0-9]{3}\.blob', str(o.get('payload_relpath')))}
    try:
        with zipfile.ZipFile(archive) as z:
            members=set(z.namelist())
            if members != expected_members or len(z.namelist()) != len(expected_members):
                errors.append('archive member set differs from manifest')
            if z.read('manifest.json') != (base / 'manifest.json').read_bytes():
                errors.append('archive manifest mismatch')
            for obj in manifest.get('objects', []):
                rel=obj.get('payload_relpath')
                if rel not in members or not re.fullmatch(r'objects/object-[0-9]{3}\.blob', str(rel)):
                    continue
                with z.open(rel) as stream:
                    h=hashlib.sha256()
                    total=0
                    while chunk := stream.read(CHUNK):
                        h.update(chunk)
                        total += len(chunk)
                if h.hexdigest()!=obj['sha256'] or total!=obj['size_bytes']:
                    errors.append(f'archive data mismatch: {rel}')
    except (OSError,zipfile.BadZipFile,KeyError) as e:
        errors.append('archive verification failed: '+type(e).__name__)
    return {'worker':'content_hashes', 'status':'FAIL' if errors else 'PASS', 'findings':errors}


def check_authority(base: Path, manifest: dict) -> dict:
    errors=[]
    a=manifest.get('authority', {})
    if a.get('remote_use') != 'NONE' or a.get('execution') != 'NONE' or a.get('publish') != 'NONE' or a.get('credential_access') != 'NONE':
        errors.append('invalid effect authority')
    if manifest.get('effects') != {'network':0,'provider_calls':0,'messages_sent':0,'mouse_remap':0}:
        errors.append('external effect claim mismatch')
    if manifest.get('receiver', {}).get('readproof') != 'NOT_RECEIVED':
        errors.append('receiver readproof cannot be inherited')
    return {'worker':'authority_and_receiver', 'status':'FAIL' if errors else 'PASS', 'findings':errors}


def verify_capsule(folder: str, workers: int = 3, write_receipt: bool = True) -> dict:
    if workers not in (1,2,3):
        raise ValueError('Worker limit is 1-3')
    base=Path(folder)
    manifest=json.loads((base/'manifest.json').read_text('utf-8'))
    checks=(check_structure, check_bytes, check_authority)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(fn,base,manifest) for fn in checks]
        results=[f.result() for f in futures]
    state='PASS_LOCAL_CHECKS' if all(x['status']=='PASS' for x in results) else 'FAIL_LOCAL_CHECKS'
    receipt={'schema':RECEIPT_SCHEMA,'capsule_id':manifest.get('capsule_id'),'at':utc_now().isoformat(), 'state':state,'checks':results,'logical_checks':3,'max_worker_threads':workers, 'independent_provider_reproductions':0,'external_effects':0,'receiver_readproof':'NONE','evidence_scope':'This host, these bytes; no network/provider/device test'}
    if write_receipt:
        # Uniquely named receipts retain historical failure/success evidence without rewriting.
        name='verify-'+uuid.uuid4().hex[:12]+'.json'
        write_new(base/name,json_bytes(receipt))
    return receipt


def main(argv=None):
    p=argparse.ArgumentParser(description='CoThumb R1 explicit local capsule. NO provider calls or mouse hooks.')
    sub=p.add_subparsers(dest='verb',required=True)
    c=sub.add_parser('capture',help='Copy selected exact file bytes to a local content-addressed evidence capsule')
    c.add_argument('--file',action='append',required=True,help='Explicit file path; max eight')
    c.add_argument('--output-dir',required=True)
    c.add_argument('--intent',default='inspect',choices=['inspect','compare','summarize','challenge','archive-local'])
    c.add_argument('--origin',default='CLI_EXPLICIT_FILE',choices=['EXPLICIT_FILE_SELECTION','CLI_EXPLICIT_FILE'])
    c.add_argument('--max-bytes',type=int,default=LIMIT_TOTAL)
    c.add_argument('--verify-local',action='store_true',help='Automatically run bounded local verification after explicit capture')
    v=sub.add_parser('verify',help='Run three bounded, deterministic local validators')
    v.add_argument('--capsule',required=True)
    v.add_argument('--max-workers',type=int,default=3)
    a=p.parse_args(argv)
    if a.verb=='capture':
        root,manifest,receipt=create_capsule(a.file,a.output_dir,a.intent,a.origin,a.max_bytes)
        answer={'status':'LOCAL_CREATED','capsule_path':str(root), 'capsule_id':manifest['capsule_id'], 'objects':len(manifest['objects']), 'bytes':manifest['total_bytes'], 'sha256':receipt['manifest_sha256'], 'receiver':'NONE'}
        if a.verify_local:
            v=verify_capsule(str(root),workers=3)
            answer['local_verification']=v['state']
            if v['state']!='PASS_LOCAL_CHECKS':
                print(json.dumps(answer,sort_keys=True))
                return 2
        print(json.dumps(answer,sort_keys=True))
    else:
        r=verify_capsule(a.capsule,workers=a.max_workers)
        print(json.dumps(r,sort_keys=True))
        if r['state']!='PASS_LOCAL_CHECKS': return 2
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, zipfile.BadZipFile) as e:
        print(f'HOLD: {type(e).__name__}: {e}',file=sys.stderr)
        sys.exit(3)
