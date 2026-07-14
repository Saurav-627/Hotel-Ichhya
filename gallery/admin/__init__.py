from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.category import GalleryCategory
from ..models.item import GalleryItem

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GalleryItem)
class GalleryItemAdmin(ModelAdmin):
    list_display = ('id', 'category', 'caption', 'is_video', 'is_drone')
    list_filter = ('category', 'is_video', 'is_drone')
    search_fields = ('caption',)
