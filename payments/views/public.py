from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from booking.models.booking import Booking
from ..models.payment import Payment
import uuid

def process_payment(request, booking_uid, gateway):
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    
    if booking.status != 'pending':
        return HttpResponse("This booking has already been processed.")

    if gateway not in ['stripe', 'esewa', 'khalti']:
        raise Http404("Invalid payment gateway.")

    # Create a pending Payment record
    payment = Payment.objects.create(
        booking=booking,
        gateway=gateway,
        transaction_id=str(uuid.uuid4())[:18].upper(),
        amount=booking.total,
        status='pending'
    )

    # In a live app, you would redirect to Stripe/eSewa/Khalti SDKs/APIs.
    # We will simulate a successful payment gateway callback for demo purposes.
    context = {
        'booking': booking,
        'gateway': gateway,
        'payment': payment,
    }
    return render(request, 'payments/process.html', context)

def payment_callback(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    booking = payment.booking

    # Mock gateway validation success
    payment.status = 'success'
    payment.save()

    booking.status = 'confirmed'
    booking.save()

    # Trigger background tasks (send email confirmation/SMS notification via Celery) here if desired!
    messages_success_html = f"Payment of ${payment.amount} successful via {payment.gateway.upper()}!"
    
    return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': messages_success_html})

def view_invoice(request, booking_uid):
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    payment = booking.payments.filter(status='success').first()
    
    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'payments/invoice.html', context)
