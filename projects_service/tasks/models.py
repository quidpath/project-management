from django.db import models
from projects_service.projects.models import Project, Sprint
from projects_service.core.base_models import BaseModel


class TaskLabel(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="labels")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#6B7280")

    class Meta:
        unique_together = [("project", "name")]

    def __str__(self):
        return f"{self.project.key}:{self.name}"


class Column(BaseModel):
    """Kanban column / workflow state for a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)
    is_done_column = models.BooleanField(default=False)
    wip_limit = models.PositiveSmallIntegerField(default=0, help_text="0 = unlimited")

    class Meta:
        ordering = ["order"]
        unique_together = [("project", "name")]

    def __str__(self):
        return f"{self.project.key} – {self.name}"


class Task(BaseModel):
    TYPE_EPIC = "epic"
    TYPE_STORY = "story"
    TYPE_TASK = "task"
    TYPE_BUG = "bug"
    TYPE_SUBTASK = "subtask"
    TYPE_CHOICES = [
        (TYPE_EPIC, "Epic"),
        (TYPE_STORY, "Story"),
        (TYPE_TASK, "Task"),
        (TYPE_BUG, "Bug"),
        (TYPE_SUBTASK, "Subtask"),
    ]

    PRIORITY_CRITICAL = "critical"
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    PRIORITY_CHOICES = [
        (PRIORITY_CRITICAL, "Critical"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_LOW, "Low"),
    ]

    STATUS_BACKLOG = "backlog"
    STATUS_TODO = "todo"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_IN_REVIEW = "in_review"
    STATUS_DONE = "done"
    STATUS_CHOICES = [
        (STATUS_BACKLOG, "Backlog"),
        (STATUS_TODO, "To Do"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_IN_REVIEW, "In Review"),
        (STATUS_DONE, "Done"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_tasks")
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="sprint_tasks")
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, blank=True, related_name="column_tasks")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks")

    task_number = models.PositiveIntegerField(help_text="Auto-increment within project")
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_TASK)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BACKLOG)

    assignee_id = models.UUIDField(null=True, blank=True, db_index=True)
    reporter_id = models.UUIDField(db_index=True)

    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    story_points = models.PositiveSmallIntegerField(default=0)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    progress = models.PositiveSmallIntegerField(default=0, help_text="0-100 percent")

    labels = models.ManyToManyField(TaskLabel, blank=True)

    order = models.FloatField(default=0.0, help_text="Float order for drag-and-drop")
    is_billable = models.BooleanField(default=False)

    class Meta:
        unique_together = [("project", "task_number")]
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.project.key}-{self.task_number}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.task_number:
            last = Task.objects.filter(project=self.project).order_by("-task_number").first()
            self.task_number = (last.task_number + 1) if last else 1
        super().save(*args, **kwargs)


class TaskComment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author_id = models.UUIDField(db_index=True)
    body = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.task}"


class TaskAttachment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="task_attachments/")
    uploaded_by_id = models.UUIDField(db_index=True)

    def __str__(self):
        return self.name


class TaskDependency(BaseModel):
    TYPE_BLOCKS = "blocks"
    TYPE_BLOCKED_BY = "blocked_by"
    TYPE_RELATES_TO = "relates_to"
    TYPE_DUPLICATES = "duplicates"
    TYPE_CHOICES = [
        (TYPE_BLOCKS, "Blocks"),
        (TYPE_BLOCKED_BY, "Blocked By"),
        (TYPE_RELATES_TO, "Relates To"),
        (TYPE_DUPLICATES, "Duplicates"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="dependencies")
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="dependants")
    dependency_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        unique_together = [("task", "related_task", "dependency_type")]


class TaskWatcher(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="watchers")
    user_id = models.UUIDField(db_index=True)

    class Meta:
        unique_together = [("task", "user_id")]
