from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator

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
        today = timezone.localdate()
        active_tab = request.GET.get('tab', 'venues')
        page_number = request.GET.get('page', 1)

        # 1. Summary Metrics & KPIs
        total_venues = DiningVenue.objects.count()
        total_reservations = DiningReservation.objects.count()
        pending_reservations = DiningReservation.objects.filter(status='pending').count()
        confirmed_reservations = DiningReservation.objects.filter(status='confirmed').count()
        today_reservations = DiningReservation.objects.filter(date=today).count()

        kpi = {
            'total_venues': total_venues,
            'total_reservations': total_reservations,
            'pending_reservations': pending_reservations,
            'confirmed_reservations': confirmed_reservations,
            'today_reservations': today_reservations,
        }

        # 2. Venues Tab
        venues_qs = DiningVenue.objects.all().order_by('id')
        venues_paginator = Paginator(venues_qs, 10)
        venues_page = venues_paginator.get_page(page_number if active_tab == 'venues' else 1)

        # 3. Reservations Tab (with Search and Filters)
        reservations_qs = DiningReservation.objects.all().select_related('venue').order_by('-created_at', '-date', '-time')

        search_query = request.GET.get('q', '').strip()
        status_filter = request.GET.get('status', '').strip()
        venue_filter = request.GET.get('venue', '').strip()

        if search_query:
            reservations_qs = reservations_qs.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(special_requests__icontains=search_query)
            )

        if status_filter:
            reservations_qs = reservations_qs.filter(status=status_filter)

        if venue_filter:
            if venue_filter.isdigit():
                reservations_qs = reservations_qs.filter(venue_id=int(venue_filter))
            else:
                reservations_qs = reservations_qs.filter(venue__slug=venue_filter)

        reservations_paginator = Paginator(reservations_qs, 10)
        reservations_page = reservations_paginator.get_page(page_number if active_tab == 'reservations' else 1)

        all_venues = DiningVenue.objects.all().order_by('name')

        return render(request, 'admin_dashboard/dining/dashboard.html', {
            'venues': venues_page,
            'reservations': reservations_page,
            'active_tab': active_tab,
            'kpi': kpi,
            'all_venues': all_venues,
            'search_query': search_query,
            'status_filter': status_filter,
            'venue_filter': venue_filter,
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


class DiningReservationDeleteView(StaffRequiredMixin, DeleteView):
    model = DiningReservation
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Dining reservation cleared successfully.")
        return reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=reservations"


class ClearAllDiningReservationsView(StaffRequiredMixin, View):
    def post(self, request):
        count = DiningReservation.objects.count()
        DiningReservation.objects.all().delete()
        messages.success(request, f"Cleared all {count} dining reservation record(s).")
        return redirect(reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=reservations")


class DiningReservationDetailJsonView(StaffRequiredMixin, View):
    def get(self, request, pk):
        reservation = get_object_or_404(DiningReservation.objects.select_related('venue'), pk=pk)
        return JsonResponse({
            'id': reservation.id,
            'name': reservation.name,
            'email': reservation.email,
            'phone': reservation.phone,
            'venue_name': reservation.venue.name,
            'venue_id': reservation.venue.id,
            'date': reservation.date.strftime('%Y-%m-%d') if reservation.date else '—',
            'time': reservation.time.strftime('%I:%M %p') if reservation.time else '—',
            'guests': reservation.guests,
            'special_requests': reservation.special_requests or '',
            'status': reservation.status,
            'status_display': reservation.get_status_display(),
            'created_at': reservation.created_at.strftime('%Y-%m-%d %H:%M') if reservation.created_at else '—',
        })
