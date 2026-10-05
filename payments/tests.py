import datetime
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase
from django.urls import reverse

from admin_dashboard.models.notification import Notification
from booking.models.booking import Booking
from payments.models.payment import Payment
from payments.models.payment_processor import PaymentProcessor
from payments.services import get_processor_by_gateway_name
from payments.services.base_payment import PaymentValidationResult
from payments.services.stripe_payment import StripePayment
from rooms.models.room import Room
from rooms.models.room_base_price import RoomBasePrice
from rooms.models.room_category import RoomCategory
from settings_manager.models.currency import Currency
from settings_manager.models.hotel_settings import HotelSettings


class StripeServiceTests(TestCase):
    def test_get_processor_by_gateway_name_returns_stripe_payment(self):
        processor = get_processor_by_gateway_name("stripe")
        self.assertIsInstance(processor, StripePayment)

    @patch("stripe.checkout.Session.create")
    def test_initiate_payment_creates_stripe_session(self, mock_session_create):
        mock_session = MagicMock()
        mock_session.id = "cs_test_12345"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_12345"
        mock_session_create.return_value = mock_session

        processor = StripePayment(client_secret="sk_test_mock")
        res = processor.initiate_payment(
            total_amount=150.00,
            transaction_id="txn-uuid-1",
            return_url="http://example.com/callback/",
            currency="usd",
            display_name="Hotel Ichchha Deluxe Room",
            customer_info={"email": "guest@example.com"},
            booking_uid="buid-123",
            payment_id="10"
        )

        self.assertEqual(res["api_url"], "https://checkout.stripe.com/pay/cs_test_12345")
        self.assertEqual(res["session_id"], "cs_test_12345")
        mock_session_create.assert_called_once()
        args, kwargs = mock_session_create.call_args
        self.assertEqual(kwargs["line_items"][0]["price_data"]["unit_amount"], 15000)
        self.assertEqual(kwargs["line_items"][0]["price_data"]["currency"], "usd")
        self.assertEqual(kwargs["metadata"]["booking_uid"], "buid-123")

    @patch("stripe.checkout.Session.retrieve")
    def test_validate_payment_success(self, mock_session_retrieve):
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.to_dict.return_value = {"id": "cs_test_12345", "payment_status": "paid"}
        mock_session_retrieve.return_value = mock_session

        processor = StripePayment(client_secret="sk_test_mock")
        res = processor.validate_payment(
            total_amount=150.00,
            transaction_id="txn-uuid-1",
            session_id="cs_test_12345"
        )

        self.assertEqual(res.status, PaymentValidationResult.Status.SUCCESS)
        self.assertIn("paid", res.details.get("payment_status"))


class StripeIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.hotel_settings = HotelSettings.objects.create(
            site_name="Hotel Ichchha",
            contact_email="concierge@hotelichchha.com"
        )

        self.usd = Currency.objects.create(iso_code='USD', name='US Dollar', symbol='$', is_published=True)
        self.npr = Currency.objects.create(iso_code='NPR', name='Nepalese Rupee', symbol='Rs.', is_published=True)

        self.category = RoomCategory.objects.create(name="Suite", order=1, is_published=True)
        self.room = Room.objects.create(
            title="Deluxe Garden View",
            slug="deluxe-garden-view",
            category=self.category,
            description="Luxury room overlooking gardens",
            total_rooms=3,
            is_published=True
        )
        RoomBasePrice.objects.create(room=self.room, currency=self.usd, base_price=Decimal("150.00"))
        RoomBasePrice.objects.create(room=self.room, currency=self.npr, base_price=Decimal("20000.00"))

        self.stripe_proc = PaymentProcessor.objects.create(
            name="Stripe",
            code="stripe",
            apply_tax=False,
            is_published=True
        )
        self.stripe_proc.payment_currencies.add(self.usd)

        self.esewa_proc = PaymentProcessor.objects.create(
            name="eSewa",
            code="esewa",
            apply_tax=False,
            is_published=True
        )
        self.esewa_proc.payment_currencies.add(self.npr)

        self.booking_usd = Booking.objects.create(
            room=self.room,
            guest_name="Jane Doe",
            guest_email="jane@example.com",
            guest_phone="+1234567890",
            check_in=datetime.date.today() + datetime.timedelta(days=1),
            check_out=datetime.date.today() + datetime.timedelta(days=3),
            num_rooms=1,
            subtotal=Decimal("300.00"),
            currency_code="USD",
            total=Decimal("300.00"),
            status="draft"
        )

        self.booking_npr = Booking.objects.create(
            room=self.room,
            guest_name="Ram Bahadur",
            guest_email="ram@example.com",
            guest_phone="+9779800000000",
            check_in=datetime.date.today() + datetime.timedelta(days=1),
            check_out=datetime.date.today() + datetime.timedelta(days=3),
            num_rooms=1,
            subtotal=Decimal("40000.00"),
            currency_code="NPR",
            total=Decimal("40000.00"),
            status="draft"
        )

    @patch("stripe.checkout.Session.create")
    def test_process_payment_usd_redirects_to_stripe(self, mock_session_create):
        mock_session = MagicMock()
        mock_session.id = "cs_test_session_abc"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_session_abc"
        mock_session_create.return_value = mock_session

        url = reverse('payments:process_payment', kwargs={'booking_uid': self.booking_usd.booking_uid, 'gateway': 'stripe'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://checkout.stripe.com/pay/cs_test_session_abc")

        payment = Payment.objects.filter(booking=self.booking_usd, gateway='stripe').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.currency, self.usd)

    def test_process_payment_npr_rejects_stripe(self):
        url = reverse('payments:process_payment', kwargs={'booking_uid': self.booking_npr.booking_uid, 'gateway': 'stripe'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        expected_checkout_url = reverse('booking:checkout_page', kwargs={'booking_uid': self.booking_npr.booking_uid})
        self.assertIn(expected_checkout_url, response.url)

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_callback_stripe_success(self, mock_session_retrieve):
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.to_dict.return_value = {"id": "cs_test_123", "payment_status": "paid"}
        mock_session_retrieve.return_value = mock_session

        payment = Payment.objects.create(
            booking=self.booking_usd,
            gateway="stripe",
            currency=self.usd,
            transaction_id="txn-callback-test",
            amount=Decimal("300.00"),
            status="pending"
        )

        callback_url = reverse('payments:payment_callback', kwargs={'payment_id': payment.id})
        response = self.client.get(callback_url, {'session_id': 'cs_test_123'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservation Confirmed")

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'success')

        self.booking_usd.refresh_from_db()
        self.assertEqual(self.booking_usd.status, 'confirmed')

        # Admin notification was created
        notif = Notification.objects.filter(notification_type='payment_success').first()
        self.assertIsNotNone(notif)
        self.assertIn(str(self.booking_usd.booking_uid), notif.title)

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_checkout_session_completed(self, mock_construct_event):
        payment = Payment.objects.create(
            booking=self.booking_usd,
            gateway="stripe",
            currency=self.usd,
            transaction_id="txn-webhook-test",
            amount=Decimal("300.00"),
            status="pending"
        )

        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"
        mock_event.data = MagicMock()
        mock_session_obj = MagicMock()
        mock_session_obj.to_dict.return_value = {
            "id": "cs_test_webhook_123",
            "client_reference_id": "txn-webhook-test",
            "metadata": {
                "booking_uid": str(self.booking_usd.booking_uid),
                "payment_id": str(payment.id),
                "transaction_id": "txn-webhook-test"
            }
        }
        mock_event.data.object = mock_session_obj
        mock_construct_event.return_value = mock_event

        webhook_url = reverse('payments:stripe_webhook')
        response = self.client.post(
            webhook_url,
            data=json.dumps({"id": "evt_test"}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=123,v1=signature_test"
        )

        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'success')

        self.booking_usd.refresh_from_db()
        self.assertEqual(self.booking_usd.status, 'confirmed')

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_payment_intent_failed(self, mock_construct_event):
        payment = Payment.objects.create(
            booking=self.booking_usd,
            gateway="stripe",
            currency=self.usd,
            transaction_id="txn-failed-test",
            amount=Decimal("300.00"),
            status="pending"
        )

        mock_event = MagicMock()
        mock_event.type = "payment_intent.payment_failed"
        mock_event.data = MagicMock()
        mock_pi_obj = MagicMock()
        mock_pi_obj.to_dict.return_value = {
            "id": "pi_failed_123",
            "metadata": {
                "booking_uid": str(self.booking_usd.booking_uid),
                "payment_id": str(payment.id)
            }
        }
        mock_event.data.object = mock_pi_obj
        mock_construct_event.return_value = mock_event

        webhook_url = reverse('payments:stripe_webhook')
        response = self.client.post(
            webhook_url,
            data=json.dumps({"id": "evt_failed"}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=123,v1=sig"
        )

        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'failed')
