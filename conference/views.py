from django.shortcuts import render, get_object_or_404, redirect
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

class VenueListView(ListView):
    model = EventVenue
    template_name = 'conference/venue_list.html'
    context_object_name = 'venues'

    def get_queryset(self):
        return EventVenue.objects.filter(is_active=True)

class VenueDetailView(DetailView):
    model = EventVenue
    template_name = 'conference/venue_detail.html'
    context_object_name = 'venue'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return EventVenue.objects.filter(is_active=True)

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
            inquiry.venue = self.object
            inquiry.save()
            messages.success(request, "Thank you! Your event inquiry has been submitted. Our events coordinator will contact you shortly.")
            return redirect('conference:venue_detail', slug=self.object.slug)
        
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)
