from django.db import models

class RoomPrice(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='seasonal_prices')
    name = models.CharField(max_length=100, help_text="e.g. Christmas Season, Summer Special")
    start_date = models.DateField()
    end_date = models.DateField()
    price_override = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per night during this period")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Room Seasonal Price"
        verbose_name_plural = "Room Seasonal Prices"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} - {self.room.title}: ${self.price_override} ({self.start_date} to {self.end_date})"
