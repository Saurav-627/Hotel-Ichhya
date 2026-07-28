from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from conference.models.venue import EventVenue
from conference.models.inquiry import EventInquiry
from admin_dashboard.forms import EventVenueForm, VenueBasePriceFormSet

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

class EventVenueCreateView(StaffRequiredMixin, CreateView):
    model = EventVenue
    form_class = EventVenueForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['price_formset'] = VenueBasePriceFormSet(self.request.POST)
        else:
            context['price_formset'] = VenueBasePriceFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        price_formset = context['price_formset']
        if price_formset.is_valid():
            self.object = form.save()
            price_formset.instance = self.object
            price_formset.save()
            messages.success(self.request, "Event venue hall created successfully with multi-currency pricing.")
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=venues"

class EventVenueUpdateView(StaffRequiredMixin, UpdateView):
    model = EventVenue
    form_class = EventVenueForm
    template_name = 'admin_dashboard/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['price_formset'] = VenueBasePriceFormSet(self.request.POST, instance=self.object)
        else:
            context['price_formset'] = VenueBasePriceFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        price_formset = context['price_formset']
        if price_formset.is_valid():
            self.object = form.save()
            price_formset.instance = self.object
            price_formset.save()
            messages.success(self.request, "Event venue hall updated successfully with multi-currency pricing.")
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('admin_dashboard:conference_dashboard') + "?tab=venues"

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
