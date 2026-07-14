from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.hotel_settings import HotelSettings
from ..models.navigation import NavigationMenu
from ..models.currency import Currency

@admin.register(HotelSettings)
class HotelSettingsAdmin(ModelAdmin):
    list_display = ('site_name', 'theme', 'contact_phone', 'contact_email')
    
    def has_add_permission(self, request):
        # Don't allow adding more than one settings entry (Singleton)
        return not HotelSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(NavigationMenu)
class NavigationMenuAdmin(ModelAdmin):
    list_display = ('name', 'url', 'position', 'order', 'parent')
    list_filter = ('position', 'parent')
    search_fields = ('name', 'url')
    ordering = ('position', 'order')

@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'rate', 'is_published', 'is_default')
    list_filter = ('is_published', 'is_default')
    search_fields = ('code', 'name')
    list_editable = ('rate', 'is_published', 'is_default')
