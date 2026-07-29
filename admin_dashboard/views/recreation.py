from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory

from admin_dashboard.mixins import StaffRequiredMixin
from recreation.models.activity import RecreationActivity
from recreation.models.activity_image import RecreationActivityImage
from admin_dashboard.forms import RecreationActivityForm, RecreationActivityImageForm

RecreationImageFormSet = inlineformset_factory(
    RecreationActivity, RecreationActivityImage, form=RecreationActivityImageForm,
    fields=('image',),
    extra=3, can_delete=True
)


class RecreationDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        activities = RecreationActivity.objects.all()
        return render(request, 'admin_dashboard/recreation/dashboard.html', {
            'activities': activities
        })


class RecreationCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = RecreationActivityForm()
        image_formset = RecreationImageFormSet()
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': 'Add Recreation Activity',
        })

    def post(self, request):
        form = RecreationActivityForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save()
            image_formset = RecreationImageFormSet(request.POST, request.FILES, instance=activity)
            if image_formset.is_valid():
                image_formset.save()
                messages.success(request, "Recreational activity created successfully.")
                return redirect(reverse('admin_dashboard:recreation_dashboard'))
            else:
                activity.delete()
        else:
            image_formset = RecreationImageFormSet(request.POST, request.FILES)

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': 'Add Recreation Activity',
        })


class RecreationUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        activity = get_object_or_404(RecreationActivity, pk=pk)
        form = RecreationActivityForm(instance=activity)
        image_formset = RecreationImageFormSet(instance=activity)
        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': f'Edit Activity: {activity.name}',
        })

    def post(self, request, pk):
        activity = get_object_or_404(RecreationActivity, pk=pk)
        form = RecreationActivityForm(request.POST, request.FILES, instance=activity)
        image_formset = RecreationImageFormSet(request.POST, request.FILES, instance=activity)

        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            messages.success(request, "Recreational activity updated successfully.")
            return redirect(reverse('admin_dashboard:recreation_dashboard'))

        return render(request, 'admin_dashboard/generic_form.html', {
            'form': form,
            'image_formset': image_formset,
            'title': f'Edit Activity: {activity.name}',
        })


class RecreationDeleteView(StaffRequiredMixin, DeleteView):
    model = RecreationActivity
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Recreational activity deleted successfully.")
        return reverse('admin_dashboard:recreation_dashboard')
