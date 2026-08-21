from django.db import models
from django.core.validators import FileExtensionValidator
from core.utils import UploadTo, ValidateFileSize

class AboutPreview(models.Model):
    title = models.CharField(max_length=150, default="About Our Resort")
    subtitle = models.CharField(max_length=250, default="A Haven of Luxury & Hospitality")
    content = models.TextField(help_text="Introductory text about the hotel")
    image = models.ImageField(
        upload_to=UploadTo('homepage/about'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    video_file = models.FileField(
        upload_to=UploadTo('homepage/about/videos'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(50), FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg', 'mov', 'm4v'])],
        help_text="Uploaded promo video file (MP4/WebM/MOV)"
    )
    video_url = models.URLField(blank=True, null=True, help_text="Promo video YouTube/Vimeo link")

    # Statistics Counters
    stat1_value = models.CharField(max_length=10, default="120")
    stat1_label = models.CharField(max_length=50, default="Luxury Rooms")
    
    stat2_value = models.CharField(max_length=10, default="5")
    stat2_label = models.CharField(max_length=50, default="Star Rating")
    
    stat3_value = models.CharField(max_length=10, default="3")
    stat3_label = models.CharField(max_length=50, default="Elite Restaurants")
    
    stat4_value = models.CharField(max_length=10, default="15+")
    stat4_label = models.CharField(max_length=50, default="Awards Won")

    # Search Bar Widget
    search_button_text = models.CharField(max_length=50, default="Search Rooms", help_text="Search widget button text")

    # Featured Rooms Section Headers
    rooms_badge = models.CharField(max_length=100, default="Premium Sanctuary", help_text="Featured rooms section badge")
    rooms_title = models.CharField(max_length=150, default="Rooms & Suites", help_text="Featured rooms section title")
    rooms_subtitle = models.CharField(max_length=255, default="Explore our signature guest chambers designed for ultimate relaxation and comfort.", help_text="Featured rooms section subtitle")

    # Signature Facilities Section Headers
    facilities_badge = models.CharField(max_length=100, default="Elite Hospitality", help_text="Facilities section badge")
    facilities_title = models.CharField(max_length=150, default="Resort Services & Facilities", help_text="Facilities section title")
    facilities_subtitle = models.CharField(max_length=255, default="Indulge in our carefully curated amenities, designed to elevate your stay to a world-class level.", help_text="Facilities section subtitle")

    # Fine Dining Preview Section Headers
    dining_badge = models.CharField(max_length=100, default="Fine Culinary", help_text="Dining preview section badge")
    dining_title = models.CharField(max_length=150, default="Gastronomy & Lounge", help_text="Dining preview section title")
    dining_subtitle = models.CharField(max_length=255, default="Savor international delicacies, authentic Nepalese cuisine, and masterfully mixed cocktails curated by globally acclaimed chefs.", help_text="Dining preview section subtitle")
    dining_button_text = models.CharField(max_length=50, default="Explore More", help_text="Dining preview explore button text")

    # Testimonials Section Headers
    testimonials_badge = models.CharField(max_length=100, default="Guest Memoirs", help_text="Testimonials section badge")
    testimonials_title = models.CharField(max_length=150, default="What Our Guests Say", help_text="Testimonials section title")

    # Nearby Attractions Section Headers
    attractions_badge = models.CharField(max_length=100, default="Explore Nearby", help_text="Attractions section badge")
    attractions_title = models.CharField(max_length=150, default="Local Sights & Attractions", help_text="Attractions section title")

    # Newsletter Subscription Section
    newsletter_badge = models.CharField(max_length=100, default="Newsletter Subscription", help_text="Newsletter section badge")
    newsletter_title = models.CharField(max_length=150, default="Join The Elite Guild", help_text="Newsletter section title")
    newsletter_subtitle = models.CharField(max_length=255, default="Subscribe to receive exclusive offers, luxury travel logs, seasonal booking discounts, and resort news.", help_text="Newsletter section subtitle")
    newsletter_button_text = models.CharField(max_length=50, default="Subscribe", help_text="Newsletter submit button text")
    newsletter_image = models.ImageField(
        upload_to=UploadTo('homepage/newsletter'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(3)],
        help_text="Background photo for newsletter banner"
    )

    class Meta:
        verbose_name = "Homepage CMS Settings"
        verbose_name_plural = "Homepage CMS Settings"

    def __str__(self):
        return "Homepage CMS Settings"

    def save(self, *args, **kwargs):
        if not self.pk and AboutPreview.objects.exists():
            self.pk = AboutPreview.objects.first().pk
        super().save(*args, **kwargs)
