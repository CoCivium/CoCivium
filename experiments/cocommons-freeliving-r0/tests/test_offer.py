import copy
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def validate(d):
    issues=[]
    def require(value, msg):
        if not value: issues.append(msg)
    a=d.get('access',{})
    f=d.get('funding',{})
    p=d.get('publication',{})
    c=d.get('community',{})
    o=d.get('outreach',{})
    e=d.get('interpretation',{})
    require(d.get('state')=='REVIEW_CANDIDATE_NOT_LIVE_DONATION_SERVICE','not_live_claim')
    require(a.get('public_research_free_to_read') is True,'public_read_access')
    require(a.get('mandatory_donation') is False,'no_required_donation')
    require(a.get('pay_to_jump_review_or_access') is False,'no_pay_to_jump')
    require(a.get('unlimited_hosted_inference_promised') is False,'no_unlimited_inference')
    require(a.get('unlimited_operating_resources_promised') is False,'no_unlimited_resources')
    require(a.get('foss_rights_and_license_check_required') is True,'licensing')
    require(f.get('donations_optional') is True,'support_optional')
    require(f.get('donations_buy_priority_governance_or_endorsement') is False,'donation_no_control')
    require(f.get('tax_deductible_claim') is None,'no_unverified_tax_claim')
    require(f.get('partners_verified_to_receive_funds')==[],'no_partner_promotion')
    require(f.get('donation_channel_status')=='HELD_UNVERIFIED','receiver_is_held')
    require(f.get('donation_url') is None,'no_payment_link')
    require(f.get('verified_recipient_id') is None,'no_unsupported_receiver')
    require(f.get('fiscal_host_affiliation') is None,'no_fiscal_host_claim')
    for needed in ['payment_processor_and_fees','recipient_specific_allocation','conflict_of_interest_disclosures']:
        require(needed in f.get('reporting_before_live_collection',[]),'financial_disclosure_'+needed)
    require(p.get('original_edition_immutable') is True,'old_versions_immutable')
    require(p.get('old_versions_recoverable_where_lawful') is True,'edition_recovery')
    require(p.get('corrections_and_retractions_exposed') is True,'corrections_visible')
    require(p.get('automatic_external_publication') is False,'no_auto_publish')
    require(p.get('reader_activity_grants_publication_authority') is False,'clicks_no_authority')
    require(p.get('generated_claims_self_certify') is False,'generator_no_authorship_proof')
    require(c.get('attribution_default')=='OPT_IN','contributor_consent')
    require(c.get('endorsement_required_for_name_use') is True,'no_inferred_affiliation')
    require(c.get('public_praise_without_consent') is False,'no_unapproved_spotlights')
    require(c.get('negative_feedback_retained') is True,'retain_dissent')
    require(c.get('tracking_or_sensitive_profiling') is False,'no_unapproved_tracking')
    require(o.get('bulk_academic_blast_enabled') is False,'no_bulk_blast')
    require(o.get('first_thousand_sent_or_authorized') is False,'no_false_thousand_claim')
    require(o.get('recipients_verified_and_permissioned')==[],'no_unverified_recipients')
    require(o.get('sender_mailbox')=='UNBOUND_INSEED_CONTEXT','no_wrong_sender')
    require(e.get('partners_endorsed') is False,'no_partner_endorsement')
    require(e.get('operational_continuous_evolution_proven') is False,'no_fake_auto_runtime')
    return issues

class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/'offer.json').read_text(encoding='utf-8'))
    def test_candidate_passes(self):self.assertEqual(validate(self.d),[])
    def test_marked_as_review_only(self):self.assertEqual(self.d['state'],'REVIEW_CANDIDATE_NOT_LIVE_DONATION_SERVICE')
    def test_no_accounts_or_recipients(self):self.assertEqual(self.d['outreach']['recipients_verified_and_permissioned'],[])
    def test_license_gate(self):self.assertTrue(self.d['access']['foss_rights_and_license_check_required'])
    def test_relevant_existing_donors(self):
        self.assertIn('COPUBLICATION_METABOLISM',self.d['source_links']['living_publication_design'])
    def test_no_fundraiser_link(self):self.assertIsNone(self.d['funding']['donation_url'])
    def test_no_perpetual_resource_promise(self):self.assertFalse(self.d['access']['unlimited_operating_resources_promised'])
    def test_statements_are_public_safe(self):
        text=(ROOT/'FREE_COMMONS_OFFER_R0.md').read_text(encoding='utf-8').lower()
        for phrase in ['status: proposed','no payment link','opt-in','corrected or retracted','not a live donation']:
            self.assertIn(phrase,text)
    def test_each_bad_mutation_rejected(self):
        cases=[
            (('access','mandatory_donation'), True),
            (('access','unlimited_hosted_inference_promised'), True),
            (('access','pay_to_jump_review_or_access'), True),
            (('funding','donation_url'),'https://example.org/pay'),
            (('funding','donation_channel_status'),'LIVE'),
            (('funding','verified_recipient_id'),'fabricated'),
            (('funding','tax_deductible_claim'), True),
            (('funding','partners_verified_to_receive_funds'),['Imaginary University']),
            (('funding','donations_buy_priority_governance_or_endorsement'),True),
            (('publication','original_edition_immutable'),False),
            (('publication','automatic_external_publication'),True),
            (('publication','reader_activity_grants_publication_authority'),True),
            (('publication','generated_claims_self_certify'),True),
            (('community','attribution_default'),'AUTOMATIC'),
            (('community','public_praise_without_consent'),True),
            (('community','tracking_or_sensitive_profiling'),True),
            (('outreach','bulk_academic_blast_enabled'),True),
            (('outreach','first_thousand_sent_or_authorized'),True),
            (('outreach','recipients_verified_and_permissioned'),['unknown@example.com']),
            (('interpretation','partners_endorsed'),True),
            (('interpretation','operational_continuous_evolution_proven'),True),
        ]
        for path,value in cases:
            with self.subTest(path=path,value=value):
                data=copy.deepcopy(self.d); data[path[0]][path[1]]=value
                self.assertNotEqual(validate(data),[])

if __name__=='__main__':unittest.main()
