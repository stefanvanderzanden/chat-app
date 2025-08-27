import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message, RoomReadState

@database_sync_to_async
def save_message(user, room_id, text):
    room = Room.objects.get(id=room_id)
    msg = Message.objects.create(room=room, user=user, text=text)
    return msg

@database_sync_to_async
def mark_as_read(room_id, user, message_id):
    room = Room.objects.get(id=room_id)
    state, _ = RoomReadState.objects.get_or_create(room=room, user=user)
    state.last_read_id = message_id
    state.save()
    return state

@database_sync_to_async
def get_unread_count(room_id, user):
    room = Room.objects.get(id=room_id)
    try:
        state = RoomReadState.objects.get(room=room, user=user)
        last_read_id = state.last_read.id if state.last_read else 0
        return room.messages.filter(id__gt=last_read_id).count()
    except RoomReadState.DoesNotExist:
        return room.messages.count()


@database_sync_to_async
def get_user_rooms(user):
    return list(Room.objects.filter(participants=user))


@database_sync_to_async
def get_last_message(room_id):
    return Message.objects.filter(room=Room.objects.get(id=room_id)).order_by('-timestamp').first()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        rooms = await get_user_rooms(self.user)
        self.rooms = rooms

        for room in rooms:
            await self.channel_layer.group_add(
                f"chat_{room.id}",
                self.channel_name,
            )

        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        # Nieuw bericht
        if action == "send_message":
            room_id = data["room_id"]
            msg = await save_message(self.user, room_id, data["message"])
            await mark_as_read(room_id, self.user, msg.id)

            # Push bericht naar alle deelnemers
            await self.channel_layer.group_send(
                f"chat_{room_id}",
                {
                    "type": "chat_message",
                    "room_id": room_id,
                    "message_id": msg.id,
                    "message": msg.text,
                    "user": self.user.email,
                },
            )

        # Mark as read
        elif action == "mark_as_read":
            room_id = data["room_id"]
            last_message = await get_last_message(room_id)

            if last_message:
                await mark_as_read(room_id, self.user, last_message.id)

            unread = await get_unread_count(room_id, self.user)
            print("YES: ", unread)

            # Send update
            await self.send(text_data=json.dumps({
                "type": "unread_update",
                "room_id": room_id,
                "unread": unread,
            }))

    async def chat_message(self, event):
        """
        Received message, send to frontend
        """
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "room_id": event["room_id"],
            "message_id": event["message_id"],
            "message": event["message"],
            "user": event["user"],
        }))

    async def disconnect(self, close_code):
        for room in getattr(self, "rooms", []):
            await self.channel_layer.group_discard(
                f"chat_{room.id}",
                self.channel_name,
            )
