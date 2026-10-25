#!/usr/bin/env python3
"""Chromium manual QA on the exact generated HTML; not invoked by lean CI."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
RESULT=Path(__file__).resolve().parents[3] / 'browser_receipt.json'


def main():
    outcomes=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,width,height in [('desktop',1260,900),('mobile',390,820)]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            requests=[];errors=[]
            page.on('request',lambda req:requests.append(req.url) if req.url.startswith(('http:','https:')) else None)
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.emulate_media(reduced_motion='reduce')
            page.set_content((ROOT/'visual_prior_bridge.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
            def check(value,label): outcomes.append({'status':'PASS' if value else 'FAIL','label':name+':'+label})
            check(page.title()=='CoVisual source to CoLens | Map / Orb / Text','title')
            check('NO SOURCE IMAGE COPIED' in page.locator('.alert').inner_text(),'warning')
            check(page.locator('a[href^="https://commons.wikimedia.org/"]').count()==2,'two_source_links')
            check(page.locator('img').count()==0,'no_media_embed')
            check(page.locator('#storyboard .scene').count()==6,'six_step_storyboard')
            check(page.locator('script#manifest').count()==1,'one_machine_twin')
            check('source-linked' in page.locator('#sourcebound').text_content().lower(),'sourcebound_receipt')
            check('NONE' in page.locator('#details').inner_text(),'no_authority')
            check(page.locator('body').evaluate('(e)=>e.scrollWidth<=window.innerWidth+1'),'no_horizontal_overflow')
            first='Text' if width<620 else 'Map'
            check(page.locator('[data-view="'+first+'"]').get_attribute('aria-pressed')=='true','correct_default')
            page.locator('[data-view="Orb"]').click()
            check(page.locator('#projection-title').inner_text().startswith('Orb'),'orb_switch')
            check(page.locator('#projection .item').count()==9,'orb_nine_nodes')
            page.locator('[data-view="Text"]').click()
            check(page.locator('#projection-title').inner_text().startswith('Text'),'text_switch')
            check(page.locator('#projection .item').count()==9,'text_nine_nodes')
            page.locator('[data-lens="Science"]').click()
            check('lens: Science' in page.locator('#status').inner_text(),'lens_switch')
            check(page.locator('#projection .item').count()==3,'science_theme_plus_two')
            page.locator('[data-lens="All"]').click()
            page.locator('[data-view="Map"]').click()
            check(page.locator('svg[role="img"] g.node').count()==9,'map_nine_nodes')
            page.locator('svg g.node[aria-label^="Original source"]').focus()
            page.keyboard.press('Enter')
            check('EXTERNAL_METADATA_POINTER' in page.locator('#details').inner_text(),'keyboard_inspection')
            check('NO_IMAGE_BYTES' in page.locator('#details').inner_text(),'source_status_preserved')
            check(not errors,'no_javascript_errors')
            check(not requests,'no_scripted_network')
            page.screenshot(path=str(RESULT.parent/(name+'_visual_bridge.png')),full_page=True)
            page.close()
        browser.close()
    RESULT.write_text(json.dumps({'schema':'CoCivium.CoVisualBridge.ChromiumReceipt.R1',
           'source':'examples/colensmedia/visual_prior_bridge.html','results':outcomes,
           'pass':sum(x['status']=='PASS' for x in outcomes),
           'fail':sum(x['status']=='FAIL' for x in outcomes),
           'nonclaims':['EXTRACTED_HTML_NE_DIRECT_FILE_NAVIGATION','NO_INDEPENDENT_RECEIVER',
           'NO_EXTERNAL_SOURCE_ARTWORK','NO_NATIVE_DEVICE']},indent=2)+'\n',encoding='utf-8')
    print('CHROMIUM',sum(x['status']=='PASS' for x in outcomes),'PASS',sum(x['status']=='FAIL' for x in outcomes),'FAIL')
    for x in outcomes:
        if x['status']=='FAIL': print('FAIL',x['label'])
    if any(x['status']=='FAIL' for x in outcomes): raise SystemExit(1)

if __name__=='__main__': main()
