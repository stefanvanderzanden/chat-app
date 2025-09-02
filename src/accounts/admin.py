from django.contrib import admin

from accounts.models import InviteCode, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "is_staff", "is_active", "is_superuser"]
    fields = ["first_name", "last_name", "email"]


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    fields = ["code"]