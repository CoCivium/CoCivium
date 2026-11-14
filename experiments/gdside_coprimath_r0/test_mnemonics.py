import json
import unittest
from pathlib import Path
class TestMnemonicRegistry(unittest.TestCase):
    def test_spelling(self):
        reg=json.loads(Path(__file__).with_name('mnemonics.json').read_text())
        for item in reg['terms']:
            self.assertEqual(item['label'], ''.join(word[0].upper() for word in item['expansion']))
            self.assertEqual(item['letters'],[w[0].upper() for w in item['expansion']])
    def test_registry_unique(self):
        reg=json.loads(Path(__file__).with_name('mnemonics.json').read_text())
        labels=[x['label'] for x in reg['terms']]
        self.assertEqual(len(labels),len(set(labels)))
    def test_guardrails(self):
        reg=json.loads(Path(__file__).with_name('mnemonics.json').read_text())
        self.assertIn('CANDIDATE_NOT_CANON',reg['state'])
        self.assertIn('No hidden persuasion',reg['guardrails'])
if __name__=='__main__':unittest.main()
