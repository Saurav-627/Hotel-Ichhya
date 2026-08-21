from django.db import models
from core.utils import UploadTo, ValidateFileSize


class TeamMember(models.Model):
    """
    Board of Directors & Executive Leadership Team Members.
    """
    name = models.CharField(max_length=150, help_text="Full Name")
    role = models.CharField(max_length=150, help_text="Designation (e.g., Chairman, Director, CEO)")
    bio = models.TextField(help_text="Short bio and professional experience summary")
    image = models.ImageField(
        upload_to=UploadTo('about/team'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="Profile portrait photo"
    )
    order = models.PositiveIntegerField(default=0, help_text="Ordering sequence in the team grid")
    is_published = models.BooleanField(default=True, help_text="Whether to display this member on the live site")
    
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn profile URL")
    email = models.EmailField(blank=True, null=True, help_text="Contact email address")
    twitter_url = models.URLField(blank=True, null=True, help_text="X / Twitter profile URL")
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook profile URL")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'about'
        verbose_name = "Leadership Team Member"
        verbose_name_plural = "Leadership Team Members"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} - {self.role}"
