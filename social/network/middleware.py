import jwt
from django.conf import settings
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from .models import UserProfile


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        token = headers.get(b"authorization", b"").decode("utf-8")

        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
        else:
            token = None

        scope["user"] = await self.get_user_from_token(token)

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return None  # Нет токена — нет пользователя

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return UserProfile.objects.get(id=payload["user_id"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, UserProfile.DoesNotExist):
            return None  # Ошибки токена — юзер не найден
