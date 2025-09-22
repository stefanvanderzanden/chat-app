from django.conf import settings
from rest_framework import serializers

from accounts.models import User
from chat.models import Room, Message


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "first_name", "last_name"]


class RoomSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "display_name",
            "room_type",
            "created_at",
            "unread_count",
            "last_message",
            "participants"
        ]

    def get_display_name(self, obj):
        """Get the display name for the current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_display_name(request.user)
        return obj.name or "Unknown"

    def get_unread_count(self, obj):
        """Get unread count for the current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user_id = request.user.id
            return obj.unread_counts.get(user_id, 0)
        return 0

    def get_last_message(self, obj):
        """Get the last message in the room"""
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return {
                'id': str(last_message.id),
                'text': last_message.text,
                'user_name': last_message.user.full_name,
                'timestamp': last_message.timestamp.isoformat(),
                'is_own': last_message.user == self.context.get('request').user if self.context.get(
                    'request') else False
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "room_id", "user_id", "user_name", "text", "timestamp", "is_own"]

    def get_is_own(self, obj):
        """Check if message belongs to current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False


