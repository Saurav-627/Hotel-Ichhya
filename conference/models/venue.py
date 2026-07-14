from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize

class EventVenue(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    capacity = models.IntegerField(help_text="Max seating/floating capacity")
    layout_options = models.TextField(help_text="e.g. Theatre: 300, Classroom: 150, Banquet: 200")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Starting price for renting the hall")
    image = models.ImageField(
        upload_to=UploadTo('conference'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"
