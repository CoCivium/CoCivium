#!/usr/bin/env python3
"""Reproducible no-network, no-dependency single-file UX build."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
html=(ROOT/'index.template.html').read_text(encoding='utf-8')
logic=(ROOT/'cogbx_logic.js').read_text(encoding='utf-8')
assert html.count('/*INLINE_LOGIC*/')==1
final=html.replace('/*INLINE_LOGIC*/',logic)
assert '/*INLINE_LOGIC*/' not in final
(ROOT/'CoGbx_OneWork_Exemplar_R0.html').write_text(final,encoding='utf-8')
print('Built',ROOT/'CoGbx_OneWork_Exemplar_R0.html')
