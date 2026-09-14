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
        from django.db.models import Q

        applies_to_filter = request.GET.get('applies_to', '').strip()
        search_query = request.GET.get('q', '').strip()

        addons_qs = Addon.objects.all().prefetch_related('prices__currency').order_by('order', 'id')
        if applies_to_filter in ['room', 'events', 'both']:
            addons_qs = addons_qs.filter(applies_to=applies_to_filter)
        if search_query:
            addons_qs = addons_qs.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        currencies = Currency.objects.filter(is_published=True)
        page_number = request.GET.get('page', 1)
        paginator = Paginator(addons_qs, 12)
        addons_page = paginator.get_page(page_number)

        return render(request, 'admin_dashboard/addons/dashboard.html', {
            'addons': addons_page,
            'currencies': currencies,
            'applies_to_filter': applies_to_filter,
            'search_query': search_query,
            'total_count': Addon.objects.count(),
            'room_count': Addon.objects.filter(applies_to='room').count(),
            'event_count': Addon.objects.filter(applies_to='events').count(),
            'both_count': Addon.objects.filter(applies_to='both').count(),
        })


class AddonCreateView(StaffRequiredMixin, View):
    def get(self, request):
        applies_to = request.GET.get('applies_to', '').strip()
        initial = {}
        if applies_to in ['events', 'room', 'both']:
            initial['applies_to'] = applies_to
            if applies_to == 'events':
                initial['price_type'] = 'per_booking'
        form = AddonForm(initial=initial) if initial else AddonForm()
        currency_price_formset = AddonPriceFormSet()
        return_to = request.GET.get('return_to', '')
        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'return_to': return_to,
            'title': 'Create New Add-on Service'
        })

    def post(self, request):
        return_to = request.POST.get('return_to', '') or request.GET.get('return_to', '')
        form = AddonForm(request.POST)
        if form.is_valid():
            addon = form.save()
            currency_price_formset = AddonPriceFormSet(request.POST, instance=addon)
            if currency_price_formset.is_valid():
                currency_price_formset.save()
                messages.success(request, f"Add-on '{addon.name}' created successfully.")
                if return_to == 'conference':
                    return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=services')
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
            'return_to': return_to,
            'title': 'Create New Add-on Service'
        })


class AddonUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        form = AddonForm(instance=addon)
        currency_price_formset = AddonPriceFormSet(instance=addon)
        return_to = request.GET.get('return_to', '')
        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'addon': addon,
            'return_to': return_to,
            'title': f'Edit Add-on: {addon.name}'
        })

    def post(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        return_to = request.POST.get('return_to', '') or request.GET.get('return_to', '')
        form = AddonForm(request.POST, instance=addon)
        currency_price_formset = AddonPriceFormSet(request.POST, instance=addon)
        if form.is_valid() and currency_price_formset.is_valid():
            form.save()
            currency_price_formset.save()
            messages.success(request, f"Add-on '{addon.name}' updated successfully.")
            if return_to == 'conference':
                return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=services')
            return redirect(reverse('admin_dashboard:addon_dashboard'))

        messages.error(request, "Error updating add-on. Please check the form errors below.")
        return render(request, 'admin_dashboard/addons/form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'addon': addon,
            'return_to': return_to,
            'title': f'Edit Add-on: {addon.name}'
        })


class AddonDeleteView(StaffRequiredMixin, View):
    def get(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        return_to = request.GET.get('return_to', '')
        return render(request, 'admin_dashboard/addons/confirm_delete.html', {
            'addon': addon,
            'return_to': return_to,
        })

    def post(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        return_to = request.POST.get('return_to', '') or request.GET.get('return_to', '')
        name = addon.name
        addon.delete()
        messages.success(request, f"Add-on '{name}' deleted successfully.")
        if return_to == 'conference':
            return redirect(reverse('admin_dashboard:conference_dashboard') + '?tab=services')
        return redirect(reverse('admin_dashboard:addon_dashboard'))
