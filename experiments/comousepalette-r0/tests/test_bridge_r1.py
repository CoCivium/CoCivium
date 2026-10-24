import pathlib, unittest
base=pathlib.Path(__file__).resolve().parents[1]
class BridgeTests(unittest.TestCase):
  def test_readme_includes_no_send(self):
    t=(base/('CoPayload_README_R1.md' if (base/'CoPayload_README_R1.md').exists() else 'README.md')).read_text(encoding='utf-8');self.assertIn('No content is uploaded',t)
  def test_test_ps1_is_noninteractive(self):
    t=(base/'tests/test_pwsh_r1.ps1').read_text(encoding='utf-8');self.assertIn('-SelfTest',t);self.assertIn('-Canary',t)
  def test_no_unrestricted_access(self):
    t=(base/'CoPayload_R1.ps1').read_text(encoding='utf-8');self.assertIn('MaxFiles=12',t);self.assertIn('FILE_COUNT_LIMIT',t)
if __name__=='__main__': unittest.main()
