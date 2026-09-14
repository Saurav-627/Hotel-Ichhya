from django.db import models
from django.utils.text import slugify


class InquiryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True, help_text="Brief description or purpose of this category")
    is_active = models.BooleanField(default=True, help_text="Designates whether this category is active and visible in the contact form")
    display_order = models.PositiveIntegerField(default=0, help_text="Display sort order sequence")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Inquiry Category"
        verbose_name_plural = "Inquiry Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
