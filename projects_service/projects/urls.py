from django.urls import path
from . import views
from .views.product_views import (
    search_materials,
    get_material,
    list_materials,
    get_materials_bulk,
    check_material_stock,
)

urlpatterns = [
    path("", views.ProjectListCreateView.as_view()),
    path("<int:pk>/", views.ProjectDetailView.as_view()),
    path("<int:pk>/gantt/", views.project_gantt),
    path("<int:pk>/budget/", views.project_budget),
    path("<int:project_pk>/members/", views.ProjectMemberListView.as_view()),
    path("<int:project_pk>/members/<int:pk>/", views.ProjectMemberDetailView.as_view()),
    path("<int:project_pk>/sprints/", views.SprintListCreateView.as_view()),
    path("<int:project_pk>/sprints/<int:pk>/", views.SprintDetailView.as_view()),
    path("<int:project_pk>/sprints/<int:pk>/start/", views.StartSprintView.as_view()),
    path("<int:project_pk>/sprints/<int:pk>/complete/", views.CompleteSprintView.as_view()),
    path("<int:project_pk>/milestones/", views.MilestoneListCreateView.as_view()),
    path("<int:project_pk>/milestones/<int:pk>/", views.MilestoneDetailView.as_view()),
    path("<int:project_pk>/risks/", views.ProjectRiskListCreateView.as_view()),
    path("<int:project_pk>/risks/<int:pk>/", views.ProjectRiskDetailView.as_view()),
    path("<int:project_pk>/documents/", views.ProjectDocumentListView.as_view()),
    # Material query endpoints (from inventory service)
    path("materials/", list_materials, name="list_materials"),
    path("materials/search/", search_materials, name="search_materials"),
    path("materials/bulk/", get_materials_bulk, name="get_materials_bulk"),
    path("materials/<uuid:product_id>/", get_material, name="get_material"),
    path("materials/<uuid:product_id>/stock/", check_material_stock, name="check_material_stock"),
]
