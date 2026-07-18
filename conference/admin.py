from django.contrib import admin
from .models.venue import EventVenue
from .models.inquiry import EventInquiry

@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'base_price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(EventInquiry)
class EventInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'event_date', 'guest_count', 'status')
    list_filter = ('status', 'event_date', 'venue')
    search_fields = ('name', 'email', 'phone')
