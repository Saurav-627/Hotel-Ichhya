import uuid
from django.db import models
from django.conf import settings

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]

    booking_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='bookings')
    
    # Guest details
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    
    # Dates
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.IntegerField(default=2)
    children = models.IntegerField(default=0)
    
    # Pricing fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True, null=True)

    # Channel Manager / OTA Sync Fields (Setup Only)
    channel_name = models.CharField(max_length=50, default='direct', help_text="e.g. direct, booking.com, expedia, agoda")
    ota_reservation_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reservation ID from the OTA/channel manager")
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='pay_later', choices=[('card', 'Visa/Mastercard'), ('pay_later', 'Pay at Hotel')])
    channel_raw_payload = models.JSONField(blank=True, null=True, help_text="Raw payload received from the channel manager/OTA API")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_uid} - {self.guest_name} ({self.room.title})"
