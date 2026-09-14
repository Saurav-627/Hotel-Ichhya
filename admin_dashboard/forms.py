from django import forms
from settings_manager.models.hotel_settings import HotelSettings
from payments.models.payment_processor import PaymentProcessor, PaymentProcessorCurrency
from settings_manager.models.navigation import NavigationMenu
from settings_manager.models.currency import Currency
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from rooms.models.room_category import RoomCategory
from rooms.models.room import Room
from rooms.models.room_image import RoomImage
from rooms.models.room_facility import RoomFacility
from rooms.models.room_policy import RoomPolicy
from rooms.models.room_seasonal_price import RoomSeasonalPrice
from booking.models.booking import Booking
from booking.models.coupon import Coupon, CouponMinSpend
from booking.models.addon import Addon, AddonPrice
from dining.models.venue import DiningVenue
from dining.models.reservation import DiningReservation
from dining.models.venue_image import DiningVenueImage
from recreation.models.activity import RecreationActivity
from recreation.models.activity_image import RecreationActivityImage
from gallery.models.category import GalleryCategory
from gallery.models.item import GalleryItem
from conference.models.venue import EventVenue
from conference.models.inquiry import EventInquiry
from conference.models.event_type import EventType
from conference.models.venue_layout import VenueLayout
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
from contact.models.inquiry_category import InquiryCategory
from blogs.models.post import BlogPost
from nearby_places.models.attraction import Attraction
from testimonials.models.testimonial import Testimonial
from seo.models.seo_data import SEOData
from about.models import AboutPage, TeamMember, AboutFacility
from django.contrib.auth import get_user_model

User = get_user_model()

