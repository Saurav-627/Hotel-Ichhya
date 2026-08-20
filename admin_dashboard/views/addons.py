from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from booking.models.addon import Addon
from settings_manager.models.currency import Currency
from admin_dashboard.mixins import StaffRequiredMixin
from admin_dashboard.forms import AddonForm, AddonPriceFormSet


class AddonDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        from django.core.paginator import Paginator
        addons_qs = Addon.objects.all().prefetch_related('prices__currency')
        currencies = Currency.objects.filter(is_published=True)
        page_number = request.GET.get('page', 1)
        paginator = Paginator(addons_qs, 10)
        addons_page = paginator.get_page(page_number)

        return render(request, 'admin_dashboard/addons/dashboard.html', {
            'addons': addons_page,
            'currencies': currencies,
        })


class AddonCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = AddonForm()
        currency_price_formset = AddonPriceFormSet()
        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'title': 'Create New Add-on Service'
        })

    def post(self, request):
        form = AddonForm(request.POST)
        if form.is_valid():
            addon = form.save()
            currency_price_formset = AddonPriceFormSet(request.POST, instance=addon)
            if currency_price_formset.is_valid():
                currency_price_formset.save()
                messages.success(request, f"Add-on '{addon.name}' created successfully.")
                return redirect(reverse('admin_dashboard:addon_dashboard'))
            else:
                addon.delete()
                messages.error(request, "Error saving add-on pricing. Please review form errors.")
        else:
            currency_price_formset = AddonPriceFormSet(request.POST)
            messages.error(request, "Error saving add-on details. Please review form errors.")

        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'title': 'Create New Add-on Service'
        })


class AddonUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        form = AddonForm(instance=addon)
        currency_price_formset = AddonPriceFormSet(instance=addon)
        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'addon': addon,
            'title': f'Edit Add-on: {addon.name}'
        })

    def post(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        form = AddonForm(request.POST, instance=addon)
        currency_price_formset = AddonPriceFormSet(request.POST, instance=addon)
        if form.is_valid() and currency_price_formset.is_valid():
            form.save()
            currency_price_formset.save()
            messages.success(request, f"Add-on '{addon.name}' updated successfully.")
            return redirect(reverse('admin_dashboard:addon_dashboard'))

        messages.error(request, "Error updating add-on. Please check the form errors below.")
        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'addon': addon,
            'title': f'Edit Add-on: {addon.name}'
        })


class AddonDeleteView(StaffRequiredMixin, View):
    def get(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        return render(request, 'admin_dashboard/addons/confirm_delete.html', {
            'addon': addon
        })

    def post(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        name = addon.name
        addon.delete()
        messages.success(request, f"Add-on '{name}' deleted successfully.")
        return redirect(reverse('admin_dashboard:addon_dashboard'))
