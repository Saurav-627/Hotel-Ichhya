from django.contrib import admin
from .models.venue import EventVenue
from .models.inquiry import EventInquiry
from .models.event_type import EventType
from .models.venue_layout import VenueLayout


class VenueLayoutInline(admin.TabularInline):
    model = VenueLayout
    extra = 1


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'base_price', 'is_featured', 'is_active')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VenueLayoutInline]


from django.contrib import messages


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_featured', 'is_active', 'display_order')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['set_as_exclusive_featured_event']

    @admin.action(description="Brand this event exclusively on homepage hero (un-feature others)")
    def set_as_exclusive_featured_event(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one event type to brand exclusively.", level=messages.WARNING)
            return
        target = queryset.first()
        EventType.objects.exclude(pk=target.pk).update(is_featured=False)
        target.is_featured = True
        target.save()
        self.message_user(
            request, 
            f"'{target.name}' is now exclusively branded on the homepage hero spotlight.", 
            level=messages.SUCCESS
        )

    def save_model(self, request, obj, form, change):
        if obj.is_featured and 'is_featured' in form.changed_data:
            # When admin sets an event as featured, un-feature other events to keep 1 branded at a time
            EventType.objects.exclude(pk=obj.pk).update(is_featured=False)
            messages.info(
                request, 
                f"'{obj.name}' is set as the primary branded event on the homepage hero spotlight. Other events have been un-featured."
            )
        super().save_model(request, obj, form, change)



@admin.register(VenueLayout)
class VenueLayoutAdmin(admin.ModelAdmin):
    list_display = ('venue', 'name', 'capacity', 'is_active', 'display_order')
    list_filter = ('venue', 'is_active')
    search_fields = ('name', 'venue__name')


@admin.register(EventInquiry)
class EventInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'event_type', 'event_date', 'guest_count', 'status')
    list_filter = ('status', 'event_date', 'venue', 'event_type')
    search_fields = ('name', 'email', 'phone')
