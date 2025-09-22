from rest_framework_nested import routers
from chat.views import RoomViewSet

app_name = "chat"

router = routers.DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="room")

urlpatterns = router.urls
