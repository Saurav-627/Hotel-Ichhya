from django.contrib import admin
from unfold.admin import ModelAdmin
from .models.seo_data import SEOData

@admin.register(SEOData)
class SEODataAdmin(ModelAdmin):
    list_display = ('path', 'meta_title', 'meta_description')
    search_fields = ('path', 'meta_title', 'meta_description')
