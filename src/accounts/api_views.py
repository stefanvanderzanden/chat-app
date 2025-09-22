from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200 and "refresh" in response.data:
            refresh_token = response.data["refresh"]
            response.set_cookie(
                key="refresh",
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Strict",
                path="/api/auth/token/refresh/",
                # max_age=settings.REFRESH_TOKEN_LIFETIME,
            )
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # refresh token komt automatisch mee in cookie
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        # voeg refresh token toe aan request.data zodat de super() het kan gebruiken
        request.data["refresh"] = refresh_token

        # haal de response van de standaard TokenRefreshView
        response = super().post(request, *args, **kwargs)

        # check of refresh succesvol was
        if response.status_code == 200 and "refresh" in response.data:
            # update de cookie met de nieuwe refresh token
            response.set_cookie(
                key="refresh",
                value=response.data["refresh"],
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Strict",
                path="/api/auth/token/refresh/",
                # max_age=settings.REFRESH_TOKEN_LIFETIME,
            )
            # je kan de refresh token uit de body verwijderen als je dat wilt
            # del response.data["refresh"]

        return response


class LogoutView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie(
            key="refresh",
            path="/api/auth/token/refresh/",
            samesite="Strict",
        )
        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({
        "id": request.user.id,
        "email": request.user.email,
    })