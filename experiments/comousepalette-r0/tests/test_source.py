from pathlib import Path
import re, unittest
SRC=Path(__file__).resolve().parents[1]/'CoMousePalette_R0.ps1'
text=SRC.read_text(encoding='utf-8')
class SourceBoundaries(unittest.TestCase):
    def test_no_network(self):
        for pattern in (r'Invoke-WebRequest',r'Invoke-RestMethod',r'Send-MailMessage',r'HttpClient',r'TcpClient'):
            self.assertNotRegex(text, pattern)
    def test_no_windows_hooks(self):
        self.assertNotIn('SetWindowsHookEx',text)
        self.assertNotIn('RegisterHotKey',text)
    def test_explicit_clipboard_read(self):
        self.assertIn('$bPreview.Add_Click({',text)
        self.assertRegex(text,r'\$bPreview\.Add_Click\(\{[\s\S]+?Clipboard\]::GetText\(\)')
    def test_no_persistence(self):
        for name in ('Start-Transcript','Set-Content','Out-File','Add-Content','ConvertTo-Json | Out-File','New-ItemProperty'):
            self.assertNotIn(name,text)
    def test_exits(self):
        self.assertIn('$bClose.Add_Click({$form.Close()})',text)
        self.assertIn('Escape',text)
    def test_hard_separation(self):
        self.assertIn('Authority: NONE / NOT SENT',text)
        self.assertIn('Copy capsule',text)
        self.assertIn('PRIVACY HOLD',text)
if __name__=='__main__':unittest.main()
