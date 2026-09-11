from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from events.models import ExpoEvent, EventStat, FocusArea, Partner


class EventSetupMixin:
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='pass123', role='admin'
        )
        self.event = ExpoEvent.objects.create(
            year=2026,
            title='Tanzania DPI Expo 2026',
            tagline='Building the Digital Foundation',
            description='Test description',
            start_date='2026-11-18T08:00:00Z',
            end_date='2026-11-19T18:00:00Z',
            venue_name='Diamond Jubilee Expo Center',
            venue_address='Ohio Street, Dar es Salaam',
            venue_lat=-6.8161,
            venue_lng=39.2804,
            hero_images=['https://example.com/hero1.jpg'],
            is_active=True,
            is_published=True,
        )
        self.stat = EventStat.objects.create(
            event=self.event, label='Speakers', value='50+', order=1
        )
        self.focus_area = FocusArea.objects.create(
            event=self.event, num='01', title='Keynotes',
            description='Inspiring talks', accent_color='#F97316',
            badge_color='#EA580C', image_url='https://example.com/img.jpg', order=1
        )
        self.partner = Partner.objects.create(
            event=self.event, name='iDEA', logo_url='https://example.com/logo.png',
            tier='HOST', order=1
        )
        self.client = APIClient()


class LandingPageAPITest(EventSetupMixin, TestCase):
    def test_landing_page_returns_200(self):
        resp = self.client.get('/api/events/landing/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['event']['year'], 2026)
        self.assertEqual(len(data['data']['stats']), 1)
        self.assertEqual(len(data['data']['focusAreas']), 1)
        self.assertEqual(len(data['data']['partners']), 1)

    def test_landing_page_404_no_published_event(self):
        self.event.is_published = False
        self.event.save()
        resp = self.client.get('/api/events/landing/')
        self.assertEqual(resp.status_code, 404)


class AdminEventCRUDTest(EventSetupMixin, TestCase):
    def test_admin_list_requires_auth(self):
        resp = self.client.get('/api/admin/expo-events/')
        self.assertEqual(resp.status_code, 401)

    def test_admin_list_events(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/api/admin/expo-events/')
        self.assertEqual(resp.status_code, 200)

    def test_admin_retrieve_event_with_nested(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(f'/api/admin/expo-events/{self.event.year}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['year'], 2026)
        self.assertEqual(len(data['stats']), 1)
        self.assertEqual(len(data['focus_areas']), 1)
        self.assertEqual(len(data['partners']), 1)

    def test_admin_activate_event(self):
        ExpoEvent.objects.create(
            year=2027, title='Test 2027', tagline='Test',
            start_date='2027-11-18T08:00:00Z', end_date='2027-11-19T18:00:00Z',
            venue_name='Test', venue_address='Test',
            is_active=True, is_published=True,
        )
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(f'/api/admin/expo-events/{self.event.year}/activate/')
        self.assertEqual(resp.status_code, 200)
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_active)
        other = ExpoEvent.objects.get(year=2027)
        self.assertFalse(other.is_active)

    def test_admin_publish_unpublish(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(f'/api/admin/expo-events/{self.event.year}/unpublish/')
        self.assertEqual(resp.status_code, 200)
        self.event.refresh_from_db()
        self.assertFalse(self.event.is_published)

        resp = self.client.patch(f'/api/admin/expo-events/{self.event.year}/publish/')
        self.assertEqual(resp.status_code, 200)
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_published)

    def test_admin_create_event(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post('/api/admin/expo-events/', {
            'year': 2028,
            'title': 'Test 2028',
            'tagline': 'Test tagline',
            'start_date': '2028-11-18T08:00:00Z',
            'end_date': '2028-11-19T18:00:00Z',
            'venue_name': 'Test Venue',
            'venue_address': 'Test Address',
            'hero_images': [],
        }, format='json')
        self.assertEqual(resp.status_code, 201)


class AdminEventStatCRUDTest(EventSetupMixin, TestCase):
    def test_admin_list_stats(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(f'/api/admin/event-stats/?event={self.event.id}')
        self.assertEqual(resp.status_code, 200)


class AdminFocusAreaCRUDTest(EventSetupMixin, TestCase):
    def test_admin_list_focus_areas(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(f'/api/admin/focus-areas/?event={self.event.id}')
        self.assertEqual(resp.status_code, 200)


class AdminPartnerCRUDTest(EventSetupMixin, TestCase):
    def test_admin_list_partners(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(f'/api/admin/partners/?event={self.event.id}')
        self.assertEqual(resp.status_code, 200)
