from django.db import models

class ContactInquiry(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('room', 'Room Booking Inquiry'),
        ('event', 'Event & Banquets Inquiry'),
        ('dining', 'Dining & Table Booking'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    category = models.ForeignKey(
        'contact.InquiryCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        help_text="Category/nature of the inquiry"
    )
    is_read = models.BooleanField(default=False, help_text="Designates whether this inquiry has been viewed by admin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def get_category_display(self):
        if self.category:
            return self.category.name
        return "General Inquiry"

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_category_display()})"
