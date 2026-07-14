from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.activity import RecreationActivity

@admin.register(RecreationActivity)
class RecreationActivityAdmin(ModelAdmin):
    list_display = ('name', 'category', 'timings', 'price_info', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
