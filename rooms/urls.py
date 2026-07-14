from django.urls import path
from .views.public import RoomListView, RoomDetailView, check_room_availability

app_name = 'rooms'

urlpatterns = [
    path('', RoomListView.as_view(), name='room_list'),
    path('<slug:slug>/', RoomDetailView.as_view(), name='room_detail'),
    path('api/<int:room_id>/check-availability/', check_room_availability, name='check_room_availability'),
]
