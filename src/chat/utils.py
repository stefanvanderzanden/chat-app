# chat/utils.py
from django.db.models import Q
from .models import Room

def get_or_create_direct_room(user1, user2):
    room = Room.objects.filter(
        type="direct",
        participants=user1
    ).filter(participants=user2).first()

    if room:
        return room, False

    # nieuw direct room maken
    room = Room.objects.create(type="direct")
    room.participants.add(*[user1, user2])
    return room, True
