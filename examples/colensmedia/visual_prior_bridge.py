#!/usr/bin/env python3
"""CoVisualFinder source record -> one CoLens Map/Orb/Text render, no media copy.

This adapter is intentionally read-only except when emitting its two exact,
self-contained local derivative artifacts.  No browser scraping or provider APIs.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REGISTRY = REPO / 'examples' / 'covisual_finder_r1' / 'sources.json'
TEMPLATE = HERE / 'template.html'
MANIFEST_OUT = HERE / 'visual_prior_bridge.json'
HTML_OUT = HERE / 'visual_prior_bridge.html'
TARGET_ID = 'visual-external-commons-linkgraph-r1'
SCHEMA = 'CoCivium.CoVisual.SourceLinkedCoLensBridge.R1'
STATUS = 'INSPIRES_CANDIDATE__NO_DERIVATIVE_OR_SEND'
RIGHTS = 'LICENSE_IDENTIFIED_CONDITIONS_REMAIN'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256(value).hexdigest()


def assert_registry(reg):
    if reg.get('schema') != 'CoCivium.CoVisual.ExternalInspiration.R1':
        raise ValueError('registry schema mismatch')
    rows = reg.get('public_donors', [])
    p = reg.get('policy', {})
    if not (1 <= len(rows) <= 4) or not isinstance(rows, list):
        raise ValueError('bounded sample required')
    if p.get('route_mode') != 'INTERNAL_PROPOSED_READONLY_ROLES_NO_SEND' or p.get('media_bytes_permitted') is not False:
        raise ValueError('forbidden route or media source copy')
    if p.get('license_qualified_for_derivative') is not False:
        raise ValueError('unqualified license promotion')
    if any(reg.get('effects', {}).values()):
        raise ValueError('unexpected upstream effect')
    chosen = [row for row in rows if row.get('id') == TARGET_ID]
    if len(chosen) != 1:
        raise ValueError('exactly one source identity required')
    row = chosen[0]
    required = ['id','title','source_page','origin','source_type','rights_state',
                'stated_license','rights_evidence_page','credit','motif','accessible_twin',
                'inverse_challenge','next_test','epistemic_class','consumers','selected_reuse']
    for field in required:
        if not isinstance(row.get(field), str) and field != 'consumers':
            raise ValueError('missing or invalid: '+field)
        if field != 'consumers' and not row[field].strip():
            raise ValueError('empty: '+field)
    if row['rights_state'] != RIGHTS or row.get('noendorsement') is not True:
        raise ValueError('rights / endorsement gate')
    if row['selected_reuse'] != 'MOTIF_ONLY_LINK_BACK_TO_SOURCE':
        raise ValueError('image reuse / derivative gate')
    if row['consumers'] != ['CoMap','CoTurtle','CoA11y']:
        raise ValueError('role gate changed')
    if not row['inverse_challenge'].endswith('?'):
        raise ValueError('unqualified inverse question')
    u = urlparse(row['source_page'])
    if (u.scheme, u.hostname) != ('https','commons.wikimedia.org') or u.username or u.password or u.fragment:
        raise ValueError('bad original source URL')
    if row['rights_evidence_page'] != row['source_page']:
        raise ValueError('rights pointer mismatch')
    return row


def projection(reg):
    source = assert_registry(reg)
    digest = sha(canonical(source).encode('utf-8'))
    nodes = [
        {'id':'theme','label':'Visual question','kind':'DESIGN_CANDIDATE_NOT_EVIDENCE','lens':'Story',
         'summary':'Can a licensed historical diagram inspire an original, useful and evidence-bound interface?'},
        {'id':'source','label':'Original source','kind':'EXTERNAL_METADATA_POINTER_NOT_MEDIA','lens':'Systems',
         'summary':source['title']+' | '+source['source_page']+' | source-record SHA-256 '+digest},
        {'id':'motif','label':'Directed edges','kind':'DESIGN_INSPIRATION_ONLY','lens':'Systems',
         'summary':source['motif']+'; accessible description: '+source['accessible_twin']},
        {'id':'inverse','label':'Inverse question','kind':'COINVERSION_QUESTION_ONLY','lens':'Science',
         'summary':source['inverse_challenge']},
        {'id':'unknown','label':'Unknown evidence','kind':'UNKNOWN_NOT_FALSE_AND_NOT_TRUE','lens':'Science',
         'summary':'Visual arrows do not establish reciprocal edges or source-independent causation. No source image bytes were checked.'},
        {'id':'rights','label':'Rights and credit','kind':'RIGHTS_CONDITIONAL_NOT_APPROVAL','lens':'Systems',
         'summary':source['credit']+' | '+source['stated_license']+' | '+source['rights_state']+' | no derivative authorized here.'},
        {'id':'map','label':'CoMap' ,'kind':'PROJECTION_OF_THIS_WORK_OBJECT','lens':'Systems',
         'summary':'Typed relations are between this source pointer, conceptual motif, inverse question and rights gate; not a claimed reproduction of the source diagram.'},
        {'id':'orb','label':'CoOrb' ,'kind':'PROJECTION_OF_THIS_WORK_OBJECT','lens':'Story',
         'summary':'Compact focus on the selected source with one useful proposed test and explicit HELD reuse gate.'},
        {'id':'text','label':'Text twin','kind':'EQUIVALENT_TEXT_PROJECTION','lens':'Story',
         'summary':source['accessible_twin']+' | Next test: '+source['next_test']}
    ]
    links = [
        ('theme','source','SELECTS_EXTERNAL_SOURCE','LINK_ONLY'),
        ('source','motif','INSPIRES_CANDIDATE_MOTIF','PROPOSED'),
        ('source','rights','REQUIRES_ITEM_SPECIFIC_RIGHTS','REQUIRED_HELD'),
        ('motif','inverse','HAS_COUNTERQUESTION_NOT_FACT','PROPOSED'),
        ('inverse','unknown','EXPOSES_UNVERIFIED_REVERSE','UNKNOWN'),
        ('motif','map','MAY_RENDER_AS_TYPED_MAP','PROPOSED'),
        ('motif','orb','MAY_RENDER_AS_FOCUS','PROPOSED'),
        ('motif','text','HAS_ACCESSIBLE_DESCRIPTION','PROPOSED')
    ]
    relations = [dict(zip(['from','to','type','status'], x)) for x in links]
    frames = [
        ('01','Select one public source pointer; do not copy its image','SOURCE_POINTER'),
        ('02','Show the source credit and still-open rights question','RIGHTS_GATE'),
        ('03','Extract a motif without inheriting unsupported facts','INSPIRATION'),
        ('04','Ask whether an apparent inverse is justified','COINVERSION'),
        ('05','Switch CoMap, CoOrb and Text over the same work ID','PROJECTION_PARITY'),
        ('06','Hold release until a real reader verifies useful meaning','RECEIVER_GATE')
    ]
    out={
        'schema':SCHEMA,'work_id':'coal.covisual.commons-source-graph.r1',
        'version':'R1','date':reg.get('observed_date','2026-10-25'),
        'state':'PUBLIC_SAFE_METADATA_PROJECTION__NOT_IMAGE_BYTES__NOT_RECEIVER_ACCEPTED',
        'authority':'NONE','views':['Map','Orb','Text'],'lenses':['All','Story','Science','Systems'],
        'source_provenance':{
            'source_status':'EXTERNAL_SOURCE_PAGE_METADATA_ONLY__NO_IMAGE_BYTES',
            'named_theme':'One externally linked visual source informs an original diagram design',
            'source_page':source['source_page'],'source_record_sha256':digest,
            'image_sha256':None,'image_bytes_verified':False,'private_material_included':False,
            'credit':source['credit'],'rights_status':source['rights_state'],
            'stated_license':source['stated_license'],'legal_governance_status':'NONE',
            'image_derivative_permission':'NOT_GRANTED_BY_THIS_ADAPTER'
        },
        'public_donors':[],
        'nodes':nodes,'relations':relations,
        'storyboard':[{'frame':n,'caption':cap,'kind':kind,'node_ids':['theme']} for n,cap,kind in frames],
        'evolution':{'auto_rewrite':False,'auto_public_media':False,'auto_enable_device_io':False,
                     'new_version_trigger':['SOURCE_RECORD_CHANGE','REVIEWER_RECEIPT','ACCESSIBILITY_DEFECT','RIGHTS_EVIDENCE_CHANGE'],
                     'no_change':'QUIESCE'},
        'privacy':{'raw_private_source':'NOT_EMBEDDED','external_network':False,'tracking':False,'clipboard_read':False},
        'nonclaims':['SOURCE_PAGE_NE_IMAGE_BYTES','MOTIF_NE_DERIVATIVE_LICENSE',
            'INVERSE_QUESTION_NE_REVERSE_FACT','THREE_VIEWS_NE_INDEPENDENT_RECEIVER',
            'DISPLAYED_NODES_NE_ACTUAL_SOURCE_DIAGRAM','VISUAL_STYLE_NE_CAUSATION',
            'PASS_TEST_NE_USER_ACCEPTANCE','NO_EXTERNAL_BROADCAST','NO_DEVICE_CONTROL'],
        'bridge':{'id':source['id'],'source_type':source['source_type'],
                  'inspiration_status':STATUS,
                  'visible_source_record_sha256':digest,
                  'title':source['title'],'source_page':source['source_page'],
                  'rights_evidence_page':source['rights_evidence_page'],
                  'selected_reuse':'MOTIF_ONLY_LINK_BACK_TO_SOURCE',
                  'next_test':source['next_test'],'inverse_challenge':source['inverse_challenge'],
                  'projection_loss':['Original image pixels absent','Original directional edges not independently verified',
                                     'No spatial coordinates or physical metrics transferred'],
                  'evidence_state':'PUBLIC_SOURCE_METADATA_ONLY__NO_ORIGINAL_IMAGE_INSPECTION',
                  'receiver_ack':False}
    }
    return out


def render(manifest, source, template):
    replacements={
       '<title>CoLens / CoOrb / CoMap | Living media R0</title>':
         '<title>CoVisual source to CoLens | Map / Orb / Text</title>',
       '<div class="alert">THEME-ONLY PROTOTYPE | NOT AN AUTHENTICATED DECLARATION OR PRODUCED VIDEO</div>':
         '<div class="alert">SOURCE-PAGE METADATA | NO SOURCE IMAGE COPIED | NO REUSE LICENCE GRANTED</div>',
       '<h1>One relationship, many honest lenses</h1>':
         '<h1>One visual inspiration, three source-bound views</h1>',
       '<p>CoLens+ / CoOrb+ / CoMap+ candidate. Explore a <strong>Synthkind independence theme</strong> without converting philosophical, scientific, operational and aesthetic links into claims of causation.</p>':
         '<p>CoLens+ / CoOrb+ / CoMap+ bridge. One publicly linked historical diagram inspires an <strong>original, proposed</strong> relation map, Orb focus and accessible Text. This is not the original artwork.</p>',
       '<p class="small">Public-safe synthetic graph. Offline, no tracking, no network, no credentials, no device input hooks and no external effects.</p>':
         '<p class="small">Original: <a rel="noopener noreferrer" target="_blank" href="'+html.escape(source['source_page'],quote=True)+'">'+html.escape(source['title'])+'</a>. Source page and rights conditions require separate review. Offline page, no scripted network, no third-party media bytes, no device effects.</p>',
       '<h2>Proposed six-beat media storyboard, not rendered video</h2>':
         '<h2>Six-step source-to-design storyboard, not a produced film</h2>'
    }
    for old,new in replacements.items():
        if template.count(old)!=1: raise ValueError('upstream CoLens template drift: '+old[:60])
        template=template.replace(old,new)
    a=template.index('<details class="panel"><summary>Sources, limits and next independent proof</summary>')
    b=template.index('</details>',a)+len('</details>')
    details='''<details class="panel"><summary>Original source, credits, projection loss, and next proof</summary>
<p id="sourcebound">One identity through Map, Orb and Text. This is a source-linked design proposal, not the original public diagram or a claim that its arrows are facts.</p>
<p>Original source page: <a rel="noopener noreferrer" target="_blank" href="%s">%s</a>. Source credit: %s.</p>
<p>Rights: %s; %s. Attribution and derivative permission must be checked separately. The original image was not copied.</p>
<p>Inverse question: %s. <strong>Not an observed reverse edge.</strong></p>
<p>Next acceptance: %s No CoOrbWare device runtime, public media release, private screenshot redistribution or recipient readproof is claimed.</p></details>'''%tuple(html.escape(x,quote=True) for x in [source['source_page'],source['title'],source['credit'],source['rights_state'],source['stated_license'],source['inverse_challenge'],source['next_test']])
    template=template[:a]+details+template[b:]
    if template.count('</style>') != 1: raise ValueError('upstream stylesheet drift')
    template=template.replace('</style>', 'a { color: #a9dbff; } a:focus-visible { outline: 3px solid #fbd17f; outline-offset: 3px; } .panel,#projection,.grid { min-width:0; } .dl dd { overflow-wrap:anywhere; word-break:break-word; } @media(max-width:760px){ .grid { grid-template-columns:minmax(0,1fr); } }\n</style>')
    old_field='data.source_provenance.primary_declaration_text'
    if template.count(old_field)!=1: raise ValueError('source status field template drift')
    template=template.replace(old_field,'data.source_provenance.source_status')
    if template.count('__MANIFEST_JSON__')!=1: raise ValueError('lost manifest slot')
    serialized=json.dumps(manifest,sort_keys=True,separators=(',', ':'),ensure_ascii=True)
    serialized=serialized.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    result=template.replace('__MANIFEST_JSON__',serialized+'\n')
    if 'Synthkind' in result or 'not been located' in result.lower():
        raise ValueError('stale prior theme text leaked to new source projection')
    return result


def build(registry=REGISTRY, template=TEMPLATE):
    data=json.loads(Path(registry).read_text(encoding='utf-8'))
    source=assert_registry(data)
    twin=projection(data)
    page=render(twin,source,Path(template).read_text(encoding='utf-8'))
    manifest_bytes=(json.dumps(twin,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    html_bytes=page.encode('utf-8')
    return twin, manifest_bytes, html_bytes


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--check',action='store_true')
    p.add_argument('--registry',type=Path,default=REGISTRY)
    p.add_argument('--template',type=Path,default=TEMPLATE)
    p.add_argument('--manifest-out',type=Path,default=MANIFEST_OUT)
    p.add_argument('--html-out',type=Path,default=HTML_OUT)
    args=p.parse_args()
    _obj,manifest,page=build(args.registry,args.template)
    outputs=[(args.manifest_out,manifest),(args.html_out,page)]
    for path,content in outputs:
        if args.check:
            if not path.exists() or path.read_bytes()!=content:
                raise SystemExit('FAIL: output drift or missing '+str(path))
            print('PASS EXACT',path.name,sha(content))
        else:
            path.write_bytes(content)
            print('WROTE',path.name,sha(content))

if __name__=='__main__': main()
