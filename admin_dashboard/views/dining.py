from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory

from admin_dashboard.mixins import StaffRequiredMixin
from dining.models.venue import DiningVenue
from dining.models.reservation import DiningReservation
from dining.models.venue_image import DiningVenueImage
from admin_dashboard.forms import DiningVenueForm, DiningVenueImageForm

DiningImageFormSet = inlineformset_factory(
    DiningVenue, DiningVenueImage, form=DiningVenueImageForm,
    fields=('image',),
    extra=3, can_delete=True
)


class DiningDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        venues = DiningVenue.objects.all()
        # pyrefly: ignore [missing-attribute]
        reservations = DiningReservation.objects.all().select_related('venue')
        active_tab = request.GET.get('tab', 'venues')

        return render(request, 'admin_dashboard/dining/dashboard.html', {
            'venues': venues,
            'reservations': reservations,
            'active_tab': active_tab,
        })


class DiningVenueCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = DiningVenueForm()
        image_formset = DiningImageFormSet()
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': 'Add Dining Venue',
        })

    def post(self, request):
        form = DiningVenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save()
            image_formset = DiningImageFormSet(request.POST, request.FILES, instance=venue)
            if image_formset.is_valid():
                image_formset.save()
                messages.success(request, "Dining venue created successfully.")
                return redirect(reverse('admin_dashboard:dining_dashboard') + '?tab=venues')
            else:
                venue.delete()
        else:
            image_formset = DiningImageFormSet(request.POST, request.FILES)

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': 'Add Dining Venue',
        })


class DiningVenueUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        venue = get_object_or_404(DiningVenue, pk=pk)
        form = DiningVenueForm(instance=venue)
        image_formset = DiningImageFormSet(instance=venue)
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': f'Edit Dining Venue: {venue.name}',
        })

    def post(self, request, pk):
        venue = get_object_or_404(DiningVenue, pk=pk)
        form = DiningVenueForm(request.POST, request.FILES, instance=venue)
        image_formset = DiningImageFormSet(request.POST, request.FILES, instance=venue)

        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            messages.success(request, "Dining venue updated successfully.")
            return redirect(reverse('admin_dashboard:dining_dashboard') + '?tab=venues')

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': f'Edit Dining Venue: {venue.name}',
        })


class DiningVenueDeleteView(StaffRequiredMixin, DeleteView):
    model = DiningVenue
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Dining venue deleted successfully.")
        return reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=venues"


class DiningReservationUpdateStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(DiningReservation, pk=pk)
        status = request.POST.get('status')
        if status in ['confirmed', 'cancelled', 'pending']:
            reservation.status = status
            reservation.save()
            messages.success(request, f"Dining reservation updated to {status.capitalize()}.")
        else:
            messages.error(request, "Invalid status choice.")
        return redirect(reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=reservations")
