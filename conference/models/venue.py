from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize

class EventVenue(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    capacity = models.IntegerField(help_text="Max seating/floating capacity")
    layout_options = models.TextField(blank=True, default="", help_text="e.g. Theatre: 300, Classroom: 150, Banquet: 200")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Legacy fallback price")
    image = models.ImageField(
        upload_to=UploadTo('conference'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Feature this hall on homepage")
    event_types = models.ManyToManyField(
        'conference.EventType',
        blank=True,
        related_name='venues',
        help_text="Select event categories / occasions hosted in this banquet venue hall"
    )
    available_addons = models.ManyToManyField(
        'booking.Addon',
        blank=True,
        related_name='event_venues',
        limit_choices_to={'applies_to__in': ['events', 'both']},
        help_text="Select complimentary add-on services included with this venue package"
    )
    allow_custom_addons = models.BooleanField(
        default=True,
        help_text="Allow guests to select optional add-on services in the proposal inquiry form"
    )

    @property
    def included_addons(self):
        return self.available_addons.all()

    def set_active_currency(self, currency_code):
        self._active_currency_code = currency_code
        if hasattr(self, 'active_currency_price') and self.active_currency_price:
            matches = [p for p in self.active_currency_price if p.currency.iso_code == currency_code]
            self._active_price = matches[0] if matches else None
        else:
            self._active_price = self.base_prices.filter(currency__iso_code=currency_code).first()

    @property
    def current_base_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.base_price is not None:
            return active_price.base_price
        first_price = self.base_prices.first()
        if first_price and first_price.base_price is not None:
            return first_price.base_price
        return self.base_price

    @property
    def currency_symbol(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.currency:
            return active_price.currency.symbol
        first_price = self.base_prices.first()
        if first_price and first_price.currency:
            return first_price.currency.symbol
        return '$'

    @property
    def parsed_layouts(self):
        # Prefer structured VenueLayout records if present
        structured = list(self.layouts.filter(is_active=True).order_by('display_order', 'name'))
        if structured:
            return [{'id': l.id, 'name': l.name, 'value': f"{l.capacity} pax", 'capacity': l.capacity} for l in structured]

        if not self.layout_options:
            return []
        
        results = []
        raw_entries = []
        if '\n' in self.layout_options:
            raw_entries = [line.strip() for line in self.layout_options.splitlines() if line.strip()]
        else:
            raw_entries = [item.strip() for item in self.layout_options.split(',') if item.strip()]
            
        for item in raw_entries:
            if ':' in item:
                parts = item.rsplit(':', 1)
                name = parts[0].strip()
                val = parts[1].strip()
                if val.isdigit():
                    val = f"{val} pax"
                results.append({'name': name, 'value': val})
            else:
                words = item.split()
                if len(words) > 1 and words[-1].lower() in ('available', 'pax', 'setup'):
                    results.append({'name': ' '.join(words[:-1]), 'value': words[-1].capitalize()})
                else:
                    results.append({'name': item, 'value': 'Available'})
        return results

    @property
    def suitable_event_slugs(self):
        if self.pk and self.event_types.exists():
            return list(self.event_types.filter(is_active=True).values_list('slug', flat=True))
        slugs = []
        layouts = [l['name'].lower() for l in self.parsed_layouts]
        # Weddings & Receptions (Banquet / Round Table, or capacity >= 80)
        if any(k in layouts for k in ['banquet', 'round table']) or self.capacity >= 80:
            slugs.append('luxury-weddings')
        # Conferences & Summits (Theatre / Classroom and capacity >= 40, or capacity >= 100)
        if (any(k in layouts for k in ['theatre', 'classroom']) and self.capacity >= 40) or self.capacity >= 100:
            slugs.append('corporate-conferences')
        # Gala Dinners & Banquets (Banquet / Round Table, or capacity >= 60)
        if any(k in layouts for k in ['banquet', 'round table']) or self.capacity >= 60:
            slugs.append('gala-dinners')
        # Workshops & Seminars (Classroom / U-Shape / Theatre / Board Room)
        if any(k in layouts for k in ['classroom', 'u-shape', 'theatre', 'board room']):
            slugs.append('workshops-seminars')
        # Boardroom & Executive Meetings (Board Room / U-Shape / Classroom and capacity <= 60)
        if any(k in layouts for k in ['board room', 'u-shape']) and self.capacity <= 60:
            slugs.append('executive-meetings')
        # Social Celebrations
        if self.capacity >= 15:
            slugs.append('social-celebrations')
        return slugs

    @property
    def suitable_event_slugs_json(self):
        import json
        return json.dumps(self.suitable_event_slugs)

    @property
    def suitable_event_slugs_js(self):
        quoted = [f"'{s}'" for s in self.suitable_event_slugs]
        return f"[{', '.join(quoted)}]"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        gallery_images = getattr(self, '_prefetched_objects_cache', {}).get('images', None)
        if gallery_images is not None:
            valid_imgs = [img for img in gallery_images if img.image]
            if valid_imgs:
                primary_imgs = [img for img in valid_imgs if getattr(img, 'is_primary', False)]
                if primary_imgs:
                    return primary_imgs[0].image.url
                return valid_imgs[0].image.url
        else:
            primary_img = self.images.filter(is_primary=True, image__isnull=False).exclude(image='').first()
            if primary_img and primary_img.image:
                return primary_img.image.url
            first_img = self.images.filter(image__isnull=False).exclude(image='').first()
            if first_img and first_img.image:
                return first_img.image.url
        try:
            from django.templatetags.static import static
            return static('images/conference/default_venue.jpg')
        except Exception:
            return '/static/images/conference/default_venue.jpg'

