from decimal import Decimal
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from rooms.models.room import Room
from rooms.models.room_category import RoomCategory
from rooms.models.room_facility import RoomFacility
from rooms.models.room_base_price import RoomBasePrice
from rooms.models.room_availability import RoomAvailability
from settings_manager.models.currency import Currency
from settings_manager.models.hotel_settings import HotelSettings
from booking.models.addon import Addon, AddonPrice
from booking.models.booking import Booking
from payments.models.payment import Payment
from contact.models.inquiry import ContactInquiry
from admin_dashboard.models.notification import Notification

User = get_user_model()

class RoomFeatureTests(TestCase):
    def setUp(self):
        # pyrefly: ignore [missing-attribute]
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@hotelichchha.com',
            password='adminpassword123'
        )
        self.client = Client()

        self.hotel_settings = HotelSettings.objects.create(
            site_name="Hotel Ichchha",
            contact_email="concierge@hotelichchha.com",
            contact_phone="+977-51-580200",
            address="Simara, Bara, Nepal"
        )

        self.usd = Currency.objects.create(iso_code='USD', name='US Dollar', symbol='$', is_published=True)
        self.npr = Currency.objects.create(iso_code='NPR', name='Nepalese Rupee', symbol='Rs.', is_published=True)

        self.category = RoomCategory.objects.create(
            name="Deluxe Suite",
            order=1,
            is_published=True
        )

        self.addon_breakfast = Addon.objects.create(
            name="Complimentary Gourmet Breakfast",
            description="Daily buffet breakfast for all guests",
            applies_to="room",
            price_type="per_day",
            is_active=True
        )
        AddonPrice.objects.create(addon=self.addon_breakfast, currency=self.usd, price=Decimal('0.00'))

        self.addon_spa = Addon.objects.create(
            name="Signature Herbal Spa Treatment",
            description="60 min relaxing aroma therapy",
            applies_to="room",
            price_type="per_stay",
            is_active=True
        )
        AddonPrice.objects.create(addon=self.addon_spa, currency=self.usd, price=Decimal('45.00'))

        self.room = Room.objects.create(
            title="Presidential King Suite",
            room_number="101",
            category=self.category,
            description="Luxury suite with panoramic views",
            total_rooms=3,
            room_size=650,
            max_adults=2,
            max_children=1,
            bed_type="King Size",
            allow_custom_addons=True,
            is_published=True
        )
        self.room.included_addons.add(self.addon_breakfast)

        RoomBasePrice.objects.create(room=self.room, currency=self.usd, base_price=Decimal('250.00'))
        RoomBasePrice.objects.create(room=self.room, currency=self.npr, base_price=Decimal('33000.00'))

    def test_room_attributes_and_inclusions(self):
        """Verify room_number, total_rooms, and included_addons on Room model."""
        self.assertEqual(self.room.room_number, "101")
        self.assertEqual(self.room.total_rooms, 3)
        self.assertTrue(self.room.included_addons.filter(id=self.addon_breakfast.id).exists())
        self.assertEqual(len(self.room.added_base_prices), 2)

    def test_room_detail_view_addon_filtering(self):
        """Verify RoomDetailView excludes included complimentary add-ons from optional add-ons list."""
        self.client.cookies['currency'] = 'USD'
        url = reverse('rooms:room_detail', kwargs={'slug': self.room.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        addons_in_context = response.context['addons']
        addon_ids = [a.id for a in addons_in_context]
        self.assertIn(self.addon_spa.id, addon_ids)
        self.assertNotIn(self.addon_breakfast.id, addon_ids)

    def test_room_detail_view_allow_custom_addons_false(self):
        """When allow_custom_addons is False, no optional add-ons should be in context."""
        self.room.allow_custom_addons = False
        self.room.save()

        url = reverse('rooms:room_detail', kwargs={'slug': self.room.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['addons'], [])

    def test_admin_room_search_by_name_and_number(self):
        """Verify admin room dashboard filters rooms by title and room_number."""
        self.client.force_login(self.user)
        
        # Room 2
        Room.objects.create(
            title="Executive Villa",
            room_number="VILLA-B",
            category=self.category,
            description="Private villa with pool",
            total_rooms=1,
            is_published=True
        )

        dashboard_url = reverse('admin_dashboard:room_dashboard')

        # Search by room number '101'
        res = self.client.get(dashboard_url, {'tab': 'rooms', 'search': '101'})
        self.assertEqual(res.status_code, 200)
        rooms_titles = [r.title for r in res.context['rooms']]
        self.assertIn("Presidential King Suite", rooms_titles)
        self.assertNotIn("Executive Villa", rooms_titles)

        # Search by title 'Villa'
        res2 = self.client.get(dashboard_url, {'tab': 'rooms', 'search': 'Villa'})
        self.assertEqual(res2.status_code, 200)
        rooms_titles2 = [r.title for r in res2.context['rooms']]
        self.assertIn("Executive Villa", rooms_titles2)
        self.assertNotIn("Presidential King Suite", rooms_titles2)

    def test_notifications_only_on_success_booking_and_inquiry(self):
        """Verify notifications are not created for draft bookings, but created upon successful payment and inquiries."""
        Notification.objects.all().delete()

        # 1. Draft booking creation
        booking = Booking.objects.create(
            guest_name="Saurav Sharma",
            guest_email="guest@example.com",
            guest_phone="+977-9800000000",
            room=self.room,
            check_in=datetime.date.today() + datetime.timedelta(days=1),
            check_out=datetime.date.today() + datetime.timedelta(days=3),
            adults=2,
            num_rooms=1,
            subtotal=Decimal('500.00'),
            total=Decimal('500.00'),
            currency_code="USD",
            status="draft"
        )
        self.assertEqual(Notification.objects.count(), 0)

        # 2. Payment confirmation
        payment = Payment.objects.create(
            booking=booking,
            amount=Decimal('500.00'),
            gateway="stripe",
            status="pending",
            transaction_id="TXN_12345"
        )
        callback_url = reverse('payments:payment_callback', kwargs={'payment_id': payment.id})
        self.client.get(callback_url)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        self.assertTrue(Notification.objects.filter(notification_type='payment_success').exists())

        # 3. Contact inquiry submission
        inquiry_res = self.client.post(reverse('contact:submit_inquiry_ajax'), {
            'name': 'Bikash Pandey',
            'email': 'bikash@example.com',
            'phone': '9841234567',
            'subject': 'Conference Hall Booking',
            'message': 'We need a conference hall for 50 attendees next week.'
        })
        self.assertEqual(inquiry_res.status_code, 200)
        self.assertTrue(Notification.objects.filter(notification_type='inquiry_received').exists())

    def test_email_service_dispatches(self):
        """Verify send_booking_invoice_email, send_hotel_booking_notification_email, and send_contact_inquiry_emails."""
        mail.outbox = []

        booking = Booking.objects.create(
            guest_name="Pooja Shrestha",
            guest_email="pooja@example.com",
            guest_phone="+977-9812345678",
            room=self.room,
            check_in=datetime.date.today() + datetime.timedelta(days=5),
            check_out=datetime.date.today() + datetime.timedelta(days=7),
            adults=2,
            num_rooms=1,
            subtotal=Decimal('500.00'),
            total=Decimal('500.00'),
            currency_code="USD",
            status="confirmed"
        )
        payment = Payment.objects.create(
            booking=booking,
            amount=Decimal('500.00'),
            gateway="stripe",
            status="success",
            transaction_id="TXN_POOJA"
        )

        from core.services.email_service import send_booking_invoice_email, send_contact_inquiry_emails

        # 1. Booking invoice email (dispatches both guest invoice & hotel alert)
        success, msg = send_booking_invoice_email(booking, payment=payment)
        self.assertTrue(success)
        # Should have sent 2 emails: 1 to guest, 1 to hotel
        self.assertEqual(len(mail.outbox), 2)
        recipients = [m.to[0] for m in mail.outbox]
        self.assertIn("pooja@example.com", recipients)
        self.assertIn("concierge@hotelichchha.com", recipients)

        # 2. Contact inquiry email
        inquiry = ContactInquiry.objects.create(
            name="Aayush Nepal",
            email="aayush@example.com",
            phone="9812345678",
            subject="Wedding Hall Availability",
            message="Looking for banquet space for December."
        )
        inquiry_success, inq_msg = send_contact_inquiry_emails(inquiry)
        self.assertTrue(inquiry_success)
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[2].to[0], "concierge@hotelichchha.com")
        self.assertEqual(mail.outbox[2].reply_to, ["aayush@example.com"])
