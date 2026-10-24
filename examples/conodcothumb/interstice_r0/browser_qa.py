"""Optional isolated-browser QA for CoInput Interstice R0. Requires Playwright and Chromium."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
checks=[]
network=[]
errors=[]

def check(name,fn):
    try:
        fn()
        checks.append({'name':name,'status':'PASS'})
    except Exception as exc:
        checks.append({'name':name,'status':'FAIL','detail':str(exc)[:280]})

def ensure(cond, why):
    if not cond:
        raise AssertionError(why)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    html=(ROOT/'index.html').read_text('utf-8')
    for screen,width,height in [('desktop',1260,900),('mobile',390,844)]:
        page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
        page.on('request',lambda req:network.append(req.url) if req.url.startswith(('http:','https:')) else None)
        page.on('pageerror',lambda err:errors.append(str(err)))
        check(screen+'_extracted_html_load',lambda:page.set_content(html,wait_until='load'))
        check(screen+'_h1_exists',lambda:ensure('Between the gestures' in page.locator('h1').inner_text(),'missing heading'))
        check(screen+'_default_disarmed',lambda:ensure('Not observing' in page.locator('#activity').inner_text(),'not disarmed'))
        def pick():
            page.locator('[data-zone="relations"]').click()
            page.locator('[data-glyph="negate"]').click()
            ensure('Not observed does not mean logically false' in page.locator('#proposalBody').inner_text(),'inverse meaning missing')
            ensure(page.locator('#orbZone').text_content()=='Relations','zone not reflected')
        check(screen+'_zone_symbol_view',pick)
        def make_capsule():
            page.locator('#generate').click()
            c=json.loads(page.locator('#capsule').inner_text())
            ensure(c['authority']=='NONE' and c['outward_effects']==0 and c['raw_text_included'] is False,'unsafe capsule')
            ensure('coarse_intervals' not in c,'coarse counters included without opt in')
        check(screen+'_no_effect_capsule',make_capsule)
        def block_sensitive():
            page.locator('[data-zone="sensitive"]').click()
            page.locator('#generate').click()
            ensure(json.loads(page.locator('#capsule').inner_text())['state']=='HELD_SENSITIVE','sensitive not blocked')
            ensure(page.locator('#download').is_disabled(),'held download enabled')
        check(screen+'_sensitive_held',block_sensitive)
        def bounded_intervals():
            page.locator('[data-zone="writing"]').click()
            page.locator('#arm').check()
            page.locator('#sample').focus()
            page.keyboard.type('example',delay=65)
            page.wait_for_timeout(950)
            page.keyboard.type('x',delay=65)
            page.locator('#preview').click()
            ensure('A bounded pause occurred' in page.locator('#proposalBody').inner_text(),'derived pause is not offered')
            page.locator('#includeStats').check()
            page.locator('#generate').click()
            c=json.loads(page.locator('#capsule').inner_text())
            ensure(c['raw_text_included'] is False and c['raw_keys_included'] is False,'raw content included')
            ensure(sum(c['coarse_intervals'].values())>0,'no bounded interval buckets')
            ensure('example' not in json.dumps(c),'sample source exposed')
        check(screen+'_local_opt_in_intervals',bounded_intervals)
        def clear():
            page.locator('#clear').click()
            ensure(page.locator('#sample').input_value()=='','field not cleared')
            ensure(not page.locator('#arm').is_checked(),'not disarmed')
            ensure(page.locator('#short').inner_text()=='0','interval buckets not cleared')
            ensure(page.locator('#download').is_disabled(),'download not cleared')
        check(screen+'_clear',clear)
        def overflow():
            m=page.evaluate('({scroll:document.documentElement.scrollWidth,width:window.innerWidth})')
            ensure(m['scroll']<=m['width'],f"overflow: {m}")
        check(screen+'_no_horizontal_overflow',overflow)
        def focus():
            page.locator('#preview').focus()
            page.keyboard.press('Tab')
            result=page.locator('#clear').evaluate('(el)=>({focus:el.matches(":focus-visible"),outline:getComputedStyle(el).outlineStyle})')
            ensure(result['focus'] and result['outline']!='none',f'focus style {result}')
        check(screen+'_visible_keyboard_focus',focus)
        page.screenshot(path=str(ROOT/(screen+'.png')),full_page=True)
        page.close()
    browser.close()
check('no_outgoing_http_requests',lambda:ensure(not network,f'network: {network}'))
check('zero_runtime_js_errors',lambda:ensure(not errors,f'errors: {errors}'))
passed=sum(x['status']=='PASS' for x in checks)
record={'schema':'CoAll.CoInputInterstice.BrowserR0','status':'PASS' if passed==len(checks) else 'FAIL',
        'checks':checks,'passed':passed,'total':len(checks),'failed':len(checks)-passed,
        'surface':'EXTRACTED_HTML_IN_ISOLATED_CHROMIUM_DESKTOP_AND_MOBILE',
        'navigation_note':'Direct file:// navigation is blocked by current browser sandbox. Loaded HTML source via set_content; no native URL/installation acceptance inferred.',
        'network_requests':network,'page_errors':errors,
        'nonclaims':['BROWSER_TEST_NE_INDEPENDENT_HUMAN_FIRST_USE','NO_X2_NATIVE_RUNTIME','NO_PHYSICAL_THUMB_EVENT']}
with (ROOT/'browser_qa_receipt.json').open('x',encoding='utf-8') as f:
    json.dump(record,f,indent=2)
    f.write('\n')
print(json.dumps({k:record[k] for k in ['status','passed','failed','total','surface']}))
if passed<len(checks):
    for c in checks:
        if c['status']=='FAIL':print(c)
    raise SystemExit(2)
