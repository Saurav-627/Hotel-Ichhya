from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from ..models.venue import DiningVenue
from ..models.reservation import DiningReservation
import datetime

def is_time_within_timings(selected_time, timings_str):
    if not timings_str or '-' not in timings_str:
        return True
    try:
        parts = timings_str.split('-')
        if len(parts) != 2:
            return True
        open_str = parts[0].strip()
        close_str = parts[1].strip()
        
        open_t = None
        close_t = None
        for fmt in ('%I:%M %p', '%I:%M%p', '%H:%M'):
            try:
                open_t = datetime.datetime.strptime(open_str, fmt).time()
                break
            except ValueError:
                pass
        for fmt in ('%I:%M %p', '%I:%M%p', '%H:%M'):
            try:
                close_t = datetime.datetime.strptime(close_str, fmt).time()
                break
            except ValueError:
                pass
                
        if open_t and close_t:
            if open_t <= close_t:
                return open_t <= selected_time <= close_t
            else:
                return selected_time >= open_t or selected_time <= close_t
    except Exception:
        pass
    return True


@require_POST
def book_table_ajax(request, venue_id):
    venue = get_object_or_404(DiningVenue, id=venue_id, is_published=True)
    
    # Retrieve POST data
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    date_str = request.POST.get('date')
    time_str = request.POST.get('time')
    guests_str = request.POST.get('guests', '2')
    special_requests = request.POST.get('special_requests', '')

    if not name or not email or not phone or not date_str or not time_str:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Please fill in all required fields.</span>'
            '</div>'
        )

    phone_digits = ''.join(filter(str.isdigit, phone))
    if len(phone_digits) < 10:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Phone number must contain at least 10 digits.</span>'
            '</div>'
        )
    if len(phone_digits) > 10:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Phone number cannot exceed 10 digits.</span>'
            '</div>'
        )

    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.datetime.strptime(time_str, "%H:%M").time()
        guests = int(guests_str)
    except ValueError:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Invalid date, time, or guest format.</span>'
            '</div>'
        )

    today = datetime.date.today()
    if date < today:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Reservation date cannot be in the past.</span>'
            '</div>'
        )

    if date == today and time < datetime.datetime.now().time():
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Reservation time cannot be in the past for today.</span>'
            '</div>'
        )

    if guests < 1:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Guest count must be at least 1.</span>'
            '</div>'
        )

    if venue.capacity and guests > venue.capacity:
        return HttpResponse(
            f'<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            f'<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            f'<span>This venue has a maximum seating capacity of {venue.capacity} guests. For larger parties, please contact our events desk.</span>'
            f'</div>'
        )

    if venue.timings and not is_time_within_timings(time, venue.timings):
        return HttpResponse(
            f'<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            f'<i class="fa-solid fa-clock text-red-500 text-base shrink-0"></i>'
            f'<span>Selected time ({time.strftime("%I:%M %p")}) is outside operating hours ({venue.timings}).</span>'
            f'</div>'
        )

    # Save reservation
    DiningReservation.objects.create(
        venue=venue,
        name=name,
        email=email,
        phone=phone,
        date=date,
        time=time,
        guests=guests,
        special_requests=special_requests
    )

    import json
    guest_text = f"{guests} guest" if guests == 1 else f"{guests} guests"
    response_html = (
        f'<div class="p-5 sm:p-6 rounded-2xl border bg-emerald-500/10 border-emerald-500/30 text-left animate__animated animate__fadeIn space-y-3">'
        f'<div class="flex items-center gap-3">'
        f'<div class="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 text-lg border border-emerald-500/30">'
        f'<i class="fa-solid fa-circle-check"></i>'
        f'</div>'
        f'<div>'
        f'<h4 class="font-luxury-title text-base sm:text-lg font-bold text-emerald-700 dark:text-emerald-400">Reservation Submitted</h4>'
        f'<span class="text-[11px] font-semibold uppercase tracking-wider text-emerald-600/80 dark:text-emerald-400/80">Inquiry Confirmed</span>'
        f'</div>'
        f'</div>'
        f'<p class="text-xs sm:text-sm text-emerald-900 dark:text-emerald-100 leading-relaxed pt-1">'
        f'Thank you, <strong>{name}</strong>. Your table reservation inquiry for <strong>{venue.name}</strong> on <strong>{date}</strong> at <strong>{time}</strong> ({guest_text}) has been received. Our team will contact you shortly to confirm.'
        f'</p>'
        f'</div>'
    )
    
    response = HttpResponse(response_html)
    response['HX-Trigger'] = json.dumps({
        "show-toast": {
            "message": f"Table reservation for {venue.name} submitted successfully!",
            "type": "success"
        }
    })
    return response
