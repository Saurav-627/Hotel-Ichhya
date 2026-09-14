from .models.notification import Notification
from contact.models.inquiry import ContactInquiry
from conference.models.inquiry import EventInquiry
from dining.models.reservation import DiningReservation

def admin_notifications(request):
    """
    Context processor providing recent unread notifications and count for the admin dashboard header.
    """
    if request.user.is_authenticated and request.user.is_staff:
        recent_notifications = Notification.objects.all()[:6]
        unread_sys_count = Notification.objects.filter(is_read=False).count()
        unread_contact_count = ContactInquiry.objects.filter(is_read=False).count()
        unread_event_count = EventInquiry.objects.filter(status='pending').count()
        unread_dining_count = DiningReservation.objects.filter(status='pending').count()
        unread_inquiries_count = unread_contact_count + unread_event_count + unread_dining_count
        
        return {
            'header_notifications': recent_notifications,
            'unread_notifications_count': unread_sys_count + unread_inquiries_count,
            'unread_inquiries_count': unread_inquiries_count,
            'unread_contact_count': unread_contact_count,
            'unread_event_count': unread_event_count,
            'unread_dining_count': unread_dining_count,
        }
    return {
        'header_notifications': [],
        'unread_notifications_count': 0,
        'unread_inquiries_count': 0,
        'unread_contact_count': 0,
        'unread_event_count': 0,
        'unread_dining_count': 0,
    }
