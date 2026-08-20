from decimal import Decimal
from django.db import models
from settings_manager.models.currency import Currency


class Addon(models.Model):
    prices: models.QuerySet

    APPLIES_TO_CHOICES = (
        ('both', 'Both Rooms & Services'),
        ('room', 'Room Bookings Only'),
    )

    PRICE_TYPE_CHOICES = (
        ('per_night', 'Per Room / Per Night'),
        ('per_person', 'Per Guest'),
        ('per_person_per_night', 'Per Guest / Per Night'),
        ('per_booking', 'Per Room Booking'),
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True, help_text="Optional short summary shown to guests during booking")
    icon = models.CharField(max_length=50, default='fa-plus-circle', help_text="FontAwesome icon class e.g. fa-utensils, fa-camera, fa-car, fa-bed, fa-spa")
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO_CHOICES, default='room')
    price_type = models.CharField(max_length=20, choices=PRICE_TYPE_CHOICES, default='per_night')
    is_active = models.BooleanField(default=True, help_text="Whether this add-on is available for selection during booking")
    order = models.PositiveIntegerField(default=0, help_text="Display order sequence")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Add-on Service'
        verbose_name_plural = 'Add-on Services'

    def __str__(self):
        return f"{self.name} ({self.get_price_type_display()})"

    def set_active_currency(self, currency_code='USD'):
        self._active_currency_code = currency_code
        if hasattr(self, 'active_currency_price') and self.active_currency_price:
            matches = [p for p in self.active_currency_price if p.currency.iso_code == currency_code]
            self._active_price = matches[0] if matches else None
        else:
            self._active_price = self.prices.filter(currency__iso_code=currency_code).first()

    @property
    def current_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.price is not None:
            return active_price.price
        first_price = self.prices.first()
        return first_price.price if first_price else Decimal('0.00')

    @property
    def currency(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.currency:
            return active_price.currency
        first_price = self.prices.first()
        return first_price.currency if first_price else None


class AddonPrice(models.Model):
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE, related_name='prices')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='addon_prices')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")

    class Meta:
        unique_together = ('addon', 'currency')
        verbose_name = "Add-on Price"
        verbose_name_plural = "Add-on Prices"

    def __str__(self):
        return f"{self.addon.name} ({self.currency.iso_code}): {self.price}"


class BookingAddon(models.Model):
    booking = models.ForeignKey('booking.Booking', on_delete=models.CASCADE, related_name='booking_addons')
    addon = models.ForeignKey(Addon, on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_links')
    addon_name = models.CharField(max_length=150)
    price_type = models.CharField(max_length=30)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id',)

    @property
    def price_type_display(self):
        mapping = {
            'per_night': 'Per Room / Per Night',
            'per_person': 'Per Guest',
            'per_person_per_night': 'Per Guest / Per Night',
            'per_booking': 'Per Room Booking',
        }
        return mapping.get(self.price_type, self.price_type.replace('_', ' ').title())

    def __str__(self):
        return f"{self.addon_name} x {self.quantity} = {self.total_price} for Booking #{self.booking_id}"
