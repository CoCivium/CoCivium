import pathlib,re,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
S=(ROOT/'CoPayload_R1.ps1').read_text(encoding='utf-8')
class SafetyTests(unittest.TestCase):
    def test_explicit_file_picker(self):self.assertIn('OpenFileDialog',S);self.assertIn("$d.Multiselect=$true",S)
    def test_privacy_states(self):
        for s in ['LOCAL_PRIVATE_DEFAULT','NOT_PERFORMED','NOT_OBSERVED','execution_authority']:
            with self.subTest(s=s):self.assertIn(s,S)
    def test_file_hash_and_manifest(self):
        for s in ['Get-FileHash','SHA256','manifest.json','MEDIA_HASH_MISMATCH','SOURCE_CHANGED_DURING_COPY']:
            with self.subTest(s=s):self.assertIn(s,S)
    def test_no_auto_receivers(self):
        for s in ['Invoke-WebRequest','Invoke-RestMethod','HttpClient','Net.WebClient','Register-ObjectEvent','SetWindowsHookEx','SendKeys','SendInput']:
            with self.subTest(s=s):self.assertNotIn(s,S)
    def test_no_auto_clipboard_reads(self):self.assertNotIn('Clipboard]::Get',S);self.assertNotIn('Clipboard]::Contains',S)
    def test_bounds(self):self.assertIn('$MaxFiles=12',S);self.assertIn('1073741824L',S);self.assertIn('536870912L',S)
    def test_controlled_file_paste(self):self.assertIn('Clipboard]::SetFileDropList',S);self.assertIn('Clipboard]::SetImage',S)
    def test_canary_is_distinct(self):self.assertIn('if($Canary){',S);self.assertIn('if($SelfTest){',S)
    def test_unique_paths(self):self.assertIn('[guid]::NewGuid()',S);self.assertIn("throw 'NO_CLOBBER'",S)
    def test_original_not_removed(self):self.assertNotRegex(S,r'Remove-Item.*\$source');self.assertIn("Directory]::Delete($stage,$true)",S)
if __name__=='__main__':unittest.main()
