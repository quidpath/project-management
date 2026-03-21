from rest_framework import serializers
from .models import Issue, IssueComment, IssueAttachment, IssueCategory


class IssueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueCategory
        fields = "__all__"


class IssueCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueComment
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "author_id"]


class IssueAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueAttachment
        fields = "__all__"
        read_only_fields = ["created_at", "uploaded_by_id"]


class IssueSerializer(serializers.ModelSerializer):
    comments = IssueCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = "__all__"
        read_only_fields = ["issue_number", "created_at", "updated_at"]


class IssueListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id", "issue_number", "title", "severity", "status", "reporter_id",
            "assignee_id", "due_date", "category", "created_at",
        ]
