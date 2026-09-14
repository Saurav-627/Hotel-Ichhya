from django.db import models


class VenueLayout(models.Model):
    venue = models.ForeignKey(
        'EventVenue',
        on_delete=models.CASCADE,
        related_name='layouts'
    )
    name = models.CharField(max_length=100, help_text="e.g. Theatre, Banquet, Classroom, U-Shape, Boardroom")
    capacity = models.PositiveIntegerField(help_text="Seating capacity for this layout setup")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Venue Layout"
        verbose_name_plural = "Venue Layouts"

    def __str__(self):
        return f"{self.venue.name} — {self.name} ({self.capacity} pax)"
