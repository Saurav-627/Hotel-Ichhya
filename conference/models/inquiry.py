from django.db import models


class EventInquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('proposal_sent', 'Proposal Sent'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('processed', 'Processed (Legacy)'),
    ]

    venue = models.ForeignKey('EventVenue', on_delete=models.CASCADE, related_name='inquiries')
    event_type = models.ForeignKey('EventType', on_delete=models.PROTECT, null=True, blank=True, related_name='inquiries')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    event_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    guest_count = models.IntegerField()
    preferred_layout = models.ForeignKey('VenueLayout', on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    catering_required = models.BooleanField(default=True)
    addons = models.ManyToManyField('booking.Addon', blank=True, related_name='event_inquiries', help_text="Requested event add-on services")
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        type_str = self.event_type.name if self.event_type else "Event"
        return f"{type_str} Inquiry for {self.name} on {self.event_date}"

    @property
    def event_type_name(self):
        return self.event_type.name if self.event_type else "Not specified"

    @property
    def has_conflict(self):
        """Flags potential scheduling overlap with another active inquiry for the same venue & date."""
        if not self.venue_id or not self.event_date:
            return False
        return EventInquiry.objects.filter(
            venue_id=self.venue_id,
            event_date=self.event_date
        ).exclude(pk=self.pk).exclude(status='cancelled').exists()

