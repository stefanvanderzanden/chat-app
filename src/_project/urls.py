from django.contrib import admin
from django.urls import path, include

from accounts.api_views import CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView, me

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),

    path("api/auth/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/me/", me, name="me"),

    path("api/chat/", include("chat.urls", namespace="chat"))
]
