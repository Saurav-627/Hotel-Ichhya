from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from dashboard.mixins import StaffRequiredMixin
from settings_manager.models.hotel_settings import HotelSettings
from settings_manager.models.currency import Currency
from settings_manager.models.navigation import NavigationMenu
from dashboard.forms import HotelSettingsForm, CurrencyForm, NavigationMenuForm

class SettingsDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        settings_obj = HotelSettings.objects.first()
        if not settings_obj:
            settings_obj = HotelSettings.objects.create()
            
        settings_form = HotelSettingsForm(instance=settings_obj)
        currencies = Currency.objects.all()
        menus = NavigationMenu.objects.all().select_related('parent')
        
        # Determine active tab
        active_tab = request.GET.get('tab', 'general')
        
        return render(request, 'dashboard/settings_manager.html', {
            'settings_form': settings_form,
            'currencies': currencies,
            'menus': menus,
            'active_tab': active_tab,
        })
        
    def post(self, request):
        settings_obj = HotelSettings.objects.first()
        if not settings_obj:
            settings_obj = HotelSettings.objects.create()
            
        settings_form = HotelSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, "Global settings updated successfully.")
            return redirect('dashboard:settings_dashboard')
        
        # If invalid
        currencies = Currency.objects.all()
        menus = NavigationMenu.objects.all()
        return render(request, 'dashboard/settings_manager.html', {
            'settings_form': settings_form,
            'currencies': currencies,
            'menus': menus,
            'active_tab': 'general',
        })

# Currencies Views
class CurrencyCreateView(StaffRequiredMixin, CreateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Currency created successfully.")
        return reverse_lazy('dashboard:settings_dashboard') + "?tab=currencies"

class CurrencyUpdateView(StaffRequiredMixin, UpdateView):
    model = Currency
    form_class = CurrencyForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Currency updated successfully.")
        return reverse_lazy('dashboard:settings_dashboard') + "?tab=currencies"

class CurrencyDeleteView(StaffRequiredMixin, DeleteView):
    model = Currency
    template_name = 'dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Currency deleted successfully.")
        return reverse_lazy('dashboard:settings_dashboard') + "?tab=currencies"

# Navigation Menu Views
class NavigationMenuCreateView(StaffRequiredMixin, CreateView):
    model = NavigationMenu
    form_class = NavigationMenuForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Navigation menu item created successfully.")
        return reverse_lazy('dashboard:settings_dashboard') + "?tab=navigation"

class NavigationMenuUpdateView(StaffRequiredMixin, UpdateView):
    model = NavigationMenu
    form_class = NavigationMenuForm
    template_name = 'dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Navigation menu item updated successfully.")
        return reverse_lazy('dashboard:settings_dashboard') + "?tab=navigation"

class NavigationMenuDeleteView(StaffRequiredMixin, DeleteView):
    model = NavigationMenu
    template_name = 'dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Navigation menu item deleted successfully.")
        return reverse_lazy('dashboard:settings_dashboard') + "?tab=navigation"
