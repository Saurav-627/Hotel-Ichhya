from django.urls import path
from .views.public import RecreationListView

app_name = 'recreation'

urlpatterns = [
    path('', RecreationListView.as_view(), name='recreation_list'),
]
