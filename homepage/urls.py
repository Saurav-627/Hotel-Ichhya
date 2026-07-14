from django.urls import path
from .views.public import HomeView

app_name = 'homepage'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
