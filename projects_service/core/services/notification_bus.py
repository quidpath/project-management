"""Single entry point for email and in-app notifications. Persists to audit.Notification, sends email via Celery, pushes to WebSocket."""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from projects_service.audit.models import Notification
from projects_service.audit.tasks import send_notification_email

logger = logging.getLogger(__name__)


class NotificationBus:
    def send(
        self,
        recipient_id,
        notification_type="email",
        title="",
        message="",
        data=None,
        corporate_id=None,
    ):
        data = data or {}
        notification = Notification.objects.create(
            recipient_id=recipient_id,
            corporate_id=corporate_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data,
        )
        if notification_type == "email":
            send_notification_email.delay(str(notification.id))
        # Push to user's WebSocket channel for in-app toast
        try:
            channel_layer = get_channel_layer()
            payload = {
                "type": "user_notification",
                "notification": {
                    "id": str(notification.id),
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                },
            }
            async_to_sync(channel_layer.group_send)(f"user_{recipient_id}", payload)
        except Exception as e:
            logger.warning("WebSocket push failed for user %s: %s", recipient_id, e)
        return notification

    def send_email(self, recipient_id, subject, body, destination_email=None, corporate_id=None):
        data = {}
        if destination_email:
            data["email"] = destination_email
        return self.send(
            recipient_id=recipient_id,
            notification_type="email",
            title=subject,
            message=body,
            data=data,
            corporate_id=corporate_id,
        )
