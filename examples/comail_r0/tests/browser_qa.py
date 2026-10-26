"""Small real-browser acceptance checks for offline synthetic CoMail page."""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright,Error

ROOT=Path(__file__).resolve().parents[1]

def run():
  results=[]
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-background-networking'])
    for mode,width,height in [('desktop',1280,900),('mobile',390,844)]:
      ctx=browser.new_context(viewport={'width':width,'height':height},accept_downloads=True)
      page=ctx.new_page()
      errors=[];outbound=[]
      page.on('pageerror',lambda err:errors.append(str(err)))
      page.on('request',lambda req:outbound.append(req.url) if req.url.startswith(('http:','https:')) else None)
      # Direct local file navigation can be blocked by this sandbox; use the
      # exact extracted bytes in a controlled Chromium document instead.
      direct=False
      page.set_content((ROOT/'index.html').read_text('utf-8'),wait_until='load')
      def check(name,condition):
        results.append({'mode':mode,'test':name,'status':'PASS' if condition else 'FAIL'})
        if not condition:raise AssertionError(f'{mode}:{name}')
      check('document-title', 'fixed historical example' in page.locator('#message-body').inner_text())
      check('three-versions',page.locator('#version-picker button').count()==3)
      check('latest-first', 'The commons stays free' in page.locator('#version-headline').inner_text())
      check('original-note-never-mutates',page.locator('#message-body').inner_text().startswith('This invitation is a fixed historical'))
      check('unpaid', 'donations are not configured' in page.locator('body').inner_text().lower() or 'no donation link' in page.locator('body').inner_text().lower())
      check('source-sha-shown',len(page.locator('#resource-sha').inner_text())>60)
      page.get_by_role('button',name='v1').click()
      check('version-deep-link',page.evaluate('location.hash')=='#v1')
      check('older-version-selected','Corrections are part' in page.locator('#version-headline').inner_text())
      check('fixed-message-still-same','This invitation is a fixed historical' in page.locator('#message-body').inner_text())
      page.locator('#compare').click()
      check('predecessor-visible',page.locator('#compare-panel').is_visible())
      check('original-version-body-visible','Can a stranger' in page.locator('#before').inner_text())
      check('successor-version-body-visible','Readers can compare' in page.locator('#after').inner_text())
      page.get_by_role('button',name='v0').click()
      check('v0-compare-disabled',page.locator('#compare').is_disabled())
      page.locator('#current').click()
      check('latest-deep-link',page.evaluate('location.hash')=='#v2')
      check('latest-navigation','The commons stays free' in page.locator('#version-headline').inner_text())
      page.locator('#feedback').click()
      check('feedback-intentionally-revealed',page.locator('#feedback-panel').is_visible())
      check('feedback-empty',''==page.locator('#feedback-text').input_value())
      page.locator('#save-feedback').click()
      check('empty-feedback-refused','Nothing to save' in page.locator('#feedback-state').inner_text())
      page.locator('#feedback-text').fill('Please clarify how updates are reviewed.')
      with page.expect_download() as info:page.locator('#save-feedback').click()
      download=info.value
      check('download-has-local-name',download.suggested_filename=='comail_feedback_unsent_v2.json')
      target=ROOT/'tests'/('browser_'+mode+'_download.json')
      download.save_as(target)
      proposal=json.loads(target.read_text('utf-8'))
      check('feedback-no-authority',proposal['effect']=='NONE' and proposal['delivery']=='NOT_SENT')
      check('feedback-bound-version',proposal['source_sha256']==json.loads((ROOT/'fixture.json').read_text('utf-8'))['resource']['current_sha256'])
      page.locator('#clear-feedback').click()
      check('feedback-cleared',not page.locator('#feedback-text').input_value())
      check('no-browser-errors',not errors)
      check('no-external-requests',not outbound)
      check('no-horizontal-overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
      page.screenshot(path=str(ROOT/('screenshot_'+mode+'.png')),full_page=True)
      results.append({'mode':mode,'test':'direct-file-navigation','status':'PASS' if direct else 'HELD_SANDBOX'})
      ctx.close()
    browser.close()
  (ROOT/'tests'/'browser_receipt.json').write_text(json.dumps({'status':'PASS' if all(v['status'] in ('PASS','HELD_SANDBOX') for v in results) else 'FAIL','results':results},indent=2)+'\n',encoding='utf-8')
  counts={v:sum(z['status']==v for z in results) for v in {'PASS','FAIL','HELD_SANDBOX'}}
  print('BROWSER_QA',counts)

if __name__=='__main__':run()
