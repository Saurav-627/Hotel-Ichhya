from django.db import models
from django.utils.text import slugify

class Room(models.Model):
    ROOM_CATEGORIES = [
        ('deluxe', 'Deluxe Room'),
        ('super_deluxe', 'Super Deluxe Room'),
        ('premium', 'Premium Room'),
        ('premium_suite', 'Premium Junior Suite'),
        ('deluxe_suite', 'Deluxe Suite'),
        ('honeymoon_suite', 'Honeymoon Suite'),
        ('executive', 'Executive Room'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD ($)'),
        ('NPR', 'NPR (₨)'),
        ('EUR', 'EUR (€)'),
        ('GBP', 'GBP (£)'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=ROOM_CATEGORIES, default='deluxe')
    description = models.TextField()
    highlights = models.TextField(help_text="Comma-separated or line-separated list of room highlights")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', help_text="Currency of the base and discount price")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=13.00) # e.g. 13% VAT
    room_size = models.IntegerField(help_text="Size in sq. ft. or sq. meters")
    max_adults = models.IntegerField(default=2)
    max_children = models.IntegerField(default=0)
    bed_type = models.CharField(max_length=100, default="King Size")
    facilities = models.ManyToManyField('RoomFacility', related_name='rooms', blank=True)
    virtual_tour_url = models.URLField(blank=True, null=True, help_text="Link to 3D virtual tour")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo embed link")
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, help_text="Designates whether this room is visible on the website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['base_price']

    def __str__(self):
        return f"{self.title} ({self.currency} {self.base_price}/night)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.base_price

    @property
    def price_with_tax(self):
        price = self.final_price
        return price + (price * (self.tax_percentage / 100))
