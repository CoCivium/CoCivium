#!/usr/bin/env python3
import json, pathlib, hashlib
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent
source=json.loads((ROOT/'evidence_snapshot.json').read_text(encoding='utf-8'))
html=(ROOT/'index.html').read_text(encoding='utf-8')
checks={}
checks['145_source_counts']=sum(sum(day[k] for k in ('PASS','HELD','FAIL')) for day in source['benchmark_by_day'])==145
checks['status_totals_correct']=all(sum(d[k] for d in source['benchmark_by_day'])==source['benchmark_totals'][k] for k in ('PASS','HELD','FAIL'))
checks['unique_id_total']=source['benchmark_totals']['unique_record_ids']==145
checks['seven_windows']=len(source['scorecard_windows'])==7
checks['five_unknown_two_partial']=(sum(x['status']=='UNKNOWN' for x in source['scorecard_windows'])==5 and sum(x['status'].startswith('PARTIAL') for x in source['scorecard_windows'])==2)
checks['no_exponent']=source['growth_exponent_per_day'] is None and source['qualified_value_series'] is None
checks['no_fake_zero']=source['comparable_value_windows'] is None
checks['minimum_four']=source['minimum_comparable_value_windows']==4
checks['evidence_pins_sha']=len(source['source_pins']['benchmark']['git_blob_sha1'])==40 and len(source['source_pins']['scorecard']['git_blob_sha1'])==40
checks['offline_no_fetch']=all(x not in html for x in ('fetch(', 'XMLHttpRequest(', 'WebSocket(', 'EventSource(', 'setInterval('))
checks['no_remote_assets']=not any(x in html for x in ('<script src=', '<link rel="stylesheet"', '<iframe '))
checks['no_false_green']=('Not established' in html and 'Remote observer offline' in html)
checks['not_live']=source['exponent_status'].startswith('HELD') and 'NO_LIVE_BACKGROUND_REFRESH' in source['nonclaims']
checks['source_snapshot']='application/json' in html and '<script type="application/json" id="evidenceSnapshot">' in html
browser_checks={}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1440,'height':1000}, device_scale_factor=1, accept_downloads=True)
 errors=[]; network=[]
 page.on('pageerror',lambda e: errors.append(str(e)))
 page.on('console',lambda m: errors.append('CONSOLE '+m.text) if m.type=='error' else None)
 page.on('request',lambda req: network.append(req.url) if not req.url.startswith('file://') else None)
 page.set_content(html, wait_until='load')
 page.screenshot(path=str(ROOT/'screenshot_desktop.png'), full_page=True)
 browser_checks['title']=page.title()=='CoSpeedo+ | CoValue evidence'
 browser_checks['cards_count']=page.locator('.tile').count()==4
 browser_checks['kpi_values']=[page.locator('#'+x).inner_text() for x in ('totalRecords','totalPass','totalHeld','totalFail')]==['145','84','47','14']
 browser_checks['four_bars']=page.locator('.barline').count()==4
 browser_checks['seven_days']=page.locator('.statusday').count()==7
 browser_checks['six_gates']=page.locator('.gate').count()==6
 browser_checks['growth_held']=page.locator('#growthVal').inner_text()=='Not established'
 browser_checks['git_source_pinned']='5c76703b19eebe9192f928634a14b760129382c3' in page.locator('#benchLink').get_attribute('href')
 page.get_by_role('button', name='CoValue').click()
 browser_checks['tab_value_shows_hold']=page.locator('#valuePane').is_visible() and not page.locator('#activityPane').is_visible()
 page.get_by_role('button', name='Activity').click()
 browser_checks['tab_activity_restores']=page.locator('#activityPane').is_visible() and not page.locator('#valuePane').is_visible()
 with page.expect_download() as d:
  page.get_by_role('button', name='Export aggregated CSV').click()
 dl=d.value
 path=ROOT/'export_test.csv';dl.save_as(str(path));csv=path.read_text()
 browser_checks['download_filename']=dl.suggested_filename=='CoSpeedo_benchmark_log_snapshot_20261027.csv'
 browser_checks['csv_header']=csv.startswith('date,PASS,HELD,FAIL,total\n')
 browser_checks['csv_four_day_lines']=len(csv.strip().splitlines())==5 and '2026-10-24,40,26,3,69' in csv
 browser_checks['network_free']=len(network)==0
 browser_checks['no_js_errors']=len(errors)==0
 mobile=browser.new_page(viewport={'width':390,'height':844}, device_scale_factor=1)
 mobile.set_content(html,wait_until='load')
 mobile.screenshot(path=str(ROOT/'screenshot_mobile.png'),full_page=True)
 browser_checks['mobile_no_horizontal_scroll']=mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
 browser_checks['mobile_working']=mobile.locator('.barline').count()==4
 browser.close()
all_checks={**checks,**browser_checks}
receipt={'schema':'CoSpeedo.DashboardTestReceipt.R1.v0.1','local_run_utc_date':'2026-10-27','scope':'SELF_CONTAINED_STATIC_SOURCE_BROWSER_INTERACTIONS__NOT_X1_X2_RUNTIME','total':len(all_checks),'passed':sum(all_checks.values()),'checks':all_checks,'browser_errors':errors,'non_file_network_requests':network,'sources':source['source_pins'],'nonclaims':['LOCAL_RENDER_NE_X2_INSTALL','SOURCE_ACTIVITY_NE_COVALUE_GROWTH','TEST_PASS_NE_INDEPENDENT_ACCEPTANCE','ONE_SNAPSHOT_NE_LIVE_TELEMETRY']}
(ROOT/'test_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'passed':receipt['passed'],'total':receipt['total'],'failures':[k for k,v in all_checks.items() if not v],'errors':errors,'network':network},indent=2))
if not all(all_checks.values()): raise SystemExit(1)
