from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.hero_slide import HeroSlide
from ..models.about_preview import AboutPreview

@admin.register(HeroSlide)
class HeroSlideAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')

@admin.register(AboutPreview)
class AboutPreviewAdmin(ModelAdmin):
    list_display = ('title', 'subtitle', 'stat1_label', 'stat2_label')

    def has_add_permission(self, request):
        return not AboutPreview.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
