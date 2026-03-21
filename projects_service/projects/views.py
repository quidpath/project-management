from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum as models_sum
from django.shortcuts import get_object_or_404
from .models import Project, ProjectMember, Sprint, Milestone, ProjectRisk, ProjectDocument
from .serializers import (
    ProjectSerializer, ProjectListSerializer, ProjectMemberSerializer,
    SprintSerializer, MilestoneSerializer, ProjectRiskSerializer, ProjectDocumentSerializer
)


class ProjectListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.filter(corporate_id=self.request.corporate_id)
        status_filter = self.request.query_params.get("status")
        methodology = self.request.query_params.get("methodology")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if methodology:
            qs = qs.filter(methodology=methodology)
        return qs.prefetch_related("members", "sprints", "milestones")

    def perform_create(self, serializer):
        serializer.save(
            corporate_id=self.request.corporate_id,
            owner_id=self.request.user_id,
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(corporate_id=self.request.corporate_id)


class ProjectMemberListView(generics.ListCreateAPIView):
    serializer_class = ProjectMemberSerializer

    def get_queryset(self):
        return ProjectMember.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class ProjectMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectMemberSerializer

    def get_queryset(self):
        return ProjectMember.objects.filter(project_id=self.kwargs["project_pk"])


class SprintListCreateView(generics.ListCreateAPIView):
    serializer_class = SprintSerializer

    def get_queryset(self):
        return Sprint.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class SprintDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SprintSerializer

    def get_queryset(self):
        return Sprint.objects.filter(project_id=self.kwargs["project_pk"])


class StartSprintView(APIView):
    def post(self, request, project_pk, pk):
        sprint = get_object_or_404(Sprint, pk=pk, project_id=project_pk)
        # Mark any active sprint as completed first
        Sprint.objects.filter(project_id=project_pk, status=Sprint.STATUS_ACTIVE).update(
            status=Sprint.STATUS_COMPLETED
        )
        sprint.status = Sprint.STATUS_ACTIVE
        sprint.save()
        return Response(SprintSerializer(sprint).data)


class CompleteSprintView(APIView):
    def post(self, request, project_pk, pk):
        sprint = get_object_or_404(Sprint, pk=pk, project_id=project_pk)
        sprint.status = Sprint.STATUS_COMPLETED
        # Move unfinished tasks to backlog
        incomplete = sprint.sprint_tasks.exclude(status="done")
        incomplete.update(sprint=None)
        sprint.velocity = sprint.sprint_tasks.filter(status="done").aggregate(
            total=models_sum("story_points")
        )["total"] or 0
        sprint.save()
        return Response(SprintSerializer(sprint).data)


class MilestoneListCreateView(generics.ListCreateAPIView):
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        return Milestone.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class MilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        return Milestone.objects.filter(project_id=self.kwargs["project_pk"])


class ProjectRiskListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectRiskSerializer

    def get_queryset(self):
        return ProjectRisk.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project)


class ProjectRiskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectRiskSerializer

    def get_queryset(self):
        return ProjectRisk.objects.filter(project_id=self.kwargs["project_pk"])


class ProjectDocumentListView(generics.ListCreateAPIView):
    serializer_class = ProjectDocumentSerializer

    def get_queryset(self):
        return ProjectDocument.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"],
                                    corporate_id=self.request.corporate_id)
        serializer.save(project=project, uploaded_by_id=self.request.user_id)


@api_view(["GET"])
def project_gantt(request, pk):
    """Return tasks with dates formatted for Gantt chart rendering."""
    project = get_object_or_404(Project, pk=pk, corporate_id=request.corporate_id)
    tasks = project.project_tasks.select_related("parent").order_by("start_date")
    data = []
    for task in tasks:
        data.append({
            "id": task.pk,
            "title": task.title,
            "start": str(task.start_date) if task.start_date else None,
            "end": str(task.due_date) if task.due_date else None,
            "progress": task.progress,
            "assignee_id": task.assignee_id,
            "parent_id": task.parent_id,
            "status": task.status,
            "story_points": task.story_points,
        })
    return Response({"project": project.name, "tasks": data})


@api_view(["GET"])
def project_budget(request, pk):
    """Return budget vs actual spend breakdown."""
    from projects_service.timelog.models import TimeEntry
    from django.db.models import Sum
    project = get_object_or_404(Project, pk=pk, corporate_id=request.corporate_id)
    logged_hours = TimeEntry.objects.filter(
        project=project, is_billable=True
    ).aggregate(total=Sum("hours"))["total"] or 0
    billable_amount = float(logged_hours) * float(project.hourly_rate)
    return Response({
        "project_id": project.pk,
        "budget": project.budget,
        "hours_budget": project.hours_budget,
        "logged_hours": logged_hours,
        "billable_amount": billable_amount,
        "budget_utilization_pct": round(
            (billable_amount / float(project.budget) * 100) if project.budget else 0, 1
        ),
    })
