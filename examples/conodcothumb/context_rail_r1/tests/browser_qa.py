#!/usr/bin/env python3
"""Headless browser canary for offline HTML, no OS input hook or external requests."""
import hashlib,json,pathlib,sys,time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent
checks=[]
def check(name, condition):
    checks.append({'id':name,'status':'PASS' if condition else 'FAIL'})
    if not condition: print('FAIL',name)

def view(page,mode):
    page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='domcontentloaded',timeout=20000)
    page.wait_for_selector('#count')
    check(mode+'_header',page.locator('h1').inner_text().startswith('One gesture'))
    check(mode+'_source_options',page.locator('#context option').count()==15)
    check(mode+'_glyph_count',page.locator('#glyphRail .chip').count()==20)
    check(mode+'_count_millions','2,313,360' in page.locator('#count').inner_text())
    check(mode+'_no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
    check(mode+'_download_disabled_by_default',page.locator('#download').is_disabled())
    page.locator('#preview').click()
    check(mode+'_visible_preview',page.locator('#state').inner_text()=='PROPOSED_ONLY')
    check(mode+'_default_what_else', 'Generate alternative branches' in page.locator('#actions').inner_text())
    check(mode+'_one_primary_option',page.locator('#actions li').count()==1)
    page.locator('#more').click()
    check(mode+'_bounded_many_options',1 < page.locator('#actions li').count() <= 7)
    page.select_option('#gesture','NATIVE_MIDDLE')
    page.locator('#preview').click()
    check(mode+'_native_middle_pass_through',page.locator('#state').inner_text()=='PASS_THROUGH_NATIVE')
    check(mode+'_native_no_options',page.locator('#actions li').count()==0)
    page.select_option('#gesture','EXPLICIT_RING')
    page.select_option('#privacy','SENSITIVE')
    page.locator('#preview').click()
    check(mode+'_privacy_block',page.locator('#state').inner_text()=='HELD_PRIVACY')
    check(mode+'_privacy_export_disabled',page.locator('#download').is_disabled())
    page.select_option('#privacy','PUBLIC')
    page.select_option('#context','MEDIA')
    page.locator('#more').click()
    check(mode+'_media_needs_selection','Explicit file/media selection' in page.locator('#explanation').inner_text())
    page.locator('#fixture').check()
    page.locator('#more').click()
    check(mode+'_synthetic_media',page.locator('#state').inner_text()=='PROPOSED_ONLY')
    page.select_option('#context','RESEARCH')
    page.select_option('#lens','ET_HYPOTHESIS')
    page.locator('#preview').click()
    check(mode+'_et_scoped','Separate story from empirical claim' in page.locator('#actions').inner_text())
    page.select_option('#lens','PRACTICAL')
    page.select_option('#question','AT_RECEIVER')
    page.locator('#preview').click()
    check(mode+'_at_not_send','Check sender and receiver authority' in page.locator('#actions').inner_text())
    page.select_option('#question','WHAT_ELSE')
    page.select_option('#privacy','PRIVATE_LOCAL')
    page.select_option('#context','FILE')
    page.locator('#preview').click()
    check(mode+'_private_preview',page.locator('#state').inner_text()=='PROPOSED_ONLY')
    with page.expect_download(timeout=10000) as e:
        page.locator('#download').click()
    download=e.value
    data=json.loads(pathlib.Path(download.path()).read_text())
    check(mode+'_private_reference_redacted',data['source_ref'] is None)
    check(mode+'_download_has_zero_effect',data['outbound_effects']==0 and data['effects']['send']==0 and data['receiver_ack'] is False)
    page.locator('#reset').click()
    check(mode+'_reset_erases_preview',page.locator('#state').inner_text()=='NOT RUN')
    check(mode+'_reset_disables_export',page.locator('#download').is_disabled())
    return page

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking'])
        contexts=[('desktop',{'width':1280,'height':850}),('mobile',{'width':390,'height':844})]
        for mode,viewport in contexts:
            ctx=browser.new_context(viewport=viewport,accept_downloads=True,reduced_motion='reduce')
            requests=[];errors=[]
            page=ctx.new_page()
            page.on('request',lambda req:requests.append(req.url) if not req.url.startswith('file:') else None)
            page.on('pageerror',lambda err:errors.append(str(err)))
            try:
                page=view(page,mode)
                check(mode+'_no_external_requests',not requests)
                check(mode+'_no_js_errors',not errors)
                page.locator('#fixture').uncheck()
                page.select_option('#privacy','PUBLIC')
                page.select_option('#context','RESEARCH')
                page.select_option('#question','WHAT_ELSE')
                page.locator('#preview').click()
                page.screenshot(path=str(ROOT/(mode+'.png')),full_page=True)
            except Exception as e:
                checks.append({'id':mode+'_browser_exception','status':'FAIL','error':str(e)})
                print('ERROR',mode,str(e))
            finally:ctx.close()
        browser.close()
    passed=sum(x['status']=='PASS' for x in checks)
    out={'schema':'CoAll.CoContextRail.BrowserQA.R1','state':'PASS' if passed==len(checks) else 'FAIL','pass':passed,'fail':len(checks)-passed,'total':len(checks),
      'html_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),
      'environment':'Chromium in isolated container, extracted offline HTML injected into page, direct file:// blocked by browser sandbox, no real OS input',
      'checks':checks,'nonclaims':['BROWSER_PASS_NE_X2_DEVICE_MAPPING','NO_INDEPENDENT_HUMAN_ACCEPTANCE','NO_RECEIVER_ACK']}
    dest=ROOT/'browser_receipt.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({'state':out['state'],'pass':passed,'fail':out['fail'],'total':len(checks),'html_sha256':out['html_sha256']}))
    if out['fail']:sys.exit(2)
if __name__=='__main__':main()
