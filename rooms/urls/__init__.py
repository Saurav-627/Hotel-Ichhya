from django.urls import path
from ..views.public import RoomListView, RoomDetailView

app_name = 'rooms'

urlpatterns = [
    path('', RoomListView.as_view(), name='room_list'),
    path('<slug:slug>/', RoomDetailView.as_view(), name='room_detail'),
]
