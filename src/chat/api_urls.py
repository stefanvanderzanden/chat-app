from django.urls import path
from chat.api_views import RoomMessageListView

app_name = "chat_api"

urlpatterns = [
    path("rooms/<int:room_id>/messages/", RoomMessageListView.as_view(), name="room_messages"),
]
