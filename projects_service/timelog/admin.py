from django.contrib import admin
from .models import TimeEntry, TimerSession, ResourceAllocation


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["user_id", "project", "task", "date", "hours", "is_billable", "is_invoiced"]
    list_filter = ["is_billable", "is_invoiced"]
    date_hierarchy = "date"


@admin.register(TimerSession)
class TimerSessionAdmin(admin.ModelAdmin):
    list_display = ["user_id", "project", "task", "started_at", "is_billable"]


@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ["user_id", "project", "start_date", "end_date", "allocated_hours_per_day"]
