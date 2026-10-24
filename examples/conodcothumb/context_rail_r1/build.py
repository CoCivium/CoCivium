#!/usr/bin/env python3
"""Deterministic local build and readback. No external access or side effects outside output."""
import argparse, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parent

def build():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['schema']=='CoAll.CoContextRail.R1'
    page=(ROOT/'template.html').read_text(encoding='utf-8')
    obj=json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).replace('<','\\u003c')
    core=(ROOT/'CoContextRailR1.js').read_text(encoding='utf-8')
    page=page.replace('<!-- DATA_MARKER -->','<script type="application/json" id="manifest">'+obj+'</script>')
    page=page.replace('<!-- CORE_MARKER -->','<script>\n'+core+'</script>')
    assert '<!-- CORE_MARKER -->' not in page and '<!-- DATA_MARKER -->' not in page
    return page

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');ns=p.parse_args();page=build();dest=ROOT/'index.html'
    if ns.check:
        if not dest.exists() or dest.read_text(encoding='utf-8')!=page:
            raise SystemExit('FAIL_SOURCE_DRIFT: checked-in HTML differs from manifest+core+template')
        print('PASS_EXACT_HTML_SOURCE');return
    dest.write_text(page,encoding='utf-8');print('GENERATED',len(page.encode('utf-8')))
if __name__=='__main__':main()
