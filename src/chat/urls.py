from django.urls import path
from chat.views import (
    ChatDashboardView,
    RoomDetailPartialView,
    StartDirectChatView,
)

app_name = "chat"

urlpatterns = [
    path("", ChatDashboardView.as_view(), name="dashboard"),
    path("rooms/<int:pk>/", ChatDashboardView.as_view(), name="dashboard_with_room"),
    path("rooms/<int:pk>/partial/", RoomDetailPartialView.as_view(), name="room_detail_partial"),
    path("direct/<int:user_id>/", StartDirectChatView.as_view(), name="start_direct_chat"),
]
