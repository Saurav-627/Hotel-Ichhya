from django.views.generic import TemplateView
from apps.homepage.models.hero_slide import HeroSlide
from apps.homepage.models.about_preview import AboutPreview
from apps.rooms.models.room import Room
from apps.rooms.models.room_facility import RoomFacility
from apps.dining.models.venue import DiningVenue
from apps.testimonials.models.testimonial import Testimonial
from apps.nearby_places.models.attraction import Attraction

class HomeView(TemplateView):
    template_name = 'homepage/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        context['about_preview'] = AboutPreview.objects.first()
        context['featured_rooms'] = Room.objects.filter(is_featured=True)[:3]
        context['featured_dining'] = DiningVenue.objects.filter(is_featured=True)[:3]
        context['facilities'] = RoomFacility.objects.filter(is_featured=True)
        context['testimonials'] = Testimonial.objects.filter(is_featured=True)[:5]
        context['attractions'] = Attraction.objects.filter(is_active=True).order_by('order')[:6]
        return context
