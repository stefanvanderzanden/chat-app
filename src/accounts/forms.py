from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, InviteCode

class SignUpForm(UserCreationForm):
    invite_code = forms.CharField()

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "invite_code")

    def clean_invite_code(self):
        code = self.cleaned_data["invite_code"]
        try:
            invite = InviteCode.objects.get(code=code, is_used=False)
        except InviteCode.DoesNotExist:
            raise forms.ValidationError("Ongeldige of gebruikte uitnodigingscode")
        return invite

    def save(self, commit=True):
        user = super().save(commit=False)
        invite = self.cleaned_data["invite_code"]
        if commit:
            user.save()
            invite.use()
        return user
