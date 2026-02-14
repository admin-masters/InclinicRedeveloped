from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Campaign, CampaignSystem, Collateral, Doctor, Event, FieldRep, ReportingEvent, ShareInstance, UserProfile
from .services import create_share, doctor_status


class BaseSetup(TestCase):
    databases = {'default', 'reporting'}

    def setUp(self):
        self.publisher = User.objects.create_user('pub', password='x')
        UserProfile.objects.create(user=self.publisher, role='publisher')
        self.brand = User.objects.create_user('bm', password='x')
        UserProfile.objects.create(user=self.brand, role='brand_manager')
        self.campaign = Campaign.objects.create(
            company_name='C', brand_name='B', expected_doctors=10,
            contact_name='A', contact_phone='123', contact_email='a@a.com', created_by=self.publisher,
        )
        self.system = CampaignSystem.objects.create(campaign=self.campaign, system='inclinic')
        self.rep = FieldRep.objects.create(campaign=self.campaign, brand_rep_id='REP1', name='Rep', email='rep@x.com', phone='9999999999')
        self.col = Collateral.objects.create(campaign=self.campaign, system=self.system, classification='doctor_long', content_title='T', item_type='video', vimeo_url='https://vimeo.com/123')
        self.doc = Doctor.objects.create(campaign=self.campaign, field_rep=self.rep, name='Doc', whatsapp_number='8888888888')


class FlowTests(BaseSetup):
    def test_publisher_access(self):
        self.client.login(username='pub', password='x')
        resp = self.client.get(reverse('dashboard'))
        self.assertContains(resp, 'Publisher Dashboard')

    def test_brand_cannot_access_add_campaign(self):
        self.client.login(username='bm', password='x')
        resp = self.client.get(reverse('add_campaign'))
        self.assertEqual(resp.status_code, 403)

    def test_share_creates_event_and_link(self):
        share, url = create_share(self.campaign, self.rep, self.doc, self.col)
        self.assertIn('api.whatsapp.com', url)
        self.assertTrue(Event.objects.filter(share_instance=share, event_type='share_initiated').exists())

    def test_status_logic(self):
        share, _ = create_share(self.campaign, self.rep, self.doc, self.col)
        self.assertEqual(doctor_status(self.rep, self.doc), 'Sent')
        share.created_at = timezone.now() - timedelta(days=7)
        share.save(update_fields=['created_at'])
        self.assertEqual(doctor_status(self.rep, self.doc), 'Send Reminder')

    def test_link_clicked_once(self):
        share, _ = create_share(self.campaign, self.rep, self.doc, self.col)
        self.client.post(reverse('short_link', args=[share.short_code]), {'phone': self.doc.whatsapp_number})
        self.assertTrue(Event.objects.filter(share_instance=share, event_type='link_clicked').exists())
        self.assertTrue(Event.objects.filter(share_instance=share, event_type='landing_access').exists())

    def test_sync_reporting(self):
        share, _ = create_share(self.campaign, self.rep, self.doc, self.col)
        Event.objects.create(event_type='pdf_downloaded', campaign=self.campaign, collateral=self.col, field_rep=self.rep, doctor=self.doc, share_instance=share)
        self.assertGreater(Event.objects.count(), 0)
        call_command('sync_reporting')
        self.assertEqual(Event.objects.count(), 0)
        self.assertGreater(ReportingEvent.objects.using('reporting').count(), 0)

    def test_reporting_view_uses_reporting_db(self):
        ReportingEvent.objects.using('reporting').create(
            id='11111111-1111-1111-1111-111111111111', event_type='link_clicked', campaign_id=self.campaign.id,
            collateral_id=self.col.id, field_rep_id=self.rep.id, doctor_id=self.doc.id, share_instance_id=1,
            created_at=timezone.now(),
        )
        self.client.login(username='bm', password='x')
        resp = self.client.get(reverse('brand_reports', args=[self.campaign.id]))
        self.assertContains(resp, 'Clicked: 1')
