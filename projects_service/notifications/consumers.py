import json
import jwt
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class ProjectNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time project notifications.
    Connect: ws://projects.quidpath.com/ws/projects/<project_id>/
    Auth: JWT passed as query param ?token=<jwt>
    """

    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group_name = f"project_{self.project_id}"

        token = self._get_token()
        if not token or not self._validate_token(token):
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"type": "connected", "project_id": self.project_id}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get("type", "ping")
            if event_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except json.JSONDecodeError:
            pass

    async def project_event(self, event):
        """Receive messages from the channel layer group and forward to WebSocket."""
        await self.send(text_data=json.dumps(event))

    def _get_token(self):
        query_string = self.scope.get("query_string", b"").decode()
        for part in query_string.split("&"):
            if part.startswith("token="):
                return part.split("=", 1)[1]
        return None

    def _validate_token(self, token):
        try:
            jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_iss": True},
                issuer="quidpath-backend",
            )
            return True
        except jwt.InvalidTokenError:
            return False


class UserNotificationConsumer(AsyncWebsocketConsumer):
    """
    Personal notification channel per user.
    Connect: ws://projects.quidpath.com/ws/notifications/
    Auth: JWT passed as query param ?token=<jwt>
    """

    async def connect(self):
        token = self._get_token()
        payload = self._validate_token(token)
        if not payload:
            await self.close(code=4001)
            return

        self.user_id = payload.get("user_id")
        self.group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def user_notification(self, event):
        await self.send(text_data=json.dumps(event))

    def _get_token(self):
        query_string = self.scope.get("query_string", b"").decode()
        for part in query_string.split("&"):
            if part.startswith("token="):
                return part.split("=", 1)[1]
        return None

    def _validate_token(self, token):
        if not token:
            return None
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_iss": True},
                issuer="quidpath-backend",
            )
        except jwt.InvalidTokenError:
            return None
