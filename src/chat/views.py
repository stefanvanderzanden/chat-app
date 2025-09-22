from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Prefetch
from .models import Room, Message, RoomReadState
from .serializers import RoomSerializer, MessageSerializer


class RoomViewSet(ModelViewSet):
    """
    ViewSet for managing rooms
    """
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return rooms where current user is a participant"""
        return Room.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            'read_states',
            Prefetch(
                'messages',
                queryset=Message.objects.select_related('user').order_by('-timestamp')[:1],
                to_attr='latest_messages'
            )
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """Get all rooms for the current user"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get a specific room"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_as_read(self, request, *args, **kwargs):
        """Mark room as read for current user"""
        room = self.get_object()
        last_message = room.messages.order_by('-timestamp').first()

        if last_message:
            read_state, created = RoomReadState.objects.get_or_create(
                room=room,
                user=request.user
            )
            read_state.last_read = last_message
            read_state.save()

        return Response({'success': True})

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific room"""
        room = self.get_object()
        messages = room.messages.select_related('user').order_by('timestamp')

        # Pagination could be added here if needed
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
