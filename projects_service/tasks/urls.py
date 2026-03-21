from django.urls import path
from . import views

urlpatterns = [
    path("<int:project_pk>/columns/", views.ColumnListCreateView.as_view()),
    path("<int:project_pk>/columns/<int:pk>/", views.ColumnDetailView.as_view()),
    path("<int:project_pk>/kanban/", views.KanbanBoardView.as_view()),
    path("<int:project_pk>/", views.TaskListCreateView.as_view()),
    path("<int:project_pk>/<int:pk>/", views.TaskDetailView.as_view()),
    path("<int:project_pk>/<int:pk>/move/", views.MoveTaskView.as_view()),
    path("<int:project_pk>/<int:task_pk>/comments/", views.TaskCommentListView.as_view()),
    path("<int:project_pk>/<int:task_pk>/comments/<int:pk>/", views.TaskCommentDetailView.as_view()),
    path("<int:project_pk>/<int:task_pk>/attachments/", views.TaskAttachmentListView.as_view()),
    path("<int:project_pk>/<int:task_pk>/dependencies/", views.TaskDependencyListView.as_view()),
    path("<int:project_pk>/labels/", views.TaskLabelListCreateView.as_view()),
    path("<int:project_pk>/<int:pk>/watch/", views.WatchTaskView.as_view()),
]
