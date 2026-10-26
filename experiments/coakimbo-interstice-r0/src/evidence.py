#!/usr/bin/env python3
"""Deterministic hash-linked receipts for the explicitly synthetic CoOptics canary.

SHA-256 is a tamper-detection checksum with pinned head, NOT an author signature,
external-ACK, scientific validation, evidence of runtime adoption, or timestamp proof.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def canon(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',', ':'),allow_nan=False).encode('utf-8')


def digest(x):
    return hashlib.sha256(canon(x)).hexdigest()


def unique_keys(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('DUPLICATE_KEY')
        d[k]=v
    return d


def events(m):
    return [
      ('PASS','PINNED_SYNTHETIC_SOURCE','512 source points; source height SHA-256 pinned',m['source_surface_sha256']),
      ('PASS','GEO_SHADOW_DIRECTION_REVERSAL','Fraction of source shadow positions changed: '+str(m['fraction_changed_under_illumination_reversal']),None),
      ('PASS','PHASE_SCREEN_AVERAGING','Toy contrast single='+str(m['speckle_contrast_single_phase_screen'])+' averaged='+str(m['speckle_contrast_averaged_independent_screens']),None),
      ('FAIL','NAIVE_DARK_MEANS_EMPTY_BASELINE','90 low-intensity DETECTOR bins despite 512 defined source surface positions; baseline is falsified only within this toy',None),
      ('PASS','MODEL_SEPARATES_COORDINATE_SYSTEMS','Surface shadow positions and detector angle bins are separate coordinate spaces',None),
      ('PASS','INVALID_INPUT_REJECTION','Unit tests reject invalid angles, surfaces, wavelength and ensemble size',None),
      ('PASS','NO_HARDWARE_OR_PROVIDER_CALLS_BY_SCRIPT','Audit: source contains numerical simulation and local plot/write only',None),
      ('PASS','REGRESSION_TESTS','14 deterministic source tests initially passed in current sandbox',None),
      ('HOLD','POLARIZED_MAXWELL_MODEL','Scalar 1D toy is not a polarization-sensitive electromagnetic solver',None),
      ('NOT_RUN','LASER_LAB','No physical laser was operated or measured',None),
      ('NOT_RUN','INDEPENDENT_SURFACE_SAMPLE','No experimentally measured rough surface dataset was tested',None),
      ('NOT_RUN','INDEPENDENT_OBSERVER','No independent researcher reproduced the result',None),
      ('NOT_RUN','DMT_OBSERVER_LANE','No drug or altered-state study; no protocol for drug use',None),
      ('HOLD','EXTERNAL_ET_OR_GD_CAUSE','No evidence of external source, ET contact or G_d agency',None),
      ('HOLD','POLARIZATION_CHANNEL','No Stokes, Mueller, polarizer or full material model',None),
      ('NOT_RUN','COORBWARE_DEVICE','No CoOrbWare, desktop, webcam, CoAura, CoBar or X2 installation',None),
      ('HOLD','HUMAN_FIRST_USE_VALUE','No consenting independent reader measured comprehension or benefit',None),
      ('PASS','SOURCE_PRIOR_REUSE','Existing CoRenewal/CoOpticsGap/CoInterstice lineage identified rather than overwritten',None),
      ('PASS','BROWSER_INJECTED_DESKTOP_MOBILE','Chromium synthetic inline-media preview passed two viewport canaries, 0 remote requests, 0 page errors',None),
      ('HOLD','DIRECT_FILE_OPEN_BROWSER','file:// navigation blocked by container administrator; no native X2/Android browser result',None),
      ('PASS','CALIBRATED_GAIN_TOY','Evidence-proxy policy beat the strongest of two baselines in 12/12 seeded calibrated synthetic trials',None),
      ('FAIL','REVERSED_GAIN_TOY','Same policy lost to the stronger baseline in 12/12 seeded synthetic shifted-proxy trials',None),
      ('HOLD','REAL_GAIN_POLICY_VALUE','No real task, user, environmental energy, financial cost or external benefit measure',None),
      ('PASS','FINAL_TEST_SUITE','All 27 numerical and integrity tests passed in current sandbox before packaging',None)
    ]


def generate(m):
    prev='0'*64
    out=[]
    for i,(status,name,note,source) in enumerate(events(m),1):
        item={'schema':'CoCivium.CoAkimboInterstice.BenchmarkEvo.R0', 'seq':i,
              'observed_date':'2026-10-26','status':status,'test':name,'detail':note,
              'source_sha256':source,'prev_hash':prev}
        item['event_hash']=digest(item)
        prev=item['event_hash']
        out.append(item)
    return out,prev


def write(m):
    ev,head=generate(m)
    out=ROOT/'output'
    (out/'benchmark_evo.jsonl').write_text(''.join(json.dumps(e,sort_keys=True,ensure_ascii=True)+'\n' for e in ev),encoding='utf-8')
    (out/'HEAD.sha256').write_text(head+'\n',encoding='ascii')
    return head


def verify(path=None,head_path=None):
    path=path or ROOT/'output'/'benchmark_evo.jsonl'
    head_path=head_path or ROOT/'output'/'HEAD.sha256'
    prev='0'*64
    count=0
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        obj=json.loads(line,object_pairs_hook=unique_keys)
        count+=1
        if obj.get('seq')!=count or obj.get('prev_hash')!=prev:
            raise ValueError('BROKEN_CHAIN')
        payload={k:v for k,v in obj.items() if k!='event_hash'}
        if obj.get('event_hash')!=digest(payload):raise ValueError('BAD_EVENT_HASH')
        prev=obj['event_hash']
    if not count or prev!=Path(head_path).read_text(encoding='ascii').strip():
        raise ValueError('PINNED_HEAD_MISMATCH')
    return count

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--write',action='store_true')
    args=p.parse_args()
    if args.write:
        m=json.loads((ROOT/'output'/'measurement.json').read_text(encoding='utf-8'))
        print('NEW HEAD:',write(m))
    print('VERIFIED EVENTS:',verify())
