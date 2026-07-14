from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models.room import Room
from .models.room_image import RoomImage
from .models.room_facility import RoomFacility
from .models.room_price import RoomPrice
from .models.room_policy import RoomPolicy
from .models.room_availability import RoomAvailability

class RoomImageInline(TabularInline):
    model = RoomImage
    extra = 1

class RoomPolicyInline(TabularInline):
    model = RoomPolicy
    extra = 1

class RoomPriceInline(TabularInline):
    model = RoomPrice
    extra = 1

@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = ('title', 'category', 'base_price', 'currency', 'is_published', 'is_featured')
    list_filter = ('category', 'currency', 'is_published', 'is_featured', 'facilities')
    search_fields = ('title', 'description', 'highlights')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RoomImageInline, RoomPolicyInline, RoomPriceInline]

@admin.register(RoomFacility)
class RoomFacilityAdmin(ModelAdmin):
    list_display = ('name', 'icon_class', 'is_featured')
    search_fields = ('name',)

@admin.register(RoomPrice)
class RoomPriceAdmin(ModelAdmin):
    list_display = ('room', 'name', 'start_date', 'end_date', 'price_override', 'is_active')
    list_filter = ('is_active', 'start_date', 'room')

@admin.register(RoomPolicy)
class RoomPolicyAdmin(ModelAdmin):
    list_display = ('title', 'room')
    list_filter = ('room',)

@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(ModelAdmin):
    list_display = ('room', 'date', 'is_available', 'booking')
    list_filter = ('is_available', 'date', 'room')
