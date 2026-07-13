from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.attraction import Attraction

@admin.register(Attraction)
class AttractionAdmin(ModelAdmin):
    list_display = ('name', 'category', 'distance', 'travel_time', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
