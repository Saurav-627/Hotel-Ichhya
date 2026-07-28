from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize

class EventVenue(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    capacity = models.IntegerField(help_text="Max seating/floating capacity")
    layout_options = models.TextField(help_text="e.g. Theatre: 300, Classroom: 150, Banquet: 200")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Legacy fallback price")
    image = models.ImageField(
        upload_to=UploadTo('conference'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    is_active = models.BooleanField(default=True)

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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"
