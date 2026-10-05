import json
import logging
import uuid

import stripe
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from admin_dashboard.models.notification import create_admin_notification
from booking.models.booking import Booking
from core.services.email_service import send_booking_invoice_email

from ..models.payment import Payment
from ..models.payment_processor import PaymentProcessor
from ..services import get_processor_by_gateway_name
from ..services.base_payment import PaymentValidationResult

logger = logging.getLogger(__name__)

def process_payment(request, booking_uid, gateway):
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    
    if booking.status not in {'draft', 'pending'}:
        return HttpResponse("This booking has already been processed.")

    if gateway not in ['stripe', 'esewa', 'khalti']:
        raise Http404("Invalid payment gateway.")

    # Fetch published payment processor that supports this booking's currency
    booking_currency = (booking.currency_code or 'USD').upper()
    processor_meta = PaymentProcessor.objects.filter(
        code=gateway, 
        is_published=True,
        payment_currencies__iso_code__iexact=booking_currency
    ).first()

    if not processor_meta:
        messages.error(request, f"The selected payment method ({gateway.title()}) is currently unavailable for {booking_currency}.")
        return redirect('booking:checkout_page', booking_uid=booking.booking_uid)

    should_apply_tax = bool(processor_meta.apply_tax)
    booking.calculate_and_update_totals(apply_tax=should_apply_tax)
    tax_amount = booking.tax

    # Determine exact currency object supported by this processor
    currency_obj = processor_meta.payment_currencies.filter(iso_code__iexact=booking_currency).first()
    if not currency_obj:
        currency_obj = processor_meta.payment_currencies.first()

    # Create a pending Payment record with the correct amount and currency
    transaction_id = str(uuid.uuid4())
    payment = Payment.objects.create(
        booking=booking,
        gateway=gateway,
        currency=currency_obj,
        transaction_id=transaction_id,
        amount=booking.total,
        tax_amount=tax_amount,
        status='pending'
    )

    if gateway == 'stripe':
        try:
            processor = get_processor_by_gateway_name('stripe')
            return_url = request.build_absolute_uri(reverse('payments:payment_callback', args=[payment.id]))
            item_name = booking.room.title if booking.room else "Hotel Ichchha Room Booking"
            
            result = processor.initiate_payment(
                total_amount=float(booking.total),
                transaction_id=transaction_id,
                return_url=return_url,
                cancel_url=request.build_absolute_uri(reverse('booking:checkout_page', args=[booking.booking_uid])),
                currency=booking.currency_code.lower() if booking.currency_code else 'usd',
                display_name=f"Booking for {item_name}",
                customer_info={
                    'name': booking.guest_name,
                    'email': booking.guest_email,
                    'phone': booking.guest_phone,
                },
                booking_uid=booking.booking_uid,
                payment_id=payment.id
            )
            
            payment.gateway_response = json.dumps(result)
            payment.save(update_fields=['gateway_response'])

            return redirect(result['api_url'])
        except Exception as e:
            payment.status = 'failed'
            payment.gateway_response = str(e)
            payment.save()
            logger.error(f"Stripe payment initiation failed for booking {booking_uid}: {e}")
            messages.error(request, f"Stripe payment gateway is temporarily unavailable: {e}. Please try another payment option.")
            return redirect('booking:checkout_page', booking_uid=booking.booking_uid)

    try:
        processor = get_processor_by_gateway_name(gateway)
        return_url = request.build_absolute_uri(reverse('payments:payment_callback', args=[payment.id]))

        kwargs = {
            'tax_amount': float(tax_amount)
        }

        if gateway == 'khalti':
            # pyrefly: ignore [bad-assignment]
            kwargs['display_name'] = f"Booking for {booking.room.title}"
            # pyrefly: ignore [bad-assignment]
            kwargs['customer_info'] = {
                'name': booking.guest_name,
                'email': booking.guest_email,
                'phone': booking.guest_phone,
            }
            from ..services.utils import to_minor_units
            # pyrefly: ignore [bad-assignment]
            kwargs['product_items'] = [{
                'identity': str(booking.room.id),
                'name': booking.room.title,
                'total_price': to_minor_units(booking.total),
                'quantity': 1,
                'unit_price': to_minor_units(booking.total)
            }]

        result = processor.initiate_payment(
            total_amount=float(booking.total),
            transaction_id=transaction_id,
            return_url=return_url,
            **kwargs
        )

        # Store initiation response or reference
        if gateway == 'khalti':
            payment.gateway_response = result.get('provider_reference')
            payment.save(update_fields=['gateway_response'])
        else:
            payment.gateway_response = json.dumps(result)
            payment.save(update_fields=['gateway_response'])

        context = {
            'booking': booking,
            'gateway': gateway,
            'payment': payment,
            'api_url': result['api_url'],
            'form_method': result['form_method'],
            'form_data': result['form_data']
        }
        return render(request, 'payments/process.html', context)

    except Exception as e:
        payment.status = 'failed'
        payment.gateway_response = str(e)
        payment.save()
        logger.error(f"Payment initiation failed for booking {booking_uid} via {gateway}: {e}")
        messages.error(request, f"Payment gateway ({gateway.upper()}) is temporarily unavailable: {e}. Please try another payment option.")
        return redirect('booking:checkout_page', booking_uid=booking.booking_uid)

