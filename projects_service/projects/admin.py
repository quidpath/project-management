from django.contrib import admin
from .models import Project, ProjectMember, Sprint, Milestone, ProjectRisk, ProjectDocument


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["key", "name", "status", "methodology", "owner_id", "start_date", "end_date"]
    list_filter = ["status", "methodology", "is_billable"]
    search_fields = ["name", "key"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "user_id", "role", "joined_at"]
    list_filter = ["role"]


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "status", "start_date", "end_date", "velocity"]
    list_filter = ["status"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "due_date", "status"]
    list_filter = ["status"]


@admin.register(ProjectRisk)
class ProjectRiskAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "probability", "impact", "is_resolved"]
    list_filter = ["probability", "impact", "is_resolved"]


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "uploaded_by_id", "created_at"]
