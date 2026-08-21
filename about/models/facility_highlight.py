from django.db import models


class AboutFacility(models.Model):
    """
    Key 5-Star Hotel facilities & amenities highlights displayed on the About page.
    """
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=80, default="fa-solid fa-star", help_text="FontAwesome icon class (e.g., fa-solid fa-spa)")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        app_label = 'about'
        verbose_name = "About Facility Highlight"
        verbose_name_plural = "About Facility Highlights"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
