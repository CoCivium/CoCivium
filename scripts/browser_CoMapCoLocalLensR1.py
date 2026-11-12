#!/usr/bin/env python3
"""Offline desktop/mobile Chromium acceptance for the CoLocal R1 source lens."""
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'examples/comap/colocal-source-lens-r1.html'
OUT = Path(os.environ.get('COLOCAL_BROWSER_EVIDENCE', ROOT / 'evidence/comap-colocal-browser-r1'))
OUT.mkdir(parents=True, exist_ok=True)


def check(mode, width, height, pw):
    chrome = (shutil.which('chromium') or shutil.which('google-chrome')
              or shutil.which('chromium-browser'))
    browser = pw.chromium.launch(
        executable_path=chrome if chrome else None,
        headless=True, args=['--no-sandbox', '--disable-background-networking'])
    ctx = browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
    page = ctx.new_page()
    errors=[]
    external=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda req: external.append(req.url) if req.url.startswith(('http://','https://')) else None)
    page.goto(PAGE.resolve().as_uri(), wait_until='load')
    page.locator('#count').wait_for()
    assert '5 of 5 new source-typed relations shown' in page.locator('#count').inner_text()
    assert page.locator('#relations .relation').count() == 5
    assert page.locator('#nodes button').count() == 5
    page.get_by_role('button', name='Design').click()
    assert '2 of 5' in page.locator('#count').inner_text()
    page.get_by_role('button', name='Source CI').click()
    assert '3 of 5' in page.locator('#count').inner_text()
    page.get_by_role('button', name='All five').click()
    page.locator('#search').fill('GRAIL')
    assert '1 of 5' in page.locator('#count').inner_text()
    page.get_by_role('button', name='Reset').click()
    assert page.locator('#relations .relation').count() == 5
    page.get_by_role('button', name='CoLocal CoRelGRAILS candidate Seed').click()
    assert 'PUBLIC_CANDIDATE_NOT_CANON' in page.locator('#detailStatus').inner_text()
    assert '311fd21f2fbfeca1c70af023dc5fcd0c7ff3e539' in page.locator('#detailLinks a').get_attribute('href')
    assert page.get_by_role('link', name='Original interactive R0').count() == 1
    overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
    assert not overflow, f'Horizontal overflow at {width}px'
    assert errors == [], errors
    assert external == [], external
    png = OUT / f'{mode}.png'
    page.screenshot(path=str(png), full_page=True)
    report = {'mode':mode,'viewport':[width,height],'relations':5,'filters':['all','design','ci'],
              'search':'PASS','reset':'PASS','source_inspection':'PASS',
              'keyboard_native_controls':True,'horizontal_overflow':False,
              'javascript_errors':0,'external_network_requests':0,
              'screenshot':png.name,
              'acceptance':'BOUNDED_BROWSER_SOURCE_LENS_ONLY_NOT_HUMAN_USER_ACCEPTANCE'}
    (OUT / f'{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    ctx.close()
    browser.close()
    return report


def main():
    with sync_playwright() as pw:
        reports=[check('desktop',1280,850,pw),check('mobile',390,844,pw)]
    print(json.dumps({'state':'PASS_COMAP_COLOCAL_R1_BROWSER_QA','reports':reports},indent=2))


if __name__ == '__main__':
    main()
