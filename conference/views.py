from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django import forms
from .models.venue import EventVenue
from .models.inquiry import EventInquiry
from .models.event_type import EventType
from .models.venue_layout import VenueLayout
from booking.models.addon import Addon


class EventInquiryForm(forms.ModelForm):
    addons = forms.ModelMultipleChoiceField(
        queryset=Addon.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rounded border-neutral-300 dark:border-neutral-700 text-luxuryGold-500 focus:ring-luxuryGold-500'
        }),
        required=False,
        label="Optional Event Add-on Services"
    )

    class Meta:
        model = EventInquiry
        fields = [
            'name', 'email', 'phone', 'event_type', 'event_date',
            'start_time', 'end_time', 'guest_count', 'preferred_layout',
            'addons', 'catering_required', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Full Name',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your.email@example.com',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+977 98XXXXXXXX',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'event_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'guest_count': forms.NumberInput(attrs={
                'placeholder': 'Expected Guests Count',
                'min': '1',
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'preferred_layout': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Describe your event requirements, special setups, stage needs, food/beverage preferences...',
                'rows': 4,
                'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            })
        }

    def __init__(self, *args, venue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.venue = venue
        if venue:
            # pyrefly: ignore [missing-attribute]
            self.fields['event_type'].queryset = venue.event_types.filter(is_active=True).order_by('display_order', 'name')
        else:
            # pyrefly: ignore [missing-attribute]
            self.fields['event_type'].queryset = EventType.objects.filter(is_active=True).order_by('display_order', 'name')
        # pyrefly: ignore [missing-attribute]
        self.fields['event_type'].empty_label = "— Select Event Category (Optional) —"
        self.fields['event_type'].required = False
        
        if venue:
            if venue.allow_custom_addons:
                included_ids = list(venue.available_addons.values_list('id', flat=True))
                # pyrefly: ignore [missing-attribute]
                self.fields['addons'].queryset = Addon.objects.filter(
                    applies_to__in=['events', 'both'], is_active=True
                ).exclude(id__in=included_ids).order_by('order', 'name')
            else:
                # pyrefly: ignore [missing-attribute]
                self.fields['addons'].queryset = Addon.objects.none()
        else:
            # pyrefly: ignore [missing-attribute]
            self.fields['addons'].queryset = Addon.objects.filter(
                applies_to__in=['events', 'both'], is_active=True
            ).order_by('order', 'name')
        
        if venue:
            # pyrefly: ignore [missing-attribute]
            self.fields['preferred_layout'].queryset = venue.layouts.filter(is_active=True)
        else:
            # pyrefly: ignore [missing-attribute]
            self.fields['preferred_layout'].queryset = VenueLayout.objects.filter(is_active=True)
        # pyrefly: ignore [missing-attribute]
        self.fields['preferred_layout'].empty_label = "— Select Layout Setup (Optional) —"
        self.fields['preferred_layout'].required = False

        self.fields['catering_required'].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError("Phone number must contain at least 10 digits.")
        if len(digits) > 10:
            raise forms.ValidationError("Phone number cannot exceed 10 digits.")
        return phone

    def clean_event_date(self):
        import datetime
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < datetime.date.today():
            raise forms.ValidationError("Event date cannot be in the past.")
        return event_date

    def clean_guest_count(self):
        guest_count = self.cleaned_data.get('guest_count')
        if guest_count is not None and guest_count < 1:
            raise forms.ValidationError("Guest count must be at least 1.")
        return guest_count

    def clean(self):
        cleaned_data = super().clean()
        # pyrefly: ignore [missing-attribute]
        start_time = cleaned_data.get('start_time')
        # pyrefly: ignore [missing-attribute]
        end_time = cleaned_data.get('end_time')
        # pyrefly: ignore [missing-attribute]
        preferred_layout = cleaned_data.get('preferred_layout')
        # pyrefly: ignore [missing-attribute]
        guest_count = cleaned_data.get('guest_count')

        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', "End time must be after start time.")

        if preferred_layout and guest_count:
            if guest_count > preferred_layout.capacity:
                self.add_error('guest_count', f"Guest count ({guest_count}) exceeds the maximum capacity for '{preferred_layout.name}' layout ({preferred_layout.capacity} guests).")

        return cleaned_data


class VenueListView(ListView):
    model = EventVenue
    template_name = 'conference/venue_list.html'
    context_object_name = 'venues'

    # pyrefly: ignore [bad-override]
    def get_queryset(self):
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        qs = EventVenue.objects.filter(is_active=True).prefetch_related('base_prices__currency', 'images', 'layouts')
        venues = list(qs)
        for v in venues:
            v.set_active_currency(selected_currency)
        return venues

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = EventType.objects.filter(is_active=True)
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        addons = list(Addon.objects.filter(applies_to__in=['events', 'both'], is_active=True).prefetch_related('prices__currency'))
        for a in addons:
            a.set_active_currency(selected_currency)
        context['event_services'] = addons
        context['selected_occasion'] = self.request.GET.get('occasion', '')
        return context


class VenueDetailView(DetailView):
    model = EventVenue
    template_name = 'conference/venue_detail.html'
    context_object_name = 'venue'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return EventVenue.objects.filter(is_active=True).prefetch_related('base_prices__currency', 'images', 'layouts', 'available_addons')

    def get_object(self, queryset=None):
        venue = super().get_object(queryset)
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        venue.set_active_currency(selected_currency)
        return venue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            initial = {}
            event_type_slug = self.request.GET.get('event_type') or self.request.GET.get('occasion')
            if event_type_slug:
                from django.db.models import Q
                allowed_types = self.object.event_types.filter(is_active=True) if (self.object and self.object.event_types.exists()) else EventType.objects.filter(is_active=True)
                et = allowed_types.filter(Q(slug=event_type_slug) | Q(name__iexact=event_type_slug)).first()
                if et:
                    initial['event_type'] = et
            context['form'] = EventInquiryForm(venue=self.object, initial=initial)
        context['venue_layouts'] = self.object.layouts.filter(is_active=True)
        selected_currency = self.request.COOKIES.get('currency', 'USD')

        # 1. Complimentary Inclusions bundled with this venue package
        inclusions = []
        if self.object:
            inclusions = list(self.object.available_addons.filter(is_active=True).prefetch_related('prices__currency'))
            for inc in inclusions:
                inc.set_active_currency(selected_currency)
        context['venue_inclusions'] = inclusions

        # 2. Optional extra add-on services selectable in proposal inquiry form (if allowed)
        if self.object and self.object.allow_custom_addons:
            included_ids = [inc.id for inc in inclusions]
            addons = list(
                Addon.objects.filter(applies_to__in=['events', 'both'], is_active=True)
                .exclude(id__in=included_ids)
                .prefetch_related('prices__currency')
                .order_by('order', 'name')
            )
            for a in addons:
                a.set_active_currency(selected_currency)
            context['event_services'] = addons
        else:
            context['event_services'] = []

        if self.object and self.object.event_types.exists():
            context['event_types'] = self.object.event_types.filter(is_active=True).order_by('display_order', 'name')
        else:
            context['event_types'] = EventType.objects.filter(is_active=True).order_by('display_order', 'name')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EventInquiryForm(request.POST, venue=self.object)
        if form.is_valid():
            inquiry = form.save(commit=False)
            if inquiry.guest_count and inquiry.guest_count > self.object.capacity:
                form.add_error('guest_count', f"Guest count cannot exceed maximum venue capacity of {self.object.capacity} guests.")
                context = self.get_context_data(form=form)
                # pyrefly: ignore [bad-argument-type]
                return render(request, self.template_name, context)

            inquiry.venue = self.object
            inquiry.save()
            form.save_m2m()

            try:
                from admin_dashboard.models.notification import create_admin_notification
                from contact.utils import send_inquiry_notification_email
                from django.urls import reverse
                event_name = inquiry.event_type.name if inquiry.event_type else "Event"
                create_admin_notification(
                    notification_type='event_inquiry_received',
                    title=f"New {event_name} Inquiry from {inquiry.name}",
                    message=f"Venue: {self.object.name} on {inquiry.event_date} ({inquiry.guest_count} guests)",
                    link_url=reverse('admin_dashboard:conference_dashboard') + "?tab=inquiries"
                )
                send_inquiry_notification_email('event', inquiry)
            except Exception:
                pass

            messages.success(request, "Thank you! Your event inquiry has been submitted. Our events coordinator will contact you shortly.")
            return redirect('conference:venue_detail', slug=self.object.slug)
        
        context = self.get_context_data(form=form)
        # pyrefly: ignore [bad-argument-type]
        return render(request, self.template_name, context)

