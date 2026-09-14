from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from conference.models import EventVenue, EventInquiry, EventType, VenueLayout
from booking.models.addon import Addon
from conference.views import EventInquiryForm

User = get_user_model()


class ConferenceModelTests(TestCase):
    def setUp(self):
        self.venue = EventVenue.objects.create(
            name="Grand Ballroom",
            capacity=500,
            layout_options="Theatre: 500 pax\nBanquet: 300 pax",
            is_active=True,
            is_featured=True
        )
        self.event_type = EventType.objects.create(
            name="Royal Wedding",
            icon="fa-ring",
            is_featured=True,
            is_active=True
        )
        self.layout_theatre = VenueLayout.objects.create(
            venue=self.venue,
            name="Theatre",
            capacity=500,
            display_order=1
        )
        self.layout_banquet = VenueLayout.objects.create(
            venue=self.venue,
            name="Banquet",
            capacity=300,
            display_order=2
        )
        self.addon = Addon.objects.create(
            name="High Tea Service",
            applies_to="events",
            price_type="per_person",
            is_active=True
        )

    def test_event_type_slug_and_str(self):
        self.assertEqual(self.event_type.slug, "royal-wedding")
        self.assertEqual(str(self.event_type), "Royal Wedding")

    def test_venue_parsed_layouts_prefers_active_layouts(self):
        layouts = self.venue.parsed_layouts
        self.assertEqual(len(layouts), 2)
        self.assertEqual(layouts[0]['name'], "Theatre")
        self.assertEqual(layouts[0]['capacity'], 500)

    def test_venue_parsed_layouts_fallback_to_string(self):
        venue2 = EventVenue.objects.create(
            name="Simple Meeting Room",
            capacity=20,
            layout_options="Boardroom: 20 pax\nU-Shape: 15 pax",
            is_active=True
        )
        layouts = venue2.parsed_layouts
        self.assertEqual(len(layouts), 2)
        self.assertEqual(layouts[0]['name'], "Boardroom")
        self.assertEqual(layouts[0]['value'], "20 pax")

    def test_inquiry_has_conflict_detection(self):
        tomorrow = date.today() + timedelta(days=1)
        inq1 = EventInquiry.objects.create(
            venue=self.venue,
            event_type=self.event_type,
            name="Guest A",
            email="a@example.com",
            phone="9812345678",
            event_date=tomorrow,
            guest_count=150,
            status='confirmed'
        )
        inq2 = EventInquiry.objects.create(
            venue=self.venue,
            event_type=self.event_type,
            name="Guest B",
            email="b@example.com",
            phone="9887654321",
            event_date=tomorrow,
            guest_count=200,
            status='pending'
        )
        self.assertTrue(inq2.has_conflict)

        # Different date should not conflict
        inq3 = EventInquiry.objects.create(
            venue=self.venue,
            name="Guest C",
            email="c@example.com",
            phone="9811122233",
            event_date=tomorrow + timedelta(days=5),
            guest_count=50,
            status='pending'
        )
        self.assertFalse(inq3.has_conflict)


class ConferenceFormValidationTests(TestCase):
    def setUp(self):
        self.venue = EventVenue.objects.create(
            name="Grand Ballroom",
            capacity=500,
            is_active=True
        )
        self.layout_banquet = VenueLayout.objects.create(
            venue=self.venue,
            name="Banquet",
            capacity=250
        )

    def test_guest_count_exceeding_layout_capacity_fails(self):
        tomorrow = date.today() + timedelta(days=2)
        form_data = {
            'name': 'Ram Shrestha',
            'email': 'ram@example.com',
            'phone': '9855012345',
            'event_date': tomorrow,
            'guest_count': 260,  # Exceeds banquet capacity 250
            'preferred_layout': self.layout_banquet.id,
        }
        form = EventInquiryForm(data=form_data, venue=self.venue)
        self.assertFalse(form.is_valid())
        self.assertIn('guest_count', form.errors)

    def test_end_time_before_start_time_fails(self):
        tomorrow = date.today() + timedelta(days=2)
        form_data = {
            'name': 'Ram Shrestha',
            'email': 'ram@example.com',
            'phone': '9855012345',
            'event_date': tomorrow,
            'start_time': '16:00',
            'end_time': '14:00',
            'guest_count': 100,
        }
        form = EventInquiryForm(data=form_data, venue=self.venue)
        self.assertFalse(form.is_valid())
        self.assertIn('end_time', form.errors)

    def test_valid_form_submission(self):
        tomorrow = date.today() + timedelta(days=2)
        form_data = {
            'name': 'Ram Shrestha',
            'email': 'ram@example.com',
            'phone': '9855012345',
            'event_date': tomorrow,
            'start_time': '10:00',
            'end_time': '17:00',
            'guest_count': 200,
            'preferred_layout': self.layout_banquet.id,
        }
        form = EventInquiryForm(data=form_data, venue=self.venue)
        self.assertTrue(form.is_valid())


class PublicViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.venue = EventVenue.objects.create(
            name="Janaki Hall",
            slug="janaki-hall",
            capacity=400,
            is_active=True,
            is_featured=True
        )
        self.event_type = EventType.objects.create(
            name="Weddings",
            slug="weddings",
            icon="fa-ring",
            is_featured=True,
            is_active=True
        )
        self.addon = Addon.objects.create(
            name="Buffet Catering",
            applies_to="events",
            price_type="per_person",
            is_active=True
        )

    def test_venue_list_view(self):
        url = reverse('conference:venue_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('venues', response.context)
        self.assertIn('event_types', response.context)

    def test_venue_detail_view_and_post(self):
        self.venue.event_types.add(self.event_type)
        url = reverse('conference:venue_detail', kwargs={'slug': self.venue.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST inquiry
        post_data = {
            'name': 'Sita Sharma',
            'email': 'sita@example.com',
            'phone': '9841234567',
            'event_type': self.event_type.id,
            'event_date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'guest_count': 150,
            'addons': [self.addon.id],
            'catering_required': 'on',
            'notes': 'Looking forward to an evening reception.'
        }
        post_response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(post_response.status_code, 200)
        self.assertTrue(EventInquiry.objects.filter(name='Sita Sharma').exists())
        inquiry = EventInquiry.objects.get(name='Sita Sharma')
        self.assertEqual(inquiry.addons.count(), 1)

    def test_homepage_hero_featured_event_spotlight(self):
        url = reverse('homepage:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('featured_events', response.context)
        self.assertContains(response, "Weddings")
        self.assertContains(response, "Upcoming &amp; Featured Occasion")

    def test_venue_suitable_event_slugs(self):
        self.assertIn('luxury-weddings', self.venue.suitable_event_slugs)
        self.assertIn('corporate-conferences', self.venue.suitable_event_slugs)

    def test_venue_list_with_occasion_filter(self):
        url = reverse('conference:venue_list') + '?occasion=weddings'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_occasion'], 'weddings')
        self.assertContains(response, 'Filter by Occasion')

    def test_venue_detail_prepopulates_event_type(self):
        self.venue.event_types.add(self.event_type)
        url = reverse('conference:venue_detail', kwargs={'slug': self.venue.slug}) + f'?event_type={self.event_type.slug}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.initial.get('event_type'), self.event_type)


class AdminDashboardConferenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username="staff_admin",
            email="staff@hotelichchha.com",
            password="password123",
            is_staff=True,
            is_superuser=True
        )
        self.client.force_login(self.admin)
        self.venue = EventVenue.objects.create(
            name="Balmiki Hall",
            slug="balmiki-hall",
            capacity=50,
            is_active=True
        )
        self.event_type = EventType.objects.create(
            name="Corporate Summit",
            slug="corporate-summit",
            icon="fa-handshake",
            is_active=True
        )
        self.addon = Addon.objects.create(
            name="Projector & Sound",
            applies_to="events",
            price_type="per_booking",
            is_active=True
        )
        self.inquiry = EventInquiry.objects.create(
            venue=self.venue,
            event_type=self.event_type,
            name="Hari Bahadur",
            email="hari@example.com",
            phone="9851000000",
            event_date=date.today() + timedelta(days=7),
            guest_count=30,
            status='pending'
        )

    def test_admin_conference_dashboard_tabs(self):
        url = reverse('admin_dashboard:conference_dashboard')
        for tab in ['venues', 'inquiries', 'event_types', 'services']:
            response = self.client.get(f"{url}?tab={tab}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['active_tab'], tab)

    def test_inquiry_detail_json_view(self):
        url = reverse('admin_dashboard:event_inquiry_detail_json', kwargs={'pk': self.inquiry.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Hari Bahadur')
        self.assertEqual(data['venue_name'], 'Balmiki Hall')
        self.assertEqual(data['event_type'], 'Corporate Summit')

    def test_inquiry_update_status_view(self):
        url = reverse('admin_dashboard:event_inquiry_update_status', kwargs={'pk': self.inquiry.id})
        response = self.client.post(url, {'status': 'proposal_sent'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.inquiry.refresh_from_db()
        self.assertEqual(self.inquiry.status, 'proposal_sent')

    def test_admin_conference_dashboard_services_tab_unified_addons(self):
        from booking.models import Addon
        event_addon = Addon.objects.create(
            name="Audio Visual Rig",
            applies_to="events",
            price_type="per_booking",
            is_active=True
        )
        room_addon = Addon.objects.create(
            name="Extra Bed",
            applies_to="room",
            price_type="per_night",
            is_active=True
        )
        url = reverse('admin_dashboard:conference_dashboard') + '?tab=services'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        services = response.context['services']
        self.assertIn(event_addon, services)
        self.assertNotIn(room_addon, services)

    def test_addon_create_view_return_to_conference(self):
        from settings_manager.models import Currency
        currency = Currency.objects.create(name="US Dollar", iso_code="USD", symbol="$", is_published=True)
        url = reverse('admin_dashboard:addon_create')
        get_res = self.client.get(f"{url}?applies_to=events&return_to=conference")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.context['form'].initial.get('applies_to'), 'events')
        self.assertEqual(get_res.context['return_to'], 'conference')

        post_res = self.client.post(
            url,
            {
                'name': 'Gala Fireworks Display',
                'icon': 'fa-sparkles',
                'applies_to': 'events',
                'price_type': 'per_booking',
                'is_active': True,
                'order': 10,
                'return_to': 'conference',
                'prices-TOTAL_FORMS': '1',
                'prices-INITIAL_FORMS': '0',
                'prices-MIN_NUM_FORMS': '1',
                'prices-MAX_NUM_FORMS': '1000',
                'prices-0-currency': currency.id,
                'prices-0-price': '250.00',
            },
            follow=False
        )
        self.assertRedirects(post_res, reverse('admin_dashboard:conference_dashboard') + '?tab=services')


class UnifiedAddonAndVenueMappingTests(TestCase):
    def setUp(self):
        from booking.models import Addon
        self.wedding_type = EventType.objects.create(
            name="Luxury Weddings & Receptions",
            slug="luxury-weddings",
            icon="fa-ring",
            is_active=True
        )
        self.conf_type = EventType.objects.create(
            name="Corporate Conferences",
            slug="corporate-conferences",
            icon="fa-handshake",
            is_active=True
        )
        self.venue = EventVenue.objects.create(
            name="Royal Crystal Ballroom",
            capacity=400,
            is_active=True
        )
        self.addon_event = Addon.objects.create(
            name="Banquet Stage Styling",
            applies_to="events",
            price_type="per_booking",
            is_active=True
        )
        self.addon_both = Addon.objects.create(
            name="VIP Chauffeur Pickup",
            applies_to="both",
            price_type="per_booking",
            is_active=True
        )

    def test_venue_assigned_event_types(self):
        self.venue.event_types.set([self.wedding_type])
        self.assertEqual(self.venue.suitable_event_slugs, ['luxury-weddings'])
        self.assertIn("Royal Crystal Ballroom", self.wedding_type.matching_venue_names)

    def test_venue_assigned_addons(self):
        self.venue.available_addons.set([self.addon_event, self.addon_both])
        self.assertEqual(self.venue.available_addons.count(), 2)

    def test_event_type_showcase_image_url(self):
        url = self.wedding_type.showcase_image_url
        self.assertIn('/static/images/conference/event_types/weddings', url)
        self.assertTrue(url.endswith('.jpg'))
        self.assertNotIn('dd42fc2b', url)


class VenueAddonToggleAndPackageInclusionTests(TestCase):
    def setUp(self):
        from booking.models import Addon
        self.client = Client()
        self.venue = EventVenue.objects.create(
            name="Imperial Hall",
            slug="imperial-hall",
            capacity=300,
            is_active=True,
            allow_custom_addons=True
        )
        self.addon_included = Addon.objects.create(
            name="Complimentary Sound Rig",
            applies_to="events",
            price_type="per_booking",
            is_active=True,
            order=1
        )
        self.addon_optional = Addon.objects.create(
            name="Extra Stage Lighting",
            applies_to="events",
            price_type="per_booking",
            is_active=True,
            order=2
        )
        # Assign addon_included as package inclusion
        self.venue.available_addons.add(self.addon_included)

        self.type_assigned = EventType.objects.create(
            name="Imperial Banquet",
            slug="imperial-banquet",
            is_active=True
        )
        self.type_unassigned = EventType.objects.create(
            name="Board Meeting",
            slug="board-meeting",
            is_active=True
        )
        self.venue.event_types.add(self.type_assigned)

    def test_venue_package_inclusions_property(self):
        self.assertIn(self.addon_included, self.venue.included_addons)
        self.assertNotIn(self.addon_optional, self.venue.included_addons)

    def test_inquiry_form_when_allow_custom_addons_true_excludes_inclusions(self):
        form = EventInquiryForm(venue=self.venue)
        available_in_form = list(form.fields['addons'].queryset)
        self.assertIn(self.addon_optional, available_in_form)
        self.assertNotIn(self.addon_included, available_in_form)

    def test_inquiry_form_when_allow_custom_addons_false_has_no_addons(self):
        self.venue.allow_custom_addons = False
        self.venue.save()
        form = EventInquiryForm(venue=self.venue)
        self.assertEqual(form.fields['addons'].queryset.count(), 0)

    def test_venue_detail_view_context_with_toggle_on(self):
        url = reverse('conference:venue_detail', kwargs={'slug': self.venue.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Inclusions displayed
        self.assertIn(self.addon_included, response.context['venue_inclusions'])
        # Optional extra addons displayed, excluding package inclusions
        self.assertIn(self.addon_optional, response.context['event_services'])
        self.assertNotIn(self.addon_included, response.context['event_services'])

        # HTML assertions
        self.assertContains(response, "Included With This Venue")
        self.assertContains(response, "Complimentary Sound Rig")
        self.assertContains(response, "Optional Event Add-on Services")
        self.assertContains(response, "Extra Stage Lighting")

    def test_venue_detail_view_context_with_toggle_off(self):
        self.venue.allow_custom_addons = False
        self.venue.save()

        url = reverse('conference:venue_detail', kwargs={'slug': self.venue.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Inclusions still displayed
        self.assertIn(self.addon_included, response.context['venue_inclusions'])
        # Optional services empty
        self.assertEqual(len(response.context['event_services']), 0)

        # HTML assertions: inclusions visible, optional selection hidden
        self.assertContains(response, "Included With This Venue")
        self.assertContains(response, "Complimentary Sound Rig")
        self.assertNotContains(response, "Optional Event Add-on Services")
        self.assertNotContains(response, 'name="addons"')

    def test_inquiry_form_event_type_only_shows_assigned_categories(self):
        form = EventInquiryForm(venue=self.venue)
        available_types = list(form.fields['event_type'].queryset)
        self.assertIn(self.type_assigned, available_types)
        self.assertNotIn(self.type_unassigned, available_types)

    def test_inquiry_form_event_type_empty_when_no_categories_assigned(self):
        self.venue.event_types.clear()
        form = EventInquiryForm(venue=self.venue)
        self.assertEqual(form.fields['event_type'].queryset.count(), 0)

    def test_venue_detail_view_event_type_dropdown_visibility(self):
        url = reverse('conference:venue_detail', kwargs={'slug': self.venue.slug})
        # 1. With assigned event types, dropdown is present and contains assigned category
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event Category")
        self.assertContains(response, "Imperial Banquet")
        self.assertNotContains(response, "Board Meeting")

        # 2. When venue has no assigned event types, dropdown is hidden
        self.venue.event_types.clear()
        response_empty = self.client.get(url)
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, "Event Category")
        self.assertNotContains(response_empty, 'name="event_type"')

