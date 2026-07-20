from django.db import models

class RoomCurrencyPrice(models.Model):
    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
        related_name='currency_prices'
    )
    currency = models.ForeignKey(
        'settings_manager.Currency',
        on_delete=models.PROTECT,
        related_name='room_currency_prices'
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('room', 'currency')
        verbose_name = "Room Currency Price"
        verbose_name_plural = "Room Currency Prices"

    def __str__(self):
        return f"{self.room.title} ({self.currency.iso_code}): {self.base_price}"
