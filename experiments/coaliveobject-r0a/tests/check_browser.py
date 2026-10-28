"""Optional real Chromium offline UI canary. Requires Playwright + Chromium."""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
uri=(root/'CoAliveObject_Viewer.html').resolve().as_uri()
assert uri.startswith('file://')
errors=[];calls=[];checks=0
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for label,viewport in [('desktop',{'width':1280,'height':900}),('mobile',{'width':390,'height':850})]:
        p=browser.new_page(viewport=viewport)
        p.on('pageerror',lambda e: errors.append(str(e)))
        p.on('request',lambda req: calls.append(req.url) if req.url.startswith(('http://','https://')) else None)
        # Direct file:// is blocked by this runner; inject exact bytes instead.
        p.set_content((root/'CoAliveObject_Viewer.html').read_text(), wait_until='load')
        assert 'CoAliveObject+' in p.title();checks+=1
        assert p.locator('#frames button').count()==6;checks+=1
        assert p.locator('#objects button').count()==3;checks+=1
        assert p.locator('#work-count').inner_text()=='0';checks+=1
        p.get_by_role('button',name='Tick 4').click()
        assert p.locator('#work-count').inner_text()=='4';checks+=1
        assert p.locator('#effects-count').inner_text()=='0';checks+=1
        p.get_by_role('button',name='spiff').click()
        assert 'spiff' in p.locator('#obj-id').inner_text();checks+=1
        p.get_by_role('button',name='Tick 7').click()
        assert 'HOLD_SOURCE_MISMATCH' in p.locator('#pulse-detail').inner_text();checks+=1
        assert p.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 3');checks+=1
        # accessibility: button actions keyboard-operable by default
        p.locator('#frames button').first.focus();p.keyboard.press('Enter')
        assert p.locator('#work-count').inner_text()=='0';checks+=1
        p.screenshot(path=str(root/f'CoAliveObject_{label}.png'),full_page=True)
        p.close()
    browser.close()
assert not errors, errors
assert not calls, calls
print(f'PASS {checks} Chromium desktop/mobile checks; 0 external HTTP(S) requests; 0 JS errors')

report={'schema':'CoAliveObjectBrowserCanary/R0a','observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
'view_source_sha256':hashlib.sha256((root/'CoAliveObject_Viewer.html').read_bytes()).hexdigest(),
'checked':checks,'passed':checks,'external_requests':len(calls),'js_errors':len(errors),
'direct_file_navigation':'NOT_RUN_BLOCKED_BY_ADMINISTRATOR',
'coverage':'DESKTOP_AND_MOBILE_CHROMIUM_INJECTED_CONTENT_ONLY',
'nonclaims':['NOT_X2_OR_MAC','NOT_FILE_DOUBLE_CLICK','NOT_NATIVE_HEARTBEAT','NOT_REMOTE_RECEIVER_ACK']}
(root/'output/browser_check.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
