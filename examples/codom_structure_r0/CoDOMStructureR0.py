#!/usr/bin/env python3
"""CoDOM R0: offline structure-to-relation proof, no live capture or effects."""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SCHEMA='CoDOM.Snapshot.R0'
ROLES={'heading','button','link','status'}
BANNED={'script','style','template','noscript','iframe','object','embed','input','textarea','select'}
VOID={'input','img','br','hr','meta','link','source','area'}
SENSITIVE=('password','credential','secret','token','private','card','email','phone')
SCOPE={'capture':'EXPLICIT_LOCAL_SYNTHETIC','privacy':'PUBLIC_SYNTHETIC','authority':'READ_ONLY','external_effects':False}

def hash_obj(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()

def clean(s):
    return re.sub(r'\s+',' ',s).strip()[:90]

def ok_id(v):
    return isinstance(v,str) and re.fullmatch(r'[a-zA-Z0-9_.:-]{1,72}',v) is not None

def is_sensitive(v):
    return any(term in v.lower() for term in SENSITIVE)

class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.rows=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);blocked=any(n['blocked'] for n in self.stack) or tag in BANNED or 'hidden' in a or a.get('aria-hidden')=='true' or a.get('data-private')=='true'
        role=a.get('role') or {'h1':'heading','h2':'heading','h3':'heading','button':'button','a':'link','output':'status'}.get(tag)
        ident=a.get('data-coid');name=clean(a.get('aria-label') or '')
        blocked=blocked or (isinstance(ident,str) and is_sensitive(ident)) or is_sensitive(name)
        node={'tag':tag,'blocked':blocked,'track':not blocked and role in ROLES and ok_id(ident),'id':ident,'role':role,'name':name,'text':[]}
        if tag not in VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_data(self,data):
        if any(n['blocked'] for n in self.stack):return
        for n in self.stack:
            if n['track']:n['text'].append(data)
    def handle_endtag(self,tag):
        if not self.stack or self.stack[-1]['tag'] != tag:raise ValueError('HOLD_BAD_HTML_STRUCTURE')
        n=self.stack.pop()
        if n['track']:
            name=n['name'] or clean(' '.join(n['text']))
            if name and not is_sensitive(name):self.rows.append({'id':n['id'],'role':n['role'],'name':name})

def validate(src):
    if not isinstance(src,dict) or set(src)!={'schema','kind','work_id','source_id','observed_at','observer_scope','payload'} or src.get('schema')!=SCHEMA:
        raise ValueError('HOLD_SCHEMA')
    if src['kind'] not in {'BROWSER_HTML','NATIVE_ACCESSIBILITY'}:raise ValueError('HOLD_ADAPTER')
    if src['observer_scope']!=SCOPE:raise ValueError('HOLD_SCOPE')
    if not ok_id(src['work_id']) or not ok_id(src['source_id']):raise ValueError('HOLD_IDENTITY')
    if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',str(src['observed_at'])):raise ValueError('HOLD_OBSERVATION_TIME')
    if src['kind']=='BROWSER_HTML' and (not isinstance(src['payload'],str) or len(src['payload'])>50000):raise ValueError('HOLD_HTML_SIZE')
    if src['kind']=='NATIVE_ACCESSIBILITY' and (not isinstance(src['payload'],list) or len(src['payload'])>128):raise ValueError('HOLD_NATIVE_SIZE')

def mine(src):
    validate(src)
    if src['kind']=='BROWSER_HTML':
        parser=Extract();parser.feed(src['payload']);parser.close()
        if parser.stack:raise ValueError('HOLD_UNCLOSED_HTML')
        rows=parser.rows
    else:
        rows=[]
        for node in src['payload']:
            if not isinstance(node,dict) or set(node)-{'id','role','name','hidden','sensitive','value'}:raise ValueError('HOLD_NATIVE_FIELDS')
            if node.get('hidden') or node.get('sensitive') or not ok_id(node.get('id')) or node.get('role') not in ROLES:continue
            name=clean(str(node.get('name') or ''))
            if name and not is_sensitive(name):rows.append({'id':node['id'],'role':node['role'],'name':name})
    if len(rows)>64 or len({x['id'] for x in rows})!=len(rows):raise ValueError('HOLD_DUPLICATES_OR_OVERFLOW')
    rows=sorted(rows,key=lambda x:x['id'])
    return {'schema':'CoDOM.Projection.R0','work_id':src['work_id'],'source_id':src['source_id'],
            'observed_at':src['observed_at'],'adapter':src['kind'],'evidence':'SNAPSHOT_STRUCTURE_ONLY',
            'currentness':'UNKNOWN','authority':'READ_ONLY','relations':rows,'relations_sha256':hash_obj(rows),
            'effects':{'network':0,'devices':0,'messages':0,'credentials':0},'receiver_ack':'UNPROVEN'}

def delta(a,b):
    if a['work_id']!=b['work_id'] or a['source_id']!=b['source_id']:raise ValueError('HOLD_UNBOUND_DELTA')
    old={x['id']:x for x in a['relations']};new={x['id']:x for x in b['relations']}
    return {'changed':[k for k in sorted(old.keys()&new.keys()) if old[k]!=new[k]],
            'added':sorted(new.keys()-old.keys()),'not_observed':sorted(old.keys()-new.keys()),
            'not_observed_ne_absent':True,'receiver_ack':'UNPROVEN'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);opts=p.parse_args()
    raw=json.loads(opts.fixture.read_text());assert raw.get('schema')=='CoDOM.OfflineFixture.R0'
    p=[mine(x) for x in raw['snapshots']]
    print(json.dumps({'schema':'CoDOM.OfflineReport.R0','projections':p,'delta':delta(p[0],p[1]),
                      'cross_surface_semantics_equal':p[1]['relations_sha256']==p[2]['relations_sha256'],
                      'active_workers':0,'effects':0,'scope':'LOCAL_SYNTHETIC_ONLY',
                      'nonclaims':['NO_LIVE_DOM_OR_WINDOWS_CAPTURE','SNAPSHOT_NE_PAGE_TRUTH','NO_PROVIDER_ACCOUNT_ACCESS',
                                   'NO_X2_RUNTIME','PARITY_NE_EXTERNAL_RECEIVER_ACK','UNKNOWN_NE_ABSENT']},sort_keys=True,indent=2))
if __name__=='__main__':main()
