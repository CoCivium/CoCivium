"""Bounded CoOmni R0 same-origin browser test. No network except loopback HTTP."""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import os
import time

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

@contextmanager
def server():
    handler=partial(Quiet,directory=str(ROOT))
    httpd=ThreadingHTTPServer(('127.0.0.1',0),handler)
    t=Thread(target=httpd.serve_forever,daemon=True); t.start()
    try: yield f'http://127.0.0.1:{httpd.server_port}/index.html'
    finally: httpd.shutdown();httpd.server_close()

def main():
    chrome=os.getenv('CHROMIUM_PATH','/usr/bin/chromium')
    with server() as base, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=chrome,args=['--no-sandbox'])
        context=browser.new_context()
        source=context.new_page()
        source.goto(base,wait_until='load')
        assert 'SOURCE READY' in source.locator('#state').inner_text()
        ux=context.new_page();ux.goto(source.locator('#links a').nth(0).get_attribute('href'))
        theory=context.new_page();theory.goto(source.locator('#links a').nth(1).get_attribute('href'))
        assert 'RECEIVER UX READY' in ux.locator('#state').inner_text()
        assert 'RECEIVER THEORY READY' in theory.locator('#state').inner_text()
        source.locator('#send').click()
        source.locator('#source-log').get_by_text('ACK accepted role=ux',exact=False).wait_for(timeout=8000)
        source.locator('#source-log').get_by_text('ACK accepted role=theory',exact=False).wait_for(timeout=8000)
        assert 'Improve the first-use' in ux.locator('#received').inner_text()
        assert 'Improve the first-use' in theory.locator('#received').inner_text()
        assert 'ACCEPTED cursor=1' in ux.locator('#receiver-log').inner_text()
        assert 'ACCEPTED cursor=1' in theory.locator('#receiver-log').inner_text()
        print('PASS: one explicit source send produced two distinct role ACKs with exact digest checks')
        source.locator('#replay').click()
        theory.locator('#receiver-log').get_by_text('STALE_OR_REPLAY',exact=False).wait_for(timeout=8000)
        assert 'ACK held role=theory' in source.locator('#source-log').inner_text()
        print('PASS: stale replay rejected, sender recorded role-specific HELD')
        source.locator('#to-theory').uncheck()
        source.locator('#message').fill('Second version only for UX')
        source.locator('#send').click()
        ux.locator('#received').get_by_text('Second version only for UX').wait_for(timeout=8000)
        assert 'Second version only for UX' not in theory.locator('#received').inner_text()
        assert 'ACCEPTED cursor=2' in ux.locator('#receiver-log').inner_text()
        assert 'ACCEPTED cursor=2' not in theory.locator('#receiver-log').inner_text()
        print('PASS: role-scoped second send did not reach unselected receiver')
        source.locator('#stop').click()
        ux.locator('#state').get_by_text('STOPPED BY SOURCE').wait_for(timeout=8000)
        theory.locator('#state').get_by_text('STOPPED BY SOURCE').wait_for(timeout=8000)
        assert source.locator('#send').is_disabled()
        print('PASS: stop delivered to both receiver views and source send disabled')
        context.close();browser.close()

if __name__=='__main__': main()
