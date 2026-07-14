from django.db import models
from django.utils.text import slugify

class RecreationActivity(models.Model):
    CATEGORY_CHOICES = [
        ('spa', 'Spa & Wellness'),
        ('pool', 'Swimming Pool'),
        ('gym', 'Fitness Center / Gym'),
        ('kids', 'Kids Play Zone'),
        ('casino', 'Casino'),
        ('adventure', 'Adventure Activities'),
        ('safari', 'Wildlife Safari'),
        ('games', 'Games Area'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    timings = models.CharField(max_length=100, help_text="e.g. 6:00 AM - 10:00 PM")
    price_info = models.CharField(max_length=100, default="Complimentary for Guests", help_text="e.g. $50/Session or Free")
    capacity = models.IntegerField(blank=True, null=True, help_text="Capacity if applicable")
    image = models.ImageField(upload_to='recreation/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Recreation & Activity"
        verbose_name_plural = "Recreation & Activities"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
