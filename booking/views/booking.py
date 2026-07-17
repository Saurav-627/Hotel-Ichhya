from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from rooms.models.room import Room
from rooms.models.room_availability import RoomAvailability
from django.db.models import Sum
from ..models.booking import Booking
from ..models.coupon import Coupon
import datetime


@require_POST
def create_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_published=True)
    
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')
    adults_str = request.POST.get('adults', '2')
    children_str = request.POST.get('children', '0')
    promo_code = request.POST.get('promo_code', '').strip()
    special_requests = request.POST.get('special_requests', '')

    try:
        check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
        adults = int(adults_str)
        children = int(children_str)
        num_rooms = max(1, int(request.POST.get('num_rooms', '1')))
    except (ValueError, TypeError):
        messages.error(request, "Invalid input formats.")
        return redirect('rooms:room_detail', slug=room.slug)

    # Double check availability: blocked if any date can't accommodate num_rooms
    blocked = False
    available_rooms = room.total_rooms
    check_date = check_in
    while check_date < check_out:
        booked_count = RoomAvailability.objects.filter(room__category=room.category, date=check_date).aggregate(
            total=Sum('rooms_booked')
        )['total'] or 0
        remaining = room.total_rooms - booked_count
        if remaining < available_rooms:
            available_rooms = remaining
        if booked_count + num_rooms > room.total_rooms:
            blocked = True
        check_date += datetime.timedelta(days=1)

    if blocked:
        if available_rooms > 0:
            messages.error(request, f"Only {available_rooms} room{'s' if available_rooms != 1 else ''} available for the selected dates.")
        else:
            messages.error(request, "This room is not available for the selected dates. Please adjust your dates.")
        return redirect('rooms:room_detail', slug=room.slug)

    nights = (check_out - check_in).days
    daily_price = room.base_price
    seasonal = room.seasonal_prices.filter(start_date__lte=check_in, end_date__gte=check_out, is_active=True).first()
    if seasonal:
        daily_price = seasonal.price_override

    subtotal = daily_price * nights * num_rooms
    
    # Process promo code
    from decimal import Decimal
    discount = Decimal('0.00')
    coupon = None
    if promo_code:
        coupon_obj = Coupon.objects.filter(code__iexact=promo_code, is_active=True).first()
        if coupon_obj and coupon_obj.is_valid(subtotal):
            coupon = coupon_obj
            discount = coupon_obj.calculate_discount(subtotal)
            messages.success(request, f"Promo code '{promo_code}' applied successfully!")
        else:
            messages.warning(request, "Invalid or expired promo code.")

    taxable_amount = subtotal - discount
    tax = 0
    total = taxable_amount

    # Create Booking
    booking = Booking.objects.create(
        user=request.user if request.user.is_authenticated else None,
        room=room,
        guest_name=name,
        guest_email=email,
        guest_phone=phone,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        num_rooms=num_rooms,
        subtotal=subtotal,
        coupon=coupon,
        discount=discount,
        tax=tax,
        total=total,
        special_requests=special_requests,
        status='draft'
    )

    return redirect('booking:checkout_page', booking_uid=booking.booking_uid)

def checkout_page(request, booking_uid):
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    return render(request, 'booking/checkout.html', {'booking': booking})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def channel_manager_sync(request):
    """
    Mock endpoint to sync bookings with channel managers like Booking.com, Expedia, etc.
    Exposes setup hooks for reservation delivery (OTA_HotelResNotifRQ / JSON Webhooks).
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    # Required channel manager payload parameters
    ota_id = data.get('ota_reservation_id')
    channel = data.get('channel_name', 'OTA-Sync')
    room_id = data.get('room_id')
    check_in_str = data.get('check_in')
    check_out_str = data.get('check_out')
    guest_name = data.get('guest_name')
    guest_email = data.get('guest_email', '')
    guest_phone = data.get('guest_phone', '')
    
    if not all([ota_id, room_id, check_in_str, check_out_str, guest_name]):
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found'}, status=404)
        
    try:
        check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid dates'}, status=400)
        
    # Check if booking already exists for this OTA reservation
    booking = Booking.objects.filter(ota_reservation_id=ota_id, channel_name=channel).first()
    
    # Calculate price
    nights = (check_out - check_in).days
    subtotal = room.base_price * nights
    tax = 0
    total = subtotal
    
    if not booking:
        # Create new OTA Booking
        booking = Booking.objects.create(
            room=room,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in=check_in,
            check_out=check_out,
            subtotal=subtotal,
            tax=0,
            total=total,
            status='confirmed',  # OTA bookings are usually confirmed
            channel_name=channel,
            ota_reservation_id=ota_id,
            channel_raw_payload=data
        )
        
        return JsonResponse({'status': 'success', 'message': 'Booking created successfully', 'booking_id': booking.id})
    else:
        # Update existing booking details/dates
        booking.guest_name = guest_name
        booking.guest_email = guest_email
        booking.guest_phone = guest_phone
        booking.check_in = check_in
        booking.check_out = check_out
        booking.subtotal = subtotal
        booking.tax = 0
        booking.total = total
        booking.channel_raw_payload = data
        booking.save()
        
        return JsonResponse({'status': 'success', 'message': 'Booking updated successfully', 'booking_id': booking.id})


