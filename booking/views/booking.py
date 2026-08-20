import datetime
import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.db.models import Prefetch, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from admin_dashboard.models.notification import create_admin_notification
from core.services.email_service import send_booking_invoice_email
from rooms.models.room import Room
from rooms.models.room_availability import RoomAvailability
from rooms.models.room_base_price import RoomBasePrice

from ..models.booking import Booking
from ..models.coupon import Coupon

logger = logging.getLogger(__name__)


@require_POST
def create_booking(request, room_id):
    selected_currency = request.COOKIES.get('currency', 'USD')
    room_qs = Room.objects.prefetch_related(
        Prefetch(
            'base_prices',
            queryset=RoomBasePrice.objects.filter(currency__iso_code=selected_currency),
            to_attr='active_currency_price'
        )
    )
    room = get_object_or_404(room_qs, id=room_id, is_published=True)
    room.set_active_currency(selected_currency)
    
    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
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

    if check_out <= check_in:
        messages.error(request, "Check-out date must be after check-in date.")
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
    daily_price = room.final_price
    
    # Seasonal rate override
    seasonal = (
        room.seasonal_prices.filter(
            start_date__lte=check_out, end_date__gte=check_in, is_active=True,
            currency__iso_code=selected_currency
        ).order_by('-start_date').first()
        or room.seasonal_prices.filter(
            start_date__lte=check_out, end_date__gte=check_in, is_active=True,
            currency__isnull=True
        ).order_by('-start_date').first()
    )
    if seasonal:
        daily_price = seasonal.price_override

    room_subtotal = daily_price * nights * num_rooms

    # Process selected add-ons
    from ..models.addon import Addon, BookingAddon
    selected_addon_ids = request.POST.getlist('selected_addons') or request.POST.getlist('selected_addons[]')
    addon_items = []
    addons_subtotal = Decimal('0.00')

    if selected_addon_ids:
        addons_qs = Addon.objects.filter(id__in=selected_addon_ids, is_active=True).prefetch_related('prices__currency')
        for addon in addons_qs:
            addon.set_active_currency(selected_currency)
            unit_price = addon.current_price or Decimal('0.00')
            if addon.price_type == 'per_night':
                qty_calc = Decimal(str(nights * num_rooms))
                display_qty = nights * num_rooms
            elif addon.price_type == 'per_person':
                qty_calc = Decimal(str(adults + children))
                display_qty = adults + children
            elif addon.price_type == 'per_person_per_night':
                qty_calc = Decimal(str((adults + children) * nights))
                display_qty = (adults + children) * nights
            else:
                qty_calc = Decimal('1')
                display_qty = 1

            item_total = unit_price * qty_calc
            addons_subtotal += item_total
            addon_items.append({
                'addon': addon,
                'name': addon.name,
                'price_type': addon.price_type,
                'unit_price': unit_price,
                'quantity': display_qty,
                'total_price': item_total
            })

    subtotal = room_subtotal + addons_subtotal
    
    # Process promo code with multi-currency & min-spend validation
    discount = Decimal('0.00')
    coupon = None
    if promo_code:
        coupon_obj = Coupon.objects.filter(code__iexact=promo_code, is_active=True).first()
        if coupon_obj:
            is_valid, err_msg = coupon_obj.is_valid(order_amount=subtotal, product_type='room', active_currency_code=selected_currency)
            if is_valid:
                coupon = coupon_obj
                discount = coupon_obj.calculate_discount(subtotal)
                messages.success(request, f"Promo code '{promo_code}' applied successfully!")
            else:
                messages.warning(request, f"Promo code '{promo_code}': {err_msg}")
        else:
            messages.warning(request, f"Invalid or expired promo code '{promo_code}'.")

    taxable_amount = subtotal - discount
    tax = Decimal('0.00')
    if getattr(room, 'tax_percentage', None):
        tax_pct = Decimal(str(room.tax_percentage))
        tax = (taxable_amount * (tax_pct / Decimal('100.00'))).quantize(Decimal('0.01'))
    total = taxable_amount + tax

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
        subtotal=room_subtotal,
        currency_code=selected_currency,
        coupon=coupon,
        discount=discount,
        tax=tax,
        total=total,
        special_requests=special_requests,
        status='draft'
    )

    # Save BookingAddon line items
    for item in addon_items:
        BookingAddon.objects.create(
            booking=booking,
            addon=item['addon'],
            addon_name=item['name'],
            price_type=item['price_type'],
            unit_price=item['unit_price'],
            quantity=item['quantity'],
            total_price=item['total_price']
        )

    # Recalculate booking.tax and booking.total incorporating add-ons
    booking.calculate_and_update_totals(apply_tax=True)

    # Track coupon redemption
    if coupon:
        coupon.redeem()


    # Trigger Admin Real-Time Notification
    try:
        create_admin_notification(
            notification_type='booking_created',
            title=f"New Room Booking [{booking.booking_uid}]",
            message=f"{booking.guest_name} reserved {room.title} ({booking.currency_code} {booking.total}) for {booking.nights} night(s).",
            link_url=reverse('admin_dashboard:booking_detail', kwargs={'pk': booking.pk})
        )
    except Exception as e:
        logger.error(f"Failed to create booking notification: {e}")

    # Note: Invoice email is deferred until payment succeeds in payment_callback

    return redirect('booking:checkout_page', booking_uid=booking.booking_uid)


def checkout_page(request, booking_uid):
    booking_qs = Booking.objects.prefetch_related(
        'booking_addons__addon',
        Prefetch(
            'room__base_prices',
            queryset=RoomBasePrice.objects.all()
        )
    )

    booking = get_object_or_404(booking_qs, booking_uid=booking_uid)
    locked_currency = booking.currency_code or 'USD'
    booking.room.set_active_currency(locked_currency)
    
    context = {
        'booking': booking,
        'selected_currency': locked_currency,
        'is_checkout_page': True,
    }
    return render(request, 'booking/checkout.html', context)



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
        room = Room.objects.prefetch_related('base_prices').get(id=room_id)
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
    subtotal = (room.base_price or Decimal("0.00")) * nights
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
            tax=Decimal("0.00"),
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
        booking.tax = Decimal("0.00")
        booking.total = total
        booking.channel_raw_payload = data
        booking.save()
        
        return JsonResponse({'status': 'success', 'message': 'Booking updated successfully', 'booking_id': booking.id})
