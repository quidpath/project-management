from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from .models import TimeEntry, TimerSession, ResourceAllocation
from .serializers import TimeEntrySerializer, TimerSessionSerializer, ResourceAllocationSerializer
from projects_service.projects.models import Project
from projects_service.tasks.models import Task
from projects_service.services.erp_client import ERPClient


class TimeEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        qs = TimeEntry.objects.filter(project__corporate_id=self.request.corporate_id)
        project_id = self.request.query_params.get("project")
        user_id = self.request.query_params.get("user")
        is_billable = self.request.query_params.get("billable")
        is_invoiced = self.request.query_params.get("invoiced")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if is_billable is not None:
            qs = qs.filter(is_billable=is_billable.lower() == "true")
        if is_invoiced is not None:
            qs = qs.filter(is_invoiced=is_invoiced.lower() == "true")
        return qs

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.request.data.get("project"),
                                    corporate_id=self.request.corporate_id)
        serializer.save(user_id=self.request.user_id, project=project)


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        return TimeEntry.objects.filter(project__corporate_id=self.request.corporate_id)


class TimerSessionView(APIView):
    """Start/stop/status of active timer for the current user."""

    def get(self, request):
        try:
            session = TimerSession.objects.get(user_id=request.user_id)
            return Response(TimerSessionSerializer(session).data)
        except TimerSession.DoesNotExist:
            return Response({"active": False})

    def post(self, request):
        """Start timer."""
        TimerSession.objects.filter(user_id=request.user_id).delete()
        project = get_object_or_404(Project, pk=request.data.get("project_id"),
                                    corporate_id=request.corporate_id)
        session = TimerSession.objects.create(
            user_id=request.user_id,
            project=project,
            task_id=request.data.get("task_id"),
            description=request.data.get("description", ""),
            is_billable=request.data.get("is_billable", False),
        )
        return Response(TimerSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """Stop timer and create a TimeEntry."""
        try:
            session = TimerSession.objects.get(user_id=request.user_id)
        except TimerSession.DoesNotExist:
            return Response({"error": "No active timer"}, status=status.HTTP_400_BAD_REQUEST)

        elapsed = timezone.now() - session.started_at
        hours = round(elapsed.total_seconds() / 3600, 2)

        entry = TimeEntry.objects.create(
            project=session.project,
            task=session.task,
            user_id=request.user_id,
            description=session.description,
            date=timezone.now().date(),
            hours=hours,
            is_billable=session.is_billable,
        )
        session.delete()
        return Response(TimeEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class ExportBillableHoursView(APIView):
    """Export uninvoiced billable hours to ERP for invoicing."""

    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk, corporate_id=request.corporate_id)
        entries = TimeEntry.objects.filter(project=project, is_billable=True, is_invoiced=False)
        if not entries.exists():
            return Response({"message": "No uninvoiced billable hours"})

        total_hours = entries.aggregate(total=Sum("hours"))["total"] or 0
        total_amount = sum(float(e.hours) * float(e.hourly_rate or project.hourly_rate) for e in entries)

        client = ERPClient()
        try:
            invoice = client.export_billable_hours(
                {
                    "project_id": project.pk,
                    "project_name": project.name,
                    "client_id": project.client_id,
                    "total_hours": float(total_hours),
                    "total_amount": total_amount,
                    "currency": project.budget_currency,
                    "entries": [
                        {
                            "date": str(e.date),
                            "description": e.description,
                            "hours": float(e.hours),
                            "rate": float(e.hourly_rate or project.hourly_rate),
                        }
                        for e in entries
                    ],
                },
                corporate_id=request.corporate_id,
            )
            entries.update(is_invoiced=True, invoice_id=invoice.get("id"))
            return Response({"invoice": invoice, "entries_invoiced": entries.count()})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


class ResourceAllocationListView(generics.ListCreateAPIView):
    serializer_class = ResourceAllocationSerializer

    def get_queryset(self):
        qs = ResourceAllocation.objects.filter(project__corporate_id=self.request.corporate_id)
        project_id = self.request.query_params.get("project")
        user_id = self.request.query_params.get("user")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class ResourceAllocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResourceAllocationSerializer

    def get_queryset(self):
        return ResourceAllocation.objects.filter(project__corporate_id=self.request.corporate_id)


@api_view(["GET"])
def resource_capacity(request):
    """Overview of team capacity vs logged hours per user per week."""
    from datetime import date, timedelta
    start = request.query_params.get("start", str(date.today() - timedelta(days=7)))
    end = request.query_params.get("end", str(date.today()))
    corporate_id = request.corporate_id

    logged = (
        TimeEntry.objects
        .filter(project__corporate_id=corporate_id, date__range=[start, end])
        .values("user_id")
        .annotate(logged_hours=Sum("hours"))
    )
    allocated = (
        ResourceAllocation.objects
        .filter(project__corporate_id=corporate_id, start_date__lte=end, end_date__gte=start)
        .values("user_id")
        .annotate(allocated_hours=Sum("allocated_hours_per_day"))
    )
    return Response({"logged": list(logged), "allocated": list(allocated)})
