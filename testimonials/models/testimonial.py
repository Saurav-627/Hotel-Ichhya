from django.db import models

class Testimonial(models.Model):
    SOURCE_CHOICES = [
        ('google', 'Google Review'),
        ('booking', 'Booking.com'),
        ('agoda', 'Agoda'),
        ('tripadvisor', 'Tripadvisor'),
        ('direct', 'Direct Guest Feedback'),
    ]

    guest_name = models.CharField(max_length=100)
    guest_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. United Kingdom, Nepal")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='google')
    rating = models.IntegerField(default=5, help_text="Rating from 1 to 5 stars")
    review_text = models.TextField()
    is_featured = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.guest_name} ({self.rating} stars) - {self.source}"
