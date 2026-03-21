from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment, TaskLabel, Column, TaskDependency


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["task_number", "title", "project", "task_type", "priority", "status", "assignee_id", "due_date"]
    list_filter = ["task_type", "priority", "status"]
    search_fields = ["title", "description"]
    raw_id_fields = ["project", "sprint", "column", "parent"]


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "order", "wip_limit", "is_done_column"]


@admin.register(TaskLabel)
class TaskLabelAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "color"]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ["task", "author_id", "created_at"]


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ["name", "task", "uploaded_by_id", "created_at"]
