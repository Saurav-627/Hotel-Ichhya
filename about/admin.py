from django.contrib import admin
from .models import AboutPage, TeamMember, AboutFacility


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ['hero_title', 'ceo_name', 'updated_at']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'order', 'is_published']
    list_editable = ['order', 'is_published']
    search_fields = ['name', 'role', 'bio']


@admin.register(AboutFacility)
class AboutFacilityAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'order', 'is_published']
    list_editable = ['order', 'is_published']
