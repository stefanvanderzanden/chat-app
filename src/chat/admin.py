from django.contrib import admin

from chat.models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    fields = ["name", "room_type", "participants"]