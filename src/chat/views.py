from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from accounts.models import User
from chat.models import Room, Message
from chat.utils import get_or_create_direct_room


@method_decorator(login_required, name='dispatch')
class ChatDashboardView(View):

    def get(self, request, pk=None):
        rooms = request.user.rooms.all()
        selected_room = None
        messages = None

        if pk:
            selected_room = get_object_or_404(Room, pk=pk)
            messages = selected_room.messages.order_by("-timestamp")[:20][::-1]

        unread_counts = {}
        for room in rooms:
            unread_counts[room.id] = Message.objects.filter(room=room).exclude(user=self.request.user).count()

        return render(
            request,
            "chat/dashboard.html",
            {
                "direct_rooms": rooms.filter(room_type="direct"),
                "group_rooms": rooms.filter(room_type="group"),
                "selected_room": selected_room,
                "messages": messages,
                "unread_counts": unread_counts
            },
        )

@method_decorator(login_required, name='dispatch')
class RoomDetailPartialView(View):
    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        messages = room.messages.order_by("-timestamp")[:20][::-1]
        return render(request, "chat/_room_detail.html", {"room": room, "messages": messages})



@method_decorator(login_required, name='dispatch')
class StartDirectChatView(View):
    def get(self, request, *args, **kwargs):
        other_user = get_object_or_404(User, id=kwargs.get("user_id"))
        room, created = get_or_create_direct_room(request.user, other_user)
        return redirect("chat:dashboard_with_room", pk=room.id)
