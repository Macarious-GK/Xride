# """
# ASGI config for Xride project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# import os
# import django
# from django.core.asgi import get_asgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Xride.settings')

# django.setup()

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# # import ride_V3.routing
# from ride_V3.consumers import *


# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket":AuthMiddlewareStack(
#             URLRouter([
#                 path('ws/notification/', NotificationConsumer.as_asgi()),
#                 path("ws/car-status/", CarStatusConsumer.as_asgi()),
#             ])
#         )
#     ,
# })


"""
ASGI config for Xride project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Xride.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from ride_V3.consumers import NotificationConsumer, CarStatusConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/notification/', NotificationConsumer.as_asgi()),
            path("ws/car-status/", CarStatusConsumer.as_asgi()),
        ])
    ),
})
