from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/projects/(?P<project_id>\d+)/$", consumers.ProjectNotificationConsumer.as_asgi()),
    re_path(r"ws/notifications/$", consumers.UserNotificationConsumer.as_asgi()),
]
