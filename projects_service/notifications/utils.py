import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from projects_service.projects.models import ProjectMember

logger = logging.getLogger(__name__)


def notify_project_members(project_id, event, data):
    """
    Broadcast a project event to all project members via WebSocket
    and persist in-app notifications.
    """
    channel_layer = get_channel_layer()
    members = ProjectMember.objects.filter(project_id=project_id).values_list("user_id", flat=True)

    message = {
        "type": "project_event",
        "event": event,
        "project_id": project_id,
        **data,
    }

    group_name = f"project_{project_id}"
    try:
        async_to_sync(channel_layer.group_send)(group_name, message)
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed for project {project_id}: {e}")

    notifications = [
        Notification(
            project_id=project_id,
            recipient_id=uid,
            notification_type=event,
            title=_event_title(event, data),
            data=data,
        )
        for uid in members
    ]
    Notification.objects.bulk_create(notifications)


def notify_user(user_id, event, data, title=""):
    """Send a personal notification to a specific user."""
    channel_layer = get_channel_layer()
    message = {"type": "user_notification", "event": event, "data": data}
    try:
        async_to_sync(channel_layer.group_send)(f"user_{user_id}", message)
    except Exception as e:
        logger.warning(f"User notification failed for user {user_id}: {e}")

    Notification.objects.create(
        recipient_id=user_id,
        notification_type=event,
        title=title or event,
        data=data,
    )


def _event_title(event, data):
    titles = {
        "task_created": f"New task: {data.get('title', '')}",
        "task_updated": f"Task updated: {data.get('title', '')}",
        "task_moved": "Task moved",
        "task_comment": "New comment on task",
        "issue_created": f"New issue: {data.get('title', '')}",
        "sprint_started": "Sprint started",
        "sprint_completed": "Sprint completed",
    }
    return titles.get(event, event)
