#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path

FIXTURE = Path("fixtures/ux/cocivium_native_vertical_slice_r0.json")


def fail(code):
    raise SystemExit("FAIL:" + code)


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def esc(value):
    return html.escape(str(value), quote=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    src = doc["source_bindings"]
    checks = [
        ("public_onboarding_doc_path", "public_onboarding_doc_blob_sha"),
        ("cobar_delivery_doc_path", "cobar_delivery_doc_blob_sha"),
        ("cotime_doc_path", "cotime_doc_blob_sha"),
        ("cocivia_identity_path", "cocivia_identity_blob_sha"),
    ]
    for path_key, sha_key in checks:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("SOURCE_BIND:" + src[path_key])

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    commit_time = subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"], text=True
    ).strip()

    j = doc["journey"]
    avatar = doc["avatar"]
    evidence_html = "\n".join(
        f'''<details class="evidence-card" data-evidence-id="{esc(item["id"])}">
<summary><span>{esc(item["label"])}</span><strong>{esc(item["state"])}</strong></summary>
<p>{esc(item["detail"])}</p>
</details>'''
        for item in doc["evidence"]
    )

    learning_html = "\n".join(
        f'''<li>
<span class="step-number">{item["step"]}</span>
<div>
<h3 data-i18n data-en="{esc(item["title"]["en-CA"])}" data-fr="{esc(item["title"]["fr-CA"])}">{esc(item["title"]["en-CA"])}</h3>
<p data-i18n data-en="{esc(item["detail"]["en-CA"])}" data-fr="{esc(item["detail"]["fr-CA"])}">{esc(item["detail"]["en-CA"])}</p>
</div>
</li>'''
        for item in doc["learning_path"]
    )

    page = f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CoCivium Native Vertical Slice R0</title>
