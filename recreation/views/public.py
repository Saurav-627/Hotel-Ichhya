from django.views.generic import ListView, DetailView
from ..models.activity import RecreationActivity


class RecreationListView(ListView):
    model = RecreationActivity
    template_name = 'recreation/recreation_list.html'
    context_object_name = 'activities'

    def get_queryset(self):
        return RecreationActivity.objects.filter(is_active=True).prefetch_related('images')


class RecreationDetailView(DetailView):
    model = RecreationActivity
    template_name = 'recreation/recreation_detail.html'
    context_object_name = 'activity'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return RecreationActivity.objects.filter(is_active=True).prefetch_related('images')