class TailwindFormMixin:
    """Mixin to inject standard premium Tailwind styling to form widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Checkbox Select Multiple
            if isinstance(widget, forms.CheckboxSelectMultiple):
                css_classes = ""
            # Checkbox
            elif isinstance(widget, forms.CheckboxInput):
                if field_name == 'DELETE':
                    css_classes = "rounded border-neutral-300 dark:border-neutral-700 text-luxuryGold-500 focus:ring-luxuryGold-500 bg-white dark:bg-neutral-800 transition duration-150 ease-in-out cursor-pointer"
                else:
                    css_classes = "sr-only peer"
            # Textarea
            elif isinstance(widget, forms.Textarea):
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-luxuryGold-500/20 focus:border-luxuryGold-500 outline-none transition-all duration-200 h-28"
            # Date/Time input
            elif isinstance(widget, (forms.DateInput, forms.DateTimeInput, forms.TimeInput)):
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-luxuryGold-500/20 focus:border-luxuryGold-500 outline-none transition-all duration-200 cursor-pointer"
            # Standard Select or SelectMultiple
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-luxuryGold-500/20 focus:border-luxuryGold-500 outline-none transition-all duration-200 cursor-pointer"
            # File Uploads
            elif isinstance(widget, forms.FileInput):
                if isinstance(widget, forms.ClearableFileInput):
                    widget.template_name = 'admin_dashboard/widgets/custom_clearable_file_input.html'
                css_classes = "block w-full text-sm text-neutral-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-luxuryGold-500/10 file:text-luxuryGold-700 dark:file:text-luxuryGold-400 hover:file:bg-luxuryGold-500/20 file:cursor-pointer bg-white dark:bg-neutral-800 rounded-lg border border-neutral-300 dark:border-neutral-700 px-3 py-2 transition"
            # Standard Text Inputs
            else:
                css_classes = "w-full px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-luxuryGold-500/20 focus:border-luxuryGold-500 outline-none transition-all duration-200"
            
            # Apply styling
            existing_class = widget.attrs.get('class', '')
            widget.attrs['class'] = f"{existing_class} {css_classes}".strip()
            
            # Placeholders
            if not widget.attrs.get('placeholder') and field.label:
                widget.attrs['placeholder'] = f"Enter {field.label.lower()}..."

# Forms Definitions

class HotelSettingsForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = HotelSettings
        fields = '__all__'

class NavigationMenuForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = NavigationMenu
        fields = '__all__'

class CurrencyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Currency
        fields = '__all__'

class HeroSlideForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = '__all__'

class AboutPreviewForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AboutPreview
        fields = '__all__'

class RoomCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomCategory
        exclude = ('total_rooms',)

from rooms.models.room_base_price import RoomBasePrice

class RoomForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Room
        exclude = ('created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from booking.models.addon import Addon
        if 'room_number' in self.fields:
            self.fields['room_number'].required = False
            self.fields['room_number'].widget.attrs.update({'placeholder': 'e.g. 101, 102, Villa A'})
        self.fields['highlights'].required = False
        self.fields['room_size'].required = False
        self.fields['bed_type'].required = False
        if 'included_addons' in self.fields:
            # pyrefly: ignore [missing-attribute]
            self.fields['included_addons'].queryset = Addon.objects.filter(applies_to__in=['room', 'both'])
            self.fields['included_addons'].required = False

class RoomBasePriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomBasePrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['base_price'].required = False
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].empty_label = "— Select Currency —"

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        currency = cleaned_data.get('currency')
        # pyrefly: ignore [missing-attribute]
        base_price = cleaned_data.get('base_price')

        # If one is provided, both must be provided
        if currency and base_price is None:
            self.add_error('base_price', 'Base price is required when currency is selected.')
        elif base_price is not None and not currency:
            self.add_error('currency', 'Currency is required when base price is entered.')
            
        return cleaned_data

    def has_changed(self):
        # If both fields are submitted empty/blank, treat the form as unchanged so Django ignores it
        prefix = self.prefix
        curr_key = f"{prefix}-currency" if prefix else "currency"
        price_key = f"{prefix}-base_price" if prefix else "base_price"
        
        curr_val = self.data.get(curr_key)
        price_val = self.data.get(price_key)
        
        if not curr_val and not price_val:
            return False
        return super().has_changed()

class RoomImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = '__all__'

class RoomFacilityForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomFacility
        fields = '__all__'

class RoomPolicyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomPolicy
        fields = '__all__'


class RoomPriceForm(TailwindFormMixin, forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Season start date",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Season end date",
    )

    class Meta:
        model = RoomSeasonalPrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].empty_label = "— All Currencies (wildcard) —"
        self.fields['currency'].required = False


class BookingForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

class CouponForm(TailwindFormMixin, forms.ModelForm):
    valid_from = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'air-datepicker-from'}),
        help_text="Start date & time for this promotional code"
    )
    valid_to = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'air-datepicker-to'}),
        help_text="Expiry date & time for this promotional code"
    )

    class Meta:
        model = Coupon
        fields = '__all__'


class CouponMinSpendForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = CouponMinSpend
        fields = ('currency', 'min_spend')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].empty_label = "— Select Currency —"


class DiningVenueForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningVenue
        fields = '__all__'

class DiningVenueImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningVenueImage
        fields = ('image', 'is_primary', 'alt_text')

DiningImageFormSet = forms.inlineformset_factory(
    DiningVenue,
    DiningVenueImage,
    form=DiningVenueImageForm,
    fields=('image',),
    extra=3,
    can_delete=True
)

class DiningReservationForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningReservation
        fields = '__all__'

class RecreationActivityForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RecreationActivity
        fields = '__all__'

class RecreationActivityImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RecreationActivityImage
        fields = ('image', 'is_primary', 'alt_text')

RecreationImageFormSet = forms.inlineformset_factory(
    RecreationActivity,
    RecreationActivityImage,
    form=RecreationActivityImageForm,
    fields=('image',),
    extra=3,
    can_delete=True
)

class GalleryCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryCategory
        fields = '__all__'

class GalleryItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = '__all__'

from conference.models.venue_base_price import VenueBasePrice
from conference.models.venue_image import EventVenueImage

class VenueBasePriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = VenueBasePrice
        fields = ('currency', 'base_price')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].empty_label = "— Select Currency —"

VenueBasePriceFormSet = forms.inlineformset_factory(
    EventVenue,
    VenueBasePrice,
    form=VenueBasePriceForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class EventVenueImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EventVenueImage
        fields = ('image', 'is_primary', 'alt_text')

EventVenueImageFormSet = forms.inlineformset_factory(
    EventVenue,
    EventVenueImage,
    form=EventVenueImageForm,
    fields=('image',),
    extra=3,
    can_delete=True
)

class VenueLayoutForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = VenueLayout
        fields = ('name', 'capacity', 'is_active')

    def has_changed(self):
        # Treat empty extra forms as unchanged even if is_active was toggled
        if not self.instance.pk:
            name = self.data.get(self.add_prefix('name'), '').strip()
            capacity = self.data.get(self.add_prefix('capacity'), '').strip()
            if not name and not capacity:
                return False
        return super().has_changed()

VenueLayoutFormSet = forms.inlineformset_factory(
    EventVenue,
    VenueLayout,
    form=VenueLayoutForm,
    fields=('name', 'capacity', 'is_active'),
    extra=2,
    can_delete=True
)

class EventVenueForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EventVenue
        fields = [
            'name', 'slug', 'description', 'capacity', 'layout_options',
            'image', 'is_featured', 'is_active', 'allow_custom_addons',
            'event_types', 'available_addons'
        ]
        labels = {
            'allow_custom_addons': "Show Add-ons Selection in UI (Allow Guests to Select Optional Add-ons)",
            'available_addons': "Package Inclusions (Complimentary Included Add-ons)",
        }
        widgets = {
            'event_types': forms.CheckboxSelectMultiple,
            'available_addons': forms.CheckboxSelectMultiple,
        }
        help_texts = {
            'layout_options': "Optional. Enter each layout style and capacity on a separate line (e.g. 'Banquet: 200 pax'), or leave blank.",
            'capacity': "Maximum total seating/floating capacity of the event venue.",
            'is_featured': "Feature this venue in marketing showcases on the website homepage.",
            'allow_custom_addons': "If ON, guests can choose optional paid add-on services on the venue page inquiry form. If OFF, optional add-ons selection is hidden.",
            'event_types': "Select the event occasions / categories hosted in this hall.",
            'available_addons': "Select add-on services bundled and included free as complimentary package inclusions with this banquet hall.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'layout_options' in self.fields:
            self.fields['layout_options'].required = False
        if 'event_types' in self.fields:
            self.fields['event_types'].queryset = EventType.objects.filter(is_active=True).order_by('display_order', 'name')
            self.fields['event_types'].required = False
        if 'available_addons' in self.fields:
            self.fields['available_addons'].queryset = Addon.objects.filter(
                applies_to__in=['events', 'both'], is_active=True
            ).order_by('order', 'name')
            self.fields['available_addons'].required = False

class EventTypeForm(TailwindFormMixin, forms.ModelForm):
    venues = forms.ModelMultipleChoiceField(
        queryset=EventVenue.objects.filter(is_active=True).order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select banquet halls that host this event category / occasion."
    )

    class Meta:
        model = EventType
        fields = ['name', 'slug', 'icon', 'venues', 'description', 'image', 'is_featured', 'is_active', 'display_order']
        widgets = {
            'venues': forms.CheckboxSelectMultiple,
        }
        help_texts = {
            'icon': "FontAwesome class name (e.g., 'fa-ring', 'fa-handshake', 'fa-champagne-glasses', 'fa-cake-candles').",
            'is_featured': "Showcase this event category prominently on the homepage branding/marketing section.",
            'venues': "Select banquet halls and venues that host this event category.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['venues'].initial = self.instance.venues.all()

    def save(self, commit=True):
        instance = super().save(commit=commit)
        def save_m2m_venues():
            if 'venues' in self.cleaned_data:
                instance.venues.set(self.cleaned_data['venues'])
        if commit:
            save_m2m_venues()
        else:
            old_save_m2m = getattr(self, 'save_m2m', None)
            def new_save_m2m():
                if old_save_m2m:
                    old_save_m2m()
                save_m2m_venues()
            self.save_m2m = new_save_m2m
        return instance

class EventInquiryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EventInquiry
        fields = '__all__'

class BranchForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        fields = '__all__'

class InquiryCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = InquiryCategory
        fields = ['name', 'slug', 'description', 'is_active', 'display_order']
        help_texts = {
            'name': "Name of the category (e.g. Room Booking, Fine Dining, Events).",
            'slug': "Slug identifier (auto-generated if left blank).",
            'description': "Brief note on what this inquiry category covers.",
            'display_order': "Sequence order in dropdown selection list.",
            'is_active': "Whether this category appears in the guest contact inquiry dropdown.",
        }

class ContactInquiryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = '__all__'

class BlogPostForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'

class AttractionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Attraction
        fields = '__all__'

class TestimonialForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'

class SEODataForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SEOData
        fields = '__all__'

class UserForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'is_active', 'is_staff', 'is_superuser', 'is_hotel_admin', 'is_guest', 'avatar', 'groups', 'user_permissions']


class PaymentProcessorForm(TailwindFormMixin, forms.ModelForm):
    payment_currencies = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Supported Currencies"
    )

    class Meta:
        model = PaymentProcessor
        fields = ['name', 'code', 'apply_tax', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pyrefly: ignore [missing-attribute]
        self.fields['payment_currencies'].queryset = Currency.objects.all().order_by('sequence', 'id')
        if self.instance and self.instance.pk:
            self.fields['payment_currencies'].initial = self.instance.payment_currencies.all()

    def save(self, commit=True):
        processor = super().save(commit=commit)
        if commit:
            self.save_currencies(processor)
        else:
            original_save_m2m = self.save_m2m
            def new_save_m2m():
                # pyrefly: ignore [bad-argument-type]
                original_save_m2m()
                self.save_currencies(processor)
            self.save_m2m = new_save_m2m
        return processor

    def save_currencies(self, processor):
        selected_currencies = self.cleaned_data.get('payment_currencies', [])
        PaymentProcessorCurrency.objects.filter(payment_processor=processor).exclude(
            currency__in=selected_currencies
        ).delete()
        for currency in selected_currencies:
            PaymentProcessorCurrency.objects.get_or_create(
                payment_processor=processor,
                currency=currency
            )


class BroadcastNewsletterForm(TailwindFormMixin, forms.Form):
    subject = forms.CharField(max_length=200, label="Email Subject Header", help_text="e.g. Secret Suite Rates & Exclusive Resort News")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 8}), label="Campaign Message Content", help_text="HTML line breaks will be preserved.")


class AddonForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Addon
        fields = ('name', 'description', 'icon', 'applies_to', 'price_type', 'is_active', 'order')


class AddonPriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AddonPrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['price'].required = False
        self.fields['price'].label = "Price"
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        # pyrefly: ignore [missing-attribute]
        self.fields['currency'].empty_label = "— Select Currency —"

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        currency = cleaned_data.get('currency')
        # pyrefly: ignore [missing-attribute]
        price = cleaned_data.get('price')

        if currency and price is None:
            self.add_error('price', 'Price is required when currency is selected.')
        elif price is not None and not currency:
            self.add_error('currency', 'Currency is required when price is entered.')

        return cleaned_data

    def has_changed(self):
        prefix = self.prefix
        curr_key = f"{prefix}-currency" if prefix else "currency"
        price_key = f"{prefix}-price" if prefix else "price"

        curr_val = self.data.get(curr_key)
        price_val = self.data.get(price_key)

        if not curr_val and not price_val:
            return False
        return super().has_changed()


AddonPriceFormSet = forms.inlineformset_factory(
    Addon,
    AddonPrice,
    form=AddonPriceForm,
    extra=2,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class AboutPageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = '__all__'


class TeamMemberForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'


class AboutFacilityForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AboutFacility
        fields = '__all__'


