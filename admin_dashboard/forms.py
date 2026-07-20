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
from rooms.models.room_price import RoomPrice
from booking.models.booking import Booking
from booking.models.coupon import Coupon
from dining.models.venue import DiningVenue
from dining.models.reservation import DiningReservation
from recreation.models.activity import RecreationActivity
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
                css_classes = "block w-full text-sm text-neutral-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-luxuryGold-50/50 file:text-luxuryGold-700 hover:file:bg-luxuryGold-100/50 file:cursor-pointer bg-white dark:bg-neutral-800 rounded-lg border border-neutral-300 dark:border-neutral-700 px-4 py-2"
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

from rooms.models.room_currency_price import RoomCurrencyPrice

class RoomForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at', 'updated_at']

class RoomCurrencyPriceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RoomCurrencyPrice
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].required = False
        self.fields['base_price'].required = False
        self.fields['currency'].queryset = Currency.objects.filter(is_published=True)

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
    class Meta:
        model = RoomPrice
        fields = '__all__'

class BookingForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

class CouponForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'

class DiningVenueForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningVenue
        fields = '__all__'

class DiningReservationForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DiningReservation
        fields = '__all__'

class RecreationActivityForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RecreationActivity
        fields = '__all__'

class GalleryCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryCategory
        fields = '__all__'

class GalleryItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = '__all__'

class EventVenueForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EventVenue
        fields = '__all__'

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
        queryset=Currency.objects.filter(is_published=True),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Supported Currencies"
    )

    class Meta:
        model = PaymentProcessor
        fields = ['name', 'code', 'apply_tax', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
