from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda request: JsonResponse({"status": "ok"})),
    path("api/projects/", include("projects_service.projects.urls")),
    path("api/tasks/", include("projects_service.tasks.urls")),
    path("api/timelog/", include("projects_service.timelog.urls")),
    path("api/issues/", include("projects_service.issues.urls")),
    path("api/notifications/", include("projects_service.notifications.urls")),
]
