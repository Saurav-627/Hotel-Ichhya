from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from admin_dashboard.mixins import StaffRequiredMixin
from conference.models.venue import EventVenue
from conference.models.inquiry import EventInquiry
from conference.models.event_type import EventType
from conference.models.venue_layout import VenueLayout
from booking.models.addon import Addon
from settings_manager.models.currency import Currency
from admin_dashboard.forms import (
    EventVenueForm,
    VenueBasePriceFormSet,
    EventVenueImageFormSet,
    VenueLayoutFormSet,
    EventTypeForm,
)


class ConferenceDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        today = timezone.localdate()
        active_tab = request.GET.get('tab', 'venues')
        page_number = request.GET.get('page', 1)

        # 1. Summary Metrics & KPIs
        total_venues = EventVenue.objects.count()
        total_inquiries = EventInquiry.objects.count()
        pending_inquiries = EventInquiry.objects.filter(status='pending').count()
        confirmed_inquiries = EventInquiry.objects.filter(status__in=['confirmed', 'processed']).count()
        upcoming_events_count = EventInquiry.objects.filter(
            event_date__gte=today,
            event_date__lte=today + timedelta(days=30),
            status__in=['pending', 'contacted', 'proposal_sent', 'confirmed']
        ).count()
        active_types_count = EventType.objects.filter(is_active=True).count()
        active_services_count = Addon.objects.filter(applies_to__in=['events', 'both'], is_active=True).count()

        # 2. Upcoming events preview (next 5 upcoming)
        upcoming_inquiries = EventInquiry.objects.filter(
            event_date__gte=today,
            status__in=['pending', 'contacted', 'proposal_sent', 'confirmed']
        ).select_related('venue', 'event_type').order_by('event_date', 'start_time')[:5]

        # 3. Venues Tab
        venues_qs = EventVenue.objects.all().prefetch_related(
            'base_prices__currency', 'layouts', 'images', 'event_types', 'available_addons'
        ).order_by('id')
        venues_paginator = Paginator(venues_qs, 10)
        venues_page = venues_paginator.get_page(page_number if active_tab == 'venues' else 1)

        # 4. Inquiries Tab (with Search and Filters)
        inquiries_qs = EventInquiry.objects.all().select_related('venue', 'event_type', 'preferred_layout').prefetch_related('addons').order_by('-created_at')
        
        search_query = request.GET.get('q', '').strip()
        status_filter = request.GET.get('status', '').strip()
        venue_filter = request.GET.get('venue', '').strip()
        event_type_filter = request.GET.get('event_type', '').strip()

        if search_query:
            inquiries_qs = inquiries_qs.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        if status_filter:
            inquiries_qs = inquiries_qs.filter(status=status_filter)
        if venue_filter:
            inquiries_qs = inquiries_qs.filter(venue_id=venue_filter)
        if event_type_filter:
            inquiries_qs = inquiries_qs.filter(event_type_id=event_type_filter)

        inquiries_paginator = Paginator(inquiries_qs, 12)
        inquiries_page = inquiries_paginator.get_page(page_number if active_tab == 'inquiries' else 1)

        # 5. Event Types Tab
        event_types_list = EventType.objects.all().prefetch_related('venues').order_by('display_order', 'name')

        # 6. Event Services / Add-ons Tab (Unified Addons)
        services_list = Addon.objects.filter(
            applies_to__in=['events', 'both']
        ).prefetch_related('prices__currency').order_by('order', 'name')

        return render(request, 'admin_dashboard/conference/dashboard.html', {
            'venues': venues_page,
            'inquiries': inquiries_page,
            'event_types': event_types_list,
            'services': services_list,
            'currencies': Currency.objects.filter(is_published=True).order_by('sequence', 'id'),
            'all_venues_filter': EventVenue.objects.filter(is_active=True).order_by('name'),
            'all_event_types_filter': EventType.objects.filter(is_active=True).order_by('name'),
            'active_tab': active_tab,
            'search_query': search_query,
            'status_filter': status_filter,
            'venue_filter': venue_filter,
            'event_type_filter': event_type_filter,
            'kpi': {
                'total_venues': total_venues,
                'total_inquiries': total_inquiries,
                'pending_inquiries': pending_inquiries,
                'confirmed_inquiries': confirmed_inquiries,
                'upcoming_events_count': upcoming_events_count,
                'active_types_count': active_types_count,
                'active_services_count': active_services_count,
            },
            'upcoming_inquiries': upcoming_inquiries,
        })


class EventInquiryDetailJsonView(StaffRequiredMixin, View):
    """Returns full inquiry details as JSON for modal popups."""
    def get(self, request, pk):
        inquiry = get_object_or_404(
            EventInquiry.objects.select_related('venue', 'event_type', 'preferred_layout').prefetch_related('addons'),
            pk=pk
        )
        return JsonResponse({
            'id': inquiry.id,
            'name': inquiry.name,
            'email': inquiry.email,
            'phone': inquiry.phone,
            'venue_name': inquiry.venue.name if inquiry.venue else '—',
            'event_type': inquiry.event_type.name if inquiry.event_type else '—',
            'event_date': inquiry.event_date.strftime('%Y-%m-%d') if inquiry.event_date else '—',
            'start_time': inquiry.start_time.strftime('%H:%M') if inquiry.start_time else '—',
            'end_time': inquiry.end_time.strftime('%H:%M') if inquiry.end_time else '—',
            'guest_count': inquiry.guest_count,
            'preferred_layout': inquiry.preferred_layout.name if inquiry.preferred_layout else '—',
            'catering_required': inquiry.catering_required,
            'services': [a.name for a in inquiry.addons.all()],
            'notes': inquiry.notes or '',
            'status': inquiry.status,
            'status_display': inquiry.get_status_display(),
            'has_conflict': inquiry.has_conflict,
            'created_at': inquiry.created_at.strftime('%Y-%m-%d %H:%M') if inquiry.created_at else '—',
        })


class EventVenueCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = EventVenueForm()
        price_formset = VenueBasePriceFormSet()
        image_formset = EventVenueImageFormSet()
        layout_formset = VenueLayoutFormSet()
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'layout_formset': layout_formset,
            'title': 'Add Event Venue Hall',
        })

    def post(self, request):
        form = EventVenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            price_formset = VenueBasePriceFormSet(request.POST, instance=venue)
            image_formset = EventVenueImageFormSet(request.POST, request.FILES, instance=venue)
            layout_formset = VenueLayoutFormSet(request.POST, instance=venue)
            if price_formset.is_valid() and image_formset.is_valid() and layout_formset.is_valid():
                venue.save()
                form.save_m2m()
                price_formset.instance = venue
                price_formset.save()
                image_formset.instance = venue
                image_formset.save()
                layout_formset.instance = venue
                layout_formset.save()
                messages.success(request, "Event venue hall created successfully.")
                return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=venues')
            else:
                messages.error(request, "Please correct the highlighted errors in the form sections below.")
        else:
            price_formset = VenueBasePriceFormSet(request.POST)
            image_formset = EventVenueImageFormSet(request.POST, request.FILES)
            layout_formset = VenueLayoutFormSet(request.POST)
            messages.error(request, "Please correct the highlighted errors in the form below.")

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'layout_formset': layout_formset,
            'title': 'Add Event Venue Hall',
        })


class EventVenueUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        venue = get_object_or_404(EventVenue, pk=pk)
        form = EventVenueForm(instance=venue)
        price_formset = VenueBasePriceFormSet(instance=venue)
        image_formset = EventVenueImageFormSet(instance=venue)
        layout_formset = VenueLayoutFormSet(instance=venue)
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'layout_formset': layout_formset,
            'title': f'Edit Event Venue: {venue.name}',
        })

    def post(self, request, pk):
        venue = get_object_or_404(EventVenue, pk=pk)
        form = EventVenueForm(request.POST, request.FILES, instance=venue)
        price_formset = VenueBasePriceFormSet(request.POST, instance=venue)
        image_formset = EventVenueImageFormSet(request.POST, request.FILES, instance=venue)
        layout_formset = VenueLayoutFormSet(request.POST, instance=venue)

        if form.is_valid() and price_formset.is_valid() and image_formset.is_valid() and layout_formset.is_valid():
            form.save()
            price_formset.save()
            image_formset.save()
            layout_formset.save()
            messages.success(request, "Event venue hall updated successfully.")
            return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=venues')
        else:
            messages.error(request, "Please correct the highlighted errors in the form sections below.")

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'price_formset': price_formset,
            'image_formset': image_formset,
            'layout_formset': layout_formset,
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
        valid_statuses = ['pending', 'contacted', 'proposal_sent', 'confirmed', 'completed', 'cancelled', 'processed']
        if status in valid_statuses:
            inquiry.status = status
            inquiry.save()
            messages.success(request, f"Inquiry status updated to {inquiry.get_status_display()}.")
        else:
            messages.error(request, "Invalid status choice.")
        return redirect(reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=inquiries")


class EventInquiryDeleteView(StaffRequiredMixin, DeleteView):
    model = EventInquiry
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Event inquiry cleared successfully.")
        return reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=inquiries"


class ClearAllEventInquiriesView(StaffRequiredMixin, View):
    def post(self, request):
        count = EventInquiry.objects.count()
        EventInquiry.objects.all().delete()
        messages.success(request, f"Cleared all {count} event inquiry record(s).")
        return redirect(reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=inquiries")


# ==========================================
# EventType CRUD Views
# ==========================================

class EventTypeCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = EventTypeForm()
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'title': 'Add Event Category / Type',
        })

    def post(self, request):
        form = EventTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Event Category created successfully.")
            return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=event_types')
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'title': 'Add Event Category / Type',
        })


class EventTypeUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        event_type = get_object_or_404(EventType, pk=pk)
        form = EventTypeForm(instance=event_type)
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'title': f'Edit Event Category: {event_type.name}',
        })

    def post(self, request, pk):
        event_type = get_object_or_404(EventType, pk=pk)
        form = EventTypeForm(request.POST, request.FILES, instance=event_type)
        if form.is_valid():
            form.save()
            messages.success(request, "Event Category updated successfully.")
            return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=event_types')
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'title': f'Edit Event Category: {event_type.name}',
        })


class EventTypeDeleteView(StaffRequiredMixin, DeleteView):
    model = EventType
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Event Category deleted successfully.")
        return reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=event_types"
