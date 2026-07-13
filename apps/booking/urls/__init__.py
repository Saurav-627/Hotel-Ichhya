from django.urls import path
from ..views import booking

app_name = 'booking'

urlpatterns = [
    path('initiate/<int:room_id>/', booking.initiate_booking, name='initiate_booking'),
    path('create/<int:room_id>/', booking.create_booking, name='create_booking'),
    path('checkout/<uuid:booking_uid>/', booking.checkout_page, name='checkout_page'),
]
