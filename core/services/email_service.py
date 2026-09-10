import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_booking_invoice_email(booking, payment=None, request=None):
    """
    Renders and dispatches an official HTML booking invoice email to the guest's email.
    Supports Mailpit and any configured Django SMTP backend.
    """
    if not booking.guest_email:
        logger.warning(f"Cannot send invoice email for Booking {booking.booking_uid}: No guest email provided.")
        return False, "No guest email provided."

    # Guard: Invoice email is only sent upon successful payment / confirmed booking status
    if booking.status != 'confirmed' and (not payment or payment.status != 'success'):
        logger.info(f"Skipping invoice email for Booking {booking.booking_uid} because status is '{booking.status}' and payment is not completed.")
        return False, "Booking payment is not completed."


    try:
        # Build absolute URL for online printable invoice receipt
        invoice_path = reverse('payments:view_invoice', kwargs={'booking_uid': booking.booking_uid})
        if request:
            invoice_url = request.build_absolute_uri(invoice_path)
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            invoice_url = f"{protocol}://{domain}{invoice_path}"

        # Fetch Hotel Settings for brand logo URL
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if booking.room:
            booking.room.set_active_currency(booking.currency_code)

        context = {
            'booking': booking,
            'payment': payment,
            'invoice_url': invoice_url,
            'logo_url': logo_url,
            'hotel_settings': hotel_settings,
        }

        # Render HTML body & fallback text body
        html_content = render_to_string('emails/booking_invoice_email.html', context)
        plain_content = strip_tags(html_content)

        site_name = hotel_settings.site_name if hotel_settings else "Hotel Ichchha"
        subject = f"✓ Booking Invoice & Receipt [{booking.booking_uid}] — {site_name}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@hotelichchha.com>')
        to_email = booking.guest_email

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent invoice email for Booking {booking.booking_uid} to {to_email}")

        # Simultaneously notify hotel staff email without blocking guest invoice
        try:
            send_hotel_booking_notification_email(booking, payment=payment, request=request)
        except Exception as hotel_err:
            logger.error(f"Failed to dispatch hotel notification email for Booking {booking.booking_uid}: {hotel_err}")

        return True, "Email sent successfully."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send invoice email for Booking {booking.booking_uid} to {booking.guest_email}: {error_msg}")
        return False, error_msg


