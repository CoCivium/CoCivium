#!/usr/bin/env python3
"""Real Chromium browser proof for the portable CoObject prodlet (synthetic files only).

Runs as in-memory HTML with a Python SHA-256 shim because this execution sandbox
blocks Chromium navigation and native WebCrypto on about:blank. No backend. Reopens an exported capsule
in an isolated browser context; not an end-user acceptance or X2 test.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright, expect

HERE = Path(__file__).resolve().parent
HTML_SOURCE = (HERE / 'index.html').read_text(encoding='utf-8')
MODE = os.environ.get('COOBJECT_BROWSER_MODE','shim')
ENGINE = os.environ.get('COOBJECT_BROWSER_ENGINE','chromium')

def open_page(page):
    if MODE == 'native':
        page.goto((HERE / 'index.html').resolve().as_uri())
        check(page.evaluate('window.isSecureContext && !!crypto.subtle'),'Native secure WebCrypto unavailable')
        return
    if MODE != 'shim':
        raise RuntimeError('Unknown browser mode: '+MODE)
    page.expose_function('__sha256_external',lambda values:hashlib.sha256(bytes(values)).hexdigest())
    page.evaluate("""() => {
      Object.defineProperty(window.crypto,'subtle',{configurable:true,value:{
        digest:async (_,bytes)=> {
          const h=await window.__sha256_external(Array.from(new Uint8Array(bytes)));
          return Uint8Array.from(h.match(/../g),x=>parseInt(x,16)).buffer;
        }
      }});
    }""")
    page.set_content(HTML_SOURCE)

CONTENT = b'The object remembers exactly what was observed.\n\x00\xffSynthetic only.\n'
HASH = hashlib.sha256(CONTENT).hexdigest()

def upload_bytes(page, control, name, content, mime='application/octet-stream'):
    page.locator(control).set_input_files({'name': name, 'mimeType': mime, 'buffer': content})

def check(condition, reason):
    if not condition:
        raise AssertionError(reason)

def state(page):
    return page.locator('#state').inner_text()

def wait_state(page, wanted):
    expect(page.locator('#state')).to_have_text(wanted, timeout=15000)

def run():
    results = []
    def passed(name):
        results.append(name)
        print('PASS', name)
    with sync_playwright() as p:
        if MODE == 'native' and ENGINE == 'firefox':
            browser = p.firefox.launch(headless=True)
        elif MODE == 'native' and ENGINE == 'chromium':
            browser = p.chromium.launch(headless=True, channel='chrome', args=['--no-sandbox'])
        elif MODE == 'shim' and ENGINE == 'chromium':
            browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        else:
            raise RuntimeError('Unsupported browser mode/engine combination')
        try:
            context = browser.new_context(accept_downloads=True, viewport={'width': 1100,'height': 850})
            page = context.new_page()
            net=[]; errors=[]
            page.on('request',lambda x:net.append(x.url) if not (MODE=='native' and x.url == (HERE/'index.html').resolve().as_uri()) else None)
            page.on('pageerror',lambda x:errors.append(str(x)))
            open_page(page)
            check(state(page)=='EMPTY','Initial state wrong')
            check(page.locator('#pack').is_disabled(),'Pack should start disabled')
            check(page.locator('#restore').is_disabled(),'Restore should start disabled')
            passed('initial fail-closed controls')

            upload_bytes(page,'#source','synthetic.bin',CONTENT)
            check(state(page)=='FILE_SELECTED','Not selected')
            page.locator('#pack').click()
            wait_state(page,'READY_LOCAL_TWO_COPIES')
            check(page.locator('#copies').inner_text()=='2 / 2','Invalid copy count')
            check(HASH in page.locator('#trace').inner_text(),'Wrong file SHA-256')
            passed('real browser file bytes packaged and SHA-256 verified')
            page.screenshot(path=str(HERE/'desktop_portable_qa.png'),full_page=True)

            with tempfile.TemporaryDirectory() as td:
                temp=Path(td)
                with page.expect_download() as d:
                    page.locator('#exportCapsule').click()
                cap=temp/'capsule.json';d.value.save_as(cap)
                raw=cap.read_bytes()
                document=json.loads(raw)
                check(document['manifest']['content_sha256']==HASH,'Export digest differs')
                check(document['manifest']['privacy']=='USER_CHOSEN_BROWSER_LOCAL','Privacy mismatch')
                check(document['manifest']['origin_authentication']=='NOT_VERIFIED','Authentication greenwash')
                check(document['manifest']['recovery_scope']=='SINGLE_JSON_SHARED_FAILURE_DOMAIN','Misrepresented redundancy')
                passed('self-contained portable capsule exported with strict nonclaims')

                # New context is a distinct session with no memory inherited.
                isolated=browser.new_context(accept_downloads=True, viewport={'width': 390,'height': 844}, is_mobile=True)
                receiver=isolated.new_page();receiver.on('request',lambda x:net.append(x.url) if not (MODE=='native' and x.url == (HERE/'index.html').resolve().as_uri()) else None);receiver.on('pageerror',lambda x:errors.append(str(x)))
                open_page(receiver)
                check(state(receiver)=='EMPTY','Clean receiver did not start blank')
                upload_bytes(receiver,'#capsuleFile','capsule.json',raw,'application/json')
                receiver.locator('#inspect').click()
                wait_state(receiver,'READY_LOCAL_TWO_COPIES')
                passed('independent browser-context reimport and exact digest inspection')
                receiver.screenshot(path=str(HERE/'mobile_portable_qa.png'),full_page=True)
                check(receiver.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Imported mobile content overflows')

                # Actual deliberate one-copy loss, then original byte restoration.
                receiver.locator('#simulateLoss').click()
                wait_state(receiver,'DEGRADED_ONE_COPY')
                check(receiver.locator('#copies').inner_text()=='1 / 2','Not 1/2')
                with receiver.expect_download() as d2:
                    receiver.locator('#restore').click()
                restored=temp/'restored.dat';d2.value.save_as(restored)
                check(restored.read_bytes()==CONTENT,'Restored bytes not equal')
                check(hashlib.sha256(restored.read_bytes()).hexdigest()==HASH,'Restored hash differs')
                passed('graceful degradation and exact restored bytes')

                # Still one copy, then deliberate total corruption.
                receiver.locator('#tamperAll').click()
                wait_state(receiver,'HELD_NO_VALID_BYTES')
                check(receiver.locator('#restore').is_disabled(),'Held source must disable restore')
                passed('both copies corrupt -> fail closed, no restore')

                # Separate imported capsules with untrusted metadata.
                for case,update in [
                    ('authority forgery',lambda c:c['manifest'].__setitem__('authority','RUN_SCRIPTS')),
                    ('independent storage forgery',lambda c:c['manifest'].__setitem__('recovery_scope','TWO_INDEPENDENT_SITES')),
                    ('origin forgery',lambda c:c['manifest'].__setitem__('origin_authentication','SIGNED_VERIFIED')),
                    ('unexpected field',lambda c:c.__setitem__('extra_actor','SEND')),
                ]:
                    mut=json.loads(raw);update(mut)
                    receiver.locator('#reset').click()
                    upload_bytes(receiver,'#capsuleFile','mut.json',json.dumps(mut).encode(),'application/json')
                    receiver.locator('#inspect').click()
                    wait_state(receiver,'HELD_INVALID_CAPSULE')
                    check(receiver.locator('#restore').is_disabled(),f'{case} allowed restore')
                    passed(case+' held')

                corrupt=json.loads(raw)
                corrupt['payload_a_b64']='AAAA'  # Wrong SHA, valid base64.
                receiver.locator('#reset').click()
                upload_bytes(receiver,'#capsuleFile','partial.json',json.dumps(corrupt).encode(),'application/json')
                receiver.locator('#inspect').click()
                wait_state(receiver,'DEGRADED_ONE_COPY')
                passed('corrupt A with valid B can still restore')

                both=json.loads(raw)
                both['payload_a_b64']='AAAA';both['payload_b_b64']='AAAA'
                receiver.locator('#reset').click()
                upload_bytes(receiver,'#capsuleFile','corrupt.json',json.dumps(both).encode(),'application/json')
                receiver.locator('#inspect').click()
                wait_state(receiver,'HELD_NO_VALID_BYTES')
                passed('two plausible but incorrect base64 payloads held')

                # Mobile layout, no horizontal overflow.
                receiver.locator('#reset').click()
                check(receiver.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile 390px horizontal overflow')
                passed('mobile 390px no horizontal overflow')
                isolated.close()

                # Strong direct-copy baseline: exact bytes, one click, smaller.
                with page.expect_download() as d3:
                    page.locator('#direct').click()
                direct=temp/'baseline.dat';d3.value.save_as(direct)
                check(direct.read_bytes()==CONTENT,'Direct copy baseline does not preserve file')
                check(len(raw)>len(CONTENT),'Capsule should honestly cost more bytes')
                passed('strong direct-copy baseline preserved and lower storage cost')

                # Empty input is valid, not implicit absence.
                page.locator('#reset').click()
                upload_bytes(page,'#source','empty.txt',b'')
                page.locator('#pack').click()
                wait_state(page,'READY_LOCAL_TWO_COPIES')
                check('0 bytes' in page.locator('#contentSize').inner_text(),'Empty != unknown')
                passed('empty content distinguished from missing evidence')

                # Security / privacy policy assertions.
                check(not net,f'Unexpected browser network requests: {net}')
                check(not errors,f'JavaScript page errors: {errors}')
                check('connect-src \'none\'' in (HERE/'index.html').read_text(),'No network CSP is missing')
                passed('zero requests, zero page errors, deny-network CSP')
                page.locator('#reset').click()
                check(state(page)=='EMPTY' and page.locator('#restore').is_disabled(),'Reset not clearing state')
                passed('reset drops object references and disables recovery')
                report={'schema':'CoCivium.CoObject.PortableBrowser.BrowserQA.R0',
                    'scope':(('CI_'+ENGINE.upper()+'_FILE_URL_NATIVE_WEBCRYPTO') if MODE=='native' else 'LOCAL_CHROMIUM_IN_MEMORY_HTML_WITH_EXTERNAL_PYTHON_SHA256_SHIM_NOT_NATIVE_WEBCRYPTO'),
                    'total':len(results),'passed':len(results),'tests':results,
                    'source_sha256':hashlib.sha256((HERE/'index.html').read_bytes()).hexdigest(),
                    'source_content_sha256':HASH,
                    'origin_authenticated':False,'receiver_accepted':False,
                    'x2_verified':False,'independent_storage':False,
                    'real_user_benefit':None,'network_requests':net,'js_page_errors':errors,
                    'visual_snapshots':['desktop_portable_qa.png','mobile_portable_qa.png'],
                    'baseline':{'simple_copy_bytes':len(CONTENT),'portable_capsule_bytes':len(raw)}}
                (HERE/'browser_qa.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
                print(json.dumps({k:report[k] for k in ('total','passed','baseline','network_requests')},sort_keys=True))
            context.close()
        finally:
            browser.close()

if __name__=='__main__':run()