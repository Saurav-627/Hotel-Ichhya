from django.http import HttpResponse
from django.views.decorators.http import require_POST
from ..models.inquiry import ContactInquiry

@require_POST
def submit_inquiry_ajax(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone', '')
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    category = request.POST.get('category', 'general')

    if not name or not email or not subject or not message:
        return HttpResponse(
            '<div class="p-4 rounded-xl border bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-300 text-xs sm:text-sm flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Please fill in all required fields.</span>'
            '</div>'
        )

    if phone:
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

    # Save inquiry to database
    inquiry = ContactInquiry.objects.create(
        name=name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
        category=category
    )

    try:
        from admin_dashboard.models.notification import create_admin_notification
        from django.urls import reverse
        from ..utils import send_inquiry_notification_email
        create_admin_notification(
            notification_type='inquiry_received',
            title=f"New Contact Inquiry from {name}",
            message=f"{subject}: {message[:100]}...",
            link_url=reverse('admin_dashboard:contact_inquiry_detail', kwargs={'pk': inquiry.pk})
        )
        send_inquiry_notification_email('contact', inquiry)
    except Exception:
        pass

    import json
    response_html = (
        f'<div class="p-5 sm:p-6 rounded-2xl border bg-emerald-500/10 border-emerald-500/30 text-left animate__animated animate__fadeIn space-y-3">'
        f'<div class="flex items-center gap-3">'
        f'<div class="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 text-lg border border-emerald-500/30">'
        f'<i class="fa-solid fa-paper-plane"></i>'
        f'</div>'
        f'<div>'
        f'<h4 class="font-luxury-title text-base sm:text-lg font-bold text-emerald-700 dark:text-emerald-400">Message Sent Successfully</h4>'
        f'<span class="text-[11px] font-semibold uppercase tracking-wider text-emerald-600/80 dark:text-emerald-400/80">Inquiry Logged</span>'
        f'</div>'
        f'</div>'
        f'<p class="text-xs sm:text-sm text-emerald-900 dark:text-emerald-100 leading-relaxed pt-1">'
        f'Thank you, <strong>{name}</strong>. Your inquiry regarding "<strong>{subject}</strong>" has been received. Our concierge desk will respond to you within 24 hours.'
        f'</p>'
        f'</div>'
    )

    response = HttpResponse(response_html)
    response['HX-Trigger'] = json.dumps({
        "show-toast": {
            "message": f"Thank you {name}! Your contact message has been sent successfully.",
            "type": "success"
        }
    })
    return response
