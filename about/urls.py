from django.urls import path
from .views.public import AboutPageView

app_name = 'about'

urlpatterns = [
    path('', AboutPageView.as_view(), name='about_page'),
]
