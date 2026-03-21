from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Issue, IssueComment, IssueAttachment, IssueCategory
from .serializers import (
    IssueSerializer, IssueListSerializer, IssueCommentSerializer,
    IssueAttachmentSerializer, IssueCategorySerializer
)
from projects_service.projects.models import Project
from projects_service.notifications.utils import notify_project_members


class IssueCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = IssueCategorySerializer

    def get_queryset(self):
        return IssueCategory.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class IssueListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        return IssueListSerializer if self.request.method == "GET" else IssueSerializer

    def get_queryset(self):
        qs = Issue.objects.filter(project_id=self.kwargs["project_pk"])
        sev = self.request.query_params.get("severity")
        st = self.request.query_params.get("status")
        assignee = self.request.query_params.get("assignee")
        if sev:
            qs = qs.filter(severity=sev)
        if st:
            qs = qs.filter(status=st)
        if assignee:
            qs = qs.filter(assignee_id=assignee)
        return qs

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        issue = serializer.save(project=project, reporter_id=self.request.user_id)
        notify_project_members(
            project_id=project.pk,
            event="issue_created",
            data={"issue_id": issue.pk, "title": issue.title, "severity": issue.severity},
        )


class IssueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IssueSerializer

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        issue = serializer.save()
        if issue.status == Issue.STATUS_RESOLVED and old_status != Issue.STATUS_RESOLVED:
            issue.resolved_at = timezone.now()
            issue.save(update_fields=["resolved_at"])


class IssueCommentListView(generics.ListCreateAPIView):
    serializer_class = IssueCommentSerializer

    def get_queryset(self):
        return IssueComment.objects.filter(issue_id=self.kwargs["issue_pk"])

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs["issue_pk"])
        serializer.save(issue=issue, author_id=self.request.user_id)


class IssueAttachmentListView(generics.ListCreateAPIView):
    serializer_class = IssueAttachmentSerializer

    def get_queryset(self):
        return IssueAttachment.objects.filter(issue_id=self.kwargs["issue_pk"])

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs["issue_pk"])
        serializer.save(issue=issue, uploaded_by_id=self.request.user_id)
