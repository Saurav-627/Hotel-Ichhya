from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django import forms
from .models.venue import EventVenue
from .models.inquiry import EventInquiry

class EventInquiryForm(forms.ModelForm):
    class Meta:
        model = EventInquiry
        fields = ['name', 'email', 'phone', 'event_date', 'guest_count', 'catering_required', 'notes']
        widgets = {
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Full Name',
                'class': 'w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your.email@example.com',
                'class': 'w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+977 98XXXXXXXX',
                'class': 'w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'guest_count': forms.NumberInput(attrs={
                'placeholder': 'Expected Guests Count',
                'min': '1',
                'class': 'w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Describe your event requirements, layouts, setups, food/beverage specifications...',
                'rows': 4,
                'class': 'w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-1 focus:ring-luxuryGold-500 bg-transparent text-inherit'
            })
        }

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

class VenueListView(ListView):
    model = EventVenue
    template_name = 'conference/venue_list.html'
    context_object_name = 'venues'

    def get_queryset(self):
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        qs = EventVenue.objects.filter(is_active=True).prefetch_related('base_prices__currency', 'images')
        venues = list(qs)
        for v in venues:
            v.set_active_currency(selected_currency)
        return venues

class VenueDetailView(DetailView):
    model = EventVenue
    template_name = 'conference/venue_detail.html'
    context_object_name = 'venue'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return EventVenue.objects.filter(is_active=True).prefetch_related('base_prices__currency', 'images')

    def get_object(self, queryset=None):
        venue = super().get_object(queryset)
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        venue.set_active_currency(selected_currency)
        return venue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = EventInquiryForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EventInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            if inquiry.guest_count and inquiry.guest_count > self.object.capacity:
                form.add_error('guest_count', f"Guest count cannot exceed maximum venue capacity of {self.object.capacity} guests.")
                context = self.get_context_data(form=form)
                return render(request, self.template_name, context)

            inquiry.venue = self.object
            inquiry.save()

            try:
                from admin_dashboard.models.notification import create_admin_notification
                from contact.utils import send_inquiry_notification_email
                from django.urls import reverse
                create_admin_notification(
                    notification_type='inquiry_received',
                    title=f"New Event Inquiry from {inquiry.name}",
                    message=f"Venue: {self.object.name} on {inquiry.event_date} ({inquiry.guest_count} guests)",
                    link_url=reverse('admin_dashboard:conference_dashboard')
                )
                send_inquiry_notification_email('event', inquiry)
            except Exception:
                pass

            messages.success(request, "Thank you! Your event inquiry has been submitted. Our events coordinator will contact you shortly.")
            return redirect('conference:venue_detail', slug=self.object.slug)
        
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)
