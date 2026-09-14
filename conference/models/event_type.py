from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize


class EventType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Short description of this event type")
    image = models.ImageField(
        upload_to=UploadTo('conference/event_types'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)],
        help_text="Cover/branding photo for marketing showcase"
    )
    icon = models.CharField(
        max_length=50,
        default='fa-calendar-check',
        help_text="FontAwesome icon class (e.g. fa-ring, fa-handshake, fa-cake-candles, fa-champagne-glasses)"
    )
    is_active = models.BooleanField(default=True, help_text="Available for public inquiries")
    is_featured = models.BooleanField(default=False, help_text="Showcase on homepage for branding & marketing")
    display_order = models.PositiveIntegerField(default=0, help_text="Sorting sequence in lists and dropdowns")

    @property
    def fontawesome_icon(self):
        val = (self.icon or '').strip()
        if not val or val == 'fa-calendar-star':
            return 'fa-calendar-check'
        if not val.startswith('fa-'):
            return f"fa-{val}"
        return val

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Event Type"
        verbose_name_plural = "Event Types"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def matching_venue_names(self):
        m2m_venues = list(self.venues.filter(is_active=True).values_list('name', flat=True))
        if m2m_venues:
            return m2m_venues
        from .venue import EventVenue
        venues = EventVenue.objects.filter(is_active=True)
        return [v.name for v in venues if self.slug in v.suitable_event_slugs]

    @property
    def matching_venues_count(self):
        return len(self.matching_venue_names)

    @property
    def showcase_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        filename_map = {
            'luxury-weddings': 'weddings.jpg',
            'corporate-conferences': 'conferences.jpg',
            'gala-dinners': 'galas.jpg',
            'workshops-seminars': 'workshops.jpg',
            'executive-meetings': 'boardroom.jpg',
            'social-celebrations': 'celebrations.jpg',
        }
        filename = filename_map.get(self.slug, 'weddings.jpg')
        rel_path = f"images/conference/event_types/{filename}"
        try:
            from django.templatetags.static import static
            return static(rel_path)
        except Exception:
            return f"/static/{rel_path}"

    @property
    def max_capacity(self):
        from .venue import EventVenue
        venues = EventVenue.objects.filter(is_active=True)
        matching = [v.capacity for v in venues if self.slug in v.suitable_event_slugs]
        return max(matching) if matching else 400

