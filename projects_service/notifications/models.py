from django.db import models
from projects_service.projects.models import Project
from projects_service.core.base_models import BaseModel


class Notification(BaseModel):
    TYPE_TASK_CREATED = "task_created"
    TYPE_TASK_UPDATED = "task_updated"
    TYPE_TASK_MOVED = "task_moved"
    TYPE_TASK_COMMENT = "task_comment"
    TYPE_ISSUE_CREATED = "issue_created"
    TYPE_SPRINT_STARTED = "sprint_started"
    TYPE_SPRINT_COMPLETED = "sprint_completed"
    TYPE_MENTION = "mention"
    TYPE_CHOICES = [
        (TYPE_TASK_CREATED, "Task Created"),
        (TYPE_TASK_UPDATED, "Task Updated"),
        (TYPE_TASK_MOVED, "Task Moved"),
        (TYPE_TASK_COMMENT, "Task Comment"),
        (TYPE_ISSUE_CREATED, "Issue Created"),
        (TYPE_SPRINT_STARTED, "Sprint Started"),
        (TYPE_SPRINT_COMPLETED, "Sprint Completed"),
        (TYPE_MENTION, "Mention"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="notifications", null=True)
    recipient_id = models.UUIDField(db_index=True)
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification({self.notification_type}) for user {self.recipient_id}"
