"""CoNav nested-diagram retro metadata controls, no media reproduction."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('retro', HERE/'conav_retro_r0.py')
retro = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retro)


class RetroTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.content = b'<div>public example</div>\n'
        path = 'examples/public/example.html'
        target = self.root / path
        target.parent.mkdir(parents=True)
        target.write_bytes(self.content)
        self.item = {
            'id': 'candidate-1', 'label': 'Historical public map', 'group': 'CoMap',
            'kind': 'INTERACTIVE_VIEW', 'source_path': path,
            'git_blob': retro.git_blob(self.content),
            'visibility': 'PUBLIC_REPO_SOURCE', 'rights_state': 'METADATA_LINK_ONLY',
            'status': 'RETRO_INSPIRATION_CANDIDATE_UNREVIEWED',
            'next_gate': 'HUMAN_OR_AUTHORIZED_SEMANTIC_RIGHTS_REVIEW',
        }
        self.manifest = {'schema':retro.SCHEMA, 'candidates':[self.item]}
        self.file = self.root/'manifest.json'
        self.save()

    def save(self):
        self.file.write_text(json.dumps(self.manifest), encoding='utf-8')

    def read(self):
        self.save()
        return retro.read_manifest(self.file)

    def test_01_one_public_candidate_and_pin_pass(self):
        self.assertEqual(retro.audit_sources(self.read(), self.root), [])

    def test_02_changed_source_never_silently_requalified(self):
        (self.root/self.item['source_path']).write_text('new bytes')
        self.assertEqual(retro.audit_sources(self.read(),self.root),
                         [('candidate-1','PINNED_SOURCE_BLOB_MISMATCH')])

    def test_03_missing_source_held(self):
        (self.root/self.item['source_path']).unlink()
        self.assertEqual(retro.audit_sources(self.read(),self.root),
                         [('candidate-1','MISSING_OR_OUTSIDE_REPO')])

    def test_04_duplicate_source_does_not_get_two_discovery_ids(self):
        second=copy.deepcopy(self.item); second['id']='second'
        self.manifest['candidates'].append(second)
        with self.assertRaisesRegex(ValueError,'DUPLICATE_RETRO_CANDIDATE'):
            self.read()

    def test_05_private_candidate_cannot_enter_public_export(self):
        self.item['visibility']='PRIVATE'
        with self.assertRaisesRegex(ValueError,'PRIVATE_CANDIDATE_IN_PUBLIC_EXPORT'):
            self.read()

    def test_06_unknown_rights_cannot_copy_media(self):
        self.item['rights_state']='PUBLISH_BYTES'
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_MEDIA_PROMOTION'):
            self.read()

    def test_07_no_auto_semantic_adoption(self):
        self.item['status']='CANON'
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_MEDIA_PROMOTION'):
            self.read()

    def test_08_no_skip_human_or_authorized_review(self):
        self.item['next_gate']='READY_TO_SEND'
        with self.assertRaisesRegex(ValueError,'MISSING_REVIEW_GATE'):
            self.read()

    def test_09_path_traversal_and_external_url_fail_closed(self):
        for path in ('../secret', '/etc/passwd', 'https://site.invalid/photo.png',
                     'x/../../secret', 'C:\\private\\image.png', 'evil`node.md'):
            with self.subTest(path=path):
                self.item['source_path'] = path
                with self.assertRaisesRegex(ValueError,'UNSAFE_SOURCE_PATH'):
                    self.read()

    def test_10_html_injected_label_blocked(self):
        self.item['label']='<script>alert(1)</script>'
        with self.assertRaisesRegex(ValueError,'UNSAFE_CANDIDATE_LABEL'):
            self.read()

    def test_11_invalid_blob_denied(self):
        self.item['git_blob']='not-a-blob'
        with self.assertRaisesRegex(ValueError,'INVALID_BLOB_ID'):
            self.read()

    def test_12_turtle_budget_cannot_materialize_infinite_candidates(self):
        items=[]
        for i in range(41):
            item=copy.deepcopy(self.item);item['id']='cand-'+str(i)
            item['source_path']='examples/public/'+str(i)
            items.append(item)
        self.manifest['candidates']=items
        with self.assertRaisesRegex(ValueError,'INVALID_BOUNDED_CANDIDATES'):
            self.read()

    def test_13_multiple_groups_are_nested_not_all_on_one_level(self):
        data=self.read(); md=retro.render_markdown(data)
        self.assertIn('## CoMap:',md)
        self.assertIn('## CoMedia:',md)
        self.assertIn('## CoLUE:',md)
        self.assertEqual(md.count('```mermaid'),4)

    def test_14_accessible_static_html_with_native_expansion(self):
        source=retro.render_html(self.read())
        self.assertEqual(source.count('<details'),3)
        self.assertEqual(source.count('<summary'),3)
        self.assertIn('href="https://github.com/CoCivium/CoCivium/blob/main/',source)
        self.assertNotIn('<script',source)
        self.assertIn('default-src',source)

    def test_15_render_and_hash_stable(self):
        a=self.read()
        self.assertEqual(retro.projection_id(a),retro.projection_id(a))
        self.assertEqual(retro.render_html(a),retro.render_html(a))
        self.assertEqual(retro.render_markdown(a),retro.render_markdown(a))

    def test_16_check_mode_detects_stale_diagram_without_clobber(self):
        data=self.read()
        diagram=self.root/'view.md'; html=self.root/'index.html'
        diagram.write_text('old');html.write_text(retro.render_html(data))
        proc=subprocess.run([sys.executable,str(HERE/'conav_retro_r0.py'),
                             '--root',str(self.root),'--manifest',str(self.file),
                             '--diagram',str(diagram),'--html',str(html),'--check'],
                            capture_output=True,text=True,timeout=10)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('HOLD_STALE_CONAV_VIEW',proc.stderr)
        self.assertEqual(diagram.read_text(),'old')

    def test_17_generation_refuses_to_overwrite_prior_version(self):
        data=self.read();diagram=self.root/'view.md';html=self.root/'index.html'
        diagram.write_text(retro.render_markdown(data))
        proc=subprocess.run([sys.executable,str(HERE/'conav_retro_r0.py'),
                             '--root',str(self.root),'--manifest',str(self.file),
                             '--diagram',str(diagram),'--html',str(html)],
                            capture_output=True,text=True,timeout=10)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('HOLD_NO_OVERWRITE',proc.stderr)

    def test_18_public_projection_never_contains_private_image_bytes(self):
        data=self.read()
        generated=retro.render_html(data)+retro.render_markdown(data)
        self.assertNotIn('public example</div>',generated)
        self.assertIn('Metadata only',generated)
        self.assertIn('No media copied',retro.render_markdown(data))


if __name__=='__main__':
    unittest.main(verbosity=2)
