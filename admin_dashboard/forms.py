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
from dining.models.venue import DiningVenue
from dining.models.reservation import DiningReservation
from dining.models.venue_image import DiningVenueImage
from recreation.models.activity import RecreationActivity
from recreation.models.activity_image import RecreationActivityImage
from gallery.models.category import GalleryCategory
from gallery.models.item import GalleryItem
from conference.models.venue import EventVenue
from conference.models.inquiry import EventInquiry
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
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
        fields = '__all__'

from rooms.models.room_base_price import RoomBasePrice

class RoomForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at', 'updated_at']

class RoomBasePriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomBasePrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['base_price'].required = False
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        self.fields['currency'].empty_label = "— Select Currency —"

    def clean(self):
        cleaned_data = super().clean()
        currency = cleaned_data.get('currency')
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
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
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
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
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
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
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

class EventVenueForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EventVenue
        fields = ['name', 'slug', 'description', 'capacity', 'layout_options', 'image', 'is_active']
        help_texts = {
            'layout_options': "Enter each layout style and capacity on a separate line. Format: 'Layout Name: Capacity' (e.g. 'Banquet: 200 pax' or 'Theatre: 300 pax' or 'Classroom: 150').",
            'capacity': "Maximum total seating/floating capacity of the event venue."
        }

class EventInquiryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EventInquiry
        fields = '__all__'

class BranchForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        fields = '__all__'

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


from booking.models.addon import Addon, AddonPrice


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
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True).order_by('sequence', 'id')
        self.fields['currency'].empty_label = "— Select Currency —"

    def clean(self):
        cleaned_data = super().clean()
        currency = cleaned_data.get('currency')
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


