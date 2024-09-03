from django.urls import re_path, path

from webssh import consumers

websocket_urlpatterns = [
    re_path(r'^ws/webssh/$', consumers.TerminalConsumer.as_asgi()),
]