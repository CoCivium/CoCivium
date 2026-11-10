#!/usr/bin/env python3
"""Offline Chromium browser smoke for CoBind viewer. Renders; does not deploy."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "cobind" / "cobind-golden-braid-orb-r0.html"
PROBE = r"""
<script>
(function () {
  "use strict";
  const get = id => document.getElementById(id);
  const select = get("case");
  const choose = id => { select.value = id; select.dispatchEvent(new Event("change")); };
  const results = {};
  results.options = select.options.length;
  results.initial = get("decision").textContent;
  choose("private");
  results.privateHold = get("decision").textContent === "HELD_NO_QUALIFIED_ANCHOR";
  choose("inverse");
  get("view").textContent;
  results.inverseProposed = get("decision").textContent === "CANDIDATE_BIND_NOT_EXECUTED";
  document.querySelector('[data-lens="inverse"]').click();
  results.lensActive = document.querySelector('[data-lens="inverse"]').getAttribute("aria-pressed") === "true";
  results.inverseExplanation = get("view").textContent.includes("not physical reverse causality");
  choose("retro-unsafe");
  results.retroHeld = get("decision").textContent === "HELD_NO_QUALIFIED_ANCHOR";
  get("reset").click();
  results.reset = select.value === "retro" && get("decision").textContent === "CANDIDATE_BIND_NOT_EXECUTED";
  document.querySelector('[data-lens="braid"]').click();
  results.braidLensActive = document.querySelector('[data-lens="braid"]').getAttribute("aria-pressed") === "true";
  results.braidSvg = Boolean(document.querySelector("#view svg.braid-diagram"));
  results.braidRouteCount = document.querySelectorAll("[data-braid-route-index]").length;
  document.querySelector('[data-braid-route-index="6"]').click();
  results.braidSelected = get("view").textContent.includes("CoConscious+") &&
                          get("view").textContent.includes("Receiver acceptance: UNVERIFIED");
    document.querySelector('[data-lens="reader"]').click();
  results.readerLens = document.querySelector('[data-lens="reader"]').getAttribute("aria-pressed") === "true";
  results.readerInitiallyNoExport = document.getElementById("readerExport").disabled === true;
  document.getElementById("readerCheck").click();
  results.readerIncompleteHeld = document.getElementById("readerFeedback").textContent.includes("HOLD");
  ["typed", "none", "readproof"].forEach((v,i) => {
    const r = document.querySelector('input[name="reader_q'+i+'"][value="'+v+'"]');
    if (r) r.click();
  });
  document.getElementById("readerCheck").click();
  results.readerCorrect = document.getElementById("readerFeedback").textContent.includes("3/3");
  results.readerExportEnabled = document.getElementById("readerExport").disabled === false;
  results.scrollWidth = document.documentElement.scrollWidth;
  results.viewportWidth = document.documentElement.clientWidth;
  results.title = document.title;
  document.body.setAttribute("data-cobind-browser-probe", JSON.stringify(results));
}());
</script>
"""


def execute(browser, args, report_path):
    cmd = [
        browser, "--headless", "--no-sandbox", "--disable-gpu",
        "--disable-background-networking", "--no-first-run",
        "--no-default-browser-check", "--disable-extensions",
        "--disable-features=MediaRouter", "--force-device-scale-factor=1",
        "--virtual-time-budget=1500", "--hide-scrollbars",
        f"--window-size={args.width},{args.height}",
        f"--user-data-dir={str(args.profile)}",
    ]
    if args.screenshot:
        cmd.append(f"--screenshot={str(args.screenshot)}")
    cmd.extend(["--dump-dom", report_path.as_uri()])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if result.returncode != 0:
        raise RuntimeError(f"Browser exited {result.returncode}: {result.stderr[-1200:]}")
    match = re.search(r'data-cobind-browser-probe="([^"]+)"', result.stdout)
    if not match:
        raise RuntimeError(f"Browser did not execute the probe; stderr={result.stderr[-1200:]}")
    return json.loads(html.unescape(match.group(1)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", default="cobind-browser-smoke")
    args = ap.parse_args()
    browser = next((shutil.which(x) for x in ("google-chrome", "google-chrome-stable",
                                           "chromium", "chromium-browser")
                    if shutil.which(x)), None)
    if not browser:
        raise SystemExit("HELD_NO_CHROMIUM: no browser binary found on runner")
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    if "</body>" not in source:
        raise SystemExit("HELD_MISSING_DOCUMENT_END")
    expected_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    results = []
    with tempfile.TemporaryDirectory(prefix="cobind-browser-") as tmp:
        tmp_dir = Path(tmp)
        rendered = tmp_dir / "offline-probe.html"
        rendered.write_text(source.replace("</body>", PROBE + "</body>"), encoding="utf-8")
        for name, width, height in (("desktop", 1280, 900), ("mobile", 390, 844)):
            screenshot = out / f"cobind-{name}.png"
            options = argparse.Namespace(width=width, height=height,
                                         screenshot=screenshot, profile=tmp_dir / f"profile-{name}")
            observation = execute(browser, options, rendered)
            for key in ("privateHold", "inverseProposed", "lensActive",
                        "inverseExplanation", "retroHeld", "reset",
                        "readerLens", "readerInitiallyNoExport", "readerIncompleteHeld",
                        "readerCorrect", "readerExportEnabled"):
                if observation.get(key) is not True:
                    raise AssertionError(f"{name} {key} failed: {observation}")
            if observation["braidRouteCount"] != 7:
                raise AssertionError(f"{name} braided route count: {observation}")
            if observation["options"] != 10:
                raise AssertionError(f"{name} fixture count differs: {observation}")
            if observation["scrollWidth"] > observation["viewportWidth"]:
                raise AssertionError(f"{name} horizontal overflow: {observation}")
            if observation["initial"] != "CANDIDATE_BIND_NOT_EXECUTED":
                raise AssertionError(f"{name} initial state differs: {observation}")
            if not screenshot.is_file() or screenshot.stat().st_size < 3000:
                raise AssertionError(f"{name} screenshot missing or implausibly small")
            results.append({"viewport": name, "requested_width": width, "requested_height": height,
                            "observation": observation, "screenshot": screenshot.name,
                            "screenshot_sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest()})
    report = {
        "status": "PASS_BROWSER_SMOKE_NOT_RECEIVER_ACCEPTANCE",
        "source": "examples/cobind/cobind-golden-braid-orb-r0.html",
        "source_sha256": expected_sha,
        "tests": results,
        "nonclaims": ["NOT_PRODUCTION", "NOT_INDEPENDENT_RECEIVER",
                      "NOT_REAL_WORLD_EVIDENCE", "NOT_CROSS_SESSION_RUNTIME"],
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS CoBind browser smoke: {len(results)} viewports; source sha256={expected_sha}")


if __name__ == "__main__":
    main()
