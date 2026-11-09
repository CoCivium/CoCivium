"""Static contracts for human-facing media prototype. Not a browser acceptance test."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parent
HTML=(ROOT/"cowet_hero_audio_r0.html").read_text(encoding="utf-8")
RULE=(ROOT/"COWET_HUMAN_SURFACE_RULE_R0.md").read_text(encoding="utf-8")

class CoWetTests(unittest.TestCase):
    def test_standalone_hero_has_meaningful_svg(self):
        self.assertIn('<svg class="orbit"',HTML)
        self.assertIn('aria-label="Abstract relational orbit',HTML)
        self.assertIn('CoSeed',HTML)
        self.assertIn('CoPath',HTML)

    def test_no_autoplay_attribute_or_media_download(self):
        self.assertNotRegex(HTML, r'\bautoplay\s*(=|>|\s)')
        self.assertNotIn('<audio', HTML)
        self.assertNotIn('src="http',HTML)

    def test_audio_starts_only_inside_enable_click(self):
        start=HTML.index('$("enable").addEventListener("click"')
        click_to_start=HTML[start:]
        self.assertIn('ctx=new A()',click_to_start)
        self.assertNotIn('ctx=new A()',HTML[:start])

    def test_scroll_only_updates_existing_audio(self):
        self.assertIn('if(enabled&&!silenced)updateVolume()',HTML)

    def test_immediate_silence_and_preference(self):
        self.assertIn('function setSilence(v)',HTML)
        self.assertIn('if(v){stop();',HTML)
        self.assertIn('localStorage.setItem(key,String(v))',HTML)

    def test_capped_volume(self):
        self.assertIn('max="12"',HTML)
        self.assertIn('max*(.12+.65*progress)',HTML)

    def test_dry_always_stops_audio(self):
        self.assertIn('if(dry){stop();',HTML)

    def test_keyboard_and_reduced_motion(self):
        self.assertIn('prefers-reduced-motion:reduce',HTML)
        self.assertIn(':focus-visible',HTML)
        self.assertIn('aria-live="polite"',HTML)

    def test_hidden_tab_stops_audio(self):
        self.assertIn('document.hidden&&enabled',HTML)

    def test_design_rule_has_necessary_exceptions(self):
        self.assertIn('documented reason',RULE)
        self.assertIn('legacy/retro',RULE)
        self.assertIn('No media or Web Audio node starts audibly without a clear user gesture',RULE)

    def test_no_deployment_pretence(self):
        self.assertIn('It does not fetch the real CoSeed registry',HTML)
        self.assertIn('not deployed to CoCivium.org',RULE)

if __name__=="__main__":
    unittest.main()
