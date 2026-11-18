"""Source-only CoWet safety and parity checks; does not assert browser a11y acceptance."""
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"examples/cowet/cowet-hero-audio-r0.html").read_text(encoding="utf-8")
DOC=(ROOT/"docs/Design/COWET_HUMAN_SURFACE_AUDIO_CONTRACT_R0_20261109.md").read_text(encoding="utf-8")

class Probe(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags.append((tag,a))
        if "id" in a:self.ids.add(a["id"])

class CoWetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=Probe();cls.page.feed(HTML)

    def test_hero_is_semantically_described(self):
        self.assertIn("title",self.page.ids)
        self.assertTrue(any(tag=="svg" and a.get("aria-label") for tag,a in self.page.tags))

    def test_keyboard_and_skip_link(self):
        self.assertIn('href="#main"',HTML)
        self.assertIn("Escape",HTML)
        self.assertIn(":focus-visible",HTML)

    def test_audio_is_explicit_opt_in(self):
        self.assertNotIn("autoplay",HTML.lower())
        self.assertIn('on.addEventListener("click"',HTML)
        self.assertIn("context=new AudioCtx()",HTML)
        self.assertIn("Scrolling never enables it",HTML)

    def test_sound_off_one_click_and_escape(self):
        self.assertIn('off.addEventListener("click",silence)',HTML)
        self.assertIn('if(e.key==="Escape")silence()',HTML)

    def test_hidden_tab_and_leave_silence(self):
        self.assertIn("if(document.hidden)silence()",HTML)
        self.assertIn('window.addEventListener("pagehide",silence)',HTML)

    def test_low_capped_scroll_volume(self):
        self.assertIn("Math.min(0.017",HTML)
        self.assertIn('window.addEventListener("scroll",volume',HTML)
        self.assertIn("if(!enabled||!context||!gain||!osc)return",HTML)

    def test_plain_view_and_reduced_motion(self):
        self.assertIn('classList.toggle("plain")',HTML)
        self.assertIn("prefers-reduced-motion:reduce",HTML)

    def test_no_external_io_by_design(self):
        self.assertIn("connect-src 'none'",HTML)
        self.assertIn("media-src 'none'",HTML)
        self.assertNotIn("<audio",HTML)
        self.assertNotIn("<iframe",HTML)

    def test_wet_contract_mentions_exemptions(self):
        self.assertIn("safety-critical",DOC)
        self.assertIn("screen-reader",DOC)
        self.assertIn("permission",DOC.lower())

    def test_contract_states_plain_soundless_first(self):
        self.assertIn("Default SILENT",DOC)
        self.assertIn("scroll-triggered audio without an explicit",DOC)
        self.assertIn("No historical source should be silently rewritten",DOC)

if __name__=="__main__":
    unittest.main()
