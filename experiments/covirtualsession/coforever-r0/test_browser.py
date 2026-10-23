#!/usr/bin/env python3
"""Offline bounded browser smoke only, no external network permitted by page CSP."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parent
url=(root/'CoOrbWare_offline.html').resolve().as_uri()
checks={}
errors=[]
requests=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
    page=browser.new_page(viewport={'width':1140,'height':900},device_scale_factor=1)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda req:requests.append(req.url) if req.url.startswith(('https://','http://')) else None)
    page.goto(url,wait_until='domcontentloaded',timeout=8000)
    checks['TITLE']=page.title()=='CoOrbWare+ | Quiet Forever Field R0'
    checks['LOGICAL_SCALE_VISIBLE']='10²⁴' in page.locator('#option-count').inner_text()
    checks['WORKER_CAP_VISIBLE']=page.locator('#budget-count').inner_text()=='2'
    checks['LOCAL_COMPLETIONS_VISIBLE']=page.locator('#child-count').inner_text()=='4'
    checks['RAW_PRIVATE_STRING_ABSENT']='PRIVATE_NOT_FOR_DISPLAY' not in page.content()
    page.get_by_role('button',name='Working set').click()
    checks['PUBLIC_ONLY_WORKING_SET']=page.locator('#task-list li').count()==9
    checks['ACTIVE_BUTTON_SEMANTIC']=page.get_by_role('button',name='Working set').get_attribute('aria-pressed')=='true'
    page.get_by_role('button',name='Time / wake').click()
    checks['TIME_SHADOW_LABEL']=page.get_by_text('No persistent timer, daemon, or background automation').is_visible()
    page.get_by_role('button',name='Proof / limits').focus()
    page.keyboard.press('Enter')
    checks['KEYBOARD_ACCESS']=page.get_by_role('button',name='Proof / limits').get_attribute('aria-pressed')=='true'
    page.get_by_role('button',name='Glance').click()
    page.screenshot(path=str(root/'preview.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':780})
    checks['NARROW_VIEW_NO_HORIZONTAL_OVERFLOW']=page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2')
    page.screenshot(path=str(root/'preview_mobile.png'),full_page=True)
    checks['NO_PAGE_ERRORS']=not errors
    checks['NO_EXTERNAL_REQUESTS']=not requests
    browser.close()
assert all(checks.values()),json.dumps({'failures':[k for k,v in checks.items() if not v],'errors':errors,'requests':requests})
(root/'browser_smoke.json').write_text(json.dumps({'checks':checks,'count':len(checks),'failed':0,
  'pageerrors':errors,'external_requests':requests,'scope':'SYNTHETIC_OFFLINE_BROWSER_SMOKE_NOT_HUMAN_UX'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'requests':len(requests),'pageerrors':len(errors)}))