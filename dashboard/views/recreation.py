from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from dashboard.mixins import StaffRequiredMixin
from recreation.models.activity import RecreationActivity
from dashboard.forms import RecreationActivityForm

class RecreationDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        activities = RecreationActivity.objects.all()
        return render(request, 'dashboard/recreation/dashboard.html', {
            'activities': activities
        })

class RecreationCreateView(StaffRequiredMixin, CreateView):
    model = RecreationActivity
    form_class = RecreationActivityForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Recreational activity created successfully.")
        return reverse_lazy('dashboard:recreation_dashboard')

class RecreationUpdateView(StaffRequiredMixin, UpdateView):
    model = RecreationActivity
    form_class = RecreationActivityForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Recreational activity updated successfully.")
        return reverse_lazy('dashboard:recreation_dashboard')

class RecreationDeleteView(StaffRequiredMixin, DeleteView):
    model = RecreationActivity
    template_name = 'dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Recreational activity deleted successfully.")
        return reverse_lazy('dashboard:recreation_dashboard')
