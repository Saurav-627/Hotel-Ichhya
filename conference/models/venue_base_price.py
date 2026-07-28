from django.db import models

class VenueBasePrice(models.Model):
    """Permanent starting base price for an event venue in a specific currency."""
    venue = models.ForeignKey(
        'EventVenue',
        on_delete=models.CASCADE,
        related_name='base_prices'
    )
    currency = models.ForeignKey(
        'settings_manager.Currency',
        on_delete=models.PROTECT,
        related_name='venue_base_prices'
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('venue', 'currency')
        verbose_name = "Venue Base Price"
        verbose_name_plural = "Venue Base Prices"

    def __str__(self):
        return f"{self.venue.name} ({self.currency.iso_code}): {self.base_price}"
