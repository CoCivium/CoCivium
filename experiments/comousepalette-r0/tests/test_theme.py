"""CoMousePalette Forest/Sage/Classic source and contrast checks, no GUI calls."""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "CoMousePalette_R0.ps1"
TEXT = SOURCE.read_text(encoding="utf-8")

def colors_for(name):
    start = TEXT.index("'" + name + "' {", TEXT.index("function Get-CoPalette("))
    end = TEXT.index("default { throw 'THEME_REQUIRES_FOREST_OR_SAGE' }", start)
    segment = TEXT[start:end]
    if name == "Forest":
        segment = segment.split("'Sage' {", 1)[0]
    return dict(re.findall(r"(\w+)='(#[0-9A-Fa-f]{6})'", segment))

def luminance(hex_color):
    values = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return sum(a*b for a, b in zip((.2126, .7152, .0722), linear))

def contrast(foreground, background):
    a,b = sorted((luminance(foreground), luminance(background)))
    return (b + .05)/(a + .05)

class ThemeSafety(unittest.TestCase):
    def test_all_theme_swatches_defined(self):
        expected = {'Frame','Header','Footer','Editor','Text','Button','ButtonText','Alert','Border'}
        for variant in ('Forest','Sage'):
            with self.subTest(variant=variant):
                self.assertEqual(set(colors_for(variant)), expected)

    def test_actual_text_contrast_exceeds_7_to_1(self):
        for variant in ('Forest','Sage'):
            p=colors_for(variant)
            pairs=(('Text','Header'),('Text','Editor'),('ButtonText','Button'),('Alert','Header'))
            for fg,bg in pairs:
                with self.subTest(theme=variant,fg=fg,bg=bg):
                    self.assertGreaterEqual(contrast(p[fg],p[bg]),7.0)

    def test_classic_is_unpainted(self):
        self.assertIn("[ValidateSet('Forest','Sage','Classic')]",TEXT)
        self.assertIn("if ($effectiveTheme -cne 'Classic')",TEXT)
        self.assertIn("[System.Windows.Forms.SystemInformation]::HighContrast",TEXT)

    def test_green_is_limited_to_window_controls(self):
        for target in ('$form.BackColor=','$header.BackColor=','$panel.BackColor=','$preview.BackColor=','$button.BackColor='):
            self.assertIn(target,TEXT)
        for forbidden in ('SetWindowsHookEx','RegisterHotKey','SystemParametersInfo','SetSysColors','Set-ItemProperty'):
            self.assertNotIn(forbidden,TEXT)

    def test_privacy_warning_visible(self):
        self.assertIn("if($context.Mode -ceq 'PRIVACY HOLD') {$header.ForeColor=",TEXT)
        self.assertIn('$bPreview.Add_Click({',TEXT)
        self.assertIn("Authority: NONE / NOT SENT",TEXT)

if __name__ == '__main__':
    unittest.main()
