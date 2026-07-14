from django.views.generic import TemplateView
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from rooms.models.room import Room
from rooms.models.room_facility import RoomFacility
from dining.models.venue import DiningVenue
from testimonials.models.testimonial import Testimonial
from nearby_places.models.attraction import Attraction

class HomeView(TemplateView):
    template_name = 'homepage/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active currency from cookie, fallback to default published currency or USD
        from settings_manager.models.currency import Currency
        try:
            published_currencies = list(Currency.objects.filter(is_published=True))
            default_currency = 'USD'
            for c in published_currencies:
                if c.is_default:
                    default_currency = c.code
                    break
            selected_currency = self.request.COOKIES.get('currency', default_currency)
            valid_codes = [c.code for c in published_currencies]
            if selected_currency not in valid_codes:
                selected_currency = default_currency
        except Exception:
            selected_currency = 'USD'

        context['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        context['about_preview'] = AboutPreview.objects.first()
        context['featured_rooms'] = Room.objects.filter(is_featured=True, is_published=True, currency=selected_currency)[:3]
        context['featured_dining'] = DiningVenue.objects.filter(is_featured=True)[:3]
        context['facilities'] = RoomFacility.objects.filter(is_featured=True)
        context['testimonials'] = Testimonial.objects.filter(is_featured=True)[:5]
        context['attractions'] = Attraction.objects.filter(is_active=True).order_by('order')[:6]
        return context
