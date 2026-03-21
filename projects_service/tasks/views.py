from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Task, TaskComment, TaskAttachment, TaskDependency, TaskLabel, Column, TaskWatcher
from .serializers import (
    TaskSerializer, TaskListSerializer, TaskCommentSerializer, TaskAttachmentSerializer,
    TaskDependencySerializer, TaskLabelSerializer, ColumnSerializer, KanbanColumnSerializer
)
from projects_service.projects.models import Project
from projects_service.notifications.utils import notify_project_members


class ColumnListCreateView(generics.ListCreateAPIView):
    serializer_class = ColumnSerializer

    def get_queryset(self):
        return Column.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class ColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ColumnSerializer

    def get_queryset(self):
        return Column.objects.filter(project_id=self.kwargs["project_pk"])


class KanbanBoardView(APIView):
    def get(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk, corporate_id=request.corporate_id)
        columns = Column.objects.filter(project=project).order_by("order")
        return Response(KanbanColumnSerializer(columns, many=True).data)


class TaskListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskListSerializer
        return TaskSerializer

    def get_queryset(self):
        project_pk = self.kwargs.get("project_pk")
        qs = Task.objects.filter(project_id=project_pk)
        status_filter = self.request.query_params.get("status")
        sprint_id = self.request.query_params.get("sprint")
        assignee = self.request.query_params.get("assignee")
        task_type = self.request.query_params.get("type")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if sprint_id:
            qs = qs.filter(sprint_id=sprint_id)
        if assignee:
            qs = qs.filter(assignee_id=assignee)
        if task_type:
            qs = qs.filter(task_type=task_type)
        return qs.select_related("sprint", "column", "parent").prefetch_related("labels")

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        task = serializer.save(project=project, reporter_id=self.request.user_id)
        notify_project_members(
            project_id=project.pk,
            event="task_created",
            data={"task_id": task.pk, "title": task.title, "created_by": self.request.user_id},
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        task = serializer.save()
        if task.status == Task.STATUS_DONE and old_status != Task.STATUS_DONE:
            task.completed_at = timezone.now()
            task.save(update_fields=["completed_at"])
        notify_project_members(
            project_id=task.project_id,
            event="task_updated",
            data={"task_id": task.pk, "title": task.title, "updated_by": self.request.user_id},
        )


class MoveTaskView(APIView):
    """Move a task to a different column and/or sprint (Kanban drag-and-drop)."""
    def post(self, request, project_pk, pk):
        task = get_object_or_404(Task, pk=pk, project_id=project_pk)
        column_id = request.data.get("column_id")
        sprint_id = request.data.get("sprint_id")
        new_status = request.data.get("status")
        order = request.data.get("order")
        if column_id is not None:
            task.column_id = column_id
        if sprint_id is not None:
            task.sprint_id = sprint_id
        if new_status:
            task.status = new_status
            if new_status == Task.STATUS_DONE:
                task.completed_at = timezone.now()
        if order is not None:
            task.order = order
        task.save()
        notify_project_members(
            project_id=project_pk,
            event="task_moved",
            data={"task_id": task.pk, "column_id": column_id, "moved_by": request.user_id},
        )
        return Response(TaskSerializer(task).data)


class TaskCommentListView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs["task_pk"])

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        comment = serializer.save(task=task, author_id=self.request.user_id)
        notify_project_members(
            project_id=task.project_id,
            event="task_comment",
            data={"task_id": task.pk, "comment_id": comment.pk, "author_id": self.request.user_id},
        )


class TaskCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskCommentSerializer

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs["task_pk"])


class TaskAttachmentListView(generics.ListCreateAPIView):
    serializer_class = TaskAttachmentSerializer

    def get_queryset(self):
        return TaskAttachment.objects.filter(task_id=self.kwargs["task_pk"])

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        serializer.save(task=task, uploaded_by_id=self.request.user_id)


class TaskDependencyListView(generics.ListCreateAPIView):
    serializer_class = TaskDependencySerializer

    def get_queryset(self):
        return TaskDependency.objects.filter(task_id=self.kwargs["task_pk"])

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        serializer.save(task=task)


class TaskLabelListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskLabelSerializer

    def get_queryset(self):
        return TaskLabel.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class WatchTaskView(APIView):
    def post(self, request, project_pk, pk):
        task = get_object_or_404(Task, pk=pk, project_id=project_pk)
        watcher, _ = TaskWatcher.objects.get_or_create(task=task, user_id=request.user_id)
        return Response({"watching": True})

    def delete(self, request, project_pk, pk):
        task = get_object_or_404(Task, pk=pk, project_id=project_pk)
        TaskWatcher.objects.filter(task=task, user_id=request.user_id).delete()
        return Response({"watching": False})
