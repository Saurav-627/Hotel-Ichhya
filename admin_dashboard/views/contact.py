from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from admin_dashboard.forms import (
    BranchForm,
    BroadcastNewsletterForm,
)
from admin_dashboard.mixins import StaffRequiredMixin
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
from contact.models.newsletter import NewsletterSubscriber
from core.services.email_service import send_newsletter_broadcast_email


class ContactDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        branches = Branch.objects.all()
        inquiries_qs = ContactInquiry.objects.all().order_by('-created_at')
        subscribers_qs = NewsletterSubscriber.objects.all().order_by('-created_at')
        
        active_tab = request.GET.get('tab', 'branches')
        page_number = request.GET.get('page', 1)

        inquiries_paginator = Paginator(inquiries_qs, 15)
        inquiries_page = inquiries_paginator.get_page(page_number if active_tab == 'inquiries' else 1)

        subscribers_paginator = Paginator(subscribers_qs, 15)
        subscribers_page = subscribers_paginator.get_page(page_number if active_tab == 'subscribers' else 1)

        return render(request, 'admin_dashboard/contact/dashboard.html', {
            'branches': branches,
            'inquiries': inquiries_page,
            'inquiries_total': inquiries_qs.count(),
            'subscribers': subscribers_page,
            'subscribers_total': subscribers_qs.count(),
            'active_tab': active_tab,
        })


class BroadcastNewsletterView(StaffRequiredMixin, View):
    def get(self, request):
        form = BroadcastNewsletterForm()
        active_subscribers_count = NewsletterSubscriber.objects.filter(is_active=True, is_verified=True).count()
        return render(request, 'admin_dashboard/contact/broadcast.html', {
            'form': form,
            'active_subscribers_count': active_subscribers_count,
        })

    def post(self, request):
        form = BroadcastNewsletterForm(request.POST)
        active_subscribers = list(NewsletterSubscriber.objects.filter(is_active=True, is_verified=True).values_list('email', flat=True))
        
        if not active_subscribers:
            messages.error(request, "No verified active newsletter subscribers found to send broadcast.")
            return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers")

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            success, sent_count, msg = send_newsletter_broadcast_email(
                subject=subject,
                message=message,
                recipient_list=active_subscribers,
                request=request
            )
            
            if success:
                messages.success(request, f"🚀 Campaign broadcasted successfully to {sent_count} verified subscriber(s)!")
            else:
                messages.error(request, f"Failed to send campaign: {msg}")
            
            return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers")

        return render(request, 'admin_dashboard/contact/broadcast.html', {
            'form': form,
            'active_subscribers_count': len(active_subscribers),
        })


class NewsletterSubscriberToggleStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
        
        if not subscriber.is_verified or not subscriber.is_active:
            subscriber.is_verified = True
            subscriber.is_active = True
            subscriber.verification_token = None
            subscriber.save(update_fields=['is_verified', 'is_active', 'verification_token'])
            messages.success(request, f"Subscriber {subscriber.email} has been manually verified and activated.")
        else:
            subscriber.is_active = False
            subscriber.save(update_fields=['is_active'])
            messages.success(request, f"Subscriber {subscriber.email} has been deactivated.")
            
        return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers")


class NewsletterSubscriberDeleteView(StaffRequiredMixin, DeleteView):
    model = NewsletterSubscriber
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Newsletter subscriber deleted successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers"


class BranchCreateView(StaffRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch created successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"


class BranchUpdateView(StaffRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch updated successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"


class BranchDeleteView(StaffRequiredMixin, DeleteView):
    model = Branch
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch deleted successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"


class ContactInquiryDetailView(StaffRequiredMixin, DetailView):
    model = ContactInquiry
    template_name = 'admin_dashboard/contact/inquiry_detail.html'
    context_object_name = 'inquiry'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=['is_read'])
        return obj


class ContactInquiryDeleteView(StaffRequiredMixin, DeleteView):
    model = ContactInquiry
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Contact inquiry cleared successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=inquiries"


class ClearAllContactInquiriesView(StaffRequiredMixin, View):
    def post(self, request):
        count = ContactInquiry.objects.count()
        ContactInquiry.objects.all().delete()
        messages.success(request, f"Cleared all {count} contact inquiry record(s).")
        return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=inquiries")
