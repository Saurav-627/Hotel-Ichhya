from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.staticfiles.storage import staticfiles_storage
from settings_manager.models.hotel_settings import HotelSettings

def send_inquiry_notification_email(inquiry_type, inquiry_obj):
    """
    Sends an instant email notification (with resort logo and full request details) 
    to the admin notification email configured in General Settings whenever any guest inquiry 
    (Contact, Event, or Dining Table Reservation) is submitted.
    """
    try:
        settings = HotelSettings.objects.first()
        recipient_email = (
            settings.inquiry_notification_email 
            if settings and settings.inquiry_notification_email 
            else (settings.contact_email if settings else "info@hotelichchha.com")
        )
        
        if not recipient_email:
            recipient_email = "info@hotelichchha.com"

        # Resolve Logo URL with absolute scheme for email clients
        logo_url = ""
        if settings:
            if settings.logo and hasattr(settings.logo, 'url'):
                try:
                    logo_url = settings.logo.url
                except Exception:
                    pass
            elif settings.admin_logo and hasattr(settings.admin_logo, 'url'):
                try:
                    logo_url = settings.admin_logo.url
                except Exception:
                    pass

        if not logo_url:
            try:
                logo_url = staticfiles_storage.url('images/hotel-logo.png')
            except Exception:
                logo_url = '/static/images/hotel-logo.png'

        if logo_url and not logo_url.startswith('http'):
            logo_url = f"http://127.0.0.1:8000{logo_url}"

        if inquiry_type == 'contact':
            subject = f"[Contact Inquiry] {inquiry_obj.subject} - {inquiry_obj.name}"
            category_display = getattr(inquiry_obj, 'get_category_display', lambda: inquiry_obj.category)()
            html_content = render_to_string('emails/inquiry_notification_email.html', {
                'inquiry_type': 'Contact Inquiry',
                'name': inquiry_obj.name,
                'email': inquiry_obj.email,
                'phone': inquiry_obj.phone,
                'category': category_display,
                'subject': inquiry_obj.subject,
                'message': inquiry_obj.message,
                'created_at': inquiry_obj.created_at,
                'hotel_settings': settings,
                'logo_url': logo_url,
            })
        elif inquiry_type == 'dining':
            time_str = inquiry_obj.time.strftime("%I:%M %p") if hasattr(inquiry_obj.time, 'strftime') else str(inquiry_obj.time)
            subject = f"[Dining Table Reservation] {inquiry_obj.venue.name} - {inquiry_obj.name}"
            html_content = render_to_string('emails/inquiry_notification_email.html', {
                'inquiry_type': 'Dining Table Reservation',
                'name': inquiry_obj.name,
                'email': inquiry_obj.email,
                'phone': inquiry_obj.phone,
                'category': f"Dining Venue: {inquiry_obj.venue.name}",
                'subject': f"Reservation: {inquiry_obj.date} at {time_str} ({inquiry_obj.guests} guests)",
                'message': inquiry_obj.special_requests or "No special requests provided.",
                'created_at': inquiry_obj.created_at,
                'hotel_settings': settings,
                'logo_url': logo_url,
            })
        else:  # event
            subject = f"[Event Inquiry] {inquiry_obj.venue.name} - {inquiry_obj.name}"
            html_content = render_to_string('emails/inquiry_notification_email.html', {
                'inquiry_type': 'Event & Banquets Inquiry',
                'name': inquiry_obj.name,
                'email': inquiry_obj.email,
                'phone': inquiry_obj.phone,
                'category': f"Venue: {inquiry_obj.venue.name}",
                'subject': f"Event Date: {inquiry_obj.event_date} ({inquiry_obj.guest_count} Guests)",
                'message': inquiry_obj.notes or "No additional notes provided.",
                'created_at': inquiry_obj.created_at,
                'hotel_settings': settings,
                'logo_url': logo_url,
            })

        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email="no-reply@hotelichchha.com",
            to=[recipient_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
    except Exception as e:
        print(f"Error sending inquiry notification email: {e}")
