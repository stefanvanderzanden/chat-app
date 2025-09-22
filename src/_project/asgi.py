import os
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project.settings")
django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens
    """

    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # Parse the query string to get the token
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)

        # Get token from query parameter
        token = query_params.get('token', [None])[0]

        if token:
            try:
                # Validate the token
                access_token = AccessToken(token)
                user = await self.get_user_from_token(access_token)
                scope['user'] = user
            except (InvalidToken, TokenError, Exception) as e:
                # Invalid token - set anonymous user
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, access_token):
        """Get user from JWT token"""
        try:
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except (KeyError, User.DoesNotExist):
            return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    """
    Stack that applies JWT authentication middleware
    """
    return JWTAuthMiddleware(inner)


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(  # Use custom JWT middleware instead of AuthMiddlewareStack
                URLRouter(websocket_urlpatterns)
            )
        ),
    }
)

