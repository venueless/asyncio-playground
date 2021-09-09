"""
ASGI config for django_channels project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import venueless.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_channels.settings')

application = ProtocolTypeRouter({
    # "http": get_asgi_application(),
    "websocket": URLRouter(
        venueless.routing.websocket_urlpatterns
    )
})
