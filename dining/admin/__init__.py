from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.venue import DiningVenue
from ..models.reservation import DiningReservation

@admin.register(DiningVenue)
class DiningVenueAdmin(ModelAdmin):
    list_display = ('name', 'category', 'timings', 'capacity', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DiningReservation)
class DiningReservationAdmin(ModelAdmin):
    list_display = ('name', 'venue', 'date', 'time', 'guests', 'status')
    list_filter = ('status', 'date', 'venue')
    search_fields = ('name', 'email', 'phone')
