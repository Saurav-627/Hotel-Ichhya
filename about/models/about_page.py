from django.db import models
from django.core.validators import FileExtensionValidator
from core.utils import UploadTo, ValidateFileSize


class AboutPage(models.Model):
    """
    Singleton model for dynamic CMS management of the About Page.
    """
    # 1. Hero Section
    hero_badge = models.CharField(max_length=100, default="⭐ Nepal's First 5-Star Hotel in Simara")
    hero_title = models.CharField(max_length=200, default="Nepal's First 5-Star Hotel in Simara")
    hero_subtitle = models.CharField(max_length=250, default="Hotel Ichchha — Simara, Bara, Nepal")
    hero_description = models.TextField(
        default="A verdant oasis in the heart of Simara offering exceptional comfort, convenience, enjoyment, and five-star hospitality services."
    )
    hero_image = models.ImageField(
        upload_to=UploadTo('about/hero'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="Background hero banner image"
    )
    hero_button_text = models.CharField(max_length=60, default="Book A Stay")
    hero_button_url = models.CharField(max_length=200, default="/rooms/")
    hero_secondary_button_text = models.CharField(max_length=60, default="Our Heritage")
    hero_secondary_button_url = models.CharField(max_length=200, default="#story")

    # 2. Story Section
    story_badge = models.CharField(max_length=100, default="Our Heritage & Story")
    story_title = models.CharField(max_length=200, default="A Verdant Oasis in the Heart of Simara")
    story_subtitle = models.CharField(max_length=250, default="Redefining Five-Star Hospitality in Nepal's Southern Gateway")
    story_content = models.TextField(
        default=(
            "Being a top hospitality provider in Nepal, Hotel Ichchha guarantees finest offerings due to its convenient location in Simara, Bara. "
            "It is the premier choice for business executives, leisure seekers, destination weddings, and pilgrimage journeys. "
            "With 96 exquisitely appointed rooms and suites, multiple dining venues, a serene wellness spa, expansive conference halls, and lush gardens, "
            "Hotel Ichchha sets a new benchmark in guest experience and luxury service excellence."
        ),
        help_text="Detailed story and overview of Hotel Ichchha"
    )
    story_floating_badge = models.CharField(max_length=80, default="5-Star Certified")
    story_image_1 = models.ImageField(
        upload_to=UploadTo('about/story'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="Primary story showcase image"
    )
    story_image_2 = models.ImageField(
        upload_to=UploadTo('about/story'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="Secondary story showcase image"
    )

    # 2.5 Story Quick Highlight Features (6 badges)
    story_feature_1_icon = models.CharField(max_length=60, default="fa-solid fa-bed")
    story_feature_1_text = models.CharField(max_length=100, default="96 Luxury Rooms")
    story_feature_2_icon = models.CharField(max_length=60, default="fa-solid fa-ring")
    story_feature_2_text = models.CharField(max_length=100, default="Destination Weddings")
    story_feature_3_icon = models.CharField(max_length=60, default="fa-solid fa-plane-arrival")
    story_feature_3_text = models.CharField(max_length=100, default="Simara Airport 5 Min")
    story_feature_4_icon = models.CharField(max_length=60, default="fa-solid fa-spa")
    story_feature_4_text = models.CharField(max_length=100, default="Ayurvedic Spa")
    story_feature_5_icon = models.CharField(max_length=60, default="fa-solid fa-utensils")
    story_feature_5_text = models.CharField(max_length=100, default="Gourmet Dining")
    story_feature_6_icon = models.CharField(max_length=60, default="fa-solid fa-users-rectangle")
    story_feature_6_text = models.CharField(max_length=100, default="1,000+ Pax Hall")

    # 3. Statistics Counters
    stat1_value = models.CharField(max_length=20, default="96")
    stat1_label = models.CharField(max_length=60, default="Luxury Rooms & Suites")

    stat2_value = models.CharField(max_length=20, default="5-Star")
    stat2_label = models.CharField(max_length=60, default="Luxury Rating")

    stat3_value = models.CharField(max_length=20, default="27+")
    stat3_label = models.CharField(max_length=60, default="Years Hospitality Leadership")

    stat4_value = models.CharField(max_length=20, default="1,000+")
    stat4_label = models.CharField(max_length=60, default="Banqueting Pax Capacity")

    # 4. Message from CEO Section
    ceo_badge = models.CharField(max_length=100, default="Executive Leadership")
    ceo_title = models.CharField(max_length=200, default="Message from the CEO")
    ceo_subtitle = models.CharField(max_length=250, default="We are committed to providing the best hospitality services to our guests.")
    ceo_name = models.CharField(max_length=150, default="Rewanta Prasad Dhaubhadel")
    ceo_role = models.CharField(max_length=150, default="Chief Executive Officer (CEO)")
    ceo_credentials = models.CharField(max_length=150, default="Swiss Hotel Mgmt School Alumnus")
    ceo_designation = models.CharField(max_length=150, default="Chief Executive Officer • Hotel Ichchha")
    ceo_image = models.ImageField(
        upload_to=UploadTo('about/ceo'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="CEO portrait image"
    )
    ceo_quote = models.TextField(
        default="With a heart rooted in tradition and eyes set on innovation, I remain committed to advancing Nepal’s hospitality industry and creating opportunities for sustainable growth and global recognition."
    )
    ceo_message = models.TextField(
        default=(
            "Namaste,\n\n"
            "My name is Rewanta Prasad Dhaubhadel, though I’m more fondly known as Rebu by friends, family, and colleagues. "
            "With over 27 years of experience in the hospitality industry, my journey has been deeply rooted in a passion for service, excellence, and continuous growth.\n\n"
            "I began my career with a formal education in hospitality, earning a Hotel Management Degree from the prestigious Swiss Hotel Management School. "
            "My early professional experiences in Switzerland—across cities like Geneva, Lausanne, and Montreux—provided a strong foundation in global standards and refined hospitality practices.\n\n"
            "Upon returning to Nepal, I took on various leadership roles in the country’s hospitality sector, including at the renowned Hotel Royal Singi, "
            "contributing to the dynamic tourism and service landscape of the Kathmandu Valley. I’ve also had the honor of mentoring the next generation of hoteliers as a faculty member at GATE College, sharing both my international insights and local expertise.\n\n"
            "Currently, I serve as the Chief Executive Officer of Hotel Ichchha – Simara, a leading establishment in Nepal’s southern plains. "
            "In this role, I am driven by a vision to unlock the immense potential of Simara, transforming it into a premier hospitality destination that not only uplifts the local economy but also sets new benchmarks in guest experience and service excellence."
        ),
        help_text="Full CEO narrative and message"
    )
    ceo_signature_text = models.CharField(max_length=150, default="Rewanta Prasad Dhaubhadel (Rebu)")

    # 5. Core Philosophy (Mission, Vision, Values)
    mission_title = models.CharField(max_length=150, default="Our Mission")
    mission_text = models.TextField(
        default="To deliver authentic Nepalese warmth fused with international 5-star hospitality standards, creating unforgettable memories for every guest who walks through our doors."
    )

    vision_title = models.CharField(max_length=150, default="Our Vision")
    vision_text = models.TextField(
        default="To be recognized as Nepal's premier luxury destination resort and conference hub, setting the standard for sustainable tourism and world-class service."
    )

    values_title = models.CharField(max_length=150, default="Our Core Values")
    values_text = models.TextField(
        default="Guest-centric excellence, uncompromising integrity, cultural pride, culinary artistry, and passionate commitment to environmental sustainability."
    )

    # 5.5 Leadership Team Section Header
    team_badge = models.CharField(max_length=100, default="Visionary Governance")
    team_title = models.CharField(max_length=200, default="Get to Know the Faces Behind Our Success")
    team_subtitle = models.CharField(
        max_length=250, 
        default="Unveil the talented individuals who embark on a collective mission to elevate your experience at Hotel Ichchha."
    )

    # 6. Video Showcase Section
    video_badge = models.CharField(max_length=100, default="Resort Visual Tour")
    video_title = models.CharField(max_length=200, default="Experience Hotel Ichchha in Motion")
    video_subtitle = models.CharField(max_length=250, default="Take a glimpse into our lush resort grounds, sparkling pool, plush suites, and banquet venues.")
    video_url = models.URLField(
        blank=True,
        null=True,
        default="https://hotelichchha.com/backend/images/articles/video/LAeuf-intro_video--hqhIzqZ.mp4",
        help_text="Direct MP4 video URL or YouTube/Vimeo link"
    )
    video_file = models.FileField(
        upload_to=UploadTo('about/videos'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(50), FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg', 'mov', 'm4v'])],
        help_text="Upload custom MP4/WebM video"
    )
    video_thumbnail = models.ImageField(
        upload_to=UploadTo('about/video_posters'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="Cover poster image for the video player"
    )

    # 7. 5-Star Amenities Section Headers
    facilities_badge = models.CharField(max_length=100, default="World-Class Comfort")
    facilities_title = models.CharField(max_length=200, default="Comprehensive 5-Star Amenities")
    facilities_subtitle = models.CharField(
        max_length=250, 
        default="Everything you need for an unmatched stay, relaxing wellness retreat, or grand conference event in Simara."
    )

    # 8. Call To Action (Bottom)
    cta_badge = models.CharField(max_length=100, default="Reservations & Inquiries")
    cta_title = models.CharField(max_length=200, default="Plan Your Unforgettable Stay in Simara")
    cta_subtitle = models.CharField(max_length=250, default="Whether you are traveling for business, leisure, or a grand wedding celebration, our dedicated team awaits to welcome you.")
    cta_button_text = models.CharField(max_length=60, default="Book A Stay")
    cta_button_url = models.CharField(max_length=200, default="/rooms/")
    cta_secondary_button_text = models.CharField(max_length=60, default="Contact Concierge")
    cta_secondary_button_url = models.CharField(max_length=200, default="/contact/")
    cta_image = models.ImageField(
        upload_to=UploadTo('about/cta'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(5)],
        help_text="Background photo for bottom call to action banner"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'about'
        verbose_name = "About Page CMS Settings"
        verbose_name_plural = "About Page CMS Settings"

    def __str__(self):
        return "About Page CMS Settings"

    def save(self, *args, **kwargs):
        if not self.pk and AboutPage.objects.exists():
            self.pk = AboutPage.objects.first().pk
        super().save(*args, **kwargs)