<style>
:root {{ color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: Canvas; color: CanvasText; }}
.shell {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
.topbar {{ display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:18px; }}
.brand {{ font-size:1.4rem; font-weight:750; letter-spacing:.01em; }}
.lang {{ display:flex; gap:8px; }}
button {{ font:inherit; padding:.7rem 1rem; border-radius:999px; border:1px solid color-mix(in srgb, CanvasText 25%, transparent); background:Canvas; color:CanvasText; cursor:pointer; }}
button[aria-pressed="true"] {{ font-weight:700; outline:2px solid currentColor; outline-offset:2px; }}
.cotime {{ font-size:.82rem; border:1px solid color-mix(in srgb, CanvasText 18%, transparent); padding:10px 12px; border-radius:12px; margin-bottom:18px; overflow-wrap:anywhere; }}
.hero {{ display:grid; grid-template-columns:72px 1fr; gap:16px; align-items:center; margin:20px 0 16px; }}
.avatar {{ width:64px; height:64px; border-radius:50%; border:2px solid currentColor; display:grid; place-items:center; font-weight:800; }}
.disclosure {{ opacity:.78; font-size:.9rem; }}
.card {{ border:1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius:18px; padding:18px; margin:14px 0; }}
.cobar label {{ display:block; font-weight:700; margin-bottom:8px; }}
.cobar-row {{ display:grid; grid-template-columns:1fr auto; gap:10px; }}
input {{ width:100%; font:inherit; border:1px solid color-mix(in srgb, CanvasText 25%, transparent); background:Canvas; color:CanvasText; border-radius:14px; padding:.9rem 1rem; }}
.reply {{ display:none; }}
.reply.visible {{ display:block; }}
.meta-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
.meta-grid > div {{ border:1px solid color-mix(in srgb, CanvasText 14%, transparent); padding:12px; border-radius:12px; }}
.meta-grid h3 {{ margin:.1rem 0 .4rem; font-size:.92rem; }}
.evidence-card {{ border-top:1px solid color-mix(in srgb, CanvasText 14%, transparent); padding:10px 0; }}
.evidence-card summary {{ display:flex; justify-content:space-between; gap:12px; cursor:pointer; }}
.evidence-card strong {{ font-size:.75rem; }}
.learning ol {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
.learning li {{ display:grid; grid-template-columns:34px 1fr; gap:10px; align-items:start; }}
.step-number {{ width:28px; height:28px; border:1px solid currentColor; border-radius:50%; display:grid; place-items:center; font-weight:700; }}
.learning h3, .learning p {{ margin:.05rem 0 .35rem; }}
footer {{ opacity:.7; font-size:.8rem; margin-top:22px; }}
@media (max-width:720px) {{
  .cobar-row, .meta-grid {{ grid-template-columns:1fr; }}
  .hero {{ grid-template-columns:56px 1fr; }}
  .avatar {{ width:50px; height:50px; }}
}}
</style>
</head>
<body data-head-sha="{esc(head)}" data-state="{esc(doc["state"])}">
<main class="shell">
<header class="topbar">
<div class="brand" data-visible-root="{esc(doc["visible_root_brand"])}">{esc(doc["visible_root_brand"])}</div>
<div class="lang" aria-label="Language">
<button type="button" data-lang="en-CA" aria-pressed="true">EN</button>
<button type="button" data-lang="fr-CA" aria-pressed="false">FR</button>
</div>
</header>

<section class="cotime" data-surface="CoTime" aria-label="CoTime currentness">
<strong>CoTime</strong> · head <code>{esc(head)}</code> · commit <time>{esc(commit_time)}</time> · synthetic candidate preview
</section>

<section class="hero" data-role="CoCivia">
<div class="avatar" id="{esc(avatar["id"])}" aria-label="{esc(avatar["label"])} avatar">{esc(avatar["display"])}</div>
<div>
<h1>{esc(avatar["label"])}</h1>
<p class="disclosure" data-i18n
 data-en="Disclosed composite conversational front. Not an independent human principal."
 data-fr="Interface conversationnelle composite déclarée. Ce n'est pas une personne humaine indépendante.">Disclosed composite conversational front. Not an independent human principal.</p>
</div>
</section>

<section class="card cobar" data-surface="CoBar">
<label for="cobar-input">CoBar</label>
<div class="cobar-row">
<input id="cobar-input" aria-describedby="cobar-help"
 value="{esc(j["synthetic_user_input"]["en-CA"])}"
 data-en="{esc(j["synthetic_user_input"]["en-CA"])}"
 data-fr="{esc(j["synthetic_user_input"]["fr-CA"])}">
<button id="ask-button" type="button" data-i18n data-en="Ask CoCivia" data-fr="Demander à CoCivia">Ask CoCivia</button>
</div>
<p id="cobar-help" class="disclosure" data-i18n
 data-en="This local preview does not send the text anywhere."
 data-fr="Cet aperçu local n'envoie le texte nulle part.">This local preview does not send the text anywhere.</p>
</section>

<section id="coreply" class="card reply" data-surface="CoReply" aria-live="polite">
<h2>CoReply</h2>
<p data-i18n data-en="{esc(j["reply"]["en-CA"])}" data-fr="{esc(j["reply"]["fr-CA"])}">{esc(j["reply"]["en-CA"])}</p>
</section>

<section class="card" aria-label="Current journey summary">
<div class="meta-grid">
<div>
<h3>CoHereNow</h3>
<p data-i18n data-en="{esc(j["cohere_now"]["en-CA"])}" data-fr="{esc(j["cohere_now"]["fr-CA"])}">{esc(j["cohere_now"]["en-CA"])}</p>
</div>
<div>
<h3>Meaning</h3>
<p data-i18n data-en="{esc(j["meaning"]["en-CA"])}" data-fr="{esc(j["meaning"]["fr-CA"])}">{esc(j["meaning"]["en-CA"])}</p>
</div>
<div>
<h3>NextSafeAction</h3>
<p data-i18n data-en="{esc(j["next_safe_action"]["en-CA"])}" data-fr="{esc(j["next_safe_action"]["fr-CA"])}">{esc(j["next_safe_action"]["en-CA"])}</p>
</div>
</div>
</section>

<section class="card" data-surface="CoVIA">
<h2>CoVIA</h2>
<p class="disclosure" data-i18n
 data-en="Evidence stays behind a deliberate drill-down."
 data-fr="Les preuves restent derrière une ouverture volontaire.">Evidence stays behind a deliberate drill-down.</p>
{evidence_html}
</section>

<section class="card learning" data-surface="LearningPath">
<h2 data-i18n data-en="Learning path" data-fr="Parcours d'orientation">Learning path</h2>
<ol>
{learning_html}
</ol>
</section>

<footer>
Static candidate artifact · no account · no external network · no public deployment · no runtime effect
</footer>
</main>
<script>
(() => {{
  const langButtons = [...document.querySelectorAll('[data-lang]')];
  const i18nNodes = [...document.querySelectorAll('[data-i18n]')];
  const input = document.getElementById('cobar-input');
  const reply = document.getElementById('coreply');
  const ask = document.getElementById('ask-button');

  function setLanguage(lang) {{
    document.documentElement.lang = lang;
    const key = lang === 'fr-CA' ? 'fr' : 'en';
    i18nNodes.forEach(node => {{
      node.textContent = node.dataset[key];
    }});
    input.value = input.dataset[key];
    langButtons.forEach(button => {{
      button.setAttribute('aria-pressed', String(button.dataset.lang === lang));
    }});
  }}

  langButtons.forEach(button => {{
    button.addEventListener('click', () => setLanguage(button.dataset.lang));
  }});

  ask.addEventListener('click', () => {{
    reply.classList.add('visible');
    reply.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
  }});
}})();
</script>
</body>
</html>
'''

    out = Path(args.output)
    if out.exists():
        fail("NO_CLOBBER_OUTPUT")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")

    digest = hashlib.sha256(page.encode("utf-8")).hexdigest().upper()
    print(json.dumps({
        "STATE": "PASS_COCIVIUM_NATIVE_VERTICAL_SLICE_RENDER_R0",
        "checked_out_head_sha": head,
        "commit_time": commit_time,
        "html_sha256": digest,
        "visible_root_brand": doc["visible_root_brand"],
        "surface_roles": sorted(doc["surface_roles"].keys()),
        "languages": doc["ux_contract"]["languages"],
        "external_network_required": doc["ux_contract"]["external_network_required_by_rendered_artifact"],
        "public_deployment": False,
        "runtime_effect": False
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
