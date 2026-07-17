from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from dashboard.mixins import StaffRequiredMixin
from conference.models.venue import EventVenue
from conference.models.inquiry import EventInquiry
from dashboard.forms import EventVenueForm

class ConferenceDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        venues = EventVenue.objects.all()
        inquiries = EventInquiry.objects.all().select_related('venue')
        active_tab = request.GET.get('tab', 'venues')
        
        return render(request, 'dashboard/conference/dashboard.html', {
            'venues': venues,
            'inquiries': inquiries,
            'active_tab': active_tab,
        })

class EventVenueCreateView(StaffRequiredMixin, CreateView):
    model = EventVenue
    form_class = EventVenueForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Event venue hall created successfully.")
        return reverse_lazy('dashboard:conference_dashboard') + "?tab=venues"

class EventVenueUpdateView(StaffRequiredMixin, UpdateView):
    model = EventVenue
    form_class = EventVenueForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Event venue hall updated successfully.")
        return reverse_lazy('dashboard:conference_dashboard') + "?tab=venues"

class EventVenueDeleteView(StaffRequiredMixin, DeleteView):
    model = EventVenue
    template_name = 'dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Event venue hall deleted successfully.")
        return reverse_lazy('dashboard:conference_dashboard') + "?tab=venues"

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
        return redirect(reverse_lazy('dashboard:conference_dashboard') + "?tab=inquiries")
