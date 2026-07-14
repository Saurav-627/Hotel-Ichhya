from django.views.generic import ListView
from ..models.activity import RecreationActivity

class RecreationListView(ListView):
    model = RecreationActivity
    template_name = 'recreation/recreation_list.html'
    context_object_name = 'activities'

    def get_queryset(self):
        return RecreationActivity.objects.filter(is_active=True)
