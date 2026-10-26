#!/usr/bin/env python3
"""Source-bound static federation and negative-case controls."""
from pathlib import Path
import hashlib
import json
import re
import unittest
from copy import deepcopy
from html.parser import HTMLParser
from build import load_manifest, validate, build, decode_index

ROOT=Path(__file__).resolve().parent

class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.external=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='script' and 'src' in a:self.external.append(a['src'])
        if tag=='link' and 'href' in a:self.external.append(a['href'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])

class FederationTests(unittest.TestCase):
    def setUp(self):self.m=load_manifest()
    def test_coconnect_probe_uses_current_manifest_bytes(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        manifest=(ROOT/'manifest.json').read_bytes()
        got=hashlib.sha1(b'blob '+str(len(manifest)).encode()+b'\0'+manifest).hexdigest()
        self.assertEqual(got,probe['current_source']['manifest_git_blob_sha1'])
        self.assertEqual(probe['current_subject'],'co_giggle')
        self.assertIn('NOT_ONTOLOGY',probe['status'])
    def test_coconnect_main_donors_have_exact_git_blob_identity(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        repo=ROOT.parents[1]
        for donor in probe['donor_sources']:
            source=repo/donor['path']
            self.assertTrue(source.is_file(),donor['path'])
            raw=source.read_bytes()
            git_sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            self.assertEqual(git_sha,donor['git_blob_sha1'],donor['path'])
    def test_coconnect_graph_has_typed_links_without_implicit_authority(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        nodes={n['id'] for n in probe['nodes']}
        self.assertEqual(len(nodes),len(probe['nodes']))
        self.assertLessEqual(len(nodes),probe['acceptance_contract']['relation_query_budget']['max_nodes'])
        self.assertLessEqual(len(probe['edges']),probe['acceptance_contract']['relation_query_budget']['max_edges'])
        keys=set()
        for e in probe['edges']:
            self.assertTrue(e['from'] in nodes and e['to'] in nodes)
            self.assertNotEqual(e['from'],e['to'])
            self.assertEqual(e['authority'],'NONE')
            self.assertEqual(e['action'],'NONE')
            self.assertIs(e['causal_claim'],False)
            self.assertIn(e['epistemic'],{'SOURCE_VERIFIED','CANDIDATE_SEMANTIC','HYPOTHESIS','HELD','CANDIDATE_ARCHITECTURE'})
            k=(e['from'],e['type'],e['to'])
            self.assertNotIn(k,keys)
            keys.add(k)
    def test_coconnect_tree_is_just_one_explicit_projection(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        path=probe['tree_view']['one_proposed_parent_path']
        for parent,child in zip(path,path[1:]):
            self.assertTrue(any(e['from']==child and e['to']==parent and e['family']=='candidate_parent' for e in probe['edges']))
        self.assertEqual(probe['tree_view']['type'],'CANDIDATE_PROJECTION_NOT_UNIQUE_GENEALOGY')
        self.assertTrue(probe['tree_view']['preserve_cross_links'])
        self.assertEqual(set(probe['tree_view']['alternate_parent_or_family_affinities']),{'co_lol','co_play'})
    def test_coconnect_coverage_includes_upstream_downstream_and_unknowns(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        fam={x['family'] for x in probe['edges']}
        for k in probe['acceptance_contract']['required_classes']:
            self.assertIn(k,fam,k)
        self.assertIn('INVERSE_AND_PROJECTION_LOSS',probe['missing_link_classes_to_check_on_new_feature'])
        self.assertIn('UNKNOWN_OR_NOT_YET_SEARCHED',probe['missing_link_classes_to_check_on_new_feature'])
    def test_coconnect_main_search_miss_cannot_be_interpreted_as_absence(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        note=probe['observed_gap']['search_observation']
        self.assertEqual(note['query'],'CoGiggle')
        self.assertEqual(note['results'],0)
        self.assertEqual(note['limitation'],'BOUNDED_NONOBSERVATION_NOT_ABSENCE')
        self.assertIn('Explicit feature manifest readback',note['recovery'])
        self.assertIn('MAIN_SEARCH_MISS_NE_TERM_ABSENCE',probe['nonclaims'])
    def test_coconnect_trigger_rules_are_bounded_and_not_self_executing(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        self.assertGreaterEqual(len(probe['future_wake_signals']),7)
        self.assertTrue(all(s['signal'] and s['action'] for s in probe['future_wake_signals']))
        b=probe['acceptance_contract']['relation_query_budget']
        self.assertLessEqual(b['max_depth'],2)
        self.assertLessEqual(b['max_wake_candidates'],4)
        self.assertEqual(b['live_workers'],0)
        self.assertEqual(probe['acceptance_contract']['external_effects'],0)
        self.assertIs(probe['acceptance_contract']['auto_publish'],False)
        self.assertIs(probe['acceptance_contract']['independent_receiver_ack'],False)

    def _alien_probe(self):
        return json.loads((ROOT/'relation_coverage_r0.json').read_text())['alien_tree_lens']

    def test_alien_tree_preserves_four_meanings_without_claiming_et(self):
        lens=self._alien_probe()
        meanings={x['id'] for x in lens['interpretations']}
        self.assertEqual(meanings,{
            'OUTSIDE_THE_CURRENT_ONTOLOGY',
            'UNKNOWN_NONHUMAN_PARTICIPANT',
            'EXTRATERRESTRIAL_BIOLOGY_OR_INTELLIGENCE',
            'LITERAL_ALIEN_OR_NONNATIVE_TREE'
        })
        empirical=next(x for x in lens['interpretations'] if x['id']=='EXTRATERRESTRIAL_BIOLOGY_OR_INTELLIGENCE')
        self.assertEqual(empirical['epistemic'],'ET_EMPIRICAL_HYPOTHESIS')
        self.assertEqual(empirical['status'],'NOT_TESTED')
        self.assertIn('NOT_ET_DETECTION',lens['state'])
        self.assertIn('NO_REAL_ET_EVIDENCE',lens['result'])

    def test_alien_tree_does_not_assume_root_or_stable_individual(self):
        lens=self._alien_probe()
        kinds={x['id'] for x in lens['allowed_topology_candidates']}
        self.assertEqual(kinds,{
          'ROOTED_TREE','DIRECTED_ACYCLIC_GRAPH','CYCLIC_GRAPH',
          'HYPERGRAPH','TEMPORAL_EVENT_GRAPH','UNKNOWN_SHAPE'
        })
        self.assertIn('UNKNOWN_SHAPE',kinds)
        self.assertIn('THREE_WAY',{x['id'] for x in lens['adversarial_cases']})
        self.assertIn('NO_ROOT',{x['id'] for x in lens['adversarial_cases']})

    def test_alien_tree_synthetic_loss_is_measured(self):
        lens=self._alien_probe()
        canary=lens['synthetic_topology_canary']
        self.assertEqual(canary['state'],'SYNTHETIC_ONLY_NOT_EMPIRICAL')
        facts=canary['facts']
        self.assertEqual(len(facts),5)
        self.assertEqual(len({x['id'] for x in facts}),len(facts))
        self.assertTrue(all(set(x['members']).issubset(set(canary['nodes'])) for x in facts))
        def would_close_cycle(src,dst,edges):
            pending=[dst]; visited=set()
            while pending:
                current=pending.pop()
                if current==src:return True
                if current in visited:continue
                visited.add(current)
                pending.extend(b for a,b in edges if a==current)
            return False
        for mode in ('TREE','DAG','TYPED_HYPERGRAPH'):
            preserved=[]; directed=[]; chosen_parent=set()
            for fact in facts:
                if fact['kind']=='N_ARY':
                    if mode=='TYPED_HYPERGRAPH':preserved.append(fact['id'])
                    continue
                self.assertEqual(fact['kind'],'DIRECTED_PAIR')
                a,b=fact['members']
                if mode=='TREE' and fact['relation']=='PARENT_OF' and b in chosen_parent:
                    continue
                if mode!='TYPED_HYPERGRAPH' and would_close_cycle(a,b,directed):
                    continue
                preserved.append(fact['id'])
                if mode!='TYPED_HYPERGRAPH':directed.append((a,b))
                if mode=='TREE' and fact['relation']=='PARENT_OF':chosen_parent.add(b)
            self.assertEqual(preserved,canary['expected_retained_fact_ids'][mode])
            self.assertEqual(len(facts)-len(preserved),canary['expected_lost_counts'][mode])
        self.assertEqual(canary['expected_lost_counts'],{
          'TREE':3,'DAG':2,'TYPED_HYPERGRAPH':0
        })

    def test_alien_tree_no_effect_or_contact_authority(self):
        lens=self._alien_probe()
        g=lens['guardrails']
        self.assertIs(g['observation_ne_origin'],True)
        self.assertIs(g['hypothesis_ne_detection'],True)
        self.assertIs(g['unusual_morphology_ne_personhood'],True)
        self.assertIs(g['candidate_edge_ne_causality'],True)
        self.assertIs(g['graph_projection_ne_source_mutation'],True)
        self.assertIs(g['no_new_authority'],True)
        self.assertEqual(g['external_effects'],0)
        self.assertEqual(g['live_inference_workers'],0)
        self.assertIs(g['no_publications_or_contact_attempts'],True)

    def test_alien_tree_adversarial_cases_are_bounded_and_explain_loss(self):
        lens=self._alien_probe()
        self.assertEqual(len(lens['adversarial_cases']),7)
        self.assertLessEqual(len(lens['allowed_topology_candidates']),lens['guardrails']['max_candidate_topologies'])
        self.assertLessEqual(len(lens['adversarial_cases']),lens['guardrails']['max_adversarial_cases'])
        self.assertTrue(all(x['id'] and x['input'] and x['expected'] for x in lens['adversarial_cases']))
        self.assertEqual(lens['primary_wake_signal'],'KNOWN_RELATION_SCHEMA_FAILS_TO_PRESERVE_OBSERVED_STRUCTURE')

    def test_alien_tree_cross_links_are_hypotheses_not_implicit_authority(self):
        probe=json.loads((ROOT/'relation_coverage_r0.json').read_text())
        alien_edges=[e for e in probe['edges'] if e['from']=='co_alien_tree']
        self.assertGreaterEqual(len(alien_edges),8)
        self.assertTrue(all(e['epistemic'] not in ('OBSERVED_ET','CONTACT_CONFIRMED') for e in alien_edges))
        self.assertTrue(all(e['authority']=='NONE' and e['action']=='NONE' and e['causal_claim'] is False for e in alien_edges))
        self.assertIn('UNKNOWN_PARTICIPANT_NE_AUTHORITY',probe['nonclaims'])
        self.assertIn('TREE_NE_REQUIRED_RELATION_TOPOLOGY',probe['nonclaims'])

    def test_schema(self):self.assertEqual(self.m['schema'],'CoAll.CoPublicationFederation.FirstProof.R0')
    def test_validate(self):self.assertTrue(validate(self.m))
    def test_exclusive_six_routes(self):self.assertEqual(len(self.m['routes']),6)
    def test_source_pin(self):self.assertEqual(self.m['source']['git_blob_sha1'],'9202ab5a8d0bfef509922c8c047363ea7a346ce2')
    def test_all_six_claims(self):self.assertEqual([x['id'] for x in self.m['claims']],['C01','C02','C03','C04','C05','C06'])
    def test_no_fact_drift(self):
        kernel=self.m['claim_ids_required_in_every_route']
        for r in self.m['routes']:self.assertEqual(r['claims'],kernel)
    def test_sources_public(self):
        self.assertTrue(all(x['action_url'].startswith('https://github.com/CoCivium/CoCivium/') for x in self.m['routes']))
    def test_qualify_proposals(self):self.assertIn('NOT_RUNTIME',self.m['source']['status'])
    def test_no_runtime_claim(self):self.assertIn('NOT_SUBSTACK_POSTED',self.m['status'])
    def test_no_published_posts(self):self.assertEqual(self.m['actual_substack_posts_created'],0)
    def test_no_external_sends(self):self.assertEqual(self.m['external_sends'],0)
    def test_giggle_is_explicitly_opt_in(self):
        g=self.m['giggle_lens']
        self.assertEqual(g['default'],'OFF_UNTIL_EXPLICIT_READER_CLICK')
        self.assertEqual(g['classification'],'HUMOROUS')
        self.assertEqual(g['privacy'],'NO_INFERENCE_NO_STORAGE_NO_TRANSMISSION')
    def test_giggle_examples_cover_original_six_routes(self):
        g=self.m['giggle_lens']
        self.assertEqual({e['route_id'] for e in g['examples']},{r['id'] for r in self.m['routes']})
        self.assertEqual(g['source_claim_ids'],self.m['claim_ids_required_in_every_route'])
        self.assertTrue(all(e['claim_id'] in g['source_claim_ids'] for e in g['examples']))
    def test_giggle_never_downgrades_evidence_labels(self):
        g=self.m['giggle_lens']
        self.assertIn('HUMOR_NE_EVIDENCE',g['nonclaims'])
        self.assertIn('PUNCHLINE_NE_PERFORMANCE_METRIC',g['nonclaims'])
        self.assertTrue(all(r['claims']==self.m['claim_ids_required_in_every_route'] for r in self.m['routes']))
    def test_giggle_missing_route_fails_closed(self):
        bad=deepcopy(self.m);bad['giggle_lens']['examples'].pop()
        with self.assertRaises(AssertionError):validate(bad)
    def test_giggle_claim_drift_fails_closed(self):
        bad=deepcopy(self.m);bad['giggle_lens']['examples'][0]['claim_id']='FAKE'
        with self.assertRaises(AssertionError):validate(bad)
    def test_giggle_forced_mode_fails_closed(self):
        bad=deepcopy(self.m);bad['giggle_lens']['default']='ON_ALWAYS'
        with self.assertRaises(AssertionError):validate(bad)
    def test_giggle_interface_has_reversible_control(self):
        html=(ROOT/'index.html').read_text()
        self.assertIn('id="giggle-toggle"',html)
        self.assertIn('id="giggle-panel" hidden',html)
        self.assertIn('aria-controls="giggle-panel"',html)
        self.assertIn("giggle=!giggle;show()",html)
        self.assertIn("HUMOROUS illustration, not evidence",html)
    def test_no_tracking(self):self.assertIs(self.m['tracking'],False)
    def test_no_inferred_interests(self):self.assertIs(self.m['interest_inference'],False)
    def test_no_read_implies_send(self):self.assertEqual(self.m['reader_feedback_writeback'],'NONE_LOCAL_PREVIEW_ONLY')
    def test_no_fake_deadline(self):self.assertEqual(self.m['urgency']['mode'],'NONE_NO_REAL_DEADLINE_VERIFIED')
    def test_no_countdown(self):self.assertIs(self.m['urgency']['countdowns'],False)
    def test_no_deliberate_link_rot(self):self.assertIs(self.m['urgency']['deliberately_expiring_links'],False)
    def test_history_chain(self):self.assertEqual(self.m['edition_history'][1]['predecessor'],'r0.1')
    def test_history_nonpublic(self):self.assertTrue(all(v['kind'].startswith('LOCAL_SYNTHETIC') for v in self.m['edition_history']))
    def test_current_declared(self):self.assertEqual(self.m['current_edition'],'r0.2')
    def test_12_axes(self):self.assertEqual(len(self.m['logical_axes']),12)
    def test_10_options_each(self):self.assertTrue(all(len(set(x))==10 for x in self.m['logical_axes'].values()))
    def test_trillion_addresses(self):self.assertEqual(int(self.m['logical_candidate_space']),10**12)
    def test_zero_index(self):
        got=decode_index(0,self.m['logical_axes'])
        self.assertEqual(list(got.values()),[v[0] for v in self.m['logical_axes'].values()])
    def test_upper_index(self):
        got=decode_index(10**12-1,self.m['logical_axes'])
        self.assertEqual(list(got.values()),[v[-1] for v in self.m['logical_axes'].values()])
    def test_random_lazy_index(self):
        got=decode_index(314159265358,self.m['logical_axes'])
        self.assertEqual(len(got),12)
        self.assertTrue(all(v in self.m['logical_axes'][k] for k,v in got.items()))
    def test_negative_index_rejected(self):
        with self.assertRaises(ValueError):decode_index(-1,self.m['logical_axes'])
    def test_too_large_index_rejected(self):
        with self.assertRaises(ValueError):decode_index(10**12,self.m['logical_axes'])
    def test_float_index_rejected(self):
        with self.assertRaises(ValueError):decode_index(7.0,self.m['logical_axes'])
    def test_mutated_claim_is_held(self):
        b=deepcopy(self.m);b['routes'][0]['claims'].pop()
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_deadline_is_held(self):
        b=deepcopy(self.m);b['urgency']['countdowns']=True
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_tracking_is_held(self):
        b=deepcopy(self.m);b['tracking']=True
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_link_is_held(self):
        b=deepcopy(self.m);b['routes'][0]['action_url']='https://evil.invalid/login'
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_history_is_held(self):
        b=deepcopy(self.m);b['edition_history'][1]['predecessor']=None
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_source_state_is_held(self):
        b=deepcopy(self.m);b['source']['status']='VERIFIED_UNIVERSAL_DEPLOYMENT'
        with self.assertRaises(AssertionError):validate(b)
    def test_expected_html_exists(self):self.assertTrue((ROOT/'index.html').exists())
    def test_exact_generated_parity(self):self.assertEqual((ROOT/'index.html').read_text(),build(self.m))
    def test_no_script_injection(self):
        b=deepcopy(self.m);b['routes'][0]['entry']='</script><img onerror="bad()">'
        html=build(b)
        self.assertNotIn('</script><img',html)
        self.assertIn('\\u003c/script\\u003e',html)
    def test_csp_blocks_network(self):self.assertIn("connect-src 'none'",(ROOT/'index.html').read_text())
    def test_no_external_scripts_or_styles(self):
        p=Tags();p.feed((ROOT/'index.html').read_text())
        self.assertEqual(p.external,[])
    def test_all_html_ids_unique(self):
        p=Tags();p.feed((ROOT/'index.html').read_text())
        self.assertEqual(len(p.ids),len(set(p.ids)))
    def test_external_links_allowlisted(self):
        p=Tags();p.feed((ROOT/'index.html').read_text())
        self.assertTrue(all((link == 'https://github.com/CoCivium/CoCivium' or link.startswith('https://github.com/CoCivium/CoCivium/') or link.startswith('#') or link == 'https://rickpublic.substack.com/p/does-ai-make-the-stock-market-obsolete') for link in p.links))
    def test_reader_bridge_discoverable_from_first_screen(self):
        html=(ROOT/'index.html').read_text()
        self.assertEqual(html.count('href="#edge-in-heading"'),1)
        self.assertIn('Compare a published article with the draft chapter',html)
    def test_one_verified_rickpublic_published_link(self):
        html=(ROOT/'index.html').read_text()
        self.assertEqual(html.count('href="https://rickpublic.substack.com/p/does-ai-make-the-stock-market-obsolete"'),1)
        self.assertIn('Read the existing public article',html)
        self.assertIn('Its forecasts are hypotheses',html)
    def test_draft_chapter_pinned_and_explicitly_unpublished(self):
        html=(ROOT/'index.html').read_text()
        self.assertEqual(html.count('https://github.com/CoCivium/CoCivium/blob/1487b330d35ddec03f32000e6846dd3b35ed774a/docs/books/great-refact-r0/01-your-product-is-still-here.md'),1)
        self.assertIn('source-controlled, unmerged working draft, not a published Substack article',html)
        self.assertIn('21bb508b5b0fe9e34011590539993e14d4325edc',html)
    def test_reader_bridge_no_automatic_send_and_clear_exit(self):
        html=(ROOT/'index.html').read_text()
        self.assertIn('id="edge-in-heading"',html)
        self.assertIn('or simply leave',html)
        self.assertIn('No reading behavior or responses are transmitted by this page.',html)
        self.assertIn("connect-src 'none'",html)
    def test_single_html_manifest(self):self.assertEqual((ROOT/'index.html').read_text().count('id="manifest"'),1)
    def test_keyboard_access(self):self.assertIn('focus-visible',(ROOT/'index.html').read_text())
    def test_reduced_motion(self):self.assertIn('prefers-reduced-motion',(ROOT/'index.html').read_text())
    def test_source_digests_wrap_without_mobile_overflow(self):
        html=(ROOT/'index.html').read_text()
        template=(ROOT/'template.html').read_text()
        self.assertIn('.panel{overflow-wrap:anywhere;',html)
        self.assertIn('.panel{overflow-wrap:anywhere;',template)
    def test_cyclic_highlight_contract_and_source(self):
        asset=json.loads((ROOT/'coliving_highlight_cycle_r0.json').read_text())
        schema=json.loads((ROOT.parents[1]/'schemas/coliving-highlight-asset-v0.1.schema.json').read_text())
        self.assertEqual(asset['schema'],'CoLivingHighlightAsset.v0.1')
        self.assertTrue(set(schema['required']).issubset(asset))
        self.assertTrue(set(asset).issubset(schema['properties']))
        self.assertEqual(asset['privacy_class'],'PUBLIC_SAFE')
        self.assertEqual(asset['read_mode'],'SNAPSHOT_PINNED')
        self.assertEqual(asset['currentness']['state'],'UNKNOWN')
        self.assertIn('NOT_PHYSICS_OR_GD_PROOF',asset['readiness'])
        self.assertIn('candidate',asset['projection_ref'].lower())
        self.assertTrue((ROOT/'HIGHLIGHT_CYCLIC_REGENERATION_R0.md').is_file())
        self.assertEqual(len(asset['source_bindings']),len(set(asset['source_bindings'])))
        for binding in asset['source_bindings']:
            if not binding.startswith('github:'):continue
            src,digest=binding[len('github:'):].split('@blob:')
            repo_id,relpath=src.split(':',1)
            self.assertEqual(repo_id,'CoCivium/CoCivium')
            raw=(ROOT.parents[1]/relpath).read_bytes()
            git_sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            self.assertEqual(git_sha,digest)

    def test_cyclic_synthetic_four_regimes_no_perpetual_motion_claim(self):
        data=json.loads((ROOT/'cyclic_regeneration_canary_r0.json').read_text())
        self.assertEqual(data['cycles'],8)
        self.assertEqual(data['schema'],'CoAll.CoAmplificatory.CycleCanary.R0')
        self.assertIn('SYNTHETIC',data['state'])
        self.assertEqual(data['unit'],'NORMALIZED_DIMENSIONLESS_PROXY_NOT_JOULES_OR_USER_UTILITY')
        results={}
        for r in data['regimes']:
            value=r['initial']
            predicted=[value]
            for step in range(data['cycles']):
                correction=r['correction_per_cycle'] if step>=r['correction_after_cycle'] else 0
                value=min(r['ceiling'],max(0,(1-r['damping'])*value+r['drive_per_cycle']-correction))
                predicted.append(value)
            self.assertEqual(len(predicted),len(r['expected_series']))
            for actual,expected in zip(predicted,r['expected_series']):
                self.assertAlmostEqual(actual,expected,places=5)
            results[r['id']]=predicted
        self.assertEqual(len(results),4)
        self.assertLess(results['damped_closed_proxy'][-1],1)
        self.assertEqual(results['bounded_replenishment'][-1],1.5)
        self.assertGreater(results['unchecked_positive_feedback_proxy'][-1],results['bounded_replenishment'][-1])
        self.assertLess(results['adaptive_correction'][-1],results['bounded_replenishment'][-1])
        self.assertIsNone(data['audit']['measured_energy_joules'])
        self.assertIsNone(data['audit']['verified_reader_improvement'])
        self.assertIsNone(data['audit']['qualified_gd_measurement'])
        self.assertEqual(data['audit']['external_effect_count'],0)

    def test_cyclic_highlight_is_optional_and_not_seventh_claim(self):
        page=(ROOT/'index.html').read_text()
        self.assertIn('id="cyclic-heading"',page)
        self.assertIn('id="cyclic-details"',page)
        self.assertIn('<summary>Explore four bounded cycle behaviors</summary>',page)
        self.assertIn('.pulse-highlight{background:linear-gradient(155deg,#17382f,#0e2724)',page)
        self.assertIn('synthetic normalized examples, not physical measurements',page)
        self.assertIn('G_d remains a philosophical or explicitly testable hypothesis lane',page)
        self.assertIn('docs/Architecture/COAMPLIFICATORY_CYCLIC_REGENERATION_R0_20261026.md',page)
        self.assertEqual(len(self.m['claims']),6)
        self.assertEqual(len(self.m['routes']),6)
        self.assertIn("connect-src 'none'",page)
    def test_forest_surfaces_are_selective_and_contrast_friendly(self):
        html=(ROOT/'index.html').read_text()
        template=(ROOT/'template.html').read_text()
        for surface in (html,template):
            self.assertIn('--forest:#15382e',surface)
            self.assertIn('--forest-deep:#0f2523',surface)
            self.assertIn('--forest-edge:#638f75',surface)
            self.assertIn('var(--forest-glow)',surface)
            self.assertIn('.aside{align-self:start;background:linear-gradient(160deg,var(--forest),var(--forest-deep))',surface)
            self.assertIn('.giggle{margin-top:16px;background:linear-gradient(155deg,#17372f,#102a25)',surface)
            self.assertIn('.public-bridge{background:linear-gradient(165deg,#142f29,#0e2522)',surface)
            self.assertIn('class="panel section public-bridge" aria-labelledby="edge-in-heading"',surface)
            self.assertIn('@media(prefers-contrast:more)',surface)
            self.assertIn('button:focus-visible,a:focus-visible',surface)
            self.assertIn('class="panel" id="article"',surface)
            self.assertIn('class="panel section" aria-labelledby="editions-heading"',surface)

    def test_forest_text_and_edge_wcag_contrast(self):
        html=(ROOT/'index.html').read_text()
        tokens=dict(re.findall(r'(--[a-z-]+):(#(?:[a-fA-F0-9]{6}))',html))
        def luminance(value):
            values=[int(value[i:i+2],16)/255 for i in (1,3,5)]
            linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
            return 0.2126*linear[0]+0.7152*linear[1]+0.0722*linear[2]
        def contrast(a,b):
            l1,l2=sorted((luminance(a),luminance(b)),reverse=True)
            return (l1+0.05)/(l2+0.05)
        backgrounds=[tokens['--forest'],tokens['--forest-deep'],'#17372f','#102a25','#142f29','#0e2522']
        for bg in backgrounds:
            for foreground in (tokens['--ink'],tokens['--muted']):
                self.assertGreaterEqual(contrast(foreground,bg),4.5,(foreground,bg))
            self.assertGreaterEqual(contrast(tokens['--forest-edge'],bg),3.0,(tokens['--forest-edge'],bg))
    def test_mobile_breakpoints(self):self.assertIn('@media(max-width:760px)',(ROOT/'index.html').read_text())
    def test_no_raw_private_media(self):self.assertNotIn('WhatsApp',(ROOT/'index.html').read_text())
    def test_title_and_source(self):self.assertIn('The Great ReFact | Six reader doorways',(ROOT/'index.html').read_text())
    def test_no_fake_viral_guarantee(self):self.assertIn('No artificial timers',(ROOT/'index.html').read_text())
    def test_action_not_automatic(self):self.assertIn('UNSENT_LOCAL_PROPOSAL',(ROOT/'index.html').read_text())
    def test_conditional_false_metrics(self):self.assertFalse(any('300% more leads' in r['entry'] for r in self.m['routes']))
    def test_claim_kernel_not_medium_specific(self):self.assertTrue(all('claims' in r for r in self.m['routes']))
    def test_manifest_is_ascii_transportable(self):self.assertTrue((ROOT/'manifest.json').read_text().isascii())
    def test_static_source_is_not_substack_domain(self):self.assertNotIn('substack.com/p/',self.m['source']['url'])
    def test_local_only_copy_preview(self):self.assertIn('No feedback prepared or sent.',(ROOT/'index.html').read_text())
    def test_all_actions_named(self):self.assertTrue(all(r['task'] and r['action_label'] for r in self.m['routes']))
    def test_no_brittle_snapshot(self):self.assertGreater(len(self.m['edition_history']),1)
    def test_risk_counterpoint_present(self):self.assertTrue(all(len(r['counterpoint'])>30 for r in self.m['routes']))
    def test_status_unknown_not_erased(self):self.assertTrue(any('time saved' in c['text'] for c in self.m['claims']))

if __name__=='__main__':unittest.main(verbosity=2)