def send_hotel_booking_notification_email(booking, payment=None, request=None):
    """
    Renders and dispatches an instant booking notification alert to the hotel's contact email.
    """
    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        hotel_email = hotel_settings.contact_email if hotel_settings and hotel_settings.contact_email else 'info@hotelichchha.com'

        # Build absolute URL for admin dashboard booking detail view
        admin_booking_path = reverse('admin_dashboard:booking_detail', kwargs={'pk': booking.pk})
        if request:
            admin_booking_url = request.build_absolute_uri(admin_booking_path)
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            admin_booking_url = f"{protocol}://{domain}{admin_booking_path}"

        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if booking.room:
            booking.room.set_active_currency(booking.currency_code)

        context = {
            'booking': booking,
            'payment': payment,
            'admin_booking_url': admin_booking_url,
            'logo_url': logo_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/booking_notification_hotel_email.html', context)
        plain_content = strip_tags(html_content)

        site_name = hotel_settings.site_name if hotel_settings else "Hotel Ichchha"
        subject = f"🛎️ New Booking Alert [{booking.booking_uid}] — {booking.guest_name} ({booking.currency_code} {booking.total})"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@hotelichchha.com>')

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[hotel_email],
            reply_to=[booking.guest_email] if booking.guest_email else None
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent hotel booking alert for Booking {booking.booking_uid} to {hotel_email}")
        return True, "Hotel notification sent successfully."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send hotel booking alert for Booking {booking.booking_uid}: {error_msg}")
        return False, error_msg


def send_contact_inquiry_emails(inquiry, request=None):
    """
    Dispatches a staff notification alert to hotel_settings.contact_email upon receiving a contact inquiry.
    """
    if not inquiry:
        return False, "No inquiry provided."

    from settings_manager.models.hotel_settings import HotelSettings
    hotel_settings = HotelSettings.objects.first()
    hotel_email = hotel_settings.contact_email if hotel_settings and hotel_settings.contact_email else 'info@hotelichchha.com'
    site_name = hotel_settings.site_name if hotel_settings else "Hotel Ichchha"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@hotelichchha.com>')

    logo_url = None
    if hotel_settings and hotel_settings.logo:
        logo_url = hotel_settings.logo.url
        if not logo_url.startswith('http'):
            if request:
                logo_url = request.build_absolute_uri(logo_url)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{logo_url}"

    if not logo_url:
        static_logo = '/static/images/hotel-logo.png'
        if request:
            logo_url = request.build_absolute_uri(static_logo)
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            logo_url = f"{protocol}://{domain}{static_logo}"

    # Build Admin Inquiry Detail URL
    admin_inquiry_url = None
    try:
        inquiry_path = reverse('admin_dashboard:contact_inquiry_detail', kwargs={'pk': inquiry.pk})
        if request:
            admin_inquiry_url = request.build_absolute_uri(inquiry_path)
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            admin_inquiry_url = f"{protocol}://{domain}{inquiry_path}"
    except Exception:
        admin_inquiry_url = None

    context = {
        'inquiry': inquiry,
        'admin_inquiry_url': admin_inquiry_url,
        'logo_url': logo_url,
        'hotel_settings': hotel_settings,
    }

    try:
        html_content = render_to_string('emails/contact_inquiry_hotel_email.html', context)
        plain_content = strip_tags(html_content)

        subject = f"📬 New Inquiry: {inquiry.subject} — From {inquiry.name}"

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[hotel_email],
            reply_to=[inquiry.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully dispatched contact inquiry email #{inquiry.pk} to {hotel_email}")
        return True, "Contact inquiry email sent successfully."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send contact inquiry notification for Inquiry #{inquiry.pk}: {error_msg}")
        return False, error_msg


def send_newsletter_welcome_email(subscriber_email, request=None):
    """
    Renders and dispatches a welcome email to new newsletter subscribers.
    """
    if not subscriber_email:
        return False, "No subscriber email provided."

    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if request:
            site_url = request.build_absolute_uri('/')
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            site_url = f"{protocol}://{domain}/"

        context = {
            'subscriber_email': subscriber_email,
            'logo_url': logo_url,
            'site_url': site_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/newsletter_welcome_email.html', context)
        plain_content = strip_tags(html_content)

        site_name = hotel_settings.site_name if hotel_settings else "Hotel Ichchha"
        subject = f"✨ Welcome to {site_name} — Exclusive Membership"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@hotelichchha.com>')

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[subscriber_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent newsletter welcome email to {subscriber_email}")
        return True, "Welcome email sent."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send newsletter welcome email to {subscriber_email}: {error_msg}")
        return False, error_msg


def send_newsletter_verification_email(subscriber, verification_url, request=None):
    """
    Renders and dispatches a double opt-in email verification email to new subscribers.
    """
    if not subscriber or not subscriber.email:
        return False, "No subscriber email provided."

    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if request:
            site_url = request.build_absolute_uri('/')
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            site_url = f"{protocol}://{domain}/"

        context = {
            'subscriber_email': subscriber.email,
            'verification_url': verification_url,
            'logo_url': logo_url,
            'site_url': site_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/newsletter_verification_email.html', context)
        plain_content = strip_tags(html_content)

        site_name = hotel_settings.site_name if hotel_settings else "Hotel Ichchha"
        subject = f"✉️ Please Confirm Your Newsletter Subscription — {site_name}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@hotelichchha.com>')

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[subscriber.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent newsletter verification email to {subscriber.email}")
        return True, "Verification email sent."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send newsletter verification email to {subscriber.email}: {error_msg}")
        return False, error_msg


def send_newsletter_broadcast_email(subject, message, recipient_list, request=None):
    """
    Renders and dispatches a bulk newsletter broadcast email to all active subscriber emails.
    """
    if not recipient_list:
        return False, 0, "No active recipient emails provided."

    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if request:
            site_url = request.build_absolute_uri('/')
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            site_url = f"{protocol}://{domain}/"

        context = {
            'subject': subject,
            'message': message,
            'logo_url': logo_url,
            'site_url': site_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/newsletter_broadcast_email.html', context)
        plain_content = strip_tags(html_content)
        site_name = hotel_settings.site_name if hotel_settings else "Hotel Ichchha"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@hotelichchha.com>')

        sent_count = 0
        for email in recipient_list:
            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_content,
                    from_email=from_email,
                    to=[email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                sent_count += 1
            except Exception as item_err:
                logger.error(f"Error sending campaign email to {email}: {item_err}")

        logger.info(f"Successfully broadcasted campaign '{subject}' to {sent_count}/{len(recipient_list)} subscribers.")
        return True, sent_count, f"Campaign sent to {sent_count} subscribers."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to execute broadcast email: {error_msg}")
        return False, 0, error_msg
