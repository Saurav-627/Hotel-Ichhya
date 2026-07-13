from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models.testimonial import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('guest_name', 'source', 'rating', 'is_featured')
    list_filter = ('source', 'rating', 'is_featured')
    search_fields = ('guest_name', 'review_text')
