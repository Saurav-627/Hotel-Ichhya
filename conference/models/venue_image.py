from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from core.utils import UploadTo, ValidateFileSize


class EventVenueImage(models.Model):
    venue = models.ForeignKey('EventVenue', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=UploadTo('conference/gallery'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Accessibility alt text for screen readers")

    # Generate thumbnail spec using django-imagekit for performance
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 85}
    )

    class Meta:
        verbose_name = "Event Venue Image"
        verbose_name_plural = "Event Venue Images"

    def __str__(self):
        return f"Image for {self.venue.name} (Primary: {self.is_primary})"
