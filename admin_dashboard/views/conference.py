from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory

from admin_dashboard.mixins import StaffRequiredMixin
from conference.models.venue import EventVenue
from conference.models.inquiry import EventInquiry
from conference.models.venue_image import EventVenueImage
from admin_dashboard.forms import EventVenueForm, VenueBasePriceFormSet, EventVenueImageForm

EventVenueImageFormSet = inlineformset_factory(
    EventVenue, EventVenueImage, form=EventVenueImageForm,
    fields=('image',),
    extra=3, can_delete=True
)


class ConferenceDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        venues = EventVenue.objects.all().prefetch_related('base_prices__currency')
        inquiries = EventInquiry.objects.all().select_related('venue')
        active_tab = request.GET.get('tab', 'venues')

        return render(request, 'admin_dashboard/conference/dashboard.html', {
            'venues': venues,
            'inquiries': inquiries,
            'active_tab': active_tab,
        })


class EventVenueCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = EventVenueForm()
        price_formset = VenueBasePriceFormSet()
        image_formset = EventVenueImageFormSet()
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'title': 'Add Event Venue Hall',
        })

    def post(self, request):
        form = EventVenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save()
            price_formset = VenueBasePriceFormSet(request.POST, instance=venue)
            image_formset = EventVenueImageFormSet(request.POST, request.FILES, instance=venue)
            if price_formset.is_valid() and image_formset.is_valid():
                price_formset.save()
                image_formset.save()
                messages.success(request, "Event venue hall created successfully.")
                return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=venues')
            else:
                venue.delete()
        else:
            price_formset = VenueBasePriceFormSet(request.POST)
            image_formset = EventVenueImageFormSet(request.POST, request.FILES)

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'title': 'Add Event Venue Hall',
        })


class EventVenueUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        venue = get_object_or_404(EventVenue, pk=pk)
        form = EventVenueForm(instance=venue)
        price_formset = VenueBasePriceFormSet(instance=venue)
        image_formset = EventVenueImageFormSet(instance=venue)
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'title': f'Edit Event Venue: {venue.name}',
        })

    def post(self, request, pk):
        venue = get_object_or_404(EventVenue, pk=pk)
        form = EventVenueForm(request.POST, request.FILES, instance=venue)
        price_formset = VenueBasePriceFormSet(request.POST, instance=venue)
        image_formset = EventVenueImageFormSet(request.POST, request.FILES, instance=venue)

        if form.is_valid() and price_formset.is_valid() and image_formset.is_valid():
            form.save()
            price_formset.save()
            image_formset.save()
            messages.success(request, "Event venue hall updated successfully.")
            return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=venues')

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'title': f'Edit Event Venue: {venue.name}',
        })


class EventVenueDeleteView(StaffRequiredMixin, DeleteView):
    model = EventVenue
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Event venue hall deleted successfully.")
        return reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=venues"


class EventInquiryUpdateStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        inquiry = get_object_or_404(EventInquiry, pk=pk)
        status = request.POST.get('status')
        if status in ['pending', 'processed', 'cancelled']:
            inquiry.status = status
            inquiry.save()
            messages.success(request, f"Event inquiry updated to {status.capitalize()}.")
        else:
            messages.error(request, "Invalid status choice.")
        return redirect(reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=inquiries")
