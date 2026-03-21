from django.db import models
from projects_service.projects.models import Project
from projects_service.tasks.models import Task
from projects_service.core.base_models import BaseModel


class TimeEntry(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="time_entries")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name="time_entries")
    user_id = models.UUIDField(db_index=True)
    description = models.CharField(max_length=500, blank=True)
    date = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    is_billable = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_invoiced = models.BooleanField(default=False)
    invoice_id = models.PositiveIntegerField(null=True, blank=True, help_text="ERP Invoice ID")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user_id} – {self.hours}h on {self.date}"

    @property
    def amount(self):
        return self.hours * self.hourly_rate


class TimerSession(BaseModel):
    """Active timer for real-time time tracking."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    user_id = models.UUIDField(unique=True, db_index=True, help_text="Only one active timer per user")
    description = models.CharField(max_length=500, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    is_billable = models.BooleanField(default=False)

    def __str__(self):
        return f"Timer: user {self.user_id} on {self.project.key}"


class ResourceAllocation(BaseModel):
    """Planned resource allocation for capacity planning."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="allocations")
    user_id = models.UUIDField(db_index=True)
    start_date = models.DateField()
    end_date = models.DateField()
    allocated_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"Allocation: user {self.user_id} on {self.project.key}"
