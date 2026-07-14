from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from rooms.models.room import Room
from rooms.models.room_availability import RoomAvailability
from ..models.booking import Booking
from ..models.coupon import Coupon
import datetime

def initiate_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_published=True)
    
    # Retrieve query params or set defaults
    check_in_str = request.GET.get('check_in', '')
    check_out_str = request.GET.get('check_out', '')
    adults = request.GET.get('adults', '2')
    children = request.GET.get('children', '0')

    # Convert to date objects
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    try:
        check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date() if check_in_str else today
        check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date() if check_out_str else tomorrow
        if check_in < today:
            check_in = today
            check_out = today + datetime.timedelta(days=1)
        if check_out <= check_in:
            check_out = check_in + datetime.timedelta(days=1)
    except ValueError:
        check_in = today
        check_out = tomorrow

    nights = (check_out - check_in).days
    
    # Calculate price
    # Check if we have seasonal prices during this range
    base_price = room.base_price
    # Simple seasonal average check or fallback to base price
    # (In production, you would check seasonal prices for each day of the stay)
    daily_price = base_price
    seasonal = room.seasonal_prices.filter(start_date__lte=check_in, end_date__gte=check_out, is_active=True).first()
    if seasonal:
        daily_price = seasonal.price_override

    subtotal = daily_price * nights
    tax = subtotal * (room.tax_percentage / 100)
    total = subtotal + tax

    context = {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'adults': adults,
        'children': children,
        'nights': nights,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'daily_price': daily_price,
    }
    return render(request, 'booking/booking_initiate.html', context)

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
    except (ValueError, TypeError):
        messages.error(request, "Invalid input formats.")
        return redirect('rooms:room_detail', slug=room.slug)

    # Double check availability
    blocked = RoomAvailability.objects.filter(
        room=room,
        date__gte=check_in,
        date__lt=check_out,
        is_available=False
    ).exists()

    if blocked:
        messages.error(request, "Sorry, this room is not available for the selected dates.")
        return redirect('rooms:room_detail', slug=room.slug)

    nights = (check_out - check_in).days
    daily_price = room.base_price
    seasonal = room.seasonal_prices.filter(start_date__lte=check_in, end_date__gte=check_out, is_active=True).first()
    if seasonal:
        daily_price = seasonal.price_override

    subtotal = daily_price * nights
    
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
    tax = taxable_amount * (room.tax_percentage / 100)
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
        subtotal=subtotal,
        coupon=coupon,
        discount=discount,
        tax=tax,
        total=total,
        special_requests=special_requests,
        status='pending'
    )

    # Block dates in availability
    current_date = check_in
    while current_date < check_out:
        RoomAvailability.objects.get_or_create(
            room=room,
            date=current_date,
            defaults={'is_available': False, 'booking': booking}
        )
        current_date += datetime.timedelta(days=1)

    return redirect('booking:checkout_page', booking_uid=booking.booking_uid)

def checkout_page(request, booking_uid):
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    return render(request, 'booking/checkout.html', {'booking': booking})
