from django.db import models

from projects_service.core.base_models import BaseModel


class Project(BaseModel):
    METHOD_WATERFALL = "waterfall"
    METHOD_AGILE_SCRUM = "scrum"
    METHOD_AGILE_KANBAN = "kanban"
    METHOD_CHOICES = [
        (METHOD_WATERFALL, "Waterfall"),
        (METHOD_AGILE_SCRUM, "Scrum"),
        (METHOD_AGILE_KANBAN, "Kanban"),
    ]

    STATUS_PLANNING = "planning"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_ON_HOLD = "on_hold"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PLANNING, "Planning"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_ON_HOLD, "On Hold"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=10, help_text="Short project key, e.g. PROJ")
    description = models.TextField(blank=True)
    methodology = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_AGILE_SCRUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNING)

    owner_id = models.UUIDField(db_index=True)
    client_id = models.UUIDField(null=True, blank=True, db_index=True, help_text="CRM Contact ID")

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)

    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    budget_currency = models.CharField(max_length=3, default="KES")
    hours_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_billable = models.BooleanField(default=False)
    billing_type = models.CharField(
        max_length=20,
        choices=[("fixed", "Fixed Price"), ("hourly", "Time & Material"), ("retainer", "Retainer")],
        default="fixed",
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cover_image = models.ImageField(upload_to="project_covers/", null=True, blank=True)
    color = models.CharField(max_length=7, default="#3B82F6")

    class Meta:
        unique_together = [("corporate_id", "key")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.key}] {self.name}"


class ProjectMember(BaseModel):
    ROLE_OWNER = "owner"
    ROLE_MANAGER = "manager"
    ROLE_DEVELOPER = "developer"
    ROLE_DESIGNER = "designer"
    ROLE_TESTER = "tester"
    ROLE_VIEWER = "viewer"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MANAGER, "Project Manager"),
        (ROLE_DEVELOPER, "Developer"),
        (ROLE_DESIGNER, "Designer"),
        (ROLE_TESTER, "Tester"),
        (ROLE_VIEWER, "Viewer"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    user_id = models.UUIDField(db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_DEVELOPER)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("project", "user_id")]

    def __str__(self):
        return f"Member {self.user_id} in {self.project.key}"


class Sprint(BaseModel):
    STATUS_UPCOMING = "upcoming"
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sprints")
    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    start_date = models.DateField()
    end_date = models.DateField()
    velocity = models.PositiveIntegerField(default=0, help_text="Story points completed")

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.project.key} – {self.name}"


class Milestone(BaseModel):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [(STATUS_OPEN, "Open"), (STATUS_CLOSED, "Closed")]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.project.key} – {self.title}"


class ProjectRisk(BaseModel):
    PROBABILITY_LOW = "low"
    PROBABILITY_MEDIUM = "medium"
    PROBABILITY_HIGH = "high"

    IMPACT_LOW = "low"
    IMPACT_MEDIUM = "medium"
    IMPACT_HIGH = "high"
    IMPACT_CRITICAL = "critical"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="risks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    probability = models.CharField(max_length=10, choices=[
        (PROBABILITY_LOW, "Low"), (PROBABILITY_MEDIUM, "Medium"), (PROBABILITY_HIGH, "High")
    ], default=PROBABILITY_LOW)
    impact = models.CharField(max_length=10, choices=[
        (IMPACT_LOW, "Low"), (IMPACT_MEDIUM, "Medium"), (IMPACT_HIGH, "High"), (IMPACT_CRITICAL, "Critical")
    ], default=IMPACT_MEDIUM)
    mitigation_plan = models.TextField(blank=True)
    owner_id = models.UUIDField(null=True, blank=True, db_index=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProjectDocument(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="project_docs/")
    uploaded_by_id = models.UUIDField(db_index=True)

    def __str__(self):
        return self.name
