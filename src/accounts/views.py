from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import login
from django.contrib import messages

from .forms import SignUpForm


class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("chat:room_list")  # pas dit aan naar je chat startpagina

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Je account is aangemaakt!")
        return super().form_valid(form)
