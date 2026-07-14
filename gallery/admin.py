from django.contrib import admin
from unfold.admin import ModelAdmin
from .models.category import GalleryCategory
from .models.item import GalleryItem

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_published')
    list_filter = ('is_published',)
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GalleryItem)
class GalleryItemAdmin(ModelAdmin):
    list_display = ('id', 'category', 'caption', 'is_video', 'is_drone', 'is_published')
    list_filter = ('category', 'is_video', 'is_drone', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('caption',)
