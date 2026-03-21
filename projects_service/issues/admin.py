from django.contrib import admin
from .models import Issue, IssueComment, IssueAttachment, IssueCategory


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ["issue_number", "title", "project", "severity", "status", "assignee_id", "due_date"]
    list_filter = ["severity", "status"]
    search_fields = ["title", "description"]


@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "color"]


@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ["issue", "author_id", "created_at"]


@admin.register(IssueAttachment)
class IssueAttachmentAdmin(admin.ModelAdmin):
    list_display = ["name", "issue", "uploaded_by_id", "created_at"]
