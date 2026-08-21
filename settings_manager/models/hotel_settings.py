from django.db import models
from core.utils import UploadTo, ValidateFileSize

class HotelSettings(models.Model):
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('luxury', 'Luxury Gold Mode'),
        ('festival', 'Festival Theme'),
    ]

    site_name = models.CharField(max_length=100, default="Hotel Ichchha")
    favicon = models.ImageField(
        upload_to=UploadTo('settings/favicons'),
        blank=True,
        null=True,
        help_text="Browser favicon icon (.png, .ico, .svg)",
        validators=[ValidateFileSize(2)]
    )
    logo = models.ImageField(
        upload_to=UploadTo('settings/logos'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    logo_dark = models.ImageField(
        upload_to=UploadTo('settings/logos'),
        blank=True,
        null=True,
        help_text="Dark mode logo version",
        validators=[ValidateFileSize(2)]
    )
    admin_logo = models.ImageField(
        upload_to=UploadTo('settings/logos'),
        blank=True,
        null=True,
        help_text="Admin panel logo (falls back to main logo if blank)",
        validators=[ValidateFileSize(2)]
    )
    admin_title = models.CharField(
        max_length=100,
        default="Hotel Ichchha CMS Admin Dashboard",
        help_text="Admin panel browser tab title"
    )
    admin_label = models.CharField(
        max_length=100,
        default="Ichchha Portal",
        help_text="Admin sidebar header label"
    )
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='luxury')
    
    # Contact Info
    contact_phone = models.CharField(max_length=20, default="+977-1-4XXXXXX")
    contact_email = models.EmailField(default="info@hotelichchha.com")
    inquiry_notification_email = models.EmailField(default="info@hotelichchha.com", help_text="Email address to receive instant notifications for new guest inquiries and contact queries")
    address = models.CharField(max_length=255, default="Bara, Nepal")
    google_maps_iframe = models.TextField(blank=True, null=True, help_text="Google Maps HTML embed iframe")

    # Social Links
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    tripadvisor_url = models.URLField(blank=True, null=True)

    # Header Controls
    header_badge = models.CharField(max_length=100, default="⭐ 5-Star Luxury Resort", help_text="Top header information badge")
    header_cta_text = models.CharField(max_length=50, default="Book A Stay", help_text="Header navigation button text")
    header_cta_url = models.CharField(max_length=200, default="/rooms/", help_text="Header navigation button URL")

    # Footer details
    about_text = models.TextField(default="A premium 5-star experience of hospitality and luxury.")
    copyright_text = models.CharField(max_length=255, default="&copy; 2026 Hotel Ichchha. All Rights Reserved.")
    awards_text = models.CharField(max_length=255, default="Awards: World Luxury Hotel Winner 2026", help_text="Footer awards accreditation text")

    # Contact Page Form Controls
    contact_form_title = models.CharField(max_length=150, default="Send an Inquiry", help_text="Contact page form heading")
    contact_form_subtitle = models.CharField(max_length=255, default="Have a custom event or dining reservation question? Complete the form below.", help_text="Contact page form subtitle")
    contact_form_button_text = models.CharField(max_length=50, default="Submit Inquiry Message", help_text="Contact page form submit button text")

    class Meta:
        verbose_name = "Hotel Global Settings"
        verbose_name_plural = "Hotel Global Settings"

    def __str__(self):
        return f"{self.site_name} Settings"

    def save(self, *args, **kwargs):
        # Override save to ensure only one instance of HotelSettings exists
        if not self.pk and HotelSettings.objects.exists():
            # If dynamic save occurs, replace the existing one
            self.pk = HotelSettings.objects.first().pk
        super().save(*args, **kwargs)
