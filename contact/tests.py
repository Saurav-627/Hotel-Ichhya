from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from contact.models.inquiry import ContactInquiry
from contact.models.inquiry_category import InquiryCategory

User = get_user_model()


class InquiryCategoryModelTests(TestCase):
    def test_create_inquiry_category_auto_slug(self):
        cat = InquiryCategory.objects.create(name="VIP Special Concierge")
        self.assertEqual(cat.slug, "vip-special-concierge")
        self.assertEqual(str(cat), "VIP Special Concierge")
        self.assertTrue(cat.is_active)

    def test_inquiry_category_ordering(self):
        cat2 = InquiryCategory.objects.create(name="B Category", display_order=2)
        cat1 = InquiryCategory.objects.create(name="A Category", display_order=1)
        categories = list(InquiryCategory.objects.filter(id__in=[cat1.id, cat2.id]))
        self.assertEqual(categories[0], cat1)
        self.assertEqual(categories[1], cat2)


class ContactInquiryModelTests(TestCase):
    def setUp(self):
        self.category = InquiryCategory.objects.create(name="Banquet Hall Booking")

    def test_inquiry_with_category(self):
        inquiry = ContactInquiry.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="9812345678",
            subject="Conference Booking",
            message="Looking for hall for 100 pax.",
            category=self.category
        )
        self.assertEqual(inquiry.category, self.category)
        self.assertEqual(inquiry.get_category_display(), "Banquet Hall Booking")
        self.assertIn("Banquet Hall Booking", str(inquiry))

    def test_inquiry_without_category_fallback(self):
        inquiry = ContactInquiry.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone="9812345678",
            subject="Quick Question",
            message="What time does check-in start?"
        )
        self.assertIsNone(inquiry.category)
        self.assertEqual(inquiry.get_category_display(), "General Inquiry")


class ContactPublicViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_cat = InquiryCategory.objects.create(name="Active Inquiry Type", is_active=True, display_order=1)
        self.inactive_cat = InquiryCategory.objects.create(name="Hidden Inquiry Type", is_active=False, display_order=2)

    def test_contact_page_renders_active_categories_only(self):
        response = self.client.get(reverse('contact:contact_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_cat.name)
        self.assertNotContains(response, self.inactive_cat.name)


class SubmitInquiryAjaxTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = InquiryCategory.objects.create(name="Spa & Wellness", slug="spa-wellness")

    def test_submit_inquiry_with_category_id(self):
        response = self.client.post(reverse('contact:submit_inquiry_ajax'), {
            'name': 'Samira KC',
            'email': 'samira@example.com',
            'phone': '9841234567',
            'category': str(self.category.id),
            'subject': 'Couple Massage Reservation',
            'message': 'Booking request for Saturday 4 PM.'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Message Sent Successfully")

        inquiry = ContactInquiry.objects.filter(email='samira@example.com').first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.category, self.category)
        self.assertEqual(inquiry.get_category_display(), "Spa & Wellness")

    def test_submit_inquiry_with_category_slug(self):
        response = self.client.post(reverse('contact:submit_inquiry_ajax'), {
            'name': 'Bikram Thapa',
            'email': 'bikram@example.com',
            'phone': '9801234567',
            'category': 'spa-wellness',
            'subject': 'Sauna timings',
            'message': 'What are the evening sauna hours?'
        })
        self.assertEqual(response.status_code, 200)
        inquiry = ContactInquiry.objects.filter(email='bikram@example.com').first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.category, self.category)


class AdminDashboardInquiryCategoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='adminstaff',
            email='adminstaff@hotelichchha.com',
            password='Password123!',
            is_staff=True
        )
        self.client.force_login(self.staff_user)
        self.cat1 = InquiryCategory.objects.create(name="Corporate", slug="corporate", display_order=1)
        self.cat2 = InquiryCategory.objects.create(name="Weddings", slug="weddings", display_order=2)

    def test_inquiry_category_create_view(self):
        response = self.client.post(reverse('admin_dashboard:inquiry_category_create'), {
            'name': 'Helicopter Sightseeing',
            'slug': 'helicopter-sightseeing',
            'description': 'Helipad and charter inquiries',
            'display_order': 3,
            'is_active': True,
        })
        self.assertRedirects(response, reverse('admin_dashboard:contact_dashboard') + "?tab=inquiries")
        self.assertTrue(InquiryCategory.objects.filter(name='Helicopter Sightseeing').exists())

    def test_inquiry_category_update_view(self):
        response = self.client.post(reverse('admin_dashboard:inquiry_category_edit', kwargs={'pk': self.cat1.pk}), {
            'name': 'Corporate & Government Events',
            'slug': 'corporate',
            'description': 'Updated description',
            'display_order': 1,
            'is_active': True,
        })
        self.assertRedirects(response, reverse('admin_dashboard:contact_dashboard') + "?tab=inquiries")
        self.cat1.refresh_from_db()
        self.assertEqual(self.cat1.name, 'Corporate & Government Events')

    def test_inquiry_category_delete_view(self):
        cat = InquiryCategory.objects.create(name="Temporary Category", slug="temp")
        response = self.client.post(reverse('admin_dashboard:inquiry_category_delete', kwargs={'pk': cat.pk}))
        self.assertRedirects(response, reverse('admin_dashboard:contact_dashboard') + "?tab=inquiries")
        self.assertFalse(InquiryCategory.objects.filter(pk=cat.pk).exists())

    def test_contact_dashboard_category_filtering(self):
        inq1 = ContactInquiry.objects.create(
            name="Corp Client",
            email="corp@example.com",
            subject="Corporate Meeting",
            message="Meeting for 50",
            category=self.cat1
        )
        inq2 = ContactInquiry.objects.create(
            name="Wedding Couple",
            email="wedding@example.com",
            subject="Wedding Reception",
            message="Reception in garden",
            category=self.cat2
        )

        # Filter by Corporate
        response = self.client.get(reverse('admin_dashboard:contact_dashboard') + f"?tab=inquiries&category={self.cat1.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Corp Client")
        self.assertNotContains(response, "Wedding Couple")

        # All inquiries
        response_all = self.client.get(reverse('admin_dashboard:contact_dashboard') + "?tab=inquiries")
        self.assertEqual(response_all.status_code, 200)
        self.assertContains(response_all, "Corp Client")
        self.assertContains(response_all, "Wedding Couple")
        self.assertContains(response_all, "Inquiry Categories")
