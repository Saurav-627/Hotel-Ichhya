from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models.room_category import RoomCategory
from .models.room import Room
from .models.room_image import RoomImage
from .models.room_facility import RoomFacility
from .models.room_price import RoomPrice
from .models.room_policy import RoomPolicy
from .models.room_availability import RoomAvailability

class RoomImageInline(TabularInline):
    model = RoomImage
    extra = 1

@admin.register(RoomCategory)
class RoomCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    prepopulated_fields = {'slug': ('name',)}

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
    actions = ['duplicate_room']

    @admin.action(description="Duplicate selected rooms (Deep Copy)")
    def duplicate_room(self, request, queryset):
        import uuid
        count = 0
        for room in queryset:
            original_pk = room.pk
            original_room = Room.objects.get(pk=original_pk)

            # Clone Room fields
            room.pk = None
            room.title = f"{room.title} (Copy)"
            room.slug = f"{room.slug}-copy-{str(uuid.uuid4())[:8]}"
            room.save()

            # Copy Many-to-Many facilities
            room.facilities.set(original_room.facilities.all())

            # Copy related inlines
            for img in original_room.images.all():
                img.pk = None
                img.room = room
                img.save()

            for policy in original_room.policies.all():
                policy.pk = None
                policy.room = room
                policy.save()

            for price in original_room.seasonal_prices.all():
                price.pk = None
                price.room = room
                price.save()

            count += 1

        self.message_user(request, f"Successfully duplicated {count} room(s).")


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
