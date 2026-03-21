from django.urls import path
from . import views

urlpatterns = [
    path("", views.TimeEntryListCreateView.as_view()),
    path("<int:pk>/", views.TimeEntryDetailView.as_view()),
    path("timer/", views.TimerSessionView.as_view()),
    path("capacity/", views.resource_capacity),
    path("allocations/", views.ResourceAllocationListView.as_view()),
    path("allocations/<int:pk>/", views.ResourceAllocationDetailView.as_view()),
    path("projects/<int:project_pk>/export-billable/", views.ExportBillableHoursView.as_view()),
]
