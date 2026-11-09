"""Synthetic bounded fixtures for source/link integrity. No external accounts."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'CoReboundIntegrityR0.py'
spec = importlib.util.spec_from_file_location('corebound', SOURCE)
corebound = importlib.util.module_from_spec(spec)
spec.loader.exec_module(corebound)


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for target in (
            'SESSION_BOOTSTRAP.md', 'docs/Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md',
            'docs/Architecture/orb.md', 'examples/showcase/README.md',
        ):
            self.write(target, 'test\n')
        self.write(corebound.HUBS[0], '\n'.join([
            '# Public hub',
            '[AI catchup](AI_ONRAMP_CATCHUP_HUB_20261108.md)',
            '[Machine Index](../../ai/index.json)',
            '[Lanes](../../ai/evolution-lanes.json)',
            '[Bootstrap](../../SESSION_BOOTSTRAP.md)',
            '[Register](../Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md)',
            '[Orb](../Architecture/orb.md)',
            '[External](https://example.com/source)',
        ]))
        self.write(corebound.HUBS[1], '[Rebound](COGOALL_PUBLIC_REBOUND_HUB_20261108.md)\n')
        self.write('ai/index.json', json.dumps({
            'current_surfaces': [{'id':'human','path':'SESSION_BOOTSTRAP.md'},
                                 {'id':'orb','path':'docs/Architecture/orb.md'}]
        }))
        self.write('ai/evolution-lanes.json', json.dumps({
            'domains': [['CoUX+', ['CoCivium'], 'PROJECTION'],
                        ['CoOps+', ['CoSteward'], 'CONTINUITY']]
        }))

    def write(self, name, content):
        target=self.root/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content,encoding='utf-8')

    def test_good_fixture_source_only_not_ack(self):
        result=corebound.audit(self.root)
        self.assertEqual(result['state'], 'SOURCE_LINKS_VALIDATED_ONLY')
        self.assertEqual(result['coverage']['declared_evolution_lanes'],2)
        self.assertIn('SOURCE_LINK_NE_RECEIVER_ACK', result['nonclaims'])

    def test_missing_relative_link_fails(self):
        self.write('docs/Architecture/orb.md', 'obsolete')
        (self.root/'docs/Architecture/orb.md').unlink()
        result=corebound.audit(self.root)
        self.assertEqual(result['state'], 'SOURCE_CONTINUITY_HOLD')
        self.assertIn('docs/Architecture/orb.md', result['missing_local_targets'])

    def test_cross_hub_reference_needed(self):
        self.write(corebound.HUBS[1], 'No rebound link\n')
        result=corebound.audit(self.root)
        self.assertIn('MISSING_CROSS_LINK:'+corebound.HUBS[1]+'->'+corebound.HUBS[0],result['violations'])

    def test_path_traversal_fails_closed(self):
        self.write(corebound.HUBS[0], '[Escape](../../../etc/passwd)\n')
        result=corebound.audit(self.root)
        self.assertTrue(any('SOURCE_OUTSIDE_REPOSITORY' in x for x in result['violations']))

    def test_machine_index_missing_surface_detected(self):
        self.write('ai/index.json', json.dumps({'current_surfaces':[{'id':'missing','path':'absent.md'}]}))
        result=corebound.audit(self.root)
        self.assertIn('absent.md',result['missing_local_targets'])

    def test_duplicate_lane_denied(self):
        self.write('ai/evolution-lanes.json', json.dumps({'domains':[
            ['CoUX+', ['CoCivium'], 'PROJECTION'], ['CoUX+', ['CoCivium'], 'REWRITE']]}))
        result=corebound.audit(self.root)
        self.assertIn('EVOLUTION_LANES_INVALID:DUPLICATE_EVOLUTION_LANE',result['violations'])

    def test_malformed_machine_index_denied(self):
        self.write('ai/index.json','{broken-json}')
        self.assertEqual(corebound.audit(self.root)['state'],'SOURCE_CONTINUITY_HOLD')

    def test_external_links_not_fetched_or_counted(self):
        baseline=corebound.audit(self.root)
        self.write(corebound.HUBS[0],(self.root/corebound.HUBS[0]).read_text()+'\n[Another](https://example.invalid/)\n')
        updated=corebound.audit(self.root)
        self.assertEqual(updated['coverage']['local_link_occurrences'],baseline['coverage']['local_link_occurrences'])

    def test_repeated_runs_are_identical(self):
        self.assertEqual(corebound.audit(self.root),corebound.audit(self.root))

    def test_boolean_and_missing_lane_metadata_fail_closed(self):
        self.write('ai/evolution-lanes.json',json.dumps({'domains':[['CoOps+', [], 'CONTINUITY']]}))
        self.assertEqual(corebound.audit(self.root)['state'],'SOURCE_CONTINUITY_HOLD')

if __name__ == '__main__':
    unittest.main(verbosity=2)
