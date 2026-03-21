from django.db import models
from projects_service.projects.models import Project
from projects_service.tasks.models import Task
from projects_service.core.base_models import BaseModel


class IssueCategory(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issue_categories")
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#EF4444")

    def __str__(self):
        return self.name


class Issue(BaseModel):
    SEVERITY_BLOCKER = "blocker"
    SEVERITY_CRITICAL = "critical"
    SEVERITY_MAJOR = "major"
    SEVERITY_MINOR = "minor"
    SEVERITY_TRIVIAL = "trivial"
    SEVERITY_CHOICES = [
        (SEVERITY_BLOCKER, "Blocker"),
        (SEVERITY_CRITICAL, "Critical"),
        (SEVERITY_MAJOR, "Major"),
        (SEVERITY_MINOR, "Minor"),
        (SEVERITY_TRIVIAL, "Trivial"),
    ]

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"
    STATUS_WONT_FIX = "wont_fix"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_WONT_FIX, "Won't Fix"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name="issues")
    category = models.ForeignKey(IssueCategory, on_delete=models.SET_NULL, null=True, blank=True)

    issue_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    steps_to_reproduce = models.TextField(blank=True)
    expected_result = models.TextField(blank=True)
    actual_result = models.TextField(blank=True)

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_MAJOR)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)

    reporter_id = models.UUIDField(db_index=True)
    assignee_id = models.UUIDField(null=True, blank=True, db_index=True)

    due_date = models.DateField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    environment = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=50, blank=True)
    fix_version = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = [("project", "issue_number")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.key}-I{self.issue_number}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.issue_number:
            last = Issue.objects.filter(project=self.project).order_by("-issue_number").first()
            self.issue_number = (last.issue_number + 1) if last else 1
        super().save(*args, **kwargs)


class IssueComment(BaseModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author_id = models.UUIDField(db_index=True)
    body = models.TextField()

    class Meta:
        ordering = ["created_at"]


class IssueAttachment(BaseModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="attachments")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="issue_attachments/")
    uploaded_by_id = models.UUIDField(db_index=True)
