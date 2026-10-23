#!/usr/bin/env python3
"""Embed a canonical public-safe graph as JSON for file:// offline rendering."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
graph = json.loads((root / "graph.json").read_text(encoding="utf-8"))
assert graph["source_policy"] == "PUBLIC_ONLY__NO_SECRETS__NO_REMOTE_EFFECT"
serialized = json.dumps(graph, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
assert "</" not in serialized
html = (root / "index.template.html").read_text(encoding="utf-8").replace("__GRAPH_DATA__", serialized)
(root / "index.html").write_text(html, encoding="utf-8")
inline = html.replace('<script src="./core.js"></script>', '<script>'+(root/'core.js').read_text(encoding='utf-8')+'</script>')
inline = inline.replace('<script src="./app.js"></script>', '<script>'+(root/'app.js').read_text(encoding='utf-8')+'</script>')
(root / "CoMapPulse_ONEFILE_R0.html").write_text(inline, encoding="utf-8")
print(f"Built index.html for {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
