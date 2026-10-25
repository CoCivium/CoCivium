"""Local browser interaction checks; extracts no external source media."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HERE=Path(__file__).resolve().parents[1]

async def run():
    results=[]
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,viewport in [('desktop',{'width':1250,'height':880}),('mobile',{'width':390,'height':800})]:
            page=await browser.new_page(viewport=viewport,device_scale_factor=1)
            requests=[];errors=[]
            page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('https:','http:')) else None)
            page.on('pageerror',lambda e:errors.append(str(e)))
            await page.set_content((HERE/'index.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
            async def check(condition,label): results.append((bool(condition),name+':'+label))
            await check(await page.title() == 'CoVisual+ external inspiration | bounded sample','title')
            await check(await page.locator('article.source').count()==4,'sources')
            await check(await page.locator('a[target="_blank"]').count()==4,'manual_source_links')
            await check(await page.locator('button[aria-pressed="true"]').count()==1,'one_active_lens')
            await check(await page.locator('[data-view="motif"]:visible').count()==4,'default_motif_visible')
            await page.get_by_role('button',name='¬ Inverse').click()
            await check(await page.locator('[data-view="inverse"]:visible').count()==4,'inverse_visible')
            await check(await page.locator('[data-view="motif"]:visible').count()==0,'motif_hidden')
            await page.get_by_role('button',name='© Rights').click()
            await check(await page.locator('[data-view="rights"]:visible').count()==4,'rights_visible')
            await check(await page.get_by_text('CC BY-SA 3.0 Unported').count()==1,'explicit_license')
            await page.get_by_role('button',name='◇ Test').click()
            await check(await page.locator('[data-view="test"]:visible').count()==4,'tests_visible')
            await check(await page.locator('span.role').count()==12,'12_proposed_roles')
            await check(await page.locator('img').count()==0,'no_external_images')
            await check(len(requests)==0,'zero_external_requests')
            await check(len(errors)==0,'zero_js_errors')
            await check(await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),'no_horizontal_overflow')
            await page.screenshot(path=str(HERE/('browser_'+name+'.png')),full_page=True)
            await page.close()
        await browser.close()
    print('browser QA total',len(results),'pass',sum(a for a,_ in results),'fail',sum(not a for a,_ in results))
    for ok,label in results:
        if not ok: print('FAIL',label)
    if not all(a for a,_ in results): raise SystemExit(1)

if __name__=='__main__': asyncio.run(run())
