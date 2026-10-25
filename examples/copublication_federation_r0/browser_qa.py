#!/usr/bin/env python3
"""Bounded off-network Chromium acceptance for the static federation UI."""
from pathlib import Path
import json
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
content=(ROOT/'index.html').read_text(encoding='utf-8')
results=[]
def check(ok,label):
    results.append({'name':label,'outcome':'PASS' if ok else 'FAIL'})
    if not ok:raise AssertionError(label)
with sync_playwright() as p:
    executable=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('chromium-browser')
    if not executable:
        candidate=Path(p.chromium.executable_path)
        if not candidate.is_file():
            raise RuntimeError('HELD_NO_LOCAL_CHROMIUM_OR_CHROME_EXECUTABLE')
        executable=str(candidate)
    browser=p.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height,label in [(1280,840,'desktop'),(390,844,'mobile')]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,reduced_motion='reduce')
        errors=[];network=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:network.append(request.url))
        page.set_content(content,wait_until='load')
        page.screenshot(path=str(ROOT/('preview_'+label+'.png')),full_page=True)
        # A real browser must expose both routes as links, never confuse the published post with the draft.
        shortcut=page.get_by_role('link',name='Compare a published article with the draft chapter')
        check(shortcut.count()==1 and shortcut.get_attribute('href')=='#edge-in-heading',label+'_first_screen_shortcut')
        cta_bounds=shortcut.bounding_box()
        check(bool(cta_bounds) and cta_bounds['y']>=0 and cta_bounds['y']<height and shortcut.is_visible(),label+'_shortcut_above_fold')
        bridge=page.locator('#edge-in-heading')
        check(bridge.count()==1 and bridge.is_visible(),label+'_reader_bridge_visible')
        live=page.get_by_role('link',name='Read the existing public article')
        draft=page.get_by_role('link',name='Read the pinned chapter draft')
        check(live.count()==1 and live.get_attribute('href')=='https://rickpublic.substack.com/p/does-ai-make-the-stock-market-obsolete',label+'_browser_bridge_live_link')
        check(draft.count()==1 and draft.get_attribute('href')=='https://github.com/CoCivium/CoCivium/blob/1487b330d35ddec03f32000e6846dd3b35ed774a/docs/books/great-refact-r0/01-your-product-is-still-here.md',label+'_browser_bridge_draft_link')
        check('not a published Substack article' in page.locator('#edge-in-heading').locator('xpath=..').inner_text(),label+'_draft_state_explained')
        check(all(x.get_attribute('target')=='_blank' and {'noopener','noreferrer'}.issubset(set((x.get_attribute('rel') or '').split())) for x in [live,draft]),label+'_outbound_link_isolation')
        bridge.scroll_into_view_if_needed()
        bounds=bridge.bounding_box()
        check(bool(bounds) and bounds['x']>=0 and bounds['x']+bounds['width']<=width+1,label+'_bridge_in_viewport')
        check(page.get_by_role('link',name='Read the existing public article').is_visible() and draft.is_visible(),label+'_bridge_links_render')
        check(page.locator('.route-btn').count()==6,label+'_six_routes')
        check('You were never supposed' in page.locator('#route-head').inner_text(),label+'_initial_view')
        check(page.locator('.claim').count()==6,label+'_same_claim_kernel')
        check(page.locator('#edition-note').inner_text().startswith('r0.2'),label+'_initial_current_edition')
        page.get_by_role('button',name='Developer').click()
        check('Compose one capability' in page.locator('#route-head').inner_text(),label+'_switch_reader')
        check(page.locator('.claim').count()==6,label+'_claims_preserved_after_switch')
        check(page.locator('.route-btn[aria-pressed="true"]').count()==1,label+'_selection_visible')
        page.locator('#edition-old').click()
        check(page.locator('#edition-note').inner_text().startswith('r0.1'),label+'_recover_predecessor')
        page.locator('#edition-current').click()
        check(page.locator('#edition-note').inner_text().startswith('r0.2'),label+'_recover_successor')
        page.locator('#decode').click()
        decoded=json.loads(page.locator('#descriptor-output').inner_text())
        check(len(decoded['axes'])==12,label+'_lazy_trillion_address')
        check(decoded['posts_created']==0 and decoded['workers_started']==0,label+'_zero_execution')
        page.locator('#descriptor-number').fill('bad')
        page.locator('#decode').click()
        check('HELD:' in page.locator('#descriptor-output').inner_text(),label+'_bad_descriptor_rejected')
        page.locator('#challenge-text').fill('How would we measure rollback success on a non-demo product?')
        page.locator('#prepare-challenge').click()
        challenge=json.loads(page.locator('#challenge-output').inner_text())
        check(challenge['state']=='UNSENT_LOCAL_PROPOSAL',label+'_local_challenge_only')
        check(challenge['external_send_count']==0,label+'_no_auto_send')
        check(challenge['source_blob']=='9202ab5a8d0bfef509922c8c047363ea7a346ce2',label+'_pinned_source')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),label+'_no_horizontal_overflow')
        check(not errors,label+'_zero_js_errors')
        check(not network,label+'_zero_http_requests')
        page.screenshot(path=str(ROOT/('qa_'+label+'.png')),full_page=True)
        page.close()
    browser.close()
report={'schema':'CoAll.PublicationFederation.BrowserQA.R0','method':'Chromium page.set_content exact generated source, not hosted URL or end-user acceptance','checks':results,'pass':sum(r['outcome']=='PASS' for r in results),'fail':sum(r['outcome']=='FAIL' for r in results),'public_network_requests':0,'private_source_ingestion':0,'nonclaims':['BROWSER_SMOKE_NE_HUMAN_COMPREHENSION','FILE_RENDER_NE_HOSTED_WEBSITE','SYNTHETIC_VERSION_NE_PUBLICATION_HISTORY','NO_SUBSTACK_POSTING']}
(ROOT/'browser_qa_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'pass':report['pass'],'fail':report['fail'],'method':report['method']},indent=2))
