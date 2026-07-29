from django.urls import path
from .views.public import RecreationListView, RecreationDetailView

app_name = 'recreation'

urlpatterns = [
    path('', RecreationListView.as_view(), name='recreation_list'),
    path('<slug:slug>/', RecreationDetailView.as_view(), name='recreation_detail'),
]
