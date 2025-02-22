import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social.settings')
django.setup()

# Правильный импорт Middleware
from network.middleware import JWTAuthMiddleware
from network.routing import websocket_urlpatterns

# Конфигурация ASGI
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # AuthMiddlewareStack нужен, если есть стандартная аутентификация Django
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