def payment_callback(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    booking = payment.booking

    if payment.status == 'success':
        return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': "Payment already confirmed!"})

    gateway = payment.gateway

    if gateway == 'stripe':
        session_id = request.GET.get('session_id')
        if session_id:
            try:
                processor = get_processor_by_gateway_name('stripe')
                validation_result = processor.validate_payment(
                    total_amount=float(payment.amount),
                    # pyrefly: ignore [bad-argument-type]
                    transaction_id=payment.transaction_id,
                    session_id=session_id
                )
                if validation_result.status == PaymentValidationResult.Status.SUCCESS:
                    with transaction.atomic():
                        from rooms.models.room import Room
                        Room.objects.select_for_update().get(pk=booking.room_id)

                        if booking.has_room_availability():
                            payment.status = 'success'
                            payment.gateway_response = json.dumps(validation_result.details or {}, default=str)
                            payment.save(update_fields=['status', 'gateway_response'])
                            booking.status = 'confirmed'
                            booking.save(update_fields=['status'])

                            # Send Invoice Email & Admin Notification
                            try:
                                send_booking_invoice_email(booking, payment=payment, request=request)
                                create_admin_notification(
                                    notification_type='payment_success',
                                    title=f"Booking Confirmed & Paid [{booking.booking_uid}]",
                                    message=f"Received {booking.currency_code} {payment.amount} via STRIPE from {booking.guest_name}.",
                                    link_url=reverse('admin_dashboard:booking_detail', kwargs={'pk': booking.pk})
                                )
                            except Exception as email_err:
                                logger.error(f"Error dispatching invoice/notification on Stripe callback: {email_err}")

                            message = f"Payment of {booking.currency_code} {payment.amount} successful via STRIPE!"
                        else:
                            payment.status = 'failed'
                            payment.gateway_response = 'Room inventory changed before confirmation.'
                            payment.save(update_fields=['status', 'gateway_response'])
                            booking.status = 'draft'
                            booking.save(update_fields=['status'])
                            message = "Payment succeeded, but the room is no longer available. The booking remains a draft."
                elif validation_result.status == PaymentValidationResult.Status.PENDING:
                    payment.status = 'pending'
                    payment.save(update_fields=['status'])
                    booking.status = 'draft'
                    booking.save(update_fields=['status'])
                    message = "Stripe payment is still pending. The booking remains a draft until confirmed."
                else:
                    payment.status = 'failed'
                    payment.save(update_fields=['status'])
                    booking.status = 'draft'
                    booking.save(update_fields=['status'])
                    message = f"Stripe payment failed: {validation_result.message}"
            except Exception as e:
                logger.error(f"Stripe validation exception: {e}")
                message = f"Stripe validation error: {e}"
        else:
            message = "Stripe session reference missing."
        return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': message})

    try:
        processor = get_processor_by_gateway_name(gateway)

        if gateway == 'khalti':
            pidx = request.GET.get('pidx') or payment.gateway_response
            if not pidx:
                raise ValueError("Khalti pidx transaction reference not found.")
            transaction_id = pidx
        elif gateway == 'esewa':
            transaction_id = payment.transaction_id
        else:
            raise ValueError(f"Unsupported callback gateway: {gateway}")

        validation_result = processor.validate_payment(
            total_amount=float(payment.amount),
            # pyrefly: ignore [bad-argument-type]
            transaction_id=transaction_id
        )

        if validation_result.status == PaymentValidationResult.Status.SUCCESS:
            with transaction.atomic():
                from rooms.models.room import Room

                Room.objects.select_for_update().get(pk=booking.room_id)
                if not booking.has_room_availability():
                    payment.status = 'failed'
                    payment.gateway_response = 'Room inventory changed before confirmation.'
                    payment.save(update_fields=['status', 'gateway_response'])
                    booking.status = 'draft'
                    booking.save(update_fields=['status'])

                    return render(request, 'payments/success.html', {
                        'booking': booking,
                        'payment': payment,
                        'message': "Payment succeeded, but the room is no longer available. The booking remains a draft."
                    })

                payment.status = 'success'
                payment.gateway_response = json.dumps(dict(request.GET))
                payment.save(update_fields=['status', 'gateway_response'])
                booking.status = 'confirmed'
                booking.save(update_fields=['status'])

            # Send Invoice & Receipt Email and Trigger Admin Notification upon payment success
            try:
                send_booking_invoice_email(booking, payment=payment, request=request)
                create_admin_notification(
                    notification_type='payment_success',
                    title=f"Booking Confirmed & Paid [{booking.booking_uid}]",
                    message=f"Received {booking.currency_code} {payment.amount} via {gateway.upper()} from {booking.guest_name}.",
                    link_url=reverse('admin_dashboard:booking_detail', kwargs={'pk': booking.pk})
                )
            except Exception as e:
                logger.error(f"Failed to send invoice email/notification after {gateway} payment: {e}")

            message = f"Payment of {booking.currency_code} {payment.amount} successful via {gateway.upper()}!"
            return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': message})


        elif validation_result.status == PaymentValidationResult.Status.PENDING:
            payment.status = 'pending'
            payment.save(update_fields=['status'])
            booking.status = 'draft'
            booking.save(update_fields=['status'])
            return render(request, 'payments/success.html', {
                'booking': booking,
                'payment': payment,
                'message': f"Payment is pending. Please verify with {gateway.upper()}. The booking is still a draft until payment completes."
            })
        else:
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            booking.status = 'draft'
            booking.save(update_fields=['status'])

            return render(request, 'payments/success.html', {
                'booking': booking,
                'payment': payment,
                'message': f"Payment validation failed for {gateway.upper()}. The booking remains a draft."
            })

    except Exception as e:
        payment.status = 'failed'
        payment.save(update_fields=['status'])
        booking.status = 'draft'
        booking.save(update_fields=['status'])

        logger.error(f"Callback error for payment {payment_id}: {e}")
        return render(request, 'payments/success.html', {
            'booking': booking,
            'payment': payment,
            'message': f"Payment callback error: {e}"
        })

def view_invoice(request, booking_uid):
    from django.utils import timezone
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    if booking.room:
        booking.room.set_active_currency(booking.currency_code)
    payments = Payment.objects.filter(booking=booking, status='success')
    
    context = {
        'booking': booking,
        'payments': payments,
        'print_date': timezone.now(),
    }
    return render(request, 'admin_dashboard/bookings/invoice.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handles Stripe webhooks (checkout.session.completed, payment_intent.succeeded, payment_intent.payment_failed).
    Verifies signature if STRIPE_WEBHOOK_SECRET is set in environment.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    event = None
    if webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {e}")
            return HttpResponse("Invalid payload", status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {e}")
            return HttpResponse("Invalid signature", status=400)
    else:
        try:
            event_dict = json.loads(payload.decode('utf-8'))
            api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            event = stripe.Event.construct_from(event_dict, api_key)
        except Exception as e:
            logger.error(f"Error parsing Stripe webhook JSON payload: {e}")
            return HttpResponse("Invalid JSON", status=400)

    try:
        event_type = event.type if hasattr(event, 'type') else event.get('type')
        event_data = event.data if hasattr(event, 'data') else event.get('data')

        logger.info(f"Received Stripe Webhook event: {event_type}")

        if event_type in ('checkout.session.completed', 'payment_intent.succeeded'):
            obj = event_data.object if hasattr(event_data, 'object') else (event_data.get('object', {}) if isinstance(event_data, dict) else {})
            obj_dict = obj.to_dict() if hasattr(obj, 'to_dict') else (dict(obj) if isinstance(obj, dict) else {})
            metadata = obj_dict.get('metadata') or {}
            
            booking_uid = metadata.get('booking_uid')
            payment_id = metadata.get('payment_id')
            transaction_id = obj_dict.get('client_reference_id') or metadata.get('transaction_id')

            payment = None
            if payment_id and str(payment_id).isdigit():
                payment = Payment.objects.filter(id=int(payment_id)).first()
            if not payment and transaction_id:
                payment = Payment.objects.filter(transaction_id=str(transaction_id)).first()
            if not payment and booking_uid:
                payment = Payment.objects.filter(booking__booking_uid=booking_uid, gateway='stripe').last()

            if payment and payment.status != 'success':
                booking = payment.booking
                with transaction.atomic():
                    if booking.room_id:
                        from rooms.models.room import Room
                        Room.objects.select_for_update().get(pk=booking.room_id)

                    if booking.has_room_availability():
                        payment.status = 'success'
                        try:
                            payment.gateway_response = json.dumps(obj_dict, default=str)
                        except Exception:
                            payment.gateway_response = str(obj_dict)
                        payment.save(update_fields=['status', 'gateway_response'])

                        booking.status = 'confirmed'
                        booking.save(update_fields=['status'])
                        logger.info(f"Booking {booking.booking_uid} successfully confirmed via Stripe Webhook.")

                        # Send Invoice Email & Admin Notification
                        try:
                            send_booking_invoice_email(booking, payment=payment, request=request)
                            create_admin_notification(
                                notification_type='payment_success',
                                title=f"Booking Confirmed & Paid [{booking.booking_uid}]",
                                message=f"Received {booking.currency_code} {payment.amount} via STRIPE Webhook from {booking.guest_name}.",
                                link_url=reverse('admin_dashboard:booking_detail', kwargs={'pk': booking.pk})
                            )
                        except Exception as email_err:
                            logger.error(f"Error dispatching invoice/notification in Stripe Webhook: {email_err}")
                    else:
                        payment.status = 'failed'
                        payment.gateway_response = 'Room inventory unavailable at webhook confirmation.'
                        payment.save(update_fields=['status', 'gateway_response'])
                        logger.warning(f"Booking {booking.booking_uid} failed availability check on Stripe Webhook.")

        elif event_type == 'payment_intent.payment_failed':
            pi = event_data.object if hasattr(event_data, 'object') else (event_data.get('object', {}) if isinstance(event_data, dict) else {})
            pi_dict = pi.to_dict() if hasattr(pi, 'to_dict') else (dict(pi) if isinstance(pi, dict) else {})
            metadata = pi_dict.get('metadata') or {}
            booking_uid = metadata.get('booking_uid')
            payment_id = metadata.get('payment_id')
            payment = None
            if payment_id and str(payment_id).isdigit():
                payment = Payment.objects.filter(id=int(payment_id)).first()
            if not payment and booking_uid:
                payment = Payment.objects.filter(booking__booking_uid=booking_uid, gateway='stripe').last()
            if payment and payment.status != 'success':
                payment.status = 'failed'
                payment.save(update_fields=['status'])

        return HttpResponse(status=200)

    except Exception as exc:
        logger.exception(f"Error handling Stripe webhook event ({event_type})")
        return HttpResponse(f"Webhook processing error: {exc}", status=500)
