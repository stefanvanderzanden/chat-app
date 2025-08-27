from rest_framework import generics, permissions
from chat.models import Message, Room
from chat.serializers import MessageSerializer


class RoomMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        # check of gebruiker lid is van de room
        room = Room.objects.get(pk=room_id)
        if self.request.user not in room.participants.all():
            return Message.objects.none()

        return (
            Message.objects.filter(room=room)
            .select_related("user")
            .order_by("-timestamp")
        )
