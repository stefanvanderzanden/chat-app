from django.contrib import admin

from accounts.models import InviteCode


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    fields = ["code"]