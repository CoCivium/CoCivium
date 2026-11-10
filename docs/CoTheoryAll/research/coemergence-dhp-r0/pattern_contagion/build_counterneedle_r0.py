#!/usr/bin/env python3
"""Offline, accessible CoSpeedo counter-needle projection. No telemetry or effects."""
from __future__ import annotations
import argparse
import html
import hashlib
import json
from pathlib import Path
from counter_contagion_r0 import evaluate

ROOT = Path(__file__).parent


def render():
    fixture_bytes = (ROOT / "counter_contagion_fixture.json").read_bytes()
    obj = evaluate(json.loads(fixture_bytes))
    cases = [
        ("baseline_without_correction", "No correction", "slate"),
        ("scheduled_correction", "Delayed correction", "amber"),
        ("early_correction", "Early correction", "mint"),
    ]
    max_ticks = max(obj[c]["uncorrected_exposure_ticks"] for c, _, _ in cases)
    cards = []
    for key, title, css in cases:
        report = obj[key]
        lag = report["receiver_notice_lag_ticks"]
        lag_text = "not reached" if lag is None else f"{lag} simulated tick(s)"
        v = report["uncorrected_exposure_ticks"]
        cards.append(f'''<article class="card {css}"><p class="eyebrow">{html.escape(title)}</p>
          <div class="value">{v} <span>tick-exposures</span></div>
          <div class="track" role="img" aria-label="{v} of {max_ticks} maximum synthetic uncorrected-exposure ticks"><span style="width:{v * 100 / max_ticks:.1f}%"></span></div>
          <p>Receiver notice lag: <strong>{html.escape(lag_text)}</strong>.</p>
          <p class="minor">Notice is not independently verified, accepted, or read.</p></article>''')
    ticks = range(obj[cases[0][0]]["horizon"] + 1)
    rows = []
    for t in ticks:
        values = [obj[k]["series"][t]["exposures_without_correction_notice"] for k, _, _ in cases]
        rows.append(f'<tr><th scope="row">{t}</th>' + ''.join(f'<td>{v}</td>' for v in values) + '</tr>')
    colors = {"slate": "#b2bde2", "amber": "#f2b877", "mint": "#7cddcf"}
    lines = []
    height, left, top, w, h = 220, 42, 12, 700, 160
    count = len(list(ticks))
    max_y = max(1, max(max(obj[k]["series"][t]["exposures_without_correction_notice"] for t in ticks) for k, _, _ in cases))
    for key, title, css in cases:
        pts = []
        for t in range(count):
            v = obj[key]["series"][t]["exposures_without_correction_notice"]
            pts.append(f'{left + t*w/(count-1):.1f},{top+h-v*h/max_y:.1f}')
        lines.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[css]}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"><title>{title} synthetic uncorrected exposures by tick</title></polyline>')
    source_digest = hashlib.sha256(fixture_bytes).hexdigest()
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CoSpeedo Counter-Needle | CoCounterContagion R0</title>
<style>
:root{{color-scheme:dark;--bg:#0b1220;--panel:#152236;--border:#38516b;--ink:#f1f5ff;--dim:#b8c8d8;--mint:#7cddcf;--amber:#f2b877;--slate:#b2bde2}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 90% 0%,#24354d,var(--bg) 55%);font:16px/1.55 system-ui,Segoe UI,sans-serif;color:var(--ink)}}main{{max-width:1050px;margin:auto;padding:32px 18px 70px}}header{{border-bottom:1px solid var(--border);padding-bottom:20px}}h1{{font-size:clamp(30px,6vw,48px);line-height:1.14;margin:8px 0}}h2{{font-size:22px;margin:0 0 12px}}a{{color:var(--mint)}}a:focus-visible{{outline:3px solid var(--amber)}}.eyebrow{{font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--mint);font-weight:750}}.lead{{font-size:19px;max-width:850px;color:var(--dim)}}.notice{{border-left:4px solid var(--amber);padding:15px 18px;background:#2b2a36;margin:23px 0;border-radius:9px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:15px;margin:22px 0}}.card,.panel{{border:1px solid var(--border);background:var(--panel);border-radius:14px;padding:20px}}.value{{font-size:36px;font-weight:770;font-variant-numeric:tabular-nums}}.value span{{font-size:13px;font-weight:500;color:var(--dim)}}.minor,small{{color:var(--dim)}}.track{{height:9px;border-radius:10px;background:#223449;overflow:hidden;margin:12px 0}}.track span{{display:block;height:100%;background:var(--slate)}}.card.amber .track span{{background:var(--amber)}}.card.mint .track span{{background:var(--mint)}}.legend{{display:flex;gap:18px;flex-wrap:wrap;margin:12px 0;color:var(--dim);font-size:14px}}.swatch{{display:inline-block;width:17px;height:4px;vertical-align:middle;margin-right:6px;background:var(--slate)}}.swatch.amber{{background:var(--amber)}}.swatch.mint{{background:var(--mint)}}.panel{{margin-top:18px}}svg{{display:block;width:100%;height:auto}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th,td{{padding:9px 12px;text-align:left;border-bottom:1px solid var(--border)}}td{{text-align:right}}th[scope=row]{{font-weight:500}}footer{{margin-top:30px;padding-top:15px;border-top:1px solid var(--border);color:var(--dim);font-size:13px}}code{{word-break:break-word}}.status{{font-weight:700;color:var(--amber)}}
</style></head><body><main>
<header><p class="eyebrow">CoCivium · CoSpeedo+ · CoCounterContagion+ · R0</p><h1>Can a correction catch up?</h1>
<p class="lead">An offline, inspectable counter-needle for a synthetic information cascade. Here the unit is <strong>uncorrected-exposure ticks</strong>, not verified benefit, trust, health or people reached.</p></header>
<div class="notice" role="status"><strong>SYNTHETIC RESEARCH FIXTURE.</strong> No live telemetry, prediction validation, real receiver acknowledgment, public outreach or automatic effects. A <em>correction notice</em> may itself be wrong. We do not infer truth or acceptance from delivery.</div>
<div class="cards">{''.join(cards)}</div>
<section class="panel"><h2>One trace, three alternatives</h2>
<p class="minor">The plot shows how many synthetic nodes have encountered the unverified pattern without yet receiving a challenge notice at each simulated tick. Starting the notice sooner reduces the simulated gap, but never erases history.</p>
<div class="legend"><span><i class="swatch"></i>No correction</span><span><i class="swatch amber"></i>Delayed</span><span><i class="swatch mint"></i>Early</span></div>
<svg viewBox="0 0 785 {height}" role="img" aria-label="Synthetic uncorrected exposures over ticks zero to six. No correction persists higher; delayed correction eventually catches up; early correction catches up sooner.">
<line x1="{left}" y1="{top+h}" x2="{left+w}" y2="{top+h}" stroke="#8093ae"/>
<line x1="{left}" y1="{top}" x2="{left}" y2="{top+h}" stroke="#8093ae"/>
{''.join(lines)}
<text x="{left}" y="{height-6}" fill="#b8c8d8">tick 0</text><text x="{left+w-50}" y="{height-6}" fill="#b8c8d8">tick 6</text>
<text x="0" y="{top+5}" fill="#b8c8d8">{max_y}</text><text x="18" y="{top+h}" fill="#b8c8d8">0</text></svg>
<div class="scroll"><table><caption style="text-align:left;color:var(--dim);padding:8px 0">Exact values behind the plotted lines</caption><thead><tr><th scope="col">Tick</th><th scope="col">No correction</th><th scope="col">Delayed</th><th scope="col">Early</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section class="panel"><h2>Counter-proof and source families</h2>
<p>Three source copies come from <strong>one declared source family</strong>. That is not three independent confirmations. Correction notice arrival is not independently verified as correct, read, understood or accepted. All those gauges remain <strong>unknown</strong>.</p>
<p><span class="status">CoOomph: HOLD EFFECTS.</span> No acceleration, influence campaign, network message, right to publish or automatic replication is authorized by a synthetic gain.</p>
<p>Question-driven next test: under a consented, independent review, can source-bound corrections actually reduce misunderstanding compared with a strong ordinary written correction, without reducing dissent?</p></section>
<footer>CoObject+ / CoTime+ / CoSpeedo+ source-only projection · Fixture SHA-256 <code>{source_digest}</code> · 
<a href="https://github.com/CoCivium/CoCivium/pull/445">Review research PR #445</a>.  Not merged, adopted or runtime-qualified. No scripts, third-party resources, storage or network requests are required to view this artifact.</footer>
</main></body></html>
'''


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args=p.parse_args()
    dest=ROOT/'counterneedle.html'
    text=render()
    if args.check:
        if not dest.exists() or dest.read_text(encoding='utf-8') != text:
            raise SystemExit('STALE_COUNTERNEEDLE')
        print('COUNTERNEEDLE_MATCH')
    else:
        dest.write_text(text, encoding='utf-8')
        print('COUNTERNEEDLE_WRITTEN')

if __name__=='__main__':
    main()