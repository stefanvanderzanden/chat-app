from django.db import models
from django.conf import settings

class Room(models.Model):
    ROOM_TYPES = (
        ("group", "Group"),
        ("direct", "Direct"),
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Room name',
        blank=True,
        null=True
    )
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="rooms")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="direct")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room_type"],
                condition=models.Q(room_type="direct"),
                name="unique_direct_room_per_pair",
            )
        ]

    def __str__(self):
        if self.room_type == "direct":
            users = self.participants.all()
            return f"Direct: {', '.join([u.username for u in users])}"
        return f"Group: {self.name}"

    @property
    def unread_counts(self):
        counts = {}
        for participant in self.participants.all():
            try:
                state = self.read_states.get(user=participant)
                last_read_id = state.last_read.id if state.last_read else 0
                counts[participant.id] = self.messages.filter(id__gt=last_read_id).count()
            except RoomReadState.DoesNotExist:
                counts[participant.id] = self.messages.count()
        return counts


class Message(models.Model):
    room = models.ForeignKey("chat.Room", on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)



class RoomReadState(models.Model):
    """
    Keep track of the last read message of a user
    """
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="read_states")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_read = models.ForeignKey(
        "chat.Message", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("room", "user")