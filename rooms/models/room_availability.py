from django.db import models

class RoomAvailability(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    booking = models.ForeignKey('booking.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='room_dates')

    class Meta:
        verbose_name = "Room Availability"
        verbose_name_plural = "Room Availabilities"
        unique_together = ('room', 'date')

    def __str__(self):
        status = "Available" if self.is_available else "Booked"
        return f"{self.room.title} on {self.date}: {status}"
