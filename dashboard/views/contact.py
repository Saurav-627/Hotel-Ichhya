from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages

from dashboard.mixins import StaffRequiredMixin
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
from dashboard.forms import BranchForm

class ContactDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        branches = Branch.objects.all()
        inquiries = ContactInquiry.objects.all()
        active_tab = request.GET.get('tab', 'branches')
        
        return render(request, 'dashboard/contact/dashboard.html', {
            'branches': branches,
            'inquiries': inquiries,
            'active_tab': active_tab,
        })

class BranchCreateView(StaffRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch created successfully.")
        return reverse_lazy('dashboard:contact_dashboard') + "?tab=branches"

class BranchUpdateView(StaffRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch updated successfully.")
        return reverse_lazy('dashboard:contact_dashboard') + "?tab=branches"

class BranchDeleteView(StaffRequiredMixin, DeleteView):
    model = Branch
    template_name = 'dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch deleted successfully.")
        return reverse_lazy('dashboard:contact_dashboard') + "?tab=branches"

class ContactInquiryDetailView(StaffRequiredMixin, DetailView):
    model = ContactInquiry
    template_name = 'dashboard/contact/inquiry_detail.html'
    context_object_name = 'inquiry'
