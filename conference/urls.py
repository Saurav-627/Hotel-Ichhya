from django.urls import path
from .views import VenueListView, VenueDetailView

app_name = 'conference'

urlpatterns = [
    path('', VenueListView.as_view(), name='venue_list'),
    path('<slug:slug>/', VenueDetailView.as_view(), name='venue_detail'),
]
