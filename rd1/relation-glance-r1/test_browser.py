"""Optional real-browser acceptance smoke for offline demo."""
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).parent
url = (root / 'index.html').as_uri()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--disable-background-networking'])
    page=browser.new_page(viewport={'width':1440,'height':900}, device_scale_factor=1)
    errors=[]
    requests=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.set_content((root/'index.html').read_text(encoding='utf-8'), wait_until='domcontentloaded',timeout=12000)
    assert page.locator('#edges .edge').count()==5, page.locator('#edges .edge').count()
    assert page.locator('#nodes .node').count()>=5
    assert page.locator('#visibleCount').inner_text().startswith('5 shown')
    assert 'E10' not in page.locator('#edges').inner_html()
    page.get_by_role('button',name='Map',exact=True).click()
    assert page.locator('#edges .edge').count()==8, page.locator('#edges .edge').count()
    assert 'E10' not in page.locator('#edges').inner_html()
    page.locator('#period').evaluate("el=>{el.value='2';el.dispatchEvent(new Event('input',{bubbles:true}))}")
    page.locator('#explore').check()
    assert page.locator('#edges .edge').count()==11, page.locator('#edges .edge').count()
    assert page.locator('#edges .predicted').count()==1
    assert 'E10' not in page.locator('#edges').inner_html()
    page.get_by_role('button',name='Trails',exact=True).click()
    assert page.locator('#edges .edge').count()==5
    page.get_by_role('button',name='Glance',exact=True).click()
    page.locator('#period').evaluate("el=>{el.value='1';el.dispatchEvent(new Event('input',{bubbles:true}))}")
    page.locator('#explore').uncheck()
    page.locator('#forwardInput').fill('CoM')
    assert 'CoMap+' in page.locator('#forwardOutput').inner_text()
    page.locator('#reviewCandidate').click()
    assert 'REVIEWED_LOCAL_ONLY' in page.locator('#forwardReceipt').inner_text()
    page.locator('#forwardInput').fill('CoT')
    assert 'RAW_CHANGED__NOT_ACK' in page.locator('#forwardReceipt').inner_text()
    page.locator('#forwardInput').fill('CoM extra')
    page.locator('#forwardInput').evaluate("el=>{el.setSelectionRange(3,3);el.dispatchEvent(new Event('keyup',{bubbles:true}))}")
    assert 'CoMap+' in page.locator('#forwardOutput').inner_text()
    page.locator('#reviseCandidate').click()
    assert 'REWISED_AND_CLEARED' in page.locator('#forwardReceipt').inner_text()
    page.locator('#evoAction').click()
    assert page.get_by_role('button',name='Map',exact=True).get_attribute('aria-pressed')=='true'
    page.get_by_role('button',name='Glance',exact=True).click()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2'), 'Mobile overflow'
    page.set_viewport_size({'width':1440,'height':900})
    page.set_content((root/'index.html').read_text(encoding='utf-8'), wait_until='domcontentloaded')
    page.screenshot(path=str(root/'preview.png'), full_page=True)
    assert not errors, errors
    assert not [r for r in requests if not r.startswith('file://')], requests
    print('BROWSER_SMOKE_PASS: default_glance=5 map=8 optional_full=11 trails=5 private_excluded=YES predicted_opt_in=YES forward_preview_review_rewise=YES pageerrors=0')
    print('SCREENSHOT:',root/'preview.png')
    browser.close()