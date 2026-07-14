from django.views.generic import ListView, DetailView
from django.db.models import Q
from ..models.room import Room
from ..models.room_facility import RoomFacility

class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_published=True)
        
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

        queryset = queryset.filter(currency=selected_currency)
        
        # Filtering parameters
        category = self.request.GET.get('category')
        adults = self.request.GET.get('adults')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')

        if category:
            queryset = queryset.filter(category=category)
        if adults:
            try:
                queryset = queryset.filter(max_adults__gte=int(adults))
            except ValueError:
                pass
        if price_min:
            try:
                queryset = queryset.filter(base_price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                queryset = queryset.filter(base_price__lte=float(price_max))
            except ValueError:
                pass
                
        return queryset.prefetch_related('images', 'facilities')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Room.ROOM_CATEGORIES
        context['facilities'] = RoomFacility.objects.all()
        
        # Resolve active currency symbol
        from settings_manager.models.currency import Currency
        try:
            published_currencies = list(Currency.objects.filter(is_published=True))
            default_currency = 'USD'
            for c in published_currencies:
                if c.is_default:
                    default_currency = c.code
                    break
            selected_currency = self.request.COOKIES.get('currency', default_currency)
            currency_obj = Currency.objects.filter(code=selected_currency, is_published=True).first()
            context['selected_currency_symbol'] = currency_obj.symbol if currency_obj else '$'
        except Exception:
            context['selected_currency_symbol'] = '$'
            
        return context

class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True).prefetch_related('images', 'facilities', 'policies', 'seasonal_prices')
